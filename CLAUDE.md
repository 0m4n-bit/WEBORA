# WEBORA website – notes for Claude

- Static marketing site, no dependencies. Source of truth for copy: `content/{ar,en}.json`. Layout/markup: `build.py`. Styles: `src/style.css`. Behaviour: `src/main.js`.
- Always run `python3 build.py` after any change and commit the regenerated `public/` together with the source change.
- Arabic (RTL) is the default at the site root; English (LTR) under `/en/`. Every change must be made in both languages.
- Brand: bg #0B1428 / #101C35, text #E8EFF8, accent #128BC0 (buttons #0E78AA), secondary #C0D6F2. Fonts: IBM Plex Sans Arabic + Inter. Formal tone.
- Target sectors: salons/beauty, clinics, clothing & product stores (no restaurants). Pricing not published yet ("coming soon").
- Contact: WhatsApp/phone +968 9746 4626. Domain not chosen yet — set `SITE_URL` in build.py when it is.
- Hosting: GitHub Pages via `.github/workflows/deploy-pages.yml` (BASE_PATH env set from configure-pages). Keep all page links relative.
- Before committing: check pages at 1440px and 390px (no horizontal overflow, mobile menu works, form opens WhatsApp).
