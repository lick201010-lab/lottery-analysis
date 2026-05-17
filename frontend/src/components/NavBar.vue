<script setup>
import { ref } from "vue";
import { useRoute } from "vue-router";
import { lotteryType } from "../api.js";
import LogoIcon from "./LogoIcon.vue";

const route = useRoute();
const mobileOpen = ref(false);

const links = [
  { path: "/", label: "数据概览", icon: "M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z" },
  { path: "/frequency", label: "号码统计", icon: "M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z" },
  { path: "/patterns", label: "走势分析", icon: "M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z" },
  { path: "/pairs", label: "组合分析", icon: "M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z" },
  { path: "/generate", label: "模拟选号", icon: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 14h-2v-2h2v2zm0-4h-2V6h2v6z" },
  { path: "/jackpot", label: "奖金分析", icon: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1.41 16.09V20h-2.67v-1.93c-1.71-.36-3.16-1.46-3.27-3.4h1.96c.1 1.05.82 1.87 2.65 1.87 1.96 0 2.4-.98 2.4-1.59 0-.83-.44-1.61-2.67-2.14-2.48-.6-4.18-1.62-4.18-3.67 0-1.72 1.39-2.84 3.11-3.21V4h2.67v1.95c1.86.45 2.79 1.86 2.85 3.39H14.3c-.05-1.11-.64-1.87-2.22-1.87-1.5 0-2.4.68-2.4 1.64 0 .84.65 1.39 2.67 1.91s4.18 1.39 4.18 3.91c-.01 1.83-1.38 2.83-3.12 3.16z" },
  { path: "/data", label: "历史记录", icon: "M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" },
];

const lotteryOptions = [
  { value: "marksix", label: "六合彩" },
  { value: "ssq", label: "双色球" },
];
</script>

<template>
  <nav class="sticky top-0 z-50 border-b border-[#ddd4c7] bg-[#fffdf8]/95 shadow-sm shadow-[#4a3d2d]/5">
    <div class="mx-auto max-w-[1440px] px-4 sm:px-8">
      <div class="flex h-[64px] items-center justify-between gap-4">
        <div class="flex items-center gap-4 lg:gap-7">
          <router-link to="/" class="flex items-center gap-2.5 group">
            <LogoIcon :size="32" />
            <div class="flex flex-col leading-none">
              <span class="text-[15px] font-bold tracking-tight text-[#233142]">弈彩</span>
              <span class="mt-0.5 text-[10px] uppercase tracking-widest text-[#7d867f]">YiCai</span>
            </div>
          </router-link>

          <div class="hidden items-center gap-0.5 lg:flex">
            <router-link
              v-for="link in links"
              :key="link.path"
              :to="link.path"
              class="group relative flex items-center gap-2 rounded-lg px-3 py-2 text-[13px] font-medium transition-all duration-200"
              :class="
                route.path === link.path
                  ? 'bg-[#e7dcc7] text-[#6f5737]'
                  : 'text-[#7d867f] hover:bg-[#f3ede3] hover:text-[#233142]'
              "
            >
              <svg class="h-[16px] w-[16px] opacity-80" fill="currentColor" viewBox="0 0 24 24">
                <path :d="link.icon" />
              </svg>
              <span>{{ link.label }}</span>
            </router-link>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2">
            <button
              v-for="opt in lotteryOptions"
              :key="opt.value"
              @click="lotteryType = opt.value"
              class="rounded-full px-4 py-1.5 text-[13px] font-bold whitespace-nowrap transition-all duration-200"
              :class="lotteryType === opt.value
                ? (opt.value === 'marksix' ? 'pill-marksix scale-105' : 'pill-ssq scale-105')
                : 'pill-inactive'
              "
            >
              {{ opt.label }}
            </button>
          </div>

          <button
            @click="mobileOpen = !mobileOpen"
            class="rounded-lg p-2 text-[#7d867f] transition-colors hover:bg-[#f3ede3] hover:text-[#233142] lg:hidden"
            aria-label="打开导航菜单"
          >
            <svg v-if="!mobileOpen" class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" /></svg>
            <svg v-else class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
      </div>

      <transition name="mobile-menu">
        <div v-show="mobileOpen" class="border-t border-[#ddd4c7] pb-4 pt-3 lg:hidden">
          <div class="flex flex-col gap-1">
            <router-link
              v-for="link in links"
              :key="link.path"
              :to="link.path"
              @click="mobileOpen = false"
              class="flex items-center gap-3 rounded-lg px-3 py-2.5 text-[14px] font-medium transition-all duration-200"
              :class="
                route.path === link.path
                  ? 'bg-[#e7dcc7] text-[#6f5737]'
                  : 'text-[#7d867f] hover:bg-[#f3ede3] hover:text-[#233142]'
              "
            >
              <svg class="h-[18px] w-[18px] opacity-80" fill="currentColor" viewBox="0 0 24 24">
                <path :d="link.icon" />
              </svg>
              {{ link.label }}
            </router-link>
          </div>
        </div>
      </transition>
    </div>
  </nav>
</template>
