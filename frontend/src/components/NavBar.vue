<script setup>
import { ref } from "vue";
import { useRoute } from "vue-router";
import { lotteryType } from "../api.js";

const route = useRoute();
const mobileOpen = ref(false);

const links = [
  { path: "/", label: "数据概览", icon: "M4 17h4V7H4v10Zm6 0h4V4h-4v13Zm6 0h4v-7h-4v7Z" },
  { path: "/frequency", label: "号码统计", icon: "M4 5h16v14H4V5Zm2 2v10h12V7H6Zm2 2h2v6H8V9Zm4 3h2v3h-2v-3Z" },
  { path: "/patterns", label: "走势分析", icon: "M4 18h16v2H4v-2Zm1-3 4-5 4 3 5-7 2 1-6.5 9-4-3-3 4-1.5-2Z" },
  { path: "/pairs", label: "组合分析", icon: "M7 7h4v4H7V7Zm6 0h4v4h-4V7Zm-6 6h4v4H7v-4Zm6 0h4v4h-4v-4Z" },
  { path: "/generate", label: "模拟选号", icon: "M12 3 4 7v10l8 4 8-4V7l-8-4Zm0 2.2L17 8l-5 2.8L7 8l5-2.8ZM6 9.7l5 2.8v5.8l-5-2.5V9.7Zm12 0v6.1l-5 2.5v-5.8l5-2.8Z" },
  { path: "/jackpot", label: "奖金分析", icon: "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm1 15h-2v-1.2c-1.4-.3-2.3-1.1-2.5-2.3h2c.2.5.7.8 1.6.8 1 0 1.4-.3 1.4-.8s-.5-.8-1.8-1.1c-1.9-.5-3-1.2-3-2.8 0-1.3.9-2.2 2.3-2.5V6h2v1.1c1.3.3 2.1 1.1 2.3 2.2h-2c-.2-.4-.6-.7-1.3-.7-.8 0-1.2.3-1.2.8s.5.7 1.8 1c2 .5 3 1.3 3 2.9 0 1.3-.9 2.2-2.5 2.6V17Z" },
  { path: "/data", label: "历史记录", icon: "M6 3h12v3h2v15H4V6h2V3Zm2 3h8V5H8v1Zm-2 4h12V8H6v2Zm0 2v7h12v-7H6Z" },
];

const lotteryOptions = [
  { value: "marksix", label: "六合彩" },
  { value: "ssq", label: "双色球" },
];
</script>

<template>
  <nav class="sticky top-0 z-50 h-[72px] border-b border-[#2b3942] bg-[#132531] text-[#d8e0e2] shadow-[0_8px_28px_rgba(12,24,32,0.18)]">
    <div class="mx-auto flex h-full max-w-[1920px] items-center justify-between">
      <div class="flex h-full items-center">
        <router-link to="/" class="flex h-full w-[232px] items-center gap-3 bg-[#21323c] px-5">
          <div class="relative flex h-11 w-11 shrink-0 items-center justify-center rounded-full border-2 border-[#d4a85f]">
            <span class="absolute h-4 w-4 rounded-full bg-[#d4a85f]"></span>
            <span class="absolute h-3 w-7 rounded-full bg-[#d4a85f]" style="transform: rotate(0deg) translateX(8px)"></span>
            <span class="absolute h-3 w-7 rounded-full bg-[#d4a85f]" style="transform: rotate(72deg) translateX(8px)"></span>
            <span class="absolute h-3 w-7 rounded-full bg-[#d4a85f]" style="transform: rotate(144deg) translateX(8px)"></span>
            <span class="absolute h-3 w-7 rounded-full bg-[#d4a85f]" style="transform: rotate(216deg) translateX(8px)"></span>
            <span class="absolute h-3 w-7 rounded-full bg-[#d4a85f]" style="transform: rotate(288deg) translateX(8px)"></span>
          </div>
          <div class="leading-none">
            <div class="flex items-end gap-2">
              <span class="text-[23px] font-semibold tracking-[0.11em] text-white">弈彩</span>
              <span class="text-[20px] font-semibold tracking-wide text-[#e4b96f]">YiCai</span>
            </div>
            <div class="mt-2 text-[11px] tracking-[0.42em] text-white/85">数据分析平台</div>
          </div>
        </router-link>

        <div class="hidden h-full items-center xl:flex">
          <router-link
            v-for="link in links"
            :key="link.path"
            :to="link.path"
            class="relative flex h-full min-w-[96px] items-center justify-center gap-2 px-3 text-[15px] transition-colors"
            :class="route.path === link.path ? 'bg-[#263945] text-[#e0b76d]' : 'text-[#d9e1e3]/88 hover:bg-[#1b303d] hover:text-white'"
          >
            <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24"><path :d="link.icon" /></svg>
            <span>{{ link.label }}</span>
            <span v-if="route.path === link.path" class="absolute bottom-0 left-0 right-0 h-[3px] bg-[#d1a35e]"></span>
          </router-link>
        </div>
      </div>

      <div class="flex h-full items-center gap-5 px-7">
        <div class="hidden items-center gap-2 lg:flex">
          <button
            v-for="opt in lotteryOptions"
            :key="opt.value"
            @click="lotteryType = opt.value"
            class="flex h-12 items-center gap-2 rounded-xl px-4 text-[15px] transition-all"
            :class="lotteryType === opt.value ? 'bg-[#fffaf2] text-[#20313b] shadow-[inset_0_-3px_0_#d1a35e]' : 'bg-white/6 text-white/70 hover:bg-white/10'"
          >
            <span class="grid h-7 w-7 place-items-center rounded-full border" :class="lotteryType === opt.value ? 'border-[#d1a35e]' : 'border-white/30'">
              {{ opt.value === "marksix" ? "✤" : "◎" }}
            </span>
            {{ opt.label }}
          </button>
        </div>

        <div class="hidden h-8 w-px bg-white/18 2xl:block"></div>
        <div class="hidden items-center gap-3 text-sm text-white/78 2xl:flex">
          <span class="text-xl">♟</span>
          <span>数据源：香港马会</span>
          <span>⌄</span>
        </div>

        <button
          @click="mobileOpen = !mobileOpen"
          class="rounded-lg p-2 text-white xl:hidden"
          aria-label="打开导航菜单"
        >
          <svg v-if="!mobileOpen" class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" /></svg>
          <svg v-else class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
        </button>
      </div>
    </div>

    <transition name="mobile-menu">
      <div v-show="mobileOpen" class="border-t border-white/10 bg-[#132531] px-4 py-3 xl:hidden">
        <router-link
          v-for="link in links"
          :key="link.path"
          :to="link.path"
          @click="mobileOpen = false"
          class="flex items-center gap-3 rounded-lg px-3 py-3 text-sm"
          :class="route.path === link.path ? 'bg-[#263945] text-[#e0b76d]' : 'text-white/80'"
        >
          <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 24 24"><path :d="link.icon" /></svg>
          {{ link.label }}
        </router-link>
      </div>
    </transition>
  </nav>
</template>
