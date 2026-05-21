import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    name: "Dashboard",
    component: () => import("./views/Dashboard.vue"),
  },
  {
    path: "/data",
    name: "DataManagement",
    component: () => import("./views/DataManagement.vue"),
  },
  {
    path: "/frequency",
    name: "FrequencyAnalysis",
    component: () => import("./views/FrequencyAnalysis.vue"),
  },
  {
    path: "/patterns",
    name: "PatternAnalysis",
    component: () => import("./views/PatternAnalysis.vue"),
  },
  {
    path: "/pairs",
    name: "PairAnalysis",
    component: () => import("./views/PairAnalysis.vue"),
  },
  {
    path: "/generate",
    name: "GenerateNumbers",
    component: () => import("./views/GenerateNumbers.vue"),
  },
  {
    path: "/jackpot",
    name: "JackpotAnalysis",
    component: () => import("./views/JackpotAnalysis.vue"),
  },
  {
    path: "/about",
    name: "About",
    component: () => import("./views/About.vue"),
  },
  {
    path: "/privacy",
    name: "Privacy",
    component: () => import("./views/Privacy.vue"),
  },
  {
    path: "/guide",
    name: "Guide",
    component: () => import("./views/Guide.vue"),
  },
  {
    path: "/strategy",
    name: "Strategy",
    component: () => import("./views/Strategy.vue"),
  },
  {
    path: "/patterns-article",
    name: "PatternsArticle",
    component: () => import("./views/PatternsArticle.vue"),
  },
  {
    path: "/odds",
    name: "Odds",
    component: () => import("./views/Odds.vue"),
  },
  {
    path: "/responsible",
    name: "Responsible",
    component: () => import("./views/Responsible.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

// GA4: 路由切换时触发 page_view（SPA 默认不会自动追踪）
router.afterEach((to) => {
  if (typeof window !== "undefined" && window.gtag) {
    window.gtag("event", "page_view", {
      page_path: to.fullPath,
      page_title: document.title,
      page_location: window.location.href,
    });
  }
});

export default router;