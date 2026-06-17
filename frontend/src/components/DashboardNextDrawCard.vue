<script setup>
import CountdownTimer from "./CountdownTimer.vue";

const syncFrequencyText = "平时每 30 分钟同步，开奖夜 21:00-22:50 加密同步";

const props = defineProps({
  nextDrawNumber:    { type: String, required: true },
  drawWeekLabel:     { type: String, required: true },
  displayDrawTime:   { type: String, required: true },
  // Status card props (right column)
  displayDrawNumber: { type: String, default: "--" },
  poolDisplay:       { type: String, default: "--" },
  displayDate:       { type: String, default: "--" },
  lotteryType:       { type: String, default: "marksix" },
});
</script>

<template>
  <div class="v62-glass-surface p-6 sm:p-7">
    <div class="v62-countdown-grid">
      <!-- Left: countdown -->
      <div>
        <h2 class="v62-section-title mb-1">下一期开奖</h2>
        <p class="v62-section-sub mb-5">
          {{ drawWeekLabel }} {{ displayDrawTime }} 开奖。距离第 {{ nextDrawNumber }} 期还有：
        </p>
        <CountdownTimer />
        <p class="mt-4 text-[12.5px] text-[#767d7b]">♧ 仅供参考，请以官方公布为准</p>
      </div>

      <!-- Right: status card -->
      <div class="v62-status-card">
        <div class="v62-status-label">本期数据状态 · Status</div>

        <div class="v62-status-row">
          <span class="v62-status-key">期号</span>
          <span class="v62-status-val">{{ displayDrawNumber }}</span>
        </div>
        <div class="v62-status-row">
          <span class="v62-status-key">开奖日期</span>
          <span class="v62-status-val">{{ displayDate }}</span>
        </div>
        <div class="v62-status-row">
          <span class="v62-status-key">数据完整性</span>
          <span class="v62-status-val">{{ lotteryType === 'marksix' ? '49/49 号码已归档' : '33+16 号码已归档' }}</span>
        </div>
        <div class="v62-status-row">
          <span class="v62-status-key">头奖 / 奖池</span>
          <span class="v62-status-val jackpot">{{ poolDisplay }}</span>
        </div>
        <div class="v62-status-row" style="border-bottom:0">
          <span class="v62-status-key">同步频率</span>
          <span class="v62-status-val">{{ syncFrequencyText }}</span>
        </div>

        <div class="v62-live-badge">
          <span class="v62-live-dot"></span>
          LIVE · 系统正常
        </div>
      </div>
    </div>
  </div>
</template>
