<script setup>
import { ref } from "vue";
import { lotteryType } from "../api.js";

const lotteryOptions = [
  { value: "marksix", label: "六合彩", icon: "✤" },
  { value: "ssq",     label: "双色球", icon: "◎" },
  { value: "qxc",     label: "7星彩", icon: "7" },
];

const links = [
  { path: "/",          label: "数据概览" },
  { path: "/frequency", label: "号码统计" },
  { path: "/patterns",  label: "走势分析" },
  { path: "/pairs",     label: "组合分析" },
  { path: "/generate",  label: "模拟选号" },
  { path: "/jackpot",   label: "奖金分析" },
  { path: "/data",      label: "历史记录" },
];

function applyLotteryType(value) {
  lotteryType.value = value;
}
</script>

<template>
  <nav class="v62-nav" role="navigation" aria-label="主导航">
    <!-- Logo / Brand -->
    <router-link to="/" class="v62-nav-brand">
      <img src="/logo.png" alt="弈彩 YiCai" />
      <span class="v62-nav-brand-name">弈彩<span class="v62-nav-brand-en">YiCai</span></span>
    </router-link>

    <!-- Nav links -->
    <router-link
      v-for="link in links"
      :key="link.path"
      :to="link.path"
      class="v62-nav-link"
    >{{ link.label }}</router-link>

    <!-- Separator -->
    <span class="v62-nav-sep"></span>

    <!-- Lottery switcher -->
    <button
      v-for="opt in lotteryOptions"
      :key="opt.value"
      @click="applyLotteryType(opt.value)"
      class="v62-lottery-btn"
      :class="lotteryType === opt.value ? 'active' : 'inactive'"
      :aria-label="`切换到${opt.label}`"
    >
      <span>{{ opt.icon }}</span>
      <span>{{ opt.label }}</span>
    </button>
  </nav>
</template>
