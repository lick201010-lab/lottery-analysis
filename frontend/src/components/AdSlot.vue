<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { useI18n } from "../i18n.js";
import { trackEvent } from "../analytics.js";

// Google AdSense 发布商 ID。脚本本身已在 index.html <head> 全局加载（用于 Auto Ads + 验证）。
// 此组件用于「手动广告位」：给它一个 slot 值（AdSense 后台生成的 data-ad-slot）才会渲染。
const ADSENSE_PUBLISHER_ID = "ca-pub-5316394392702028";

const { t } = useI18n();
const adElement = ref(null);
const collapsed = ref(false);
let statusObserver = null;
let lastReportedStatus = "";

const props = defineProps({
  // 在 AdSense 后台为每个广告位生成的 data-ad-slot 数值（来自 adConfig.js）
  slot: { type: String, default: "" },
  format: { type: String, default: "auto" },
  // 预留高度，减少广告加载时的布局抖动（CLS）
  minHeight: { type: Number, default: 100 },
});

const enabled = computed(() => Boolean(ADSENSE_PUBLISHER_ID && props.slot));

onMounted(() => {
  if (!enabled.value) return;
  // index.html 已全局加载 adsbygoogle.js；仅当页面上确实没有时才补一次，避免重复加载
  if (!document.querySelector('script[src*="adsbygoogle.js"]')) {
    const s = document.createElement("script");
    s.async = true;
    s.src = `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${ADSENSE_PUBLISHER_ID}`;
    s.crossOrigin = "anonymous";
    s.setAttribute("data-yicai-adsense", "1");
    document.head.appendChild(s);
  }
  try {
    (window.adsbygoogle = window.adsbygoogle || []).push({});
  } catch (e) {
    /* AdSense 未就绪时静默忽略 */
  }

  if (adElement.value && "MutationObserver" in window) {
    statusObserver = new MutationObserver(() => {
      const status = adElement.value?.dataset.adStatus || "";
      collapsed.value = status === "unfilled";
      if (status && status !== lastReportedStatus) {
        lastReportedStatus = status;
        trackEvent("ad_slot_status", {
          ad_slot: props.slot,
          ad_status: status,
          non_interaction: true,
        });
      }
    });
    statusObserver.observe(adElement.value, {
      attributes: true,
      attributeFilter: ["data-ad-status"],
    });
  }
});

onBeforeUnmount(() => {
  statusObserver?.disconnect();
});
</script>

<template>
  <!-- 未配置 slot 时整块不渲染：不占位、不影响页面 -->
  <div
    v-if="enabled"
    class="yicai-ad"
    :class="{ 'yicai-ad--collapsed': collapsed }"
    :style="{ minHeight: minHeight + 'px' }"
  >
    <span class="yicai-ad-label">{{ t("广告 Advertisement") }}</span>
    <ins
      ref="adElement"
      class="adsbygoogle"
      style="display: block"
      :data-ad-client="ADSENSE_PUBLISHER_ID"
      :data-ad-slot="slot"
      :data-ad-format="format"
      data-full-width-responsive="true"
    ></ins>
  </div>
</template>

<style scoped>
.yicai-ad {
  width: 100%;
  margin: 0 auto;
  text-align: center;
}
.yicai-ad--collapsed {
  display: none;
  min-height: 0 !important;
}
.yicai-ad-label {
  display: block;
  margin-bottom: 4px;
  font-size: 10px;
  letter-spacing: 0.08em;
  color: #b0a692;
  text-transform: uppercase;
}
</style>
