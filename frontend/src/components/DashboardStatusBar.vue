<script setup>
defineProps({
  statusSourceText: { type: String, required: true },
  displayDate: { type: String, required: true },
  displayDrawTime: { type: String, required: true },
});
</script>

<template>
  <div class="dashboard-statusbar">
    <span>盾</span>
    <span>仅供娱乐参考，不构成任何投注建议。</span>
    <span class="mx-auto">{{ statusSourceText }}</span>
    <span>最近开奖： {{ displayDate }} {{ displayDrawTime }}</span>
    <span>⟳</span>
  </div>
</template>
