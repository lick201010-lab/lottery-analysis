<script setup>
import NavBar from "./components/NavBar.vue";
</script>

<template>
  <div class="min-h-screen flex flex-col bg-[#0b0e11]">
    <NavBar />
    <main class="flex-1 w-full max-w-[1440px] mx-auto px-4 sm:px-6 py-6">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <footer class="border-t border-[#2b3139] bg-[#0b0e11]">
      <div class="max-w-[1440px] mx-auto px-6 py-8">
        <div class="flex flex-col md:flex-row items-center justify-between gap-4">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-[#fcd535] to-[#f0b90b] flex items-center justify-center">
              <span class="text-[#181a20] font-bold text-sm">彩</span>
            </div>
            <span class="text-lg font-bold tracking-tight gradient-text">彩溯</span>
          </div>
          <p class="text-sm text-[#707a8a]">彩票数据分析系统 · 仅供娱乐参考 · 理性购彩</p>
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
