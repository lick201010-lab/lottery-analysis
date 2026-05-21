// 路由配置（vite-ssg 在 build 时消费 routes 数组，自动创建 router）
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
  { path: "/404", name: "NotFound", component: () => import("./views/NotFound.vue") },
  { path: "/:pathMatch(.*)*", name: "NotFoundCatchAll", component: () => import("./views/NotFound.vue") },
];
