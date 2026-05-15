<script setup>
import { useRouter, useRoute } from "vue-router";
import { lotteryType } from "../api.js";
import LogoIcon from "./LogoIcon.vue";

const router = useRouter();
const route = useRoute();

const links = [
  { path: "/", label: "仪表盘", icon: "M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z" },
  { path: "/frequency", label: "频率分析", icon: "M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z" },
  { path: "/patterns", label: "模式分析", icon: "M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z" },
  { path: "/pairs", label: "号码对", icon: "M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z" },
  { path: "/generate", label: "号码生成", icon: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1.41 16.09V20h-2.67v-1.93c-1.71-.36-3.16-1.46-3.27-3.4h1.96c.1 1.05.82 1.87 2.65 1.87 1.96 0 2.4-.98 2.4-1.59 0-.83-.44-1.61-2.67-2.14-2.48-.6-4.18-1.62-4.18-3.67 0-1.72 1.39-2.84 3.11-3.21V4h2.67v1.95c1.86.45 2.79 1.86 2.85 3.39H14.3c-.05-1.11-.64-1.87-2.22-1.87-1.5 0-2.4.68-2.4 1.64 0 .84.65 1.39 2.67 1.91s4.18 1.39 4.18 3.91c-.01 1.83-1.38 2.83-3.12 3.16z" },
  { path: "/data", label: "数据管理", icon: "M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" },
];

const lotteryOptions = [
  { value: "marksix", label: "六合彩" },
  { value: "ssq", label: "双色球" },
];

function switchLottery(e) {
  lotteryType.value = e.target.value;
}
</script>

<template>
  <nav class="bg-[#0b0e11]/95 backdrop-blur-xl border-b border-[#2b3139] sticky top-0 z-50">
    <div class="max-w-[1440px] mx-auto px-4 sm:px-6">
      <div class="flex items-center justify-between h-16">
        <!-- Logo & Links -->
        <div class="flex items-center gap-6">
          <div class="flex items-center gap-2.5">
            <LogoIcon :size="36" />
            <span class="text-xl font-bold tracking-tight text-[#fcd535]">彩溯</span>
          </div>

          <div class="hidden md:flex items-center gap-1">
            <router-link
              v-for="link in links"
              :key="link.path"
              :to="link.path"
              class="group flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200"
              :class="
                route.path === link.path
                  ? 'bg-[#fcd535]/10 text-[#fcd535]'
                  : 'text-[#b7bdc6] hover:text-white hover:bg-[#2b3139]'
              "
            >
              <svg class="w-[18px] h-[18px] opacity-70 group-hover:opacity-100 transition-opacity" fill="currentColor" viewBox="0 0 24 24">
                <path :d="link.icon"/>
              </svg>
              {{ link.label }}
            </router-link>
          </div>
        </div>

        <!-- Lottery Selector -->
        <div class="flex items-center gap-3">
          <label class="text-sm text-[#707a8a] font-medium hidden sm:block">彩种</label>
          <div class="relative">
            <select
              :value="lotteryType"
              @change="switchLottery"
              class="appearance-none pl-3 pr-9 py-1.5 bg-[#1e2329] border border-[#2b3139] rounded-lg text-sm font-semibold text-[#eaecef] focus:outline-none focus:border-[#fcd535] focus:ring-1 focus:ring-[#fcd535]/20 cursor-pointer transition-all hover:border-[#474d57]"
            >
              <option v-for="opt in lotteryOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
            <svg class="w-4 h-4 text-[#707a8a] absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" fill="currentColor" viewBox="0 0 24 24">
              <path d="M7 10l5 5 5-5z"/>
            </svg>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>
