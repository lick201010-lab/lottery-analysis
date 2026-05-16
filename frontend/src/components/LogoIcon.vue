<template>
  <img
    src="/logo.png"
    alt="弈彩"
    class="object-contain shrink-0"
    :style="{ width: size + 'px', height: size + 'px' }"
  />
</template>

<script setup>
defineProps({
  size: { type: [Number, String], default: 40 }
});
</script>
