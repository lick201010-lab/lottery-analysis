<script setup>
import NavBar from "./components/NavBar.vue";
</script>

<template>
  <div class="min-h-screen flex flex-col bg-[#f3f4f6]">
    <NavBar />
    <main class="flex-1 w-full max-w-[1440px] mx-auto px-6 py-8">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <footer class="text-center py-6 text-sm text-gray-400 border-t border-gray-200/60">
      <p>彩票数据分析系统 · 仅供娱乐参考</p>
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
