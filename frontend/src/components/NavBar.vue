<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import { lotteryType as selectedLotteryType } from "../api.js";
import { seoTopics } from "../data/seoTopics.js";

const route = useRoute();
const topicPaths = new Set(Object.values(seoTopics).map((t) => t.path));
const isTw = computed(() => route.path.startsWith("/tw/"));
const langBase = computed(() => (isTw.value ? route.path.slice(3) : route.path));
// 仅在有繁体版本的页面（专题页）显示语言切换，避免跳到不存在的 /tw 页
const hasTw = computed(() => topicPaths.has(langBase.value));

const links = [
  { path: "/",          label: "数据概览" },
  { path: "/frequency", label: "号码统计" },
  { path: "/patterns",  label: "走势分析" },
  { path: "/pairs",     label: "组合分析" },
  { path: "/generate",  label: "模拟选号" },
  { path: "/jackpot",   label: "奖金分析" },
  { path: "/data",      label: "历史记录" },
];

const lotteryOptions = [
  { value: "marksix", label: "六合彩", short: "六", tone: "marksix" },
  { value: "ssq", label: "双色球", short: "双", tone: "ssq" },
  { value: "qxc", label: "7星彩", short: "7", tone: "qxc" },
];

const activeLotteryLabel = computed(() => {
  return lotteryOptions.find((item) => item.value === selectedLotteryType.value)?.label || "彩种";
});

function applyLotteryType(value) {
  selectedLotteryType.value = value;
}
</script>

<template>
  <nav class="v62-nav" role="navigation" aria-label="主导航">
    <router-link to="/" class="v62-nav-brand">
      <img src="/logo.png" alt="弈彩 YiCai" />
      <span class="v62-nav-brand-copy">
        <strong>弈彩</strong>
        <span>YiCai · 数据分析平台</span>
      </span>
    </router-link>

    <div class="v62-nav-lottery-switcher" :aria-label="`彩种切换，当前为${activeLotteryLabel}`">
      <button
        v-for="opt in lotteryOptions"
        :key="opt.value"
        type="button"
        class="v62-nav-switch-pill"
        :class="[opt.tone, selectedLotteryType === opt.value ? 'active' : 'inactive']"
        :aria-pressed="selectedLotteryType === opt.value"
        @click="applyLotteryType(opt.value)"
      >
        <span class="v62-nav-switch-icon">{{ opt.short }}</span>
        <span class="v62-nav-switch-label">{{ opt.label }}</span>
      </button>
    </div>

    <span class="v62-nav-sep"></span>

    <router-link
      v-for="link in links"
      :key="link.path"
      :to="link.path"
      class="v62-nav-link"
    >{{ link.label }}</router-link>

    <span v-if="hasTw" class="v62-nav-lang" role="group" aria-label="语言切换 / 語言切換">
      <router-link :to="langBase" class="v62-nav-lang-btn" :class="{ 'is-on': !isTw }">简</router-link>
      <router-link :to="`/tw${langBase}`" class="v62-nav-lang-btn" :class="{ 'is-on': isTw }">繁</router-link>
    </span>
  </nav>
</template>

<style scoped>
.v62-nav-lang {
  display: inline-flex;
  gap: 2px;
  margin-left: 6px;
  border: 1px solid #ded2c0;
  border-radius: 9999px;
  padding: 2px;
  background: #fffaf2;
}
.v62-nav-lang-btn {
  min-width: 26px;
  text-align: center;
  padding: 2px 8px;
  border-radius: 9999px;
  font-size: 13px;
  color: #8b6336;
  text-decoration: none;
  line-height: 1.5;
}
.v62-nav-lang-btn.is-on {
  background: #c5943f;
  color: #fff;
}
</style>
