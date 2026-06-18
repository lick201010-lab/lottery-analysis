<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { createFortuneResult } from "../utils/fortuneShake.js";
import NumberBall from "./NumberBall.vue";

const props = defineProps({
  lotteryLabel:    { type: String, required: true },
  lotteryType:     { type: String, required: true },
  displayDrawNumber: { type: String, required: true },
  displayDate:     { type: String, required: true },
  drawNumbers:     { type: Array,  required: true },
  specialNumber:   { type: Number, default: null },
  poolDisplay:     { type: String, required: true },
  poolSubDisplay:  { type: String, required: true },
  nextPoolDisplay: { type: String, required: true },
  nextPoolSubDisplay: { type: String, required: true },
  drawSourceText:  { type: String, required: true },
  displayDrawTime: { type: String, required: true },
  hasRollingPool:  { type: Boolean, required: true },
});

const hasNumericPool = computed(() => /\d/.test(props.poolDisplay));
const animatedAmount = ref("");
let amountFrame = 0;
const fortuneResult = ref(null);
const fortuneBurstKey = ref(0);
const fortuneCoins = [
  { x: -38, y: -42, r: -24, delay: 0 },
  { x: -18, y: -58, r: 14, delay: 18 },
  { x: 16, y: -56, r: -12, delay: 34 },
  { x: 42, y: -38, r: 28, delay: 54 },
  { x: -52, y: -12, r: 8, delay: 72 },
  { x: 54, y: -8, r: -30, delay: 88 },
  { x: -26, y: 24, r: 22, delay: 106 },
  { x: 28, y: 26, r: -18, delay: 122 },
  { x: 0, y: -70, r: 36, delay: 142 },
];

const jackpotLabel = computed(() => {
  if (props.lotteryType === "marksix" && hasNumericPool.value) return "最新头奖";
  return props.hasRollingPool ? "下一期头奖" : "奖金说明";
});

const jackpotDisplay = computed(() => hasNumericPool.value ? props.poolDisplay : props.nextPoolDisplay);
const jackpotNote    = computed(() => hasNumericPool.value ? props.poolSubDisplay : props.nextPoolSubDisplay);

// Parse jackpot for display: split currency symbol from number
const jackpotParts = computed(() => {
  const raw = jackpotDisplay.value || "";
  const m = raw.match(/^(HK\$|¥|\$)?\s*([\d,]+)(.*)$/);
  if (m) return { currency: m[1] || "", amount: m[2], suffix: m[3]?.trim() || "" };
  return { currency: "", amount: raw, suffix: "" };
});
const jackpotAmountDisplay = computed(() => animatedAmount.value || jackpotParts.value.amount);

const infoItems = computed(() => {
  const items = [
    { label: "期号", value: props.displayDrawNumber },
    { label: "开奖日期", value: props.displayDate },
    { label: "开奖时间", value: props.displayDrawTime },
  ];
  if (props.lotteryType === "marksix") {
    items.push({ label: "数据来源", value: "香港赛马会" });
  } else {
    items.push({ label: "数据来源", value: "500.com" });
  }
  return items;
});

const nextDrawNum = computed(() => {
  const match = String(props.displayDrawNumber).match(/^(\d+)\/(\d+)$/);
  if (match) return `${match[1]}/${String(Number(match[2]) + 1).padStart(match[2].length, "0")}`;
  const num = String(props.displayDrawNumber).match(/^\d+$/);
  if (num) return String(Number(props.displayDrawNumber) + 1);
  return props.displayDrawNumber;
});

const eyebrow = computed(() => {
  if (props.lotteryType === "marksix") return "香港六合彩 · Mark Six";
  if (props.lotteryType === "qxc") return "中国七星彩 · QXC";
  return "中国双色球 · SSQ";
});
const heroTitle    = computed(() => props.lotteryType === "marksix" ? "开奖数据" : "彩票数据");
const heroTitleSub = computed(() => "从容掌握");
const heroSubtitle = computed(() => props.lotteryType === "ssq"
  ? "专业、透明、实时的双色球数据统计平台。每一期开奖，皆是概率与优雅的交汇。"
  : "专业、透明、实时的开奖数据统计平台。每一期开奖，皆是概率与优雅的交汇。"
);
const specialLabel = computed(() => props.lotteryType === "ssq" ? "蓝球" : "特别号");
const ruleText = computed(() => props.lotteryType === "ssq"
  ? "6 红 + 1 蓝全中为一等奖"
  : "6 个正码全中为头奖，特别号用于部分奖项"
);
const syncFrequencyText = computed(() => "平时每 30 分钟同步，开奖夜 21:00-22:50 加密同步");
const displayDateLine = computed(() => {
  if (!props.displayDate || props.displayDate === "--") return "--";
  return `${props.displayDate} · 已开奖`;
});

function easeOutCubic(t) {
  return 1 - Math.pow(1 - t, 3);
}

function animateAmount(rawAmount) {
  const target = Number(String(rawAmount || "").replace(/,/g, ""));
  if (!Number.isFinite(target) || target <= 0) {
    animatedAmount.value = rawAmount || "";
    return;
  }
  if (typeof window === "undefined") {
    animatedAmount.value = Number(target).toLocaleString();
    return;
  }
  if (amountFrame) cancelAnimationFrame(amountFrame);
  animatedAmount.value = "0";
  const start = performance.now();
  const duration = 1400;

  const tick = (now) => {
    const progress = Math.min((now - start) / duration, 1);
    const current = Math.round(target * easeOutCubic(progress));
    animatedAmount.value = current.toLocaleString();
    if (progress < 1) amountFrame = requestAnimationFrame(tick);
  };

  amountFrame = requestAnimationFrame(tick);
}

watch(
  () => jackpotParts.value.amount,
  (amount) => animateAmount(amount),
  { immediate: true }
);

onBeforeUnmount(() => {
  if (amountFrame) cancelAnimationFrame(amountFrame);
});

watch(
  () => props.lotteryType,
  () => {
    fortuneResult.value = null;
  }
);

function shakeFortune() {
  fortuneBurstKey.value += 1;
  fortuneResult.value = createFortuneResult({
    lotteryType: props.lotteryType,
    nonce: `${fortuneBurstKey.value}-${Date.now()}`,
  });
}
</script>

<template>
  <section class="v62-hero-section">
    <!-- Color blobs (behind glass panel) -->
    <div class="hero-blob hero-blob-red"  aria-hidden="true"></div>
    <div class="hero-blob hero-blob-gold" aria-hidden="true"></div>
    <div class="hero-blob hero-blob-blue" aria-hidden="true"></div>

    <div class="v62-hero-inner">
      <!-- Left: text + jackpot + info + buttons -->
      <div class="v62-hero-left">
        <p class="v62-hero-eyebrow">{{ eyebrow }}</p>
        <h1 class="v62-hero-title">{{ heroTitle }}<br>{{ heroTitleSub }}</h1>
        <p class="v62-hero-subtitle">{{ heroSubtitle }}</p>

        <p class="v62-hero-jackpot-label">{{ jackpotLabel }}</p>
        <div class="v62-hero-jackpot-amount">
          <span v-if="jackpotParts.currency" class="currency">{{ jackpotParts.currency }}</span>{{ jackpotAmountDisplay }}<template v-if="jackpotParts.suffix"> {{ jackpotParts.suffix }}</template>
        </div>
        <p class="v62-hero-jackpot-note">{{ jackpotNote }}</p>

        <div class="v62-hero-info-list">
          <div v-for="item in infoItems" :key="item.label" class="v62-hero-info-item">
            <span class="v62-hero-info-label">{{ item.label }}</span>
            <span class="v62-hero-info-value">{{ item.value }}</span>
          </div>
        </div>

        <div class="v62-hero-actions">
          <router-link to="/generate"  class="v62-hero-btn-generate">模拟选号 <span aria-hidden="true">›</span></router-link>
          <router-link to="/data"      class="v62-hero-btn-primary">查看开奖详情 <span aria-hidden="true">›</span></router-link>
          <router-link to="/frequency" class="v62-hero-btn-secondary">号码统计 <span aria-hidden="true">›</span></router-link>
        </div>

        <div class="v62-fortune-widget" :class="{ 'is-active': fortuneResult }">
          <button type="button" class="v62-fortune-trigger" aria-label="财神摆一下，生成娱乐手气签" @click="shakeFortune">
            <span class="v62-fortune-seal" aria-hidden="true">
              <svg viewBox="0 0 64 64" role="img" focusable="false">
                <path class="v62-fortune-seal-shadow" d="M19 50c5-8 9-12 13-12s8 4 13 12H19Z" />
                <path class="v62-fortune-seal-hat" d="M18 25c4-9 9-14 14-14s10 5 14 14c-7 4-21 4-28 0Z" />
                <path class="v62-fortune-seal-face" d="M23 28c0-6 4-10 9-10s9 4 9 10v2c0 6-4 11-9 11s-9-5-9-11v-2Z" />
                <path class="v62-fortune-seal-line" d="M27 28h10M29 34c2 1.5 4 1.5 6 0" />
                <path class="v62-fortune-seal-coin" d="M30 17h4l-2 4-2-4Z" />
              </svg>
            </span>
            <span class="v62-fortune-trigger-copy">
              <strong>财神摆一下</strong>
              <small>轻点试手气</small>
            </span>
            <span class="v62-fortune-burst" :key="fortuneBurstKey" aria-hidden="true">
              <span
                v-for="(coin, index) in fortuneCoins"
                :key="`coin-${fortuneBurstKey}-${index}`"
                class="v62-fortune-coin"
                :style="{
                  '--coin-x': `${coin.x}px`,
                  '--coin-y': `${coin.y}px`,
                  '--coin-r': `${coin.r}deg`,
                  '--coin-delay': `${coin.delay}ms`,
                }"
              ></span>
            </span>
          </button>

          <transition name="v62-fortune-result">
            <div v-if="fortuneResult" class="v62-fortune-result">
              <span class="v62-fortune-kicker">今日手气签</span>
              <strong class="v62-fortune-line">{{ fortuneResult.message }}</strong>
              <div class="v62-fortune-numbers">
                <span
                  v-for="item in fortuneResult.numbers"
                  :key="item.display"
                  class="v62-fortune-number"
                >{{ item.display }}</span>
                <router-link to="/generate">带着手气去模拟选号</router-link>
                <small>{{ fortuneResult.strategy }} · 仅供娱乐，不影响开奖结果</small>
              </div>
            </div>
          </transition>
        </div>
      </div>

      <!-- Right: frosted glass panel -->
      <div class="v62-hero-right-panel">
        <div class="v62-panel-period-header">
          <div class="v62-panel-issue">第 {{ displayDrawNumber }} 期</div>
          <div class="v62-panel-live-badge">
            <span class="v62-panel-live-dot"></span>
            LIVE
          </div>
        </div>
        <div class="v62-panel-date-text">{{ displayDateLine }}</div>

        <div class="v62-panel-balls-grid">
          <NumberBall
            v-for="(n, index) in drawNumbers"
            :key="`${index}-${n}`"
            :number="n"
            size="lg"
            :lotteryType="lotteryType"
          />
        </div>
        <div class="v62-panel-special-row">
          <span class="v62-special-label">{{ specialLabel }}</span>
          <span class="v62-panel-plus">+</span>
          <NumberBall
            v-if="specialNumber !== null && specialNumber !== undefined"
            :number="specialNumber"
            size="lg"
            is-special
            :lotteryType="lotteryType"
          />
        </div>

        <div class="v62-panel-info-list">
          <div class="v62-panel-info-row">
            <strong>玩法规则</strong>
            <span>{{ lotteryLabel }} · {{ ruleText }}</span>
          </div>
          <div class="v62-panel-info-row">
            <strong>数据来源</strong>
            <span>{{ lotteryType === 'marksix' ? '香港赛马会官方公开数据同步' : '500.com / 官方公开数据同步' }}</span>
          </div>
          <div class="v62-panel-info-row">
            <strong>更新频率</strong>
            <span>{{ syncFrequencyText }}</span>
          </div>
        </div>

        <div class="v62-panel-next-footer">
          <div>
            <div class="v62-next-label">Next Draw · 下期开奖</div>
            <div class="v62-next-number">第 {{ nextDrawNum }} 期</div>
            <div class="v62-next-date">{{ displayDrawTime }}</div>
          </div>
          <span class="v62-next-badge">
            <span></span>
            NEXT
          </span>
        </div>
      </div>
    </div>
  </section>
</template>
