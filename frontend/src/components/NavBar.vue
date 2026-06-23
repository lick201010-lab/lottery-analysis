<script setup>
import { computed } from "vue";
import { lotteryType as selectedLotteryType } from "../api.js";
import { useI18n } from "../i18n.js";

const { t, prefix } = useI18n();

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
        <span>YiCai · {{ t("数据分析平台") }}</span>
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
        <span class="v62-nav-switch-label">{{ t(opt.label) }}</span>
      </button>
    </div>

    <span class="v62-nav-sep"></span>

    <router-link
      v-for="link in links"
      :key="link.path"
      :to="link.path"
      class="v62-nav-link"
    >{{ t(link.label) }}</router-link>
  </nav>
</template>
