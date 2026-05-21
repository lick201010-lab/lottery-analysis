<template>
  <img
    src="/logo.png"
    alt="弈彩 YiCai"
    class="yc-logo-mark"
    :style="{ width: logoSize, height: logoSize }"
  />
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  size: { type: [Number, String], default: 40 },
});

const logoSize = computed(() =>
  typeof props.size === "number" ? `${props.size}px` : props.size,
);
</script>

<style scoped>
.yc-logo-mark {
  display: inline-block;
  flex: 0 0 auto;
  border-radius: 999px;
  object-fit: contain;
  /* 与原版相同的金边效果保留：图片本身已含金边，不需要额外 border */
}
</style>
