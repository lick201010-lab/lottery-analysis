import { ViteSSG } from "vite-ssg";
import App from "./App.vue";
import { routes } from "./router";
import "./style.css";

// vite-ssg 入口：build 时为每个 route 生成静态 HTML，dev 时正常 mount
// @unhead/vue 由 vite-ssg 自动注册，不需要手动 app.use
export const createApp = ViteSSG(
  App,
  {
    routes,
    scrollBehavior() {
      return { top: 0 };
    },
  },
  ({ router, isClient }) => {
    // GA4: 路由切换触发 page_view（仅客户端）
    if (isClient) {
      router.afterEach((to) => {
        if (window.gtag) {
          window.gtag("event", "page_view", {
            page_path: to.fullPath,
            page_title: document.title,
            page_location: window.location.href,
          });
        }
      });
    }
  },
);
