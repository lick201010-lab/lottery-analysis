import { archiveIssueRoutes, archiveYearRoutes } from "./data/drawArchives.js";
import { seoTopics } from "./data/seoTopics.js";

// 路由配置（vite-ssg 在 build 时消费 routes 数组，自动创建 router）
const drawArchiveRoutes = [
  ...archiveYearRoutes.map((route) => ({
    path: route.path,
    name: `${route.gameKey}-${route.year}-archive`,
    component: () => import("./views/DrawArchiveYear.vue"),
    props: { gameKey: route.gameKey, year: route.year },
  })),
  ...archiveIssueRoutes.map((route) => ({
    path: route.path,
    name: `${route.gameKey}-${route.year}-${route.issue}-archive`,
    component: () => import("./views/DrawArchiveIssue.vue"),
    props: { gameKey: route.gameKey, year: route.year, issue: route.issue },
  })),
];

// SEO 专题页：每个主题生成简体(/x) + 繁体(/tw/x) 两条路由（繁体内容由 seoTopics.tw.js 提供）
const SeoTopicPage = () => import("./views/SeoTopicPage.vue");
const seoTopicRoutes = Object.entries(seoTopics).flatMap(([key, topic]) => [
  { path: topic.path, name: `topic-${key}`, component: SeoTopicPage, props: { topicKey: key, lang: "zh" } },
  { path: `/tw${topic.path}`, name: `topic-${key}-tw`, component: SeoTopicPage, props: { topicKey: key, lang: "tw" } },
]);

export const routes = [
  { path: "/", name: "Dashboard", component: () => import("./views/Dashboard.vue") },
  { path: "/data", name: "DataManagement", component: () => import("./views/DataManagement.vue") },
  { path: "/frequency", name: "FrequencyAnalysis", component: () => import("./views/FrequencyAnalysis.vue") },
  { path: "/patterns", name: "PatternAnalysis", component: () => import("./views/PatternAnalysis.vue") },
  { path: "/pairs", name: "PairAnalysis", component: () => import("./views/PairAnalysis.vue") },
  { path: "/generate", name: "GenerateNumbers", component: () => import("./views/GenerateNumbers.vue") },
  { path: "/jackpot", name: "JackpotAnalysis", component: () => import("./views/JackpotAnalysis.vue") },
  { path: "/about", name: "About", component: () => import("./views/About.vue") },
  { path: "/privacy", name: "Privacy", component: () => import("./views/Privacy.vue") },
  { path: "/guide", name: "Guide", component: () => import("./views/Guide.vue") },
  { path: "/strategy", name: "Strategy", component: () => import("./views/Strategy.vue") },
  { path: "/patterns-article", name: "PatternsArticle", component: () => import("./views/PatternsArticle.vue") },
  { path: "/odds", name: "Odds", component: () => import("./views/Odds.vue") },
  { path: "/responsible", name: "Responsible", component: () => import("./views/Responsible.vue") },
  ...seoTopicRoutes,
  ...drawArchiveRoutes,
  { path: "/404", name: "NotFound", component: () => import("./views/NotFound.vue") },
  { path: "/:pathMatch(.*)*", name: "NotFoundCatchAll", component: () => import("./views/NotFound.vue") },
];
