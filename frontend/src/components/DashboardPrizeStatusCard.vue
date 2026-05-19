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

const headline = computed(() => {
  if (props.hasRollingPool && hasNumericPool.value) return props.poolDisplay;
  return props.nextPoolDisplay;
});

const headlineLabel = computed(() =>
  props.hasRollingPool && hasNumericPool.value ? "下一期头奖" : "奖金说明"
);

const headlineNote = computed(() => {
  if (props.hasRollingPool && hasNumericPool.value) return "预计头奖基金 · 官方公告抓取";
  return props.poolSubDisplay || props.nextPoolSubDisplay;
});

const sourceText = computed(() => props.drawSourceText.replace(/^数据来源：/, ""));

const chips = computed(() => {
  if (props.lotteryType === "ssq") {
    return [
      { title: "奖池滚存", desc: "按公告显示" },
      { title: `来源：${sourceText.value}`, desc: "开奖公告数据" },
      { title: "无数据时", desc: "以下期开奖公告为准" },
    ];
  }

  return [
    { title: "金多宝 / Snowball", desc: "有则显示" },
    { title: `来源：${sourceText.value}`, desc: "官方公告抓取" },
    { title: "无数据时", desc: "以官方公告为准" },
  ];
});

const infoTiles = computed(() => [
  {
    title: "玩法",
    subtitle: props.lotteryType === "ssq" ? "6 红 + 1 蓝" : "7 个号码全对中奖",
    to: "/guide",
    icon: "★",
  },
  {
    title: "奖金",
    subtitle: props.hasRollingPool ? "奖池、注数、派彩" : "固定奖金制说明",
    to: "/jackpot",
    icon: "奖",
  },
  {
    title: "统计",
    subtitle: "走势、冷热、遗漏",
    to: "/frequency",
    icon: "◔",
  },
]);
</script>

<template>
  <section class="prize-entertainment-section">
    <div class="prize-entertainment-intro">
      <span class="prize-red-arrow">➤</span>
      <p>选择一个红色箭头，可查看更多与本期摇号相关的信息，包括奖项注数、总奖金、历史走势。</p>
    </div>

    <div class="prize-hero-card">
      <div class="prize-hero-wave" aria-hidden="true"></div>
      <div class="prize-hero-skyline" aria-hidden="true">
        <img src="/assets/hk-skyline.png" alt="" decoding="async" />
      </div>

      <div class="prize-hero-main">
        <div class="prize-game-title">
          <span class="prize-game-icon">ϟ</span>
          <span>{{ lotteryLabel }}</span>
        </div>

        <span class="prize-headline-pill">{{ headlineLabel }}</span>
        <h2 class="prize-hero-amount">{{ headline }}</h2>
        <p class="prize-hero-note">{{ headlineNote }} <span class="prize-info-dot">ⓘ</span></p>

        <div class="prize-hero-actions">
          <router-link to="/data" class="prize-hero-primary">查看开奖 <span>›</span></router-link>
          <router-link to="/jackpot" class="prize-hero-secondary">奖金详情 <span>›</span></router-link>
        </div>
      </div>

      <div class="prize-result-panel">
        <p class="prize-result-issue">{{ displayDrawNumber }} · {{ displayDate }}</p>
        <p class="prize-result-label">最新结果</p>
        <div class="prize-result-balls">
          <NumberBall
            v-for="number in drawNumbers"
            :key="number"
            :number="number"
            size="md"
            :lotteryType="lotteryType"
          />
          <span class="prize-result-plus">+</span>
          <NumberBall
            v-if="specialNumber"
            :number="specialNumber"
            size="md"
            is-special
            :lotteryType="lotteryType"
          />
        </div>
        <router-link to="/data" class="prize-result-more">更多结果 <span>›</span></router-link>
      </div>
    </div>

    <div class="prize-chip-row">
      <router-link
        v-for="chip in chips"
        :key="chip.title"
        to="/jackpot"
        class="prize-info-chip-card"
      >
        <span class="prize-chip-symbol">●</span>
        <span>
          <strong>{{ chip.title }}</strong>
          <small>{{ chip.desc }}</small>
        </span>
        <span class="prize-chip-arrow">›</span>
      </router-link>
    </div>

    <div class="prize-tile-row">
      <router-link v-for="tile in infoTiles" :key="tile.title" :to="tile.to" class="prize-info-tile">
        <span class="prize-tile-icon">{{ tile.icon }}</span>
        <span>
          <strong>{{ tile.title }}</strong>
          <small>{{ tile.subtitle }}</small>
        </span>
        <span class="prize-tile-arrow">›</span>
      </router-link>
    </div>
  </section>
</template>
