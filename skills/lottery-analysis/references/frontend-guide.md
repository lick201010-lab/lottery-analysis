# Frontend Guide

## Tech Stack

- Vue 3 (Composition API)
- Vite
- Tailwind CSS v4
- Chart.js
- No UI component library — all custom styled

## Theme System

### Colors
- Background: Diamond gradient `linear-gradient(135deg, #1a0b2e 0%, #2d1b4e 25%, #4a2c7a 50%, #6b3fa0 75%, #9d4edd 100%)`
- Cards: Glassmorphism — `rgba(255,255,255,0.92)` + `backdrop-filter: blur(12px)`
- SSQ pill: `linear-gradient(90deg, #3b82f6, #ef4444)` (blue → red)
- MarkSix pill: `linear-gradient(90deg, #ef4444, #f97316)` (red → orange)

### Ball Colors

#### MarkSix (六合彩)
Red: 1,2,7,8,12,13,18,19,23,24,29,30,34,35,40,45,46
Blue: 3,4,9,10,14,15,20,25,26,31,36,37,41,42,47,48
Green: 5,6,11,16,17,21,22,27,28,32,33,38,39,43,44,49

#### SSQ (双色球)
- Red balls: 1-33, displayed in red
- Blue ball: 1-16, displayed in blue

## Key Components

### Dashboard.vue
- Three-column hero cards: Latest Draw / Countdown / Win Stats
- Loads data via `api.summary()`, `api.latestDraw()`, `api.jackpotLatest()`
- `jackpotData` is reactive ref, used by `winStats` computed

### CountdownTimer.vue
- Uses `setInterval(1000)` for real-time countdown
- Schedule hardcoded in component
- MarkSix: Tue/Thu/Sat 21:30
- SSQ: Tue/Thu/Sun 21:15

### api.js
```javascript
async jackpotLatest() {
  return request(`/api/v1/jackpot/latest?lottery_type=${lotteryType.value}`);
},
async jackpotScrape() {
  return request(`/api/v1/jackpot/scrape`, { method: "POST" });
},
```

## Responsive Strategy

- Mobile: `< 768px` — hamburger menu, hidden table columns, `flex-col`
- Tablet: `768px–1024px` — 2-column grids
- Desktop: `> 1024px` — 3-column hero cards

## Build

```bash
cd frontend
npm run build
```

Dist output at `frontend/dist/`, served by Caddy.
