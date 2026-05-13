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
  "#ef4444", "#f97316", "#eab308", "#22c55e", "#06b6d4",
  "#3b82f6", "#8b5cf6", "#ec4899", "#6b7280", "#14b8a6",
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
          borderColor: "#ffffff",
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
          },
        },
        tooltip: {
          backgroundColor: "rgba(17, 24, 39, 0.9)",
          padding: 12,
          cornerRadius: 8,
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
  <div class="bg-white rounded-2xl border border-gray-200/80 p-6 shadow-sm card-lift">
    <div class="flex items-center gap-3 mb-5">
      <div class="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center">
        <svg class="w-5 h-5 text-gray-500" fill="currentColor" viewBox="0 0 24 24"><path d="M11 2v20c-5.07-.5-9-4.79-9-10s3.93-9.5 9-10zm2.03 0v8.99H22c-.47-4.74-4.24-8.52-8.97-8.99zm0 11.01V22c4.74-.47 8.5-4.25 8.97-8.99h-8.97z"/></svg>
      </div>
      <h3 v-if="title" class="text-base font-bold text-gray-900">{{ title }}</h3>
    </div>
    <div class="relative h-72">
      <canvas ref="canvas"></canvas>
    </div>
  </div>
</template>
