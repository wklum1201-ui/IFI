#!/usr/bin/env python3
"""Build a Word security assessment report from a findings JSON file.

Usage: generate_security_report.py findings.json output.docx
"""
import json
import sys
from collections import Counter
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

SEVERITIES = ["Critical", "High", "Medium", "Low", "Informational"]
COLORS = {"Critical": "9F1F1F", "High": "D9480F", "Medium": "E8A317",
          "Low": "2F7D32", "Informational": "5B636D"}
NAVY = RGBColor(0x1F, 0x2A, 0x44)


def shade(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill)
    tcPr.append(shd)


def set_cell(cell, text, bold=False, color=None, size=9.5, fill=None, align=None):
    cell.text = ""
    p = cell.paragraphs[0]
    run = p.add_run(str(text))
    run.bold = bold
    run.font.size = Pt(size)
    if color:
        run.font.color.rgb = RGBColor.from_string(color)
    if align:
        p.alignment = align
    if fill:
        shade(cell, fill)


def table(doc, headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        set_cell(t.rows[0].cells[i], h, bold=True, color="FFFFFF", fill="1F2A44")
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            if isinstance(v, tuple):  # (text, severity) -> coloured badge
                set_cell(cells[i], v[0], bold=True, color="FFFFFF", fill=COLORS.get(v[1], "5B636D"),
                         align=WD_ALIGN_PARAGRAPH.CENTER)
            else:
                set_cell(cells[i], v)
    if widths:
        for r in t.rows:
            for i, w in enumerate(widths):
                r.cells[i].width = Pt(w)
    doc.add_paragraph()
    return t


def code(doc, text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.name = "Consolas"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
    r.font.size = Pt(8.5)
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), "F2F4F7")
    pPr.append(shd)


def bullets(doc, items):
    for i in items:
        doc.add_paragraph(str(i), style="List Bullet")


def add_page_number(section):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("Confidential – Security Assessment    |    Page ").font.size = Pt(8)
    run = p.add_run()
    for kind, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        if kind:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), kind)
        else:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = txt
        run._r.append(el)
    run.font.size = Pt(8)


def overall_rating(counts):
    for s in SEVERITIES[:4]:
        if counts.get(s):
            return s
    return "Informational"


def main(src, dst):
    data = json.loads(Path(src).read_text(encoding="utf-8"))
    meta = data.get("meta", {})
    findings = data.get("findings", [])
    order = {s: i for i, s in enumerate(SEVERITIES)}
    findings.sort(key=lambda f: (order.get(f.get("severity"), 9), -float(f.get("cvss_score") or 0)))
    counts = Counter(f.get("severity") for f in findings)

    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(10.5)
    for name, size in (("Heading 1", 18), ("Heading 2", 14), ("Heading 3", 12)):
        h = doc.styles[name]
        h.font.name = "Calibri"
        h.font.size = Pt(size)
        h.font.color.rgb = NAVY
    add_page_number(doc.sections[0])

    # Cover
    for _ in range(5):
        doc.add_paragraph()
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = t.add_run(meta.get("title", "Security Assessment Report"))
    r.bold = True
    r.font.size = Pt(30)
    r.font.color.rgb = NAVY
    s = doc.add_paragraph()
    s.alignment = WD_ALIGN_PARAGRAPH.CENTER
    s.add_run(meta.get("target", "")).font.size = Pt(14)
    doc.add_paragraph()
    info = [("Repository", meta.get("repository", "")), ("Commit", meta.get("commit", "")),
            ("Assessment date", meta.get("date", "")), ("Assessor", meta.get("assessor", "")),
            ("Classification", "Confidential")]
    ct = doc.add_table(rows=0, cols=2)
    ct.style = "Table Grid"
    ct.alignment = WD_TABLE_ALIGNMENT.CENTER
    for k, v in info:
        c = ct.add_row().cells
        set_cell(c[0], k, bold=True, fill="E8ECF2", size=10.5)
        set_cell(c[1], v, size=10.5)
    doc.add_page_break()

    # Executive summary
    doc.add_heading("1. Executive Summary", 1)
    doc.add_paragraph(data.get("executive_summary", ""))
    overall = overall_rating(counts)
    p = doc.add_paragraph()
    p.add_run("Overall risk rating: ").bold = True
    rr = p.add_run(overall.upper())
    rr.bold = True
    rr.font.color.rgb = RGBColor.from_string(COLORS[overall])
    doc.add_heading("Findings by severity", 2)
    total = len(findings) or 1
    table(doc, ["Severity", "Count", "Share", "Distribution"],
          [[(s, s), counts.get(s, 0), f"{counts.get(s, 0) * 100 // total}%",
            "█" * counts.get(s, 0)] for s in SEVERITIES] + [["Total", len(findings), "100%", ""]],
          [90, 60, 60, 220])
    if data.get("positive_observations"):
        doc.add_heading("Positive observations", 2)
        bullets(doc, data["positive_observations"])

    # Scope & method
    doc.add_heading("2. Scope and Methodology", 1)
    doc.add_heading("In scope", 2)
    bullets(doc, meta.get("scope", []))
    doc.add_heading("Methodology", 2)
    bullets(doc, meta.get("methodology", []))
    doc.add_heading("Severity rating scale (CVSS v3.1)", 2)
    table(doc, ["Severity", "CVSS range", "Meaning"], [
        [("Critical", "Critical"), "9.0 – 10.0", "Trivially exploitable, severe impact; fix immediately."],
        [("High", "High"), "7.0 – 8.9", "Exploitable with significant impact; fix within days."],
        [("Medium", "Medium"), "4.0 – 6.9", "Exploitable under conditions or limited impact; fix within 30 days."],
        [("Low", "Low"), "0.1 – 3.9", "Minor impact or hard to exploit; fix when convenient."],
        [("Informational", "Informational"), "0.0", "Best-practice gap with no direct exploit path."]],
          [90, 80, 270])

    # Classification
    doc.add_heading("3. Vulnerability Classification", 1)
    doc.add_heading("Summary of findings", 2)
    table(doc, ["ID", "Title", "Severity", "CVSS", "CWE", "OWASP 2021"],
          [[f.get("id"), f.get("title"), (f.get("severity"), f.get("severity")),
            f.get("cvss_score", ""), f.get("cwe", ""), f.get("owasp", "")] for f in findings],
          [50, 160, 60, 40, 110, 100])

    def group(key, heading):
        doc.add_heading(heading, 2)
        g = {}
        for f in findings:
            g.setdefault(f.get(key) or "Unclassified", []).append(f)
        table(doc, [heading.replace("By ", ""), "Count", "Finding IDs", "Highest severity"],
              [[k, len(v), ", ".join(x["id"] for x in v),
                min((x.get("severity") for x in v), key=lambda s: order.get(s, 9))]
               for k, v in sorted(g.items(), key=lambda kv: -len(kv[1]))],
              [150, 40, 150, 90])

    group("owasp", "By OWASP Top 10 (2021) category")
    group("category", "By vulnerability category")
    group("cwe", "By CWE")

    doc.add_heading("Risk matrix (likelihood × impact)", 2)
    levels = ["High", "Medium", "Low"]
    mt = doc.add_table(rows=1, cols=4)
    mt.style = "Table Grid"
    set_cell(mt.rows[0].cells[0], "Likelihood \\ Impact", bold=True, color="FFFFFF", fill="1F2A44")
    for i, l in enumerate(reversed(levels), 1):
        set_cell(mt.rows[0].cells[i], l, bold=True, color="FFFFFF", fill="1F2A44")
    score = {"High": 3, "Medium": 2, "Low": 1}
    fills = {6: "F4B6B6", 9: "F4B6B6", 4: "F9D9A6", 3: "F9D9A6", 2: "CDE8CF", 1: "CDE8CF"}
    for lk in levels:
        c = mt.add_row().cells
        set_cell(c[0], lk, bold=True, fill="E8ECF2")
        for i, im in enumerate(reversed(levels), 1):
            ids = [f["id"] for f in findings if f.get("likelihood") == lk and f.get("impact") == im]
            set_cell(c[i], ", ".join(ids), fill=fills[score[lk] * score[im]], size=8.5)
    doc.add_paragraph()

    # Details
    doc.add_page_break()
    doc.add_heading("4. Detailed Findings", 1)
    for f in findings:
        doc.add_heading(f"{f.get('id')} – {f.get('title')}", 2)
        table(doc, ["Attribute", "Value"], [
            ["Severity", (f"{f.get('severity')} (CVSS {f.get('cvss_score', 'n/a')})", f.get("severity"))],
            ["CVSS vector", f.get("cvss_vector", "")], ["CWE", f.get("cwe", "")],
            ["OWASP Top 10", f.get("owasp", "")], ["Category", f.get("category", "")],
            ["Likelihood / Impact", f"{f.get('likelihood', '')} / {f.get('impact', '')}"],
            ["Effort to fix", f.get("effort", "")], ["Status", f.get("status", "Open")],
            ["Location", f.get("location", "")]], [110, 330])
        for label, key in (("Description", "description"), ("Business impact", "impact_detail")):
            if f.get(key):
                doc.add_paragraph().add_run(label).bold = True
                doc.add_paragraph(f[key])
        if f.get("evidence"):
            doc.add_paragraph().add_run("Evidence").bold = True
            code(doc, f["evidence"])
        if f.get("remediation"):
            doc.add_paragraph().add_run("Remediation").bold = True
            doc.add_paragraph(f["remediation"])
        if f.get("references"):
            doc.add_paragraph().add_run("References").bold = True
            bullets(doc, f["references"])

    # Roadmap
    doc.add_heading("5. Remediation Roadmap", 1)
    for item in data.get("remediation_roadmap", []):
        doc.add_heading(item.get("priority", ""), 3)
        bullets(doc, item.get("actions", []))

    doc.add_heading("6. Limitations", 1)
    bullets(doc, meta.get("limitations", ["None recorded."]))
    doc.add_paragraph("This report reflects the state of the application at the commit and date above. "
                      "Automated and manual review cannot guarantee the absence of vulnerabilities.")

    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    doc.save(dst)
    print(f"Wrote {dst} ({len(findings)} findings)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
