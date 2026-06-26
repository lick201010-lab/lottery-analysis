<script setup>
import { ref, onMounted } from "vue";
import { useI18n } from "../i18n.js";

const { t } = useI18n();
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
      ad_storage: "granted",
      ad_user_data: "granted",
      ad_personalization: "granted",
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
            {{ t("🍪 关于 Cookie 与数据分析") }}
          </p>
          <p class="text-xs leading-5 text-[#66706b]">
            {{ t("我们使用 Cookie 进行网站分析（Google Analytics）与广告展示（Google AdSense），用于改进网站并支持免费运营。不收集个人身份信息，你可以拒绝，不影响使用。") }}
            <router-link to="/privacy" class="text-[#8d6f47] underline-offset-2 hover:underline">{{ t("查看隐私政策") }}</router-link>
          </p>
        </div>
        <div class="flex flex-shrink-0 gap-2">
          <button
            @click="reject"
            class="rounded-lg border border-[#ddd4c7] bg-white px-4 py-2 text-sm font-medium text-[#66706b] transition hover:bg-[#f7f2e9]"
          >
            {{ t("拒绝") }}
          </button>
          <button
            @click="accept"
            class="rounded-lg bg-[#8d6f47] px-5 py-2 text-sm font-semibold text-white transition hover:bg-[#6f5737]"
          >
            {{ t("接受") }}
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
