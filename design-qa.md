# Caishen Fortune Overlay QA

Date: 2026-07-05

## Scope

- Reworked the home-page Caishen interaction into a full-screen cinematic shrine overlay.
- Kept the home-page macro layout intact.
- Moved zodiac, constellation, draw-date selection, offering, and final number reveal into the overlay.
- Fixed the interaction order: users can make offerings before shaking; generated results remain once-per-device-per-day.

## Visual Notes

- Added `frontend/public/assets/caishen-cinematic-shrine.png` as a dedicated dark-gold shrine scene.
- The implementation now uses a single dark ceremonial panel with an integrated visual stage, result panel, offering dock, and point bar.
- The remaining gap from the reference mockup is asset-level: the current scene uses the existing standing Caishen mascot instead of a newly generated seated/open-arm mascot.

## Verification

- `frontend`: `npm run build` passed.
- `backend`: `python -m compileall app` passed.
- Desktop viewport QA: `1440x900`
  - No horizontal overflow.
  - Offering dock and point bar fit in viewport before shaking.
  - Result overlay shows 7 balls and fits in viewport.
- Mobile viewport QA: `390x844`
  - No horizontal overflow.
  - Result title, balls, and action buttons are visible in viewport.
- Console errors: none during automated Chrome QA.

## QA Artifacts

Generated locally and intentionally left untracked:

- `D:/lottery-dev/qa-caishen-cinematic-viewport-setup.png`
- `D:/lottery-dev/qa-caishen-cinematic-viewport-pre-offering.png`
- `D:/lottery-dev/qa-caishen-cinematic-viewport-after-offering.png`
- `D:/lottery-dev/qa-caishen-cinematic-viewport-result.png`
- `D:/lottery-dev/qa-caishen-cinematic-viewport-mobile-result.png`
