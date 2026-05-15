<script setup>
import { ref, onMounted, watch, nextTick } from "vue";
import { Chart, registerables } from "chart.js";

Chart.register(...registerables);

const props = defineProps({
  labels: { type: Array, default: () => [] },
  values: { type: Array, default: () => [] },
  colors: { type: Array, default: () => [] },
  title: { type: String, default: "" },
  type: { type: String, default: "doughnut" },
});

const canvas = ref(null);
let chart = null;

const defaultColors = [
  "#fcd535", "#f0b90b", "#0ecb81", "#f6465d", "#2b3139",
  "#707a8a", "#b7bdc6", "#eaecef", "#1e2329", "#0b0e11",
];

function buildChart() {
  if (!canvas.value) return;
  if (chart) chart.destroy();

  const bgColors = props.colors.length > 0
    ? props.colors
    : props.labels.map((_, i) => defaultColors[i % defaultColors.length]);

  chart = new Chart(canvas.value, {
    type: props.type,
    data: {
      labels: props.labels,
      datasets: [
        {
          data: props.values,
          backgroundColor: bgColors,
          borderColor: "#1e2329",
          borderWidth: 3,
          hoverOffset: 8,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "65%",
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            padding: 20,
            usePointStyle: true,
            font: { size: 13, weight: "500" },
            color: "#b7bdc6",
          },
        },
        tooltip: {
          backgroundColor: "rgba(30, 35, 41, 0.95)",
          titleColor: "#eaecef",
          bodyColor: "#b7bdc6",
          padding: 12,
          cornerRadius: 8,
          borderColor: "#2b3139",
          borderWidth: 1,
          callbacks: {
            label: (ctx) => {
              const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
              const pct = total > 0 ? ((ctx.parsed / total) * 100).toFixed(1) : 0;
              return ` ${ctx.label}: ${ctx.parsed} (${pct}%)`;
            },
          },
        },
      },
    },
  });
}

onMounted(() => nextTick(buildChart));
watch(() => [props.labels, props.values, props.colors], () => nextTick(buildChart), { deep: true });
</script>

<template>
  <div class="bg-[#1e2329] rounded-2xl border border-[#2b3139] p-6 shadow-sm card-lift">
    <div class="flex items-center gap-3 mb-5">
      <div class="w-10 h-10 rounded-xl bg-[#2b3139] flex items-center justify-center">
        <svg class="w-5 h-5 text-[#707a8a]" fill="currentColor" viewBox="0 0 24 24"><path d="M11 2v20c-5.07-.5-9-4.79-9-10s3.93-9.5 9-10zm2.03 0v8.99H22c-.47-4.74-4.24-8.52-8.97-8.99zm0 11.01V22c4.74-.47 8.5-4.25 8.97-8.99h-8.97z"/></svg>
      </div>
      <h3 v-if="title" class="text-base font-bold text-white">{{ title }}</h3>
    </div>
    <div class="relative h-72">
      <canvas ref="canvas"></canvas>
    </div>
  </div>
</template>
