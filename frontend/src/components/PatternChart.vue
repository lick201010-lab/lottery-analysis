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
  "#533afd", "#665efd", "#0ecb81", "#ea2261", "#e3e8ee",
  "#64748d", "#94a3b8", "#273951", "#f6f9fc", "#ffffff",
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
            color: "#64748d",
          },
        },
        tooltip: {
          backgroundColor: "#ffffff",
          titleColor: "#0d253d",
          bodyColor: "#64748d",
          padding: 12,
          cornerRadius: 8,
          borderColor: "#e3e8ee",
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
  <div class="bg-white rounded-2xl border border-[#e3e8ee] p-6 shadow-sm card-stripe">
    <div class="flex items-center gap-3 mb-5">
      <div class="w-10 h-10 rounded-xl bg-[#f6f9fc] flex items-center justify-center">
        <svg class="w-5 h-5 text-[#64748d]" fill="currentColor" viewBox="0 0 24 24"><path d="M11 2v20c-5.07-.5-9-4.79-9-10s3.93-9.5 9-10zm2.03 0v8.99H22c-.47-4.74-4.24-8.52-8.97-8.99zm0 11.01V22c4.74-.47 8.5-4.25 8.97-8.99h-8.97z"/></svg>
      </div>
      <h3 v-if="title" class="text-base font-bold text-[#0d253d]">{{ title }}</h3>
    </div>
    <div class="relative h-72">
      <canvas ref="canvas"></canvas>
    </div>
  </div>
</template>
