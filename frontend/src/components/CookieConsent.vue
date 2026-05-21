<script setup>
import { ref, onMounted } from "vue";

const visible = ref(false);
const STORAGE_KEY = "yicai-consent";

onMounted(() => {
  try {
    const c = localStorage.getItem(STORAGE_KEY);
    if (c !== "accepted" && c !== "rejected") {
      visible.value = true;
    }
  } catch (e) {
    // localStorage 不可用（隐私模式）就默认显示
    visible.value = true;
  }
});

function accept() {
  try {
    localStorage.setItem(STORAGE_KEY, "accepted");
  } catch (e) {}
  if (window.gtag) {
    window.gtag("consent", "update", {
      analytics_storage: "granted",
    });
  }
  visible.value = false;
}

function reject() {
  try {
    localStorage.setItem(STORAGE_KEY, "rejected");
  } catch (e) {}
  // 不调用 gtag('consent', 'update', ...) — 保持默认 denied
  visible.value = false;
}
</script>

<template>
  <Transition name="slide-up">
    <div
      v-if="visible"
      class="fixed bottom-4 left-4 right-4 z-50 mx-auto max-w-3xl rounded-2xl border border-[#ddd4c7] bg-[#fffdf8]/98 p-4 shadow-2xl backdrop-blur-md sm:p-5"
      role="dialog"
      aria-labelledby="cookie-consent-title"
    >
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div class="flex-1">
          <p id="cookie-consent-title" class="mb-1 text-sm font-semibold text-[#233142]">
            🍪 关于 Cookie 与数据分析
          </p>
          <p class="text-xs leading-5 text-[#66706b]">
            我们使用 Google Analytics 收集匿名访问数据用于改进网站。
            不收集任何个人身份信息。你可以拒绝，不影响使用。
            <router-link to="/privacy" class="text-[#8d6f47] underline-offset-2 hover:underline">查看隐私政策</router-link>
          </p>
        </div>
        <div class="flex flex-shrink-0 gap-2">
          <button
            @click="reject"
            class="rounded-lg border border-[#ddd4c7] bg-white px-4 py-2 text-sm font-medium text-[#66706b] transition hover:bg-[#f7f2e9]"
          >
            拒绝
          </button>
          <button
            @click="accept"
            class="rounded-lg bg-[#8d6f47] px-5 py-2 text-sm font-semibold text-white transition hover:bg-[#6f5737]"
          >
            接受
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(110%);
  opacity: 0;
}
</style>
