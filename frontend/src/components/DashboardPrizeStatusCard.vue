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
  if (hasNumericPool.value) return props.poolDisplay;
  return props.nextPoolDisplay;
});

const headlineLabel = computed(() => {
  if (props.lotteryType === "marksix" && hasNumericPool.value) return "最新头奖";
  return props.hasRollingPool || props.lotteryType === "marksix" ? "下一期头奖" : "奖金说明";
});

const headlineNote = computed(() => {
  if (hasNumericPool.value) {
    return props.poolSubDisplay || "预计头奖基金 · 官方公告抓取";
  }
  return props.poolSubDisplay || props.nextPoolSubDisplay;
});

const sourceText = computed(() =>
  props.lotteryType === "marksix"
    ? "香港赛马会 / lottery.hk"
    : props.drawSourceText.replace(/^数据来源：/, "")
);

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
    { title: `来源：${sourceText.value}`, desc: "lottery.hk 抓取" },
    { title: "无数据时", desc: "以 lottery.hk 公布为准" },
  ];
});

const infoTiles = computed(() => [
  {
    title: "玩法",
    subtitle: props.lotteryType === "ssq" ? "6 红 + 1 蓝" : "7 个号码全对中奖",
    to: "/guide",
    icon: "★",
    rows: props.lotteryType === "ssq"
      ? [
          { label: "基本玩法", value: "6 红 + 1 蓝" },
          { label: "红球范围", value: "01 - 33" },
        ]
      : [
          { label: "基本玩法", value: "7个号码全对中奖" },
          { label: "多宝玩法", value: "增加中奖机会" },
        ],
  },
  {
    title: "奖金",
    subtitle: props.hasRollingPool ? "奖池、注数、派彩" : "固定奖金制说明",
    to: "/jackpot",
    icon: "奖",
    rows: props.lotteryType === "ssq"
      ? [
          { label: "一等奖", value: "浮动奖金" },
          { label: "六等奖", value: "固定奖金" },
        ]
      : [
          { label: "头奖", value: "固定奖金" },
          { label: "二等奖", value: "固定奖金" },
        ],
  },
  {
    title: "统计",
    subtitle: "走势、冷热、遗漏",
    to: "/frequency",
    icon: "◔",
    rows: [
      { label: "号码走势", value: "冷热分析，历史走势" },
      { label: "遗漏统计", value: "号码遗漏，分布统计" },
    ],
  },
]);
</script>

<template>
  <section class="prize-entertainment-section">
    <div class="prize-hero-card">
      <div class="prize-hero-wave" aria-hidden="true"></div>
      <div class="prize-confetti prize-confetti-one" aria-hidden="true"></div>
      <div class="prize-confetti prize-confetti-two" aria-hidden="true"></div>
      <div
        class="prize-hero-skyline"
        :class="{ 'prize-hero-skyline-mainland': lotteryType === 'ssq' }"
        aria-hidden="true"
      >
        <svg
          v-if="lotteryType === 'ssq'"
          class="mainland-skyline-svg"
          viewBox="0 0 900 210"
          focusable="false"
        >
          <g fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">
            <path d="M26 178H874" />
            <path d="M62 178v-30h68v30" />
            <path d="M48 148h96l-22-17H70z" />
            <path d="M72 131h48l-14-12H86z" />
            <path d="M78 160h36M84 178v-18M108 178v-18" />
            <path d="M186 178v-34h96v34" />
            <path d="M170 144h128l-28-18h-72z" />
            <path d="M204 126h60l-18-13h-24z" />
            <path d="M202 160h64M214 178v-18M254 178v-18" />
            <path d="M356 178c0-40 42-70 94-70s94 30 94 70" />
            <path d="M386 178c0-28 28-50 64-50s64 22 64 50" />
            <path d="M412 128l38-46 38 46" />
            <path d="M395 144h110M386 160h128" />
            <path d="M606 178v-38h86v38" />
            <path d="M588 140h122l-30-20h-62z" />
            <path d="M622 120h54l-16-12h-22z" />
            <path d="M628 158h42M620 178v-20M678 178v-20" />
            <path d="M744 178v-28h92v28" />
            <path d="M730 150h120l-26-17h-68z" />
            <path d="M760 133h58l-17-12h-24z" />
            <path d="M764 164h52M774 178v-14M808 178v-14" />
            <path d="M40 178c50-12 94-12 144 0M304 178c48-11 96-11 144 0M534 178c52-12 104-12 156 0M704 178c48-10 92-10 140 0" />
          </g>
        </svg>
        <img v-else src="/assets/hk-skyline.png" alt="" decoding="async" />
      </div>

      <div class="prize-hero-main">
        <div class="prize-game-title">
          <span class="prize-game-icon" aria-hidden="true">◎</span>
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
        <div class="prize-tile-heading">
          <span class="prize-tile-icon">{{ tile.icon }}</span>
          <span>
            <strong>{{ tile.title }}</strong>
            <small>{{ tile.subtitle }}</small>
          </span>
        </div>
        <div class="prize-tile-lines">
          <div v-for="row in tile.rows" :key="row.label" class="prize-tile-line">
            <span>
              <strong>{{ row.label }}</strong>
              <small>{{ row.value }}</small>
            </span>
            <span class="prize-tile-arrow">›</span>
          </div>
        </div>
      </router-link>
    </div>
  </section>
</template>
