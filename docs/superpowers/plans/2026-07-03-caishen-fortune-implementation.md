# Caishen Fortune Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the homepage Caishen fortune shrine with zodiac/constellation onboarding, daily once-per-user result generation, offering points, simulated ad rewards, and full-screen result animations.

**Architecture:** Add a focused FastAPI router for fortune state and persist records in new SQLAlchemy models on the existing `Base`. Replace the lightweight frontend-only fortune widget in `DashboardPrizeStatusCard.vue` with a dedicated `FortuneHomeShrine.vue` component that calls the new API and owns all UI states.

**Tech Stack:** FastAPI, SQLAlchemy async, SQLite/PostgreSQL-compatible columns, Vue 3 Composition API, existing Vite/Tailwind/CSS setup, no new frontend dependencies.

---

### Task 1: Backend Models And API

**Files:**
- Modify: `backend/app/models/draw.py`
- Create: `backend/app/routers/fortune.py`
- Modify: `backend/app/main.py`
- Create: `backend/tests/test_fortune.py`

- [x] **Step 1: Add fortune persistence models**

Add `FortuneProfile`, `FortuneDailyResult`, `FortunePoints`, and `FortunePointEvent` to `backend/app/models/draw.py`. Store number arrays as comma-separated strings to avoid database-specific JSON behavior.

- [x] **Step 2: Add the fortune router**

Create `backend/app/routers/fortune.py` with:

- `GET /api/v1/fortune/today`
- `POST /api/v1/fortune/profile`
- `POST /api/v1/fortune/generate`
- `POST /api/v1/fortune/offering`
- `POST /api/v1/fortune/ad-reward`

Use `user_key` from the client, enforce one generated result per `user_key + lottery_type + local_date`, and keep offering effects separate from generated number results.

- [x] **Step 3: Register the router**

Import `fortune` in `backend/app/main.py` and call `app.include_router(fortune.router)`.

- [x] **Step 4: Add backend tests**

Create `backend/tests/test_fortune.py` with in-memory SQLite tests for:

- profile upsert
- daily result idempotency
- offering insufficient-points error
- ad reward daily limit
- lottery number rules for marksix, ssq, and qxc

- [x] **Step 5: Verify backend**

Run:

```powershell
cd D:\lottery-dev\backend
python -m unittest discover -s tests
python -m compileall app
```

Expected: all tests pass and compileall reports no syntax errors.

### Task 2: Frontend API Client

**Files:**
- Modify: `frontend/src/api.js`

- [x] **Step 1: Add fortune API methods**

Add:

- `fortuneToday(params)`
- `fortuneProfile(payload)`
- `fortuneGenerate(payload)`
- `fortuneOffering(payload)`
- `fortuneAdReward(payload)`

All methods use the existing `request` helper and include `lottery_type` where relevant.

- [x] **Step 2: Verify import safety**

Run:

```powershell
cd D:\lottery-dev\frontend
npm run build
```

Expected: build succeeds or fails only on not-yet-created component references from later tasks.

### Task 3: Homepage Shrine Component

**Files:**
- Create: `frontend/src/components/FortuneHomeShrine.vue`
- Modify: `frontend/src/components/DashboardPrizeStatusCard.vue`

- [x] **Step 1: Create `FortuneHomeShrine.vue`**

Component responsibilities:

- generate or read a stable `yicai_fortune_user_key` from `localStorage`
- load today status on mount and when `lotteryType` changes
- first click opens zodiac dialog
- second click opens constellation dialog
- after profile is complete, show date input and “摇一摇请财神”
- after click, animate the homepage doll, call `fortuneGenerate`, then open full-screen overlay
- render offering buttons: 上香、桃子、元宝、锦囊
- render simulated ad dialog and call `fortuneAdReward`
- render full-screen effect overlay with four animation classes

- [x] **Step 2: Replace the old local fortune widget**

In `DashboardPrizeStatusCard.vue`, remove `createFortuneResult` state and template block, import `FortuneHomeShrine`, and render it in the same left-column area so the homepage layout does not shift dramatically.

- [x] **Step 3: Verify SSR safety**

Guard every `window`, `localStorage`, and timer call behind `typeof window !== "undefined"` or lifecycle hooks.

### Task 4: Visual Polish And Build

**Files:**
- Modify: `frontend/src/components/FortuneHomeShrine.vue`

- [x] **Step 1: Polish states**

Ensure the component has:

- loading state while generating
- disabled state while profile dialog is open
- insufficient-points state
- simulated ad countdown state
- already-generated state
- close behavior for the overlay

- [x] **Step 2: Build frontend**

Run:

```powershell
cd D:\lottery-dev\frontend
npm run build
```

Expected: Vite SSG build completes.

### Task 5: Final Verification And PR

**Files:**
- All files changed in prior tasks

- [x] **Step 1: Run full verification**

Run:

```powershell
cd D:\lottery-dev\backend
python -m unittest discover -s tests
python -m compileall app
cd D:\lottery-dev\frontend
npm run build
```

Expected: all commands pass.

- [x] **Step 2: Review changed files**

Run:

```powershell
cd D:\lottery-dev
git diff --name-only
git diff --stat
```

Expected changed files are limited to fortune backend, homepage component integration, API client, tests, and this plan.

- [ ] **Step 3: Commit and create PR**

Commit the finished feature on `codex/feature-caishen-fortune-20260703`, push, and open a PR with verification notes.
