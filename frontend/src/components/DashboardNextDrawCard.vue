<script setup>
import CountdownTimer from "./CountdownTimer.vue";

defineProps({
  nextDrawNumber: { type: String, required: true },
  drawWeekLabel: { type: String, required: true },
  displayDrawTime: { type: String, required: true },
});
</script>

<template>
  <div class="ref-card dashboard-compact-card p-6">
    <h2 class="mb-3 text-[23px] font-semibold text-[#1c3342]">下期开奖</h2>
    <div class="mb-5 flex flex-wrap gap-6 text-[15px] text-[#5f6868]">
      <span>▣ 第 {{ nextDrawNumber }} 期</span>
      <span>▣ {{ drawWeekLabel }} {{ displayDrawTime }}</span>
    </div>
    <CountdownTimer />
    <p class="mt-5 text-[14px] text-[#767d7b]">♧ 距离开奖仅供参考，请以官方公布时间为准</p>
  </div>
</template>
