**Findings**
- No actionable P0/P1/P2 findings remain.

**Source Visual Truth**
- Home reference: `C:/Users/Yvette/AppData/Local/Temp/codex-clipboard-61d2806a-16f4-4650-bc9e-061939691e10.png`
- Overlay reference: `C:/Users/Yvette/AppData/Local/Temp/codex-clipboard-3e2c18dd-e905-4f36-a017-b80407b510f4.png`

**Implementation Screenshots**
- Home implementation: `D:/lottery-caishen-ref-20260704/qa-caishen-home-v5.png`
- Overlay setup state: `D:/lottery-caishen-ref-20260704/qa-caishen-layout-refined-setup.png`
- Overlay result state: `D:/lottery-caishen-ref-20260704/qa-caishen-layout-refined-result.png`
- Mobile home: `D:/lottery-caishen-ref-20260704/qa-caishen-mobile-home-v6.png`
- Mobile overlay setup: `D:/lottery-caishen-ref-20260704/qa-caishen-layout-refined-mobile-setup.png`

**Viewport**
- Desktop: `1728 x 1100`
- Mobile: `390 x 844`, device scale factor `2`

**State**
- Lottery type: `ssq`
- Home: default first-screen state with Caishen feature presented as a visual entry only.
- Overlay setup: zodiac/constellation selection lives inside the full-screen shrine.
- Overlay result: completed zodiac/constellation flow, draw date selected, fortune result and offering dock visible.

**Verification**
- `npm run build` passed in `D:/lottery-caishen-ref-20260704/frontend`.
- `python -m compileall app` passed in `D:/lottery-caishen-ref-20260704/backend`.
- Desktop browser QA: entered the shrine, selected zodiac, selected constellation, generated a result, and captured the result overlay.
- Mobile browser QA: opened the shrine setup state at `390 x 844`; no horizontal overflow and no disabled offering dock in the first setup view.

**Design Decisions**
- Removed concrete fortune interactions from the home shrine: no home-level zodiac/constellation fields, draw-date control, shake action, offering buttons, or points rail.
- Kept the home shrine as a low-friction visual entry with the existing Caishen mascot, warm ivory/gold palette, and navy CTA.
- Moved the full interaction sequence into the full-screen overlay: select zodiac, select constellation, choose draw date, shake/generate, then offer.
- Refined the clicked-in overlay layout: setup now stays focused on profile entry and shake flow; offering dock and points bar appear only after a fortune result exists.
- Strengthened the overlay to better match the reference: persistent floating coins and jade, stronger navy/gold ceremonial stage, smoke layer, larger halo, result rail, offering altar, and point bar.
- Preserved the existing YiCai logo, navigation, lottery switcher, result card, and site-level layout.

**Residual Risk**
- The existing `caishen-mascot.png` asset is standing/holding hands rather than the arms-open seated mascot in the reference image, so the implementation gets closer through staging, particles, and altar treatment without replacing the mascot asset.

**Final Result**
final result: passed

---

## 2026-07-05 Fortune Offering Flow Fix

**User-Reported Problem**
- The shrine interaction was logically inverted: offerings appeared after the shake/result, but the intended ritual is to offer first and then shake.
- The offering dock also visually overlapped with the point bar, making the bottom area feel broken.
- The cinematic overlay still differed from the reference because the implementation uses the existing standing mascot asset plus CSS effects, while the reference is a full rendered scene with a seated open-arm mascot, dense smoke, coins, altar props, and a brighter magic-circle base.

**Root Cause**
- Frontend: `makeOffering()` required `todayResult`, and the offering dock was gated by `overlayResult`, so users could only offer after generating a result.
- Backend: offering events only deducted points and returned a temporary animation response; `/fortune/generate` did not read the day’s offering history, so offerings did not affect the generated effect probability.
- Visual: the point bar and offering shelf were styled as a result-state altar and were reused in pre-shake state without enough spacing.

**Fix**
- Offerings now appear only in the pre-shake full-screen shrine after zodiac/constellation profile is complete.
- Users can earn points and make offerings before generating the daily fortune result.
- The backend now returns `offering_summary` and uses it to select boosted effect weights during `/fortune/generate`.
- The pre-shake offering dock now has its own layout: the earn-points button is in the dock header, the point bar sits below the dock, and they no longer overlap.
- After shaking, the offering dock disappears and the result shows the applied offering summary.

**Verification Screenshots**
- Pre-shake offering layout: `D:/lottery-caishen-ref-20260704/qa-caishen-pre-shake-offering-layout-fixed.png`
- After pre-shake offering: `D:/lottery-caishen-ref-20260704/qa-caishen-after-pre-shake-offering-layout-fixed.png`
- Result after offering: `D:/lottery-caishen-ref-20260704/qa-caishen-result-after-offering-layout-fixed.png`
- Mobile result: `D:/lottery-caishen-ref-20260704/qa-caishen-mobile-result-layout-fixed.png`

**Automated QA**
- Desktop flow: open shrine -> choose zodiac -> choose constellation -> earn 20 points -> offer incense -> remain pre-shake -> shake -> result.
- Assertions passed:
  - offering dock and point bar overlap: `false`
  - still pre-shake after offering: `true`
  - boost class applied before shake: `true`
  - result balls rendered: `7`
  - offering dock hidden after result: `true`
  - desktop horizontal overflow: `false`
  - mobile horizontal overflow: `false`
  - console errors: `0`

**Residual Visual Gap**
- To match the reference exactly, the next visual step should be a dedicated full-scene Caishen overlay asset or a new mascot render. CSS-only particles and the existing standing mascot can improve the atmosphere but cannot fully reproduce the reference image’s seated pose and illustrated lighting.
