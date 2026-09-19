# EEO IBP Grant Initiative

React + TypeScript + Vite experience for eeodashboard.io. Adapts XpressTend’s public landing page, video feature, capability showcase, resource destination, and separate routed screens to CCCCO’s EEO Innovative Best Practices Grant Initiative.

## Development

```sh
npm ci
npm run dev
npm run build
npm run test:e2e
```

HashRouter supports direct links and refreshes on GitHub Pages. `src/config.ts` holds the external service links. Components, pages, and configuration are separated. No district records or authentication credentials are stored here. The public resource workspace routes users to the existing authenticated EEO Dashboard; this repository does not implement its backend or duplicate XpressTend’s financial services and native mobile layers.

## Branding

The unmodified three-color horizontal SVG in `public/brand/cccco-logo.svg` comes from https://www.cccco.edu/-/media/CCCCO-Website/Files/Communications/Brand/ccc-logos-horizontal . Display it with its original proportions and clear space. Self-hosted fonts are Crimson Text and Source Sans Pro (distributed by Google Fonts); navy #002F6D, darker blue #002755, gold #FFB600, and grey #555759 follow https://www.cccco.edu/About-Us/News-and-Media/Brand/assets/ . Gold is used decoratively or behind navy text, not as text on white.

## Publishing

Pull requests run the production build. Merging into main builds `dist` and deploys it through the existing GitHub Pages workflow. `public/CNAME` preserves eeodashboard.io. The old stream is replaced by a new 100-second 1080p silent initiative film, with English captions, a transcript, and thematic chapter navigation. The video has no narration or music. The 11 districts appear only within the film, in a brief project showcase. `src/film.json` controls its storyline and `src/grantees.json` contains only short public-facing project summaries; see `docs/content-sources.md`. `scripts/render-film.py` reproduces the video using Pillow and ffmpeg with the official logo PNG. The externally hosted portal handles district permissions and sign-in.

The WebM fallback supports browsers without H.264 playback. The browser tests require `npx playwright install chromium --with-deps`.

## Existing Pages compatibility

The Vite entry is `web/index.html`. The production build publishes into `dist` and mirrors generated assets at the repository root, matching the existing branch-based Pages configuration. Both hosting paths serve the same compiled application. After source changes, run `npm run build` and commit generated root files with the source. Do not manually edit root `index.html`; edit `web/index.html`.
