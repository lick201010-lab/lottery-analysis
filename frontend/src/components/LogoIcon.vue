<template>
  <span
    class="yc-logo-mark"
    role="img"
    aria-label="弈彩"
    :style="{ width: logoSize, height: logoSize }"
  >
    <span class="yc-logo-core"></span>
    <span
      v-for="angle in spokeAngles"
      :key="angle"
      class="yc-logo-spoke"
      :style="{ transform: `rotate(${angle}deg) translateX(calc(${logoSize} * 0.19))` }"
    ></span>
  </span>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  size: { type: [Number, String], default: 40 },
});

const spokeAngles = [0, 72, 144, 216, 288];
const logoSize = computed(() => (typeof props.size === "number" ? `${props.size}px` : props.size));
</script>

<style scoped>
.yc-logo-mark {
  position: relative;
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border: 2px solid #d4a85f;
  border-radius: 999px;
  background: #21323c;
  box-shadow: inset 0 0 0 1px rgba(255, 244, 220, 0.08);
}

.yc-logo-core {
  position: absolute;
  width: 34%;
  height: 34%;
  border-radius: 999px;
  background: #d4a85f;
}

.yc-logo-spoke {
  position: absolute;
  width: 64%;
  height: 26%;
  border-radius: 999px;
  background: #d4a85f;
  transform-origin: center;
}
</style>
