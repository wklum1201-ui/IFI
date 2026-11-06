# IT PMO – Project Board

A single-file Kanban board demo for an IT Project Management Office. Track projects across **Backlog, In Progress, Blocked and Done**, with priorities, categories and project groupings.

**Live demo:** https://wklum1201-ui.github.io/IFI/

## Features
- Four-column Kanban board with a corporate blue theme
- Project, category and priority metadata on every card
- Zero dependencies: one `index.html`, no build step
- In-memory state only (no browser storage APIs)
- Optional email notification via [FormSubmit](https://formsubmit.co)

## Run locally
Open `index.html` in a browser, or serve it:

```bash
python3 -m http.server 8000   # then visit http://localhost:8000
```

## Configuration
Set the notification address in `index.html` (`FORMSUBMIT_ENDPOINT`). The default is a placeholder, `YOUR_EMAIL@example.com`. Note that anything placed in a public static page is visible to everyone, so use an address you are happy to publish.

## Project structure
```
index.html                   # the whole app (HTML + CSS + JS)
.github/workflows/ci.yml     # HTML validation on push / PR
.github/workflows/pages.yml  # deploys to GitHub Pages
```

## Tech stack
Vanilla HTML, CSS and JavaScript. CI/CD with GitHub Actions; hosting on GitHub Pages.
