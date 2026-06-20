<script setup>
import { onMounted, computed } from "vue";

// Google AdSense 发布商 ID。脚本本身已在 index.html <head> 全局加载（用于 Auto Ads + 验证）。
// 此组件用于「手动广告位」：给它一个 slot 值（AdSense 后台生成的 data-ad-slot）才会渲染。
const ADSENSE_PUBLISHER_ID = "ca-pub-5316394392702028";

const props = defineProps({
  // 在 AdSense 后台为每个广告位生成的 data-ad-slot 数值
  slot: { type: String, default: "" },
  format: { type: String, default: "auto" },
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
});
</script>

<template>
  <ins
    v-if="enabled"
    class="adsbygoogle"
    style="display: block"
    :data-ad-client="ADSENSE_PUBLISHER_ID"
    :data-ad-slot="slot"
    :data-ad-format="format"
    data-full-width-responsive="true"
  ></ins>
</template>
