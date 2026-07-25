<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { useI18n } from "../i18n.js";

const { t, lang } = useI18n();
const visible = ref(false);
const STORAGE_KEY = "yicai-consent";
let cmpDetectionTimer = 0;

const consentCopy = computed(() => {
  if (lang.value === "en") {
    return "We use cookies for anonymous analytics and contextual, non-personalized advertising. We do not use your visits to lottery-data pages to personalize ads. You may decline without affecting access.";
  }
  if (lang.value === "tw") {
    return "我們使用 Cookie 進行匿名網站分析及情境式、非個人化廣告展示，不會根據你瀏覽彩票數據頁面的行為投放個人化廣告。你可以拒絕，且不影響網站使用。";
  }
  return "我们使用 Cookie 进行匿名网站分析及情境式、非个性化广告展示，不会根据你浏览彩票数据页面的行为投放个性化广告。你可以拒绝，且不影响网站使用。";
});

function hasCertifiedCmp() {
  return (
    typeof window.__tcfapi === "function" ||
    Boolean(document.querySelector('iframe[name="__tcfapiLocator"]'))
  );
}

onMounted(() => {
  try {
    const c = localStorage.getItem(STORAGE_KEY);
    if (c === "accepted" || c === "rejected") return;
  } catch (e) {
    // Continue to the fallback consent prompt when storage is unavailable.
  }

  // Google CMP is active for regulated regions. Give it time to expose the
  // TCF API so visitors never receive two consent dialogs.
  cmpDetectionTimer = window.setTimeout(() => {
    visible.value = !hasCertifiedCmp();
  }, 1200);
});

onBeforeUnmount(() => {
  if (cmpDetectionTimer) window.clearTimeout(cmpDetectionTimer);
});

function accept() {
  try {
    localStorage.setItem(STORAGE_KEY, "accepted");
  } catch (e) {}
  if (window.gtag) {
    window.gtag("consent", "update", {
      ad_storage: "granted",
      ad_user_data: "denied",
      ad_personalization: "denied",
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
            {{ consentCopy }}
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
