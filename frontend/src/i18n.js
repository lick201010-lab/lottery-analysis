// 应用页 i18n：用简体原文作 key。
// - 繁体：构建期 OpenCC 自动生成 i18n.tw.js（扫描 t("...") 调用）
// - 英文：人工维护 i18n.en.js（简→英）
// 组件用 const { t, lang } = useI18n(); 然后 {{ t("数据概览") }}
import { computed } from "vue";
import { useRoute } from "vue-router";
import { uiTw } from "./i18n.tw.js";
import { uiEn } from "./i18n.en.js";

export function langFromPath(p) {
  if (p === "/tw" || p.startsWith("/tw/")) return "tw";
  if (p === "/en" || p.startsWith("/en/")) return "en";
  return "zh";
}

export function useI18n() {
  const route = useRoute();
  const lang = computed(() => langFromPath(route.path));
  // 当前页对应另一语言路径的前缀（用于内链本地化）
  const prefix = computed(() => (lang.value === "zh" ? "" : `/${lang.value}`));
  function t(zh) {
    if (lang.value === "tw") return uiTw[zh] || zh;
    if (lang.value === "en") return uiEn[zh] || zh;
    return zh;
  }
  return { lang, prefix, t };
}
