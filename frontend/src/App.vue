<script setup>
import NavBar from "./components/NavBar.vue";
import LogoIcon from "./components/LogoIcon.vue";
</script>

<template>
  <div class="min-h-screen flex flex-col bg-white">
    <NavBar />
    <main class="flex-1 w-full max-w-[1280px] mx-auto px-4 sm:px-6 py-8">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <footer class="border-t border-[#e3e8ee] bg-white">
      <div class="max-w-[1280px] mx-auto px-6 py-10">
        <div class="flex flex-col md:flex-row items-center justify-between gap-4">
          <div class="flex items-center gap-2.5">
            <LogoIcon :size="32" />
            <span class="text-lg font-bold tracking-tight text-[#0d253d]">弈彩</span>
          </div>
          <p class="text-sm text-[#64748d]">开奖数据统计分析平台 · 仅供娱乐参考</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<style>
.page-enter-active,
.page-leave-active {
  transition: opacity 0.35s cubic-bezier(0.4, 0, 0.2, 1),
              transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}
.page-enter-from {
  opacity: 0;
  transform: translateY(16px) scale(0.985);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.99);
}
</style>
