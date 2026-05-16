<script setup>
import NavBar from "./components/NavBar.vue";
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
            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-[#665efd] to-[#4434d4] flex items-center justify-center">
              <span class="text-white font-bold text-xs">弈</span>
            </div>
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
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
