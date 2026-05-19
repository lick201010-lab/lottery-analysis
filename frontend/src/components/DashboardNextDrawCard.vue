<script setup>
import CountdownTimer from "./CountdownTimer.vue";

defineProps({
  nextDrawNumber: { type: String, required: true },
  drawWeekLabel: { type: String, required: true },
  displayDrawTime: { type: String, required: true },
});
</script>

<template>
  <div class="ref-card p-7">
    <h2 class="mb-3 text-[25px] font-semibold text-[#1c3342]">下期开奖</h2>
    <div class="mb-6 flex flex-wrap gap-8 text-[16px] text-[#5f6868]">
      <span>▣ 第 {{ nextDrawNumber }} 期</span>
      <span>▣ {{ drawWeekLabel }} {{ displayDrawTime }}</span>
    </div>
    <CountdownTimer />
    <p class="mt-7 text-[15px] text-[#767d7b]">♧ 距离开奖仅供参考，请以官方公布时间为准</p>
  </div>
</template>
