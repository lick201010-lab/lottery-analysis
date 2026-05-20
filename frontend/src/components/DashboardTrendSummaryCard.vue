<script setup>
import NumberBall from "./NumberBall.vue";

defineProps({
  hotNumbers: { type: Array, required: true },
  hotSupport: { type: String, required: true },
  coldNumbers: { type: Array, required: true },
  coldSupport: { type: String, required: true },
  trendHeadline: { type: String, required: true },
  consecutiveHeadline: { type: String, required: true },
  consecutiveSummary: { type: String, required: true },
  lotteryType: { type: String, required: true },
});
</script>

<template>
  <div class="ref-card dashboard-compact-card overflow-hidden p-0">
    <div class="flex items-center justify-between px-6 py-5">
      <h2 class="text-[23px] font-semibold text-[#1c3342]">
        号码趋势摘要 <span class="text-[16px] font-normal text-[#6e7373]">（近 30 期）</span>
      </h2>
      <router-link to="/frequency" class="text-[14px] text-[#7a746c]">查看详情 ›</router-link>
    </div>
    <div class="grid grid-cols-1 border-t border-[#e2d9cc] sm:grid-cols-3">
      <div class="trend-cell">
        <p>最热号码</p>
        <div class="mt-4 flex justify-center gap-2">
          <NumberBall v-for="n in hotNumbers" :key="n" :number="n" size="sm" :lotteryType="lotteryType" />
        </div>
        <span>{{ hotSupport }}</span>
      </div>
      <div class="trend-cell">
        <p>最冷号码</p>
        <div class="mt-4 flex justify-center gap-2">
          <NumberBall v-for="n in coldNumbers" :key="n" :number="n" size="sm" :lotteryType="lotteryType" />
        </div>
        <span>{{ coldSupport }}</span>
      </div>
      <div class="trend-cell">
        <p>{{ trendHeadline }}</p>
        <strong>{{ consecutiveHeadline }}</strong>
        <span>{{ consecutiveSummary }}</span>
      </div>
    </div>
  </div>
</template>
