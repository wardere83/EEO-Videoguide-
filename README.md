# EEO IBP Grant Initiative

React + TypeScript + Vite experience for eeodashboard.io. Presents the CCCCO EEO Innovative Best Practices Grant Initiative through a motion story, funding visualization, resource destination, and interactive mobile dashboard preview.

## Development

```sh
npm ci
npm run dev
npm run build
npm run test:e2e
```

HashRouter supports direct links and refreshes on GitHub Pages. `src/config.ts` holds the external service links. Components, pages, and configuration are separated. No district records or authentication credentials are stored here. The public resource workspace routes users to the existing authenticated EEO Dashboard. The mobile product walkthrough uses explicitly illustrative sample data and does not implement the portal backend.

## Branding

The unmodified three-color stacked SVG and PNG in `public/brand/` come from the official CCCCO vertical logo package at https://www.cccco.edu/About-Us/News-and-Media/Brand/assets/ . Display them with their original proportions and clear space. Self-hosted fonts are Crimson Text and Source Sans Pro (distributed by Google Fonts); navy #002F6D, darker blue #002755, gold #FFB600, and grey #555759 follow the same official brand source. Gold is used decoratively or behind navy text, not as text on white.

## Publishing

Pull requests run the production build. Merging into main builds `dist` and deploys it through the existing GitHub Pages workflow. `public/CNAME` preserves eeodashboard.io. The site features a 64-second silent cinematic motion story with English captions, a transcript, custom playback controls, interactive chapters, a district award network, a sustainable-impact sequence, and a funding explorer grounded in published CCCCO records. The video contains no audio stream and no embedded logo; website branding remains outside the film. `src/film.json`, `src/funding.json`, and `src/grantees.json` control the public narrative; see `docs/content-sources.md`. `scripts/render-film.py` reproduces the video using Pillow and ffmpeg. The externally hosted portal handles district permissions and sign-in.

The WebM fallback supports browsers without H.264 playback. The browser tests require `npx playwright install chromium --with-deps`.

## Existing Pages compatibility

The Vite entry is `web/index.html`. The production build publishes into `dist` and mirrors generated assets at the repository root, matching the existing branch-based Pages configuration. Both hosting paths serve the same compiled application. After source changes, run `npm run build` and commit generated root files with the source. Do not manually edit root `index.html`; edit `web/index.html`.
