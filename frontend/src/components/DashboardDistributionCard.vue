<script setup>
import { computed } from "vue";
import { useI18n } from "../i18n.js";

const { t } = useI18n();

const props = defineProps({
  numberStats:       { type: Array, required: true },
  observationGroups: { type: Array, required: true },
  lotteryType:       { type: String, required: true },
  recentDraws:       { type: Array, default: () => [] },
});

const marksixRed  = new Set([1,2,7,8,12,13,18,19,23,24,29,30,34,35,40,45,46]);
const marksixBlue = new Set([3,4,9,10,14,15,20,25,26,31,36,37,41,42,47,48]);

function getColor(num, isSpecial = false) {
  if (props.lotteryType === "ssq") return isSpecial ? "blue" : "red";
  if (marksixRed.has(num)) return "red";
  if (marksixBlue.has(num)) return "blue";
  return "green";
}

function drawRegularNumbers(draw) {
  return [draw?.num1, draw?.num2, draw?.num3, draw?.num4, draw?.num5, draw?.num6]
    .map((n) => Number(n))
    .filter((n) => Number.isFinite(n));
}

function countRecentNumbers() {
  const counts = new Map();
  props.recentDraws.slice(0, 24).forEach((draw) => {
    drawRegularNumbers(draw).forEach((n) => {
      counts.set(n, (counts.get(n) || 0) + 1);
    });
    const special = Number(draw?.special_num);
    if (Number.isFinite(special)) counts.set(special, (counts.get(special) || 0) + 1);
  });
  return counts;
}

const recentCounts = computed(() => countRecentNumbers());

const heatStats = computed(() => {
  if (!recentCounts.value.size) return props.numberStats;

  return props.numberStats.map((stat) => {
    const recentTotal = recentCounts.value.get(stat.number) || 0;
    return {
      ...stat,
      total: recentTotal,
      countLabel: recentTotal,
      hasData: true,
    };
  });
});

const maxFreq = computed(() => {
  const vals = heatStats.value.map((s) => s.total).filter((v) => v > 0);
  return vals.length ? Math.max(...vals) : 1;
});

const coldCutoff = computed(() => Math.max(0, Math.min(1, maxFreq.value * 0.36)));

const totalHits = computed(() => {
  return [...recentCounts.value.values()].reduce((sum, count) => sum + count, 0) || 1;
});

function cellStyle(stat) {
  const heat = stat.hasData && stat.total > 0 ? Math.max(0.08, stat.total / maxFreq.value) : 0.08;
  const isCold = stat.hasData && stat.total <= coldCutoff.value && !stat.isDrawn && !stat.isSpecial && !isColorHot(stat);
  return {
    "--heat": heat.toFixed(3),
    "--heatPct": `${Math.round(heat * 100)}%`,
    "--cold": isCold ? "1" : "0",
  };
}

function cellClass(stat) {
  const parts = [getColor(stat.number)];
  if (isColorHot(stat)) parts.push("hot-rank");
  if (stat.total <= coldCutoff.value && stat.hasData && !stat.isDrawn && !stat.isSpecial && !isColorHot(stat)) parts.push("cold-rank");
  if (stat.isSpecial) parts.push("special-hit");
  else if (stat.isDrawn) parts.push("hit");
  return parts.join(" ");
}

function isHot(stat) {
  return isColorHot(stat);
}

function isColorHot(stat) {
  return hotNumbersByColor.value.has(stat.number);
}

const colorHeatGroups = computed(() => {
  const groups = props.lotteryType === "ssq"
    ? [
        { key: "red", label: t("红球热度"), color: "red" },
        { key: "blue", label: t("蓝球热度"), color: "blue" },
      ]
    : [
        { key: "red", label: t("红波热度"), color: "red" },
        { key: "blue", label: t("蓝波热度"), color: "blue" },
        { key: "green", label: t("绿波热度"), color: "green" },
      ];

  const counts = new Map();
  props.recentDraws.slice(0, 24).forEach((draw) => {
    drawRegularNumbers(draw).forEach((n) => {
      const color = getColor(n, false);
      counts.set(n, { number: n, color, count: (counts.get(n)?.count || 0) + 1 });
    });
    const special = Number(draw?.special_num);
    if (Number.isFinite(special)) {
      const color = getColor(special, true);
      counts.set(special, { number: special, color, count: (counts.get(special)?.count || 0) + 1 });
    }
  });

  return groups.map((group) => {
    const numbers = [...counts.values()]
      .filter((item) => item.color === group.color)
      .sort((a, b) => b.count - a.count || a.number - b.number);
    const total = numbers.reduce((sum, item) => sum + item.count, 0);

    return {
      ...group,
      total,
      percent: ((total / totalHits.value) * 100).toFixed(1),
      numbers: numbers.slice(0, 6),
    };
  });
});

const hotNumbersByColor = computed(() => {
  return new Set(
    colorHeatGroups.value
      .map((group) => group.numbers[0]?.number)
      .filter((number) => Number.isFinite(number))
  );
});
</script>

<template>
  <section class="v62-glass-surface p-6 sm:p-7">
    <div class="v62-heatmap-heading">
      <div>
        <h2 class="v62-section-title">{{ t("号码热度全景") }}</h2>
        <p class="v62-section-sub">{{ t("统计近 24 期号码出现频率，热度越高颜色越深。") }}</p>
      </div>
      <div class="v62-heatmap-scale" :aria-label="t('热度说明')">
        <span>{{ t("低频") }}</span>
        <i></i>
        <span>{{ t("高频") }}</span>
      </div>
    </div>

    <aside class="v62-heat-side">
      <p class="v62-heat-side-kicker">{{ t("24期累计数据") }}</p>
      <div
        v-for="group in colorHeatGroups"
        :key="group.key"
        class="v62-color-heat-group"
        :class="group.color"
      >
        <p class="v62-color-heat-title">
          <span></span>{{ group.label }}
        </p>
        <div class="v62-color-heat-metrics">
          <strong>{{ group.total }}</strong>
          <small>{{ t("次数") }}</small>
          <strong>{{ group.percent }}<em>%</em></strong>
          <small>{{ t("占比") }}</small>
        </div>
        <p class="v62-color-heat-caption">{{ t("最热号码") }}</p>
        <div class="v62-color-heat-list">
          <span
            v-for="item in group.numbers"
            :key="group.key + '-' + item.number"
            class="v62-color-heat-num"
          >
            {{ String(item.number).padStart(2, "0") }}
          </span>
          <span v-if="!group.numbers.length" class="v62-color-heat-empty">{{ t("等待数据") }}</span>
        </div>
      </div>
    </aside>

    <div class="v62-heatmap-grid">
      <div
        v-for="stat in heatStats"
        :key="stat.number"
        class="v62-heatmap-cell"
        :class="cellClass(stat)"
        :style="cellStyle(stat)"
        :title="t('号码 {num} · 近24期出现 {count} 次 · 遗漏 {miss}', { num: String(stat.number).padStart(2,'0'), count: stat.countLabel, miss: stat.missLabel })"
      >
        <span v-if="isHot(stat)" class="v62-hot-mark">HOT</span>
        <span class="v62-heatmap-orb">
          <span class="v62-heatmap-number">{{ String(stat.number).padStart(2, "0") }}</span>
        </span>
        <span class="v62-freq-badge">{{ t("{n}次", { n: stat.countLabel }) }}</span>
      </div>
    </div>

    <div class="v62-heatmap-legend">
      <span class="lg-item"><span class="lg-dot red"></span>{{ t("红波 / 红球") }}</span>
      <span class="lg-item"><span class="lg-dot blue"></span>{{ t("蓝波 / 蓝球") }}</span>
      <span v-if="lotteryType !== 'ssq'" class="lg-item"><span class="lg-dot green"></span>{{ t("绿波") }}</span>
      <span class="lg-item"><span class="lg-dot gold" style="border-radius:50%;"></span>{{ t("当期开奖") }}</span>
      <span class="text-[11px] text-[#8a8f8c] ml-2">{{ t("下方数字 = 近24期出现次数") }}</span>
      <router-link to="/frequency" class="ml-auto text-[12px] font-semibold text-[#7c6644] hover:text-[#533f2a]">
        {{ t("详细统计 →") }}
      </router-link>
    </div>
  </section>
</template>
