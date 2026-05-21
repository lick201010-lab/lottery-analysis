<script setup>
import { ref, onMounted, watch, nextTick, computed } from "vue";
import { Chart, registerables } from "chart.js";
import { api, lotteryType } from "../api.js";
import { useSEO } from "../composables/useSEO.js";
import PatternChart from "../components/PatternChart.vue";

Chart.register(...registerables);

useSEO({
  title: "双色球 & 六合彩走势分析 - 区间、奇偶、连号",
  description: "多维度走势分析：奇偶比、大小分布、连号特征、和值分布、号码区间走势。基于历史开奖数据的统计观察。",
});

const loading = ref(false);
const patternData = ref(null);

// Canvas refs for Chart.js charts
const consecutiveCanvas = ref(null);
const rangeCanvas = ref(null);
const sumCanvas = ref(null);

let consecutiveChart = null;
let rangeChart = null;
let sumChart = null;

function destroyCharts() {
  if (consecutiveChart) { consecutiveChart.destroy(); consecutiveChart = null; }
  if (rangeChart) { rangeChart.destroy(); rangeChart = null; }
  if (sumChart) { sumChart.destroy(); sumChart = null; }
}

function buildBarChart(canvas, labels, values, label, color) {
  if (!canvas) return null;
  return new Chart(canvas, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label,
        data: values,
        backgroundColor: color,
        borderRadius: 6,
        borderSkipped: false,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "rgba(35, 49, 66, 0.94)",
          padding: 12,
          cornerRadius: 8,
          titleFont: { size: 14, weight: "bold" },
          bodyFont: { size: 13 },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: "#ddd4c7" },
          ticks: { precision: 0, font: { size: 12 } },
        },
        x: {
          grid: { display: false },
          ticks: { font: { size: 13, weight: "500" } },
        },
      },
    },
  });
}

async function loadPatterns() {
  loading.value = true;
  destroyCharts();
  try {
    patternData.value = await api.patterns();
    await nextTick();
    renderCharts();
  } catch (e) {
    console.error(e);
    patternData.value = null;
  } finally {
    loading.value = false;
  }
}

function renderCharts() {
  const d = patternData.value;
  if (!d) return;

  // Consecutive chart
  if (d.consecutive && consecutiveCanvas.value) {
    const labels = [];
    const values = [];
    if (d.consecutive.has_consecutive !== undefined) {
      labels.push("有连号");
      values.push(d.consecutive.has_consecutive);
    }
    if (d.consecutive.no_consecutive !== undefined) {
      labels.push("无连号");
      values.push(d.consecutive.no_consecutive);
    }
    if (labels.length === 0 && d.consecutive.labels && d.consecutive.values) {
      consecutiveChart = buildBarChart(
        consecutiveCanvas.value,
        d.consecutive.labels,
        d.consecutive.values,
        "期数",
        "#8d6f47"
      );
      return;
    }
    if (labels.length > 0) {
      consecutiveChart = buildBarChart(
        consecutiveCanvas.value,
        labels,
        values,
        "期数",
        "#8d6f47"
      );
    }
  }

  // Range distribution
  if (d.range_distribution && rangeCanvas.value) {
    const ranges = d.range_distribution.ranges || d.range_distribution.labels || [];
    const counts = d.range_distribution.counts || d.range_distribution.values || [];
    if (ranges.length > 0) {
      rangeChart = buildBarChart(
        rangeCanvas.value,
        ranges,
        counts,
        "出现次数",
        "#7089a6"
      );
    }
  }

  // Sum distribution
  if (d.sum_distribution && sumCanvas.value) {
    const buckets = d.sum_distribution.buckets || d.sum_distribution.labels || [];
    const counts = d.sum_distribution.counts || d.sum_distribution.values || [];
    if (buckets.length > 0) {
      sumChart = new Chart(sumCanvas.value, {
        type: "bar",
        data: {
          labels: buckets,
          datasets: [{
            label: "出现次数",
            data: counts,
            backgroundColor: "#a9868e",
            borderRadius: 4,
            borderSkipped: false,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: "rgba(35, 49, 66, 0.94)",
              padding: 12,
              cornerRadius: 8,
            },
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: { color: "#ddd4c7" },
              ticks: { precision: 0, font: { size: 12 } },
            },
            x: {
              grid: { display: false },
              ticks: { maxRotation: 45, font: { size: 11 } },
            },
          },
        },
      });
    }
  }
}

// Donut chart data computed from backend response
const oddEvenLabels = computed(() => {
  const d = patternData.value;
  if (!d || !d.odd_even) return [];
  return d.odd_even.labels || ["奇数", "偶数"];
});
const oddEvenValues = computed(() => {
  const d = patternData.value;
  if (!d || !d.odd_even) return [];
  return d.odd_even.values || [d.odd_even.odd || 0, d.odd_even.even || 0];
});
const oddEvenColors = computed(() => ["#b96d63", "#7089a6"]);

const bigSmallLabels = computed(() => {
  const d = patternData.value;
  if (!d || !d.big_small) return [];
  return d.big_small.labels || ["大数", "小数"];
});
const bigSmallValues = computed(() => {
  const d = patternData.value;
  if (!d || !d.big_small) return [];
  return d.big_small.values || [d.big_small.big || 0, d.big_small.small || 0];
});
const bigSmallColors = computed(() => ["#7f9a86", "#b8a06a"]);

onMounted(loadPatterns);
watch(lotteryType, () => {
  patternData.value = null;
  destroyCharts();
  loadPatterns();
});
</script>

<template>
  <div class="space-y-8 animate-fade-in-up">
    <div>
      <h1 class="text-2xl font-bold text-[#0d253d] tracking-tight">走势分析</h1>
      <p class="text-base text-[#64748d] mt-1">奇偶、大小、连号、区间与总和分布统计</p>
    </div>

    <div v-if="loading" class="text-center py-20 text-[#64748d]">
      <svg class="w-10 h-10 mx-auto mb-3 animate-spin text-[#64748d]" fill="currentColor" viewBox="0 0 24 24"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/></svg>
      加载中...
    </div>

    <template v-else-if="patternData">
      <!-- Donut Charts Row -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5 stagger-children">
        <PatternChart
          title="奇偶分布"
          :labels="oddEvenLabels"
          :values="oddEvenValues"
          :colors="oddEvenColors"
        />
        <PatternChart
          title="大小分布"
          :labels="bigSmallLabels"
          :values="bigSmallValues"
          :colors="bigSmallColors"
        />
      </div>

      <!-- Consecutive Numbers Chart -->
      <div class="bg-white rounded-2xl border border-[#e3e8ee] p-6 shadow-sm card-lift card-stripe">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-10 h-10 rounded-xl bg-[#f6f9fc] flex items-center justify-center">
            <svg class="w-5 h-5 text-[#533afd]" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
          </div>
          <h3 class="text-base font-bold text-[#0d253d]">连号统计</h3>
        </div>
        <div class="relative h-72">
          <canvas ref="consecutiveCanvas"></canvas>
        </div>
      </div>

      <!-- Range Distribution Chart -->
      <div v-if="patternData.range_distribution" class="bg-white rounded-2xl border border-[#e3e8ee] p-6 shadow-sm card-lift card-stripe">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-10 h-10 rounded-xl bg-[#f6f9fc] flex items-center justify-center">
            <svg class="w-5 h-5 text-[#3b82f6]" fill="currentColor" viewBox="0 0 24 24"><path d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z"/></svg>
          </div>
          <h3 class="text-base font-bold text-[#0d253d]">区间分布</h3>
        </div>
        <div class="relative h-80">
          <canvas ref="rangeCanvas"></canvas>
        </div>
      </div>

      <!-- Sum Distribution Chart -->
      <div v-if="patternData.sum_distribution" class="bg-white rounded-2xl border border-[#e3e8ee] p-6 shadow-sm card-lift card-stripe">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-10 h-10 rounded-xl bg-[#f6f9fc] flex items-center justify-center">
            <svg class="w-5 h-5 text-[#8b5cf6]" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
          </div>
          <h3 class="text-base font-bold text-[#0d253d]">总和分布</h3>
        </div>
        <div class="relative h-80">
          <canvas ref="sumCanvas"></canvas>
        </div>
      </div>

      <!-- Additional stats summary -->
      <div v-if="patternData.summary" class="bg-white rounded-2xl border border-[#e3e8ee] p-6 shadow-sm card-lift card-stripe">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-10 h-10 rounded-xl bg-[#f6f9fc] flex items-center justify-center">
            <svg class="w-5 h-5 text-[#64748d]" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/></svg>
          </div>
          <h3 class="text-base font-bold text-[#0d253d]">统计摘要</h3>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 stagger-children">
          <div v-for="(val, key) in patternData.summary" :key="key" class="p-5 bg-[#f6f9fc] rounded-xl border border-[#e3e8ee]">
            <div class="text-xs font-bold text-[#64748d] uppercase tracking-wider">{{ key }}</div>
            <div class="text-xl sm:text-2xl font-extrabold text-[#0d253d] mt-2">{{ val }}</div>
          </div>
        </div>
      </div>
    </template>

    <div v-else class="bg-white rounded-2xl border border-[#e3e8ee] p-16 text-center shadow-sm card-stripe">
      <svg class="w-12 h-12 mx-auto text-[#64748d] mb-3" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
      <p class="text-[#64748d] text-lg">暂无走势分析数据</p>
    </div>
  </div>
</template>
