<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import { seoTopicList } from "../data/seoTopics.js";
import { seoTopicListEn } from "../data/seoTopics.en.js";

const route = useRoute();
const twPaths = new Set(seoTopicList.map((t) => t.path)); // 全部专题有繁体
const enPaths = new Set(seoTopicListEn.map((t) => t.path)); // 已翻译的英文子集

// 各语言的"入口页"：当前页没有该语言版本时，切过去落到这里（避免 404 / 死路）
const TW_ENTRY = "/tw/ssq/results";
const EN_ENTRY = "/en/marksix/results";

const cur = computed(() => {
  const p = route.path;
  if (p === "/tw" || p.startsWith("/tw/")) return "tw";
  if (p === "/en" || p.startsWith("/en/")) return "en";
  return "zh";
});
const base = computed(() => {
  const p = route.path;
  return cur.value === "zh" ? p : p.slice(3) || "/";
});

const items = computed(() => [
  { code: "zh", label: "简", to: base.value },
  { code: "tw", label: "繁", to: twPaths.has(base.value) ? `/tw${base.value}` : TW_ENTRY },
  { code: "en", label: "EN", to: enPaths.has(base.value) ? `/en${base.value}` : EN_ENTRY },
]);
</script>

<template>
  <div class="lang-switch" role="group" aria-label="Language / 语言切换">
    <template v-for="it in items" :key="it.code">
      <span v-if="it.code === cur" class="lang-btn is-on">{{ it.label }}</span>
      <router-link v-else :to="it.to" class="lang-btn">{{ it.label }}</router-link>
    </template>
  </div>
</template>

<style scoped>
.lang-switch {
  position: fixed;
  top: 8px;
  right: 14px;
  z-index: 1000;
  display: inline-flex;
  gap: 2px;
  padding: 3px;
  border-radius: 9999px;
  border: 1px solid #ded2c0;
  background: rgba(255, 250, 242, 0.96);
  box-shadow: 0 2px 10px rgba(123, 85, 35, 0.16);
}
.lang-btn {
  min-width: 28px;
  padding: 3px 9px;
  text-align: center;
  font-size: 12.5px;
  line-height: 1.5;
  border-radius: 9999px;
  color: #8b6336;
  text-decoration: none;
  cursor: pointer;
}
.lang-btn.is-on {
  background: #c5943f;
  color: #fff;
  cursor: default;
}
</style>
