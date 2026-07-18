import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { join } from "node:path";

const rootDir = fileURLToPath(new URL("../", import.meta.url));
const dataDir = join(rootDir, "public", "data");
const generatedDir = join(rootDir, ".generated");
const outputFile = join(generatedDir, "seoData.js");
const sitemapFile = join(rootDir, "public", "sitemap.xml");
const baiduSitemapFile = join(rootDir, "public", "sitemap-baidu.xml");
const generatedSitemapFile = join(generatedDir, "sitemap.xml");
const generatedBaiduSitemapFile = join(generatedDir, "sitemap-baidu.xml");
const SITE_URL = "https://yicai.ckl.hk";
const API_BASE_URL = (
  process.env.SEO_API_BASE_URL ||
  process.env.VITE_API_BASE_URL ||
  "https://api.ckl.hk"
).replace(/\/$/, "");
const DETAIL_LIMIT = 24;
const REQUEST_TIMEOUT_MS = 12_000;

function getSourceLastmod() {
  try {
    return execFileSync("git", ["log", "-1", "--format=%cs", "--", "."], {
      cwd: rootDir,
      encoding: "utf8",
    }).trim();
  } catch {
    return new Date().toISOString().slice(0, 10);
  }
}

const games = {
  marksix: {
    label: "六合彩",
    sourceFile: "draws.json",
    issueLabel: "特别号",
    issueNote: "特别号用于部分奖项条件的辅助判断",
    basePath: "/marksix",
  },
  ssq: {
    label: "双色球",
    sourceFile: "ssq_draws.json",
    issueLabel: "蓝球",
    issueNote: "蓝球是头奖条件的一部分",
    basePath: "/ssq",
  },
  qxc: {
    label: "七星彩",
    sourceFile: "qxc_draws.json",
    issueLabel: "第七位",
    issueNote: "七星彩按位置记录号码，第七位单独展示",
    basePath: "/qxc",
  },
};

function readLocalDraws(game) {
  const file = join(dataDir, game.sourceFile);
  if (!existsSync(file)) return [];
  return JSON.parse(readFileSync(file, "utf8"));
}

async function fetchJson(path) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { Accept: "application/json" },
    signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
  });
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
  return response.json();
}

async function fetchAllDraws(gameKey) {
  const first = await fetchJson(`/api/v1/draws?page=1&per_page=200&lottery_type=${gameKey}`);
  const pages = Math.ceil(Number(first.total || 0) / 200);
  if (pages <= 1) return first.draws || [];

  const remainingPages = Array.from({ length: pages - 1 }, (_, index) => index + 2);
  const batches = [];
  for (let index = 0; index < remainingPages.length; index += 6) {
    batches.push(remainingPages.slice(index, index + 6));
  }

  const draws = [...(first.draws || [])];
  for (const batch of batches) {
    const results = await Promise.all(
      batch.map((page) =>
        fetchJson(`/api/v1/draws?page=${page}&per_page=200&lottery_type=${gameKey}`),
      ),
    );
    results.forEach((result) => draws.push(...(result.draws || [])));
  }
  return draws;
}

function normalizeDraw(draw) {
  return {
    ...draw,
    draw_date: String(draw.draw_date),
    special_num: Number(draw.special_num),
    num1: Number(draw.num1),
    num2: Number(draw.num2),
    num3: Number(draw.num3),
    num4: Number(draw.num4),
    num5: Number(draw.num5),
    num6: Number(draw.num6),
  };
}

async function loadDraws(gameKey, game) {
  try {
    const draws = await fetchAllDraws(gameKey);
    if (draws.length) {
      console.log(`[seo] ${gameKey}: fetched ${draws.length} draws from ${API_BASE_URL}`);
      return draws.map(normalizeDraw);
    }
  } catch (error) {
    console.warn(`[seo] ${gameKey}: API unavailable, using local fallback (${error.message})`);
  }

  const local = readLocalDraws(game).map(normalizeDraw);
  if (!local.length) {
    throw new Error(`No SEO draw data available for ${gameKey}`);
  }
  return local;
}

function toYear(draw) {
  return String(draw.draw_date).slice(0, 4);
}

function toIssueSlug(gameKey, draw) {
  if (gameKey === "marksix") {
    return String(draw.draw_number).split("/").pop().padStart(3, "0");
  }
  return String(draw.draw_number).slice(-3).padStart(3, "0");
}

function compactDraw(gameKey, draw) {
  const year = toYear(draw);
  const issue = toIssueSlug(gameKey, draw);
  return {
    gameKey,
    year,
    issue,
    drawNumber: String(draw.draw_number),
    drawDate: String(draw.draw_date),
    numbers: [draw.num1, draw.num2, draw.num3, draw.num4, draw.num5, draw.num6],
    special: draw.special_num,
    oddCount: draw.odd_count,
    evenCount: draw.even_count,
    smallCount: draw.small_count,
    bigCount: draw.big_count,
    sumTotal: draw.sum_total,
    hasConsecutive: Boolean(draw.has_consecutive),
    path: `${games[gameKey].basePath}/${year}/${issue}`,
  };
}

function summarizeYear(gameKey, year, draws) {
  const latest = draws[0];
  const earliest = draws[draws.length - 1];
  return {
    gameKey,
    year,
    path: `${games[gameKey].basePath}/${year}`,
    count: draws.length,
    latestDate: latest.drawDate,
    earliestDate: earliest.drawDate,
    sampleDraws: draws.slice(0, 18),
  };
}

function computeFrequency(draws, gameKey) {
  const start = gameKey === "qxc" ? 0 : 1;
  const end = gameKey === "ssq" ? 33 : gameKey === "qxc" ? 14 : 49;
  const recent = draws.slice(0, 100);
  return Array.from({ length: end - start + 1 }, (_, index) => {
    const number = start + index;
    const appearances = recent.reduce((count, draw) => {
      const regular = [draw.num1, draw.num2, draw.num3, draw.num4, draw.num5, draw.num6];
      return count + regular.filter((value) => Number(value) === number).length;
    }, 0);
    const lastIndex = recent.findIndex((draw) =>
      [draw.num1, draw.num2, draw.num3, draw.num4, draw.num5, draw.num6, draw.special_num]
        .some((value) => Number(value) === number),
    );
    return {
      number,
      total_appearances: appearances,
      special_appearances: recent.filter((draw) => Number(draw.special_num) === number).length,
      consecutive_missed: lastIndex < 0 ? recent.length : lastIndex,
      hotness_score: appearances,
    };
  });
}

function computeSummary(draws, frequency) {
  const hot = [...frequency].sort((a, b) => b.hotness_score - a.hotness_score || a.number - b.number);
  const cold = [...frequency].sort((a, b) => a.hotness_score - b.hotness_score || b.consecutive_missed - a.consecutive_missed);
  const overdue = [...frequency].sort((a, b) => b.consecutive_missed - a.consecutive_missed)[0] || null;
  return {
    total_draws: draws.length,
    latest_date: draws[0]?.draw_date || null,
    top_hot: hot.slice(0, 3),
    top_cold: cold.slice(0, 3),
    most_overdue: overdue,
    top_pairs: [],
  };
}

async function loadDashboardSnapshot(gameKey, draws) {
  const fallbackFrequency = computeFrequency(draws, gameKey);
  const fallback = {
    latestDraw: draws[0] || null,
    recentDraws: draws.slice(0, 24),
    frequencyData: fallbackFrequency,
    summary: computeSummary(draws, fallbackFrequency),
    jackpotData: null,
  };

  const endpoints = {
    summary: `/api/v1/analysis/summary?lottery_type=${gameKey}`,
    latestDraw: `/api/v1/draws/latest?lottery_type=${gameKey}`,
    frequencyData: `/api/v1/analysis/frequency?lottery_type=${gameKey}&type=both`,
    jackpotData: `/api/v1/jackpot/latest?lottery_type=${gameKey}`,
  };

  await Promise.all(
    Object.entries(endpoints).map(async ([key, path]) => {
      try {
        fallback[key] = await fetchJson(path);
      } catch (error) {
        console.warn(`[seo] ${gameKey}: ${key} fallback used (${error.message})`);
      }
    }),
  );
  return fallback;
}

function parseStaticRoutes(file, blockedGames = []) {
  const xml = readFileSync(file, "utf8");
  const entries = [...xml.matchAll(/<url>([\s\S]*?)<\/url>/g)].map((match) => match[1]);
  const archivePattern = new RegExp(
    `${SITE_URL.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\/(marksix|ssq|qxc)\\/\\d{4}(?:\\/[^<]+)?`,
  );

  return entries
    .map((body) => {
      const loc = body.match(/<loc>(.*?)<\/loc>/)?.[1];
      const changefreq = body.match(/<changefreq>(.*?)<\/changefreq>/)?.[1] || "monthly";
      const priority = body.match(/<priority>(.*?)<\/priority>/)?.[1] || "0.5";
      return { loc, changefreq, priority };
    })
    .filter((route) => route.loc && !archivePattern.test(route.loc))
    .filter((route) => !blockedGames.some((gameKey) => route.loc.includes(`/${gameKey}/`)));
}

function buildSitemap(routes) {
  const unique = [...new Map(routes.map((route) => [route.loc, route])).values()];
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${unique
  .map(
    (route) =>
      `  <url><loc>${route.loc}</loc><lastmod>${route.lastmod}</lastmod><changefreq>${route.changefreq}</changefreq><priority>${route.priority}</priority></url>`,
  )
  .join("\n")}
</urlset>
`;
}

mkdirSync(generatedDir, { recursive: true });

const drawsByGame = {};
for (const [gameKey, game] of Object.entries(games)) {
  drawsByGame[gameKey] = await loadDraws(gameKey, game);
}

const archive = {
  games: Object.fromEntries(
    Object.entries(games).map(([key, game]) => [
      key,
      {
        label: game.label,
        issueLabel: game.issueLabel,
        issueNote: game.issueNote,
        basePath: game.basePath,
      },
    ]),
  ),
  years: {},
  issues: {},
};

for (const [gameKey, draws] of Object.entries(drawsByGame)) {
  const compactDraws = draws.map((draw) => compactDraw(gameKey, draw));
  const detailKeys = new Set(
    compactDraws.slice(0, DETAIL_LIMIT).map((draw) => `${gameKey}-${draw.year}-${draw.issue}`),
  );
  const byYear = new Map();

  for (const draw of compactDraws) {
    draw.hasDetail = detailKeys.has(`${gameKey}-${draw.year}-${draw.issue}`);
    if (!byYear.has(draw.year)) byYear.set(draw.year, []);
    byYear.get(draw.year).push(draw);
  }

  archive.years[gameKey] = [...byYear.entries()]
    .sort(([a], [b]) => Number(b) - Number(a))
    .map(([year, yearDraws]) => summarizeYear(gameKey, year, yearDraws));

  for (const draw of compactDraws.slice(0, DETAIL_LIMIT)) {
    archive.issues[`${gameKey}-${draw.year}-${draw.issue}`] = draw;
  }
}

const yearRoutes = Object.values(archive.years)
  .flat()
  .map(({ gameKey, year, path, latestDate }) => ({ gameKey, year, path, latestDate }));
const issueRoutes = Object.values(archive.issues)
  .map(({ gameKey, year, issue, path, drawDate }) => ({ gameKey, year, issue, path, drawDate }));

const dashboardSnapshots = {};
for (const [gameKey, draws] of Object.entries(drawsByGame)) {
  dashboardSnapshots[gameKey] = await loadDashboardSnapshot(gameKey, draws);
}

const moduleSource = `// Generated at build time by scripts/generate-archive-data.mjs.
// This file is intentionally ignored by Git so production builds can use fresh API data.

export const archiveData = ${JSON.stringify(archive, null, 2)};
export const archiveYearRoutes = ${JSON.stringify(yearRoutes, null, 2)};
export const archiveIssueRoutes = ${JSON.stringify(issueRoutes, null, 2)};
export const dashboardSnapshots = ${JSON.stringify(dashboardSnapshots, null, 2)};

export function getArchiveYear(gameKey, year) {
  return archiveData.years[gameKey]?.find((item) => item.year === String(year));
}

export function getArchiveIssue(gameKey, year, issue) {
  return archiveData.issues[\`\${gameKey}-\${year}-\${issue}\`];
}
`;
writeFileSync(outputFile, moduleSource);

const sourceLastmod = getSourceLastmod();
const latestDateByGame = Object.fromEntries(
  Object.entries(drawsByGame).map(([gameKey, draws]) => [gameKey, draws[0]?.draw_date || sourceLastmod]),
);
const latestDrawDate = Object.values(latestDateByGame).sort().at(-1) || sourceLastmod;

function staticRouteLastmod(loc) {
  const gameKey = Object.keys(games).find((key) => loc.includes(`/${key}/`));
  if (gameKey && (loc.endsWith("/results") || loc.endsWith("/frequency"))) {
    return latestDateByGame[gameKey];
  }
  if ([`${SITE_URL}/`, `${SITE_URL}/data`, `${SITE_URL}/frequency`].includes(loc)) {
    return latestDrawDate;
  }
  return sourceLastmod;
}

const googleStatic = parseStaticRoutes(sitemapFile).map((route) => ({
  ...route,
  lastmod: staticRouteLastmod(route.loc),
}));
const archiveRoutes = [
  ...yearRoutes.map((route) => ({
    loc: `${SITE_URL}${route.path}`,
    lastmod: route.latestDate,
    changefreq: "monthly",
    priority: "0.65",
  })),
  ...issueRoutes.map((route) => ({
    loc: `${SITE_URL}${route.path}`,
    lastmod: route.drawDate,
    changefreq: "yearly",
    priority: "0.55",
  })),
];
writeFileSync(generatedSitemapFile, buildSitemap([...googleStatic, ...archiveRoutes]));

const baiduStatic = parseStaticRoutes(baiduSitemapFile, ["marksix"]).map((route) => ({
  ...route,
  lastmod: staticRouteLastmod(route.loc),
}));
const baiduArchive = archiveRoutes.filter(
  (route) => route.loc.includes("/ssq/") || route.loc.includes("/qxc/"),
);
writeFileSync(generatedBaiduSitemapFile, buildSitemap([...baiduStatic, ...baiduArchive]));

console.log(`[seo] generated ${yearRoutes.length} year routes and ${issueRoutes.length} issue routes`);
console.log(`[seo] wrote ${outputFile}`);
console.log(`[seo] wrote fresh Google and Baidu sitemaps`);
