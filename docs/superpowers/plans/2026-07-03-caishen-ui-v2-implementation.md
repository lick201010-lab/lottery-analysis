# Caishen Fortune UI V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the homepage Caishen feature from a utility card into a premium stage: clean homepage entry, immersive fullscreen result, offerings moved out of the homepage.

**Architecture:** Keep the existing FastAPI fortune API unchanged. Refactor only the Vue component presentation in `FortuneHomeShrine.vue`, preserving the same state machine and API calls. The homepage shows only onboarding/date/main action/points; the fullscreen stage owns result display, ad reward, and offerings.

**Tech Stack:** Vue 3 Composition API, scoped CSS, existing Vite/Tailwind app, existing `/caishen-mascot.png`, existing `NumberBall.vue`.

---

### Task 1: Homepage Entry Redesign

**Files:**
- Modify: `frontend/src/components/FortuneHomeShrine.vue`

- [x] **Step 1: Remove homepage offering controls**

Delete the homepage `.offering-row` block from the template. Keep `offerings` data and `makeOffering()` because the overlay will use them.

- [x] **Step 2: Remove homepage ad CTA**

Delete the homepage `.ad-button` beside the primary shake button. Keep `startAdReward()` and ad dialog because the overlay will use it.

- [x] **Step 3: Replace homepage layout with a stage layout**

Use this structure inside `<section class="fortune-home-shrine">`:

```vue
<div class="fortune-stage-shell">
  <button class="mascot-button" ...>...</button>
  <div class="stage-content">...</div>
  <div class="stage-meter">...</div>
</div>
```

The stage content includes kicker, title, helper copy, profile chips/date, and main CTA. The meter shows `香火积分`, `今日一次`, and current lottery label.

### Task 2: Fullscreen Result Stage Redesign

**Files:**
- Modify: `frontend/src/components/FortuneHomeShrine.vue`

- [x] **Step 1: Move offerings into overlay**

Inside `.overlay-panel`, after the number result and note, add an `.overlay-offering-dock` with the four offering buttons. Buttons call `makeOffering(offering)` and show cost and note.

- [x] **Step 2: Add overlay ad reward entry**

Inside the overlay dock footer, add a compact ad reward button using `startAdReward()` and `adRewardsRemaining`. This is the only place users earn points from the Caishen UI.

- [x] **Step 3: Add overlay “go simulator” CTA**

Keep `收下今日手气` and add a `<router-link to="/generate">去模拟选号</router-link>` so the stage connects to the existing simulator.

### Task 3: Visual Polish

**Files:**
- Modify: `frontend/src/components/FortuneHomeShrine.vue`

- [x] **Step 1: Upgrade homepage CSS**

Replace the old card-like CSS with a low-luxury stage: deep navy mascot tile, warm pearl body, gold hairline dividers, subtle radial highlight, tighter height, responsive layout.

- [x] **Step 2: Upgrade overlay CSS**

Make the fullscreen overlay more cinematic: darker navy backdrop, gold particles, larger mascot, signed-result panel, offering dock as a bottom tray, responsive mobile stacking.

- [x] **Step 3: Preserve accessibility and interaction states**

Keep real buttons, disabled states, focusable close buttons, and no emoji icons. Overlay z-index remains above nav.

### Task 4: Verification

**Files:**
- Modify: `frontend/src/components/FortuneHomeShrine.vue`

- [x] **Step 1: Run frontend build**

Run:

```powershell
cd D:\lottery-dev\frontend
npm run build
```

Expected: Vite SSG completes with no errors.

- [x] **Step 2: Run backend regression tests**

Run:

```powershell
cd D:\lottery-dev\backend
python -m unittest discover -s tests
python -m compileall app
```

Expected: tests pass and compileall reports no syntax errors.

- [x] **Step 3: Browser smoke**

With local backend on `127.0.0.1:8000` and frontend on `127.0.0.1:5174`, verify:
- First click opens zodiac dialog.
- Second click opens constellation dialog.
- Third click opens fullscreen result.
- Homepage has no offering buttons.
- Overlay has offering buttons and ad reward.
- Overlay closes above nav.
- Mobile viewport has no nav/content overlap.

### Task 5: Commit And PR Update

**Files:**
- Modify: `frontend/src/components/FortuneHomeShrine.vue`
- Create: `docs/superpowers/plans/2026-07-03-caishen-ui-v2-implementation.md`

- [ ] **Step 1: Stage only relevant files**

Stage `FortuneHomeShrine.vue` and this plan. Do not stage `data/marksix.db` or unrelated generated locale/SEO files unless they contain required new UI strings.

- [ ] **Step 2: Commit**

Run:

```powershell
git commit -m "[Agent] polish: refine caishen fortune stage UI"
```

- [ ] **Step 3: Push**

Push `codex/feature-caishen-fortune-20260703` and update PR #76.
