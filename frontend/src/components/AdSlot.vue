<script setup>
import { onMounted, computed } from "vue";

// ⬇️ 申请到 Google AdSense 后，把你的发布商 ID 填到这里（形如 "ca-pub-1234567890123456"）。
// 留空 = 不加载任何广告、不渲染任何内容、不影响页面。
const ADSENSE_PUBLISHER_ID = "";

const props = defineProps({
  // 在 AdSense 后台为每个广告位生成的 data-ad-slot 数值
  slot: { type: String, default: "" },
  format: { type: String, default: "auto" },
});

const enabled = computed(() => Boolean(ADSENSE_PUBLISHER_ID && props.slot));

onMounted(() => {
  if (!enabled.value) return;
  // 仅在配置了 ID 时按需加载 AdSense 脚本（一次）
  if (!document.querySelector("script[data-yicai-adsense]")) {
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
