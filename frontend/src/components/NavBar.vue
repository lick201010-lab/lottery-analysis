<script setup>
import { ref } from "vue";
import { useRoute } from "vue-router";
import { lotteryType } from "../api.js";
import { getLotteryMeta } from "../lotteryMeta.js";

const route = useRoute();
const mobileOpen = ref(false);

const links = [
  { path: "/", label: "首页" },
  { path: "/data", label: "开奖记录" },
  { path: "/frequency", label: "数据分析" },
  { path: "/patterns", label: "走势中心" },
  { path: "/generate", label: "模拟选号" },
  { path: "/patterns-article", label: "资讯" },
  { path: "/about", label: "关于我们" },
];

const lotteryOptions = [
  { value: "marksix", label: "六合彩" },
  { value: "ssq", label: "双色球" },
];

function applyLotteryType(value) {
  lotteryType.value = value;
  mobileOpen.value = false;
}
</script>

<template>
  <nav class="sticky top-0 z-50 h-[72px] border-b border-[#e2e8f0] bg-white/95 text-[#0f172a] shadow-[0_1px_3px_rgba(15,23,42,0.04)] backdrop-blur-md">
    <div class="nav-shell mx-auto flex h-full max-w-[1920px] items-center justify-between">
      <button
        @click="mobileOpen = !mobileOpen"
        class="nav-mobile-menu-button rounded-lg p-2 text-[#7c3aed] xl:hidden"
        aria-label="打开导航菜单"
      >
        <svg v-if="!mobileOpen" class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" /></svg>
        <svg v-else class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
      </button>
      <div class="flex h-full items-center">
        <router-link to="/" class="nav-brand flex h-full w-[232px] items-center gap-3 px-5">
          <div class="relative flex h-11 w-11 shrink-0 items-center justify-center rounded-full" style="background: linear-gradient(135deg, #7c3aed, #2563eb); box-shadow: 0 6px 18px rgba(124, 58, 237, 0.35);">
            <span class="absolute h-4 w-4 rounded-full bg-white"></span>
            <span class="absolute h-2.5 w-6 rounded-full bg-white/85" style="transform: rotate(0deg) translateX(7px)"></span>
            <span class="absolute h-2.5 w-6 rounded-full bg-white/85" style="transform: rotate(72deg) translateX(7px)"></span>
            <span class="absolute h-2.5 w-6 rounded-full bg-white/85" style="transform: rotate(144deg) translateX(7px)"></span>
            <span class="absolute h-2.5 w-6 rounded-full bg-white/85" style="transform: rotate(216deg) translateX(7px)"></span>
            <span class="absolute h-2.5 w-6 rounded-full bg-white/85" style="transform: rotate(288deg) translateX(7px)"></span>
          </div>
          <div class="leading-none">
            <div class="flex items-end gap-2">
              <span class="text-[22px] font-bold tracking-tight text-[#0f172a]">弈彩</span>
              <span class="text-[18px] font-semibold tracking-wide gradient-text">YiCai</span>
            </div>
            <div class="mt-2 text-[10px] tracking-[0.32em] text-[#94a3b8] uppercase">数据分析平台</div>
          </div>
        </router-link>

        <div class="hidden h-full items-center xl:flex">
          <router-link
            v-for="link in links"
            :key="link.path"
            :to="link.path"
            class="relative flex h-full min-w-[96px] items-center justify-center gap-1 px-4 text-[15px] font-semibold transition-all"
            :class="route.path === link.path ? 'text-[#7c3aed]' : 'text-[#475569] hover:text-[#7c3aed]'"
          >
            <span>{{ link.label }}</span>
            <span v-if="route.path === link.path" class="absolute bottom-0 left-3 right-3 h-[3px] rounded-full" style="background: linear-gradient(90deg, #7c3aed, #2563eb);"></span>
          </router-link>
        </div>
      </div>

      <div class="nav-right-controls flex h-full items-center gap-5 px-7">
        <div class="hidden items-center gap-2 lg:flex">
          <button
            v-for="opt in lotteryOptions"
            :key="opt.value"
            @click="applyLotteryType(opt.value)"
            class="flex h-11 items-center gap-2 rounded-xl px-4 text-[14px] font-semibold transition-all"
            :class="lotteryType === opt.value ? 'text-white shadow-[0_6px_16px_rgba(124,58,237,0.30)]' : 'bg-[#f1f5f9] text-[#475569] hover:bg-[#e2e8f0]'"
            :style="lotteryType === opt.value ? 'background: linear-gradient(135deg, #7c3aed, #2563eb);' : ''"
          >
            <span class="grid h-6 w-6 place-items-center rounded-full border" :class="lotteryType === opt.value ? 'border-white/50 bg-white/15' : 'border-[#cbd5e1]'">
              {{ opt.value === "marksix" ? "✤" : "◎" }}
            </span>
            {{ opt.label }}
          </button>
        </div>

        <div class="hidden h-8 w-px bg-[#e2e8f0] 2xl:block"></div>
        <div class="hidden items-center gap-2 text-sm text-[#64748b] 2xl:flex">
          <span class="text-lg text-[#7c3aed]">♟</span>
          <span>{{ getLotteryMeta(lotteryType).navSource }}</span>
        </div>

        <button
          @click="mobileOpen = !mobileOpen"
          class="rounded-lg p-2 text-[#7c3aed] xl:hidden"
          aria-label="打开导航菜单"
        >
          <svg v-if="!mobileOpen" class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" /></svg>
          <svg v-else class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
        </button>
      </div>
      <button class="nav-mobile-user-button xl:hidden text-[#7c3aed]" aria-label="用户中心">
        <svg class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm7 8a7 7 0 0 0-14 0" />
        </svg>
      </button>
    </div>

    <transition name="mobile-menu">
      <div v-show="mobileOpen" class="border-t border-[#e2e8f0] bg-white px-4 py-3 xl:hidden">
        <div class="mb-3 rounded-xl border border-[#e2e8f0] bg-[#f8fafc] p-3">
          <p class="mb-3 text-xs tracking-[0.18em] text-[#64748b] uppercase font-semibold">彩种切换</p>
          <div class="grid grid-cols-2 gap-2">
            <button
              v-for="opt in lotteryOptions"
              :key="opt.value"
              @click="applyLotteryType(opt.value)"
              class="flex items-center justify-center gap-2 rounded-lg px-3 py-2.5 text-sm font-semibold transition-all"
              :class="lotteryType === opt.value ? 'text-white' : 'bg-white text-[#475569] border border-[#e2e8f0]'"
              :style="lotteryType === opt.value ? 'background: linear-gradient(135deg, #7c3aed, #2563eb);' : ''"
            >
              <span class="grid h-6 w-6 place-items-center rounded-full border" :class="lotteryType === opt.value ? 'border-white/50' : 'border-[#cbd5e1]'">
                {{ opt.value === "marksix" ? "✤" : "◎" }}
              </span>
              {{ opt.label }}
            </button>
          </div>
        </div>
        <router-link
          v-for="link in links"
          :key="link.path"
          :to="link.path"
          @click="mobileOpen = false"
          class="flex items-center gap-2 rounded-lg px-3 py-3 text-sm font-semibold"
          :class="route.path === link.path ? 'bg-[#f5f3ff] text-[#7c3aed]' : 'text-[#475569]'"
        >
          <span>{{ link.label }}</span>
        </router-link>
      </div>
    </transition>
  </nav>
</template>
