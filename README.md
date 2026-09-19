# EEO Video Guide

Single-page video guide for the Equal Employment Opportunity **Institutional Best
Practices (IBP) Grant Initiative**, California Community Colleges Chancellor's Office.
Live at [eeodashboard.io](https://eeodashboard.io).

## How it works

| File | Purpose |
| --- | --- |
| `index.html` | The whole site — markup, styles and script inline, no build step. |
| `404.html` | Branded not-found page served by GitHub Pages. |
| `CNAME` | Custom domain (`eeodashboard.io`). |
| `.github/workflows/static.yml` | Deploys the repo root to GitHub Pages on every push to `main`. |

The video is **streamed from Cloudflare Stream**, not served from this repo, so the
site stays small and plays back well on campus networks. To point at a different
video, replace the Cloudflare video ID in the `<iframe>` `src` in `index.html`
(it also appears in the poster URL and the social-preview `og:image`/`twitter:image` tags).

## Editing

Open `index.html` in a browser — that's the full preview. No dependencies, no build.

To swap the placeholder logo lockup for the official mark, commit the image as
`cccco-logo.png` at the repo root; the page picks it up automatically.

## Conventions

- Keep raw video files out of the repo (`.gitignore` blocks `*.mov` / `*.mp4`) —
  upload them to Cloudflare Stream and reference the ID instead.
- This is a public-sector site, so keep it accessible: every control reachable by
  keyboard with a visible focus ring, the player `<iframe>` titled, and text
  contrast at WCAG AA or better.
