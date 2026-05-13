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
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
