<script setup>
import { computed } from "vue";
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

const infoItems = computed(() => {
  const items = [
    { label: "期号", value: props.displayDrawNumber },
    { label: "开奖日期", value: props.displayDate },
    { label: "开奖时间", value: props.displayDrawTime },
  ];
  if (props.lotteryType === "marksix") {
    items.push({ label: "数据来源", value: "lottery.hk" });
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
        <h1 class="v62-hero-title">{{ heroTitle }}</h1>
        <p class="v62-hero-title-sub">{{ heroTitleSub }}</p>

        <p class="v62-hero-jackpot-label">{{ jackpotLabel }}</p>
        <div class="v62-hero-jackpot-amount">
          <span v-if="jackpotParts.currency" class="currency">{{ jackpotParts.currency }}</span>{{ jackpotParts.amount }}<template v-if="jackpotParts.suffix"> {{ jackpotParts.suffix }}</template>
        </div>
        <p class="v62-hero-jackpot-note">{{ jackpotNote }}</p>

        <div class="v62-hero-info-list">
          <div v-for="item in infoItems" :key="item.label" class="v62-hero-info-item">
            <span class="v62-hero-info-label">{{ item.label }}</span>
            <span class="v62-hero-info-value">{{ item.value }}</span>
          </div>
        </div>

        <div class="v62-hero-actions">
          <router-link to="/data"      class="v62-hero-btn-primary">查看开奖详情 <span aria-hidden="true">›</span></router-link>
          <router-link to="/frequency" class="v62-hero-btn-secondary">号码统计 <span aria-hidden="true">›</span></router-link>
        </div>
      </div>

      <!-- Right: frosted glass panel -->
      <div class="v62-hero-right-panel">
        <!-- Period + date row -->
        <div class="v62-panel-issue-row">
          <span class="v62-panel-issue-pill">第 {{ displayDrawNumber }} 期</span>
          <span class="v62-panel-date">{{ displayDate }}</span>
        </div>

        <!-- Balls -->
        <p class="v62-panel-title">最新开奖号码</p>
        <div class="v62-panel-balls">
          <NumberBall
            v-for="(n, index) in drawNumbers"
            :key="`${index}-${n}`"
            :number="n"
            size="md"
            :lotteryType="lotteryType"
          />
          <span class="v62-panel-plus">+</span>
          <NumberBall
            v-if="specialNumber !== null && specialNumber !== undefined"
            :number="specialNumber"
            size="md"
            is-special
            :lotteryType="lotteryType"
          />
        </div>

        <!-- Info rows -->
        <div class="v62-panel-info-list">
          <div class="v62-panel-info-row">
            <span class="v62-panel-info-key">彩种</span>
            <span class="v62-panel-info-val">{{ lotteryLabel }}</span>
          </div>
          <div class="v62-panel-info-row">
            <span class="v62-panel-info-key">开奖时间</span>
            <span class="v62-panel-info-val">{{ displayDrawTime }}</span>
          </div>
          <div class="v62-panel-info-row">
            <span class="v62-panel-info-key">头奖</span>
            <span class="v62-panel-info-val mono">{{ jackpotDisplay }}</span>
          </div>
          <div class="v62-panel-info-row">
            <span class="v62-panel-info-key">数据来源</span>
            <span class="v62-panel-info-val">{{ lotteryType === 'marksix' ? 'lottery.hk' : '500.com' }}</span>
          </div>
        </div>

        <!-- Next draw footer -->
        <div class="v62-panel-next-footer">
          <span class="v62-next-badge">下一期</span>
          <span class="v62-next-number">第 {{ nextDrawNum }} 期</span>
        </div>
      </div>
    </div>
  </section>
</template>
