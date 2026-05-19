<script setup>
import { computed } from "vue";
import NumberBall from "./NumberBall.vue";

const props = defineProps({
  lotteryLabel: { type: String, required: true },
  lotteryType: { type: String, required: true },
  displayDrawNumber: { type: String, required: true },
  displayDate: { type: String, required: true },
  drawNumbers: { type: Array, required: true },
  specialNumber: { type: Number, default: null },
  poolDisplay: { type: String, required: true },
  poolSubDisplay: { type: String, required: true },
  nextPoolDisplay: { type: String, required: true },
  nextPoolSubDisplay: { type: String, required: true },
  drawSourceText: { type: String, required: true },
  displayDrawTime: { type: String, required: true },
  hasRollingPool: { type: Boolean, required: true },
});

const hasNumericPool = computed(() => /\d/.test(props.poolDisplay));

const featureLabel = computed(() =>
  props.hasRollingPool && hasNumericPool.value ? "下一期头奖" : "奖金说明"
);

const featureAmount = computed(() => {
  if (props.hasRollingPool && hasNumericPool.value) {
    return props.poolDisplay;
  }
  return props.nextPoolDisplay;
});

const featureSubtext = computed(() => {
  if (props.hasRollingPool && hasNumericPool.value) {
    return "预计头奖基金 · 官方公告抓取";
  }
  return props.poolSubDisplay;
});

const chipRows = computed(() => {
  if (props.lotteryType === "ssq") {
    return [
      "奖池滚存：按官方公告显示",
      `来源：${props.drawSourceText.replace(/^数据来源：/, "")}`,
      "无数据时：以下期开奖公告为准",
    ];
  }
  return [
    "金多宝 / Snowball：有则显示",
    `来源：${props.drawSourceText.replace(/^数据来源：/, "")}`,
    "无数据时：以官方公告为准",
  ];
});
</script>

<template>
  <section class="prize-feature-card ref-card p-0 overflow-hidden">
    <div class="prize-feature-panel">
      <div class="prize-feature-wave" aria-hidden="true"></div>
      <div class="prize-feature-skyline" aria-hidden="true">
        <img src="/assets/hk-skyline.png" alt="" decoding="async" />
      </div>

      <div class="prize-feature-copy">
        <p class="prize-feature-intro">
          选择一个红色箭头，可查看更多与本期摇号相关的信息，包括奖项注数、总奖金、历史走势。
        </p>

        <div class="prize-feature-shell">
          <div class="prize-feature-main">
            <div class="prize-feature-badge-row">
              <span class="prize-feature-kind">{{ lotteryLabel }}</span>
              <span class="prize-feature-refresh">已更新 {{ displayDrawTime }}</span>
            </div>

            <div class="mt-4">
              <p class="prize-feature-label">{{ featureLabel }}</p>
              <p class="prize-feature-amount">{{ featureAmount }}</p>
              <p class="prize-feature-subtext">{{ featureSubtext }}</p>
            </div>

            <div class="prize-feature-actions">
              <router-link to="/data" class="prize-feature-primary">查看开奖</router-link>
              <router-link to="/jackpot" class="prize-feature-secondary">奖金详情</router-link>
            </div>
          </div>

          <div class="prize-feature-result">
            <div class="prize-feature-result-card">
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="prize-feature-result-label">最新结果</p>
                  <p class="prize-feature-result-meta">第 {{ displayDrawNumber }} 期 · {{ displayDate }}</p>
                </div>
                <router-link to="/data" class="prize-feature-result-link">更多结果</router-link>
              </div>

              <div class="mt-5 flex flex-wrap items-center gap-3">
                <NumberBall
                  v-for="number in drawNumbers"
                  :key="number"
                  :number="number"
                  size="md"
                  :lotteryType="lotteryType"
                />
                <NumberBall
                  v-if="specialNumber"
                  :number="specialNumber"
                  size="md"
                  is-special
                  :lotteryType="lotteryType"
                />
              </div>
            </div>

            <div class="prize-feature-mobile-note">
              {{ hasRollingPool && hasNumericPool ? "预计头奖基金以官方公告页为准" : "未抓到官方奖池时：固定奖金制，不设滚动奖池" }}
            </div>
          </div>
        </div>

        <div class="prize-feature-chip-grid">
          <div v-for="chip in chipRows" :key="chip" class="prize-info-chip">
            {{ chip }}
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
