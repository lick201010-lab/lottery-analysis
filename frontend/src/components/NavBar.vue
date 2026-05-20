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
  <nav class="sticky top-0 z-50 h-[72px] border-b border-[#2b3942] bg-[#132531] text-[#d8e0e2] shadow-[0_8px_28px_rgba(12,24,32,0.18)]">
    <div class="nav-shell mx-auto flex h-full max-w-[1920px] items-center justify-between">
      <button
        @click="mobileOpen = !mobileOpen"
        class="nav-mobile-menu-button rounded-lg p-2 text-white xl:hidden"
        aria-label="打开导航菜单"
      >
        <svg v-if="!mobileOpen" class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" /></svg>
        <svg v-else class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
      </button>
      <div class="flex h-full items-center">
        <router-link to="/" class="nav-brand flex h-full w-[232px] items-center gap-3 bg-[#21323c] px-5">
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
            class="relative flex h-full min-w-[104px] items-center justify-center gap-1 px-4 text-[16px] font-semibold transition-colors"
            :class="route.path === link.path ? 'bg-[#263945] text-[#e0b76d]' : 'text-[#d9e1e3]/88 hover:bg-[#1b303d] hover:text-white'"
          >
            <span>{{ link.label }}</span>
            <span v-if="link.suffix" class="text-sm">{{ link.suffix }}</span>
            <span v-if="route.path === link.path" class="absolute bottom-0 left-0 right-0 h-[3px] bg-[#d1a35e]"></span>
          </router-link>
        </div>
      </div>

      <div class="nav-right-controls flex h-full items-center gap-5 px-7">
        <div class="hidden items-center gap-2 lg:flex">
          <button
            v-for="opt in lotteryOptions"
            :key="opt.value"
            @click="applyLotteryType(opt.value)"
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
          <span>{{ getLotteryMeta(lotteryType).navSource }}</span>
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
      <button class="nav-mobile-user-button xl:hidden" aria-label="用户中心">
        <svg class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm7 8a7 7 0 0 0-14 0" />
        </svg>
      </button>
    </div>

    <transition name="mobile-menu">
      <div v-show="mobileOpen" class="border-t border-white/10 bg-[#132531] px-4 py-3 xl:hidden">
        <div class="mb-3 rounded-xl border border-white/10 bg-white/5 p-3">
          <p class="mb-3 text-xs tracking-[0.18em] text-white/55">彩种切换</p>
          <div class="grid grid-cols-2 gap-2">
            <button
              v-for="opt in lotteryOptions"
              :key="opt.value"
              @click="applyLotteryType(opt.value)"
              class="flex items-center justify-center gap-2 rounded-lg px-3 py-2.5 text-sm transition-all"
              :class="lotteryType === opt.value ? 'bg-[#fffaf2] text-[#20313b] shadow-[inset_0_-3px_0_#d1a35e]' : 'bg-white/8 text-white/75'"
            >
              <span class="grid h-6 w-6 place-items-center rounded-full border" :class="lotteryType === opt.value ? 'border-[#d1a35e]' : 'border-white/30'">
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
          class="flex items-center gap-2 rounded-lg px-3 py-3 text-sm"
          :class="route.path === link.path ? 'bg-[#263945] text-[#e0b76d]' : 'text-white/80'"
        >
          <span>{{ link.label }}</span>
          <span v-if="link.suffix" class="text-xs">{{ link.suffix }}</span>
        </router-link>
      </div>
    </transition>
  </nav>
</template>
