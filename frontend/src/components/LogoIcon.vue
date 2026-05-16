<template>
  <img
    src="/logo.png"
    alt="弈彩"
    :width="size"
    :height="size"
    class="rounded-full object-cover"
    :style="{ width: size + 'px', height: size + 'px' }"
  />
</template>

<script setup>
defineProps({
  size: { type: [Number, String], default: 40 }
});
</script>
