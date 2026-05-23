<script setup>
import { computed } from "vue";

const props = defineProps({
  numberStats:       { type: Array, required: true },
  observationGroups: { type: Array, required: true },
  lotteryType:       { type: String, required: true },
});

// Official MarkSix ball color sets
const marksixRed   = new Set([1,2,7,8,12,13,18,19,23,24,29,30,34,35,40,45,46]);
const marksixBlue  = new Set([3,4,9,10,14,15,20,25,26,31,36,37,41,42,47,48]);
// green = everything else up to 49

function getColor(num) {
  if (props.lotteryType === "ssq") return "red"; // SSQ all red
  if (marksixRed.has(num))  return "red";
  if (marksixBlue.has(num)) return "blue";
  return "green";
}

const maxFreq = computed(() => {
  const vals = props.numberStats.map(s => s.total).filter(v => v > 0);
  return vals.length ? Math.max(...vals) : 1;
});

function cellOpacity(stat) {
  if (!stat.hasData || stat.total === 0) return 0.28;
  return 0.28 + (stat.total / maxFreq.value) * 0.72;
}

function cellClass(stat) {
  const color = getColor(stat.number);
  const parts = [color];
  if (stat.isSpecial) parts.push("special-hit");
  else if (stat.isDrawn) parts.push("hit");
  return parts.join(" ");
}

function obsGroupClass(tone) {
  if (tone === "hot")    return "v62-obs-ball hot";
  if (tone === "cold")   return "v62-obs-ball cold";
  if (tone === "hit")    return "v62-obs-ball hit";
  return "v62-obs-ball active";
}

function obsLabelClass(tone) {
  if (tone === "hot")    return "v62-obs-group-label" + " text-[#b8473f]";
  if (tone === "cold")   return "v62-obs-group-label" + " text-[#356a92]";
  if (tone === "hit")    return "v62-obs-group-label" + " text-[#7a653f]";
  return "v62-obs-group-label text-[#476555]";
}
</script>

<template>
  <section class="v62-glass-surface p-6 sm:p-7">
    <!-- Header -->
    <div class="mb-1">
      <h2 class="v62-section-title">号码热度全景</h2>
      <p class="v62-section-sub">近 100 期数据 · 颜色 = 官方波色 · 浓度 = 出现频率 · 金环 = 当期开奖</p>
    </div>

    <!-- 49-cell (or 33-cell) heatmap -->
    <div class="v62-heatmap-grid">
      <div
        v-for="stat in numberStats"
        :key="stat.number"
        class="v62-heatmap-cell"
        :class="cellClass(stat)"
        :style="{ opacity: cellOpacity(stat) }"
        :title="`号码 ${String(stat.number).padStart(2,'0')} · 出现 ${stat.countLabel} 次 · 遗漏 ${stat.missLabel}`"
      >
        {{ String(stat.number).padStart(2, "0") }}
        <span class="v62-freq-badge">{{ stat.countLabel }}</span>
      </div>
    </div>

    <!-- Legend -->
    <div class="v62-heatmap-legend">
      <span class="lg-item"><span class="lg-dot red"></span>红波</span>
      <span class="lg-item"><span class="lg-dot blue"></span>蓝波</span>
      <span class="lg-item"><span class="lg-dot green"></span>绿波</span>
      <span class="lg-item"><span class="lg-dot gold" style="border-radius:50%;"></span>当期开奖</span>
      <span class="text-[11px] text-[#8a8f8c] ml-2">透明度 = 出现频率</span>
      <router-link to="/frequency" class="ml-auto text-[12px] font-semibold text-[#7c6644] hover:text-[#533f2a]">
        详细统计 ›
      </router-link>
    </div>

    <!-- Observation groups -->
    <div v-if="observationGroups && observationGroups.length" class="v62-obs-groups">
      <div
        v-for="group in observationGroups"
        :key="group.label"
        class="v62-obs-group"
      >
        <p :class="obsLabelClass(group.tone)">{{ group.label }}</p>
        <p class="v62-obs-group-hint">{{ group.hint }}</p>
        <div class="v62-obs-group-balls">
          <span
            v-for="item in group.numbers"
            :key="group.label + '-' + item.number"
            :class="obsGroupClass(group.tone)"
          >
            {{ String(item.number).padStart(2, "0") }}
          </span>
          <span v-if="!group.numbers.length" class="text-[12px] text-[#8a8f8c]">等待数据</span>
        </div>
      </div>
    </div>
  </section>
</template>
