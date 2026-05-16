<script setup>
import { ref, onMounted, watch } from "vue";
import { Chart, registerables } from "chart.js";
import NumberBall from "./NumberBall.vue";

Chart.register(...registerables);

const props = defineProps({
  data: { type: Array, default: () => [] },
  title: { type: String, default: "数字频率" },
  showCount: { type: Number, default: 20 },
});

const canvas = ref(null);
let chart = null;

function buildChart() {
  if (!canvas.value) return;
  if (chart) chart.destroy();

  const items = props.data.slice(0, props.showCount);
  const labels = items.map((d) => "#" + d.number);
  const values = items.map((d) => d.total_appearances);

  chart = new Chart(canvas.value, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "出现次数",
          data: values,
          backgroundColor: values.map((_, i) => {
            const alpha = 0.5 + (i / values.length) * 0.5;
            return `rgba(83, 58, 253, ${alpha})`;
          }),
          borderRadius: 6,
          borderSkipped: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#ffffff",
          titleColor: "#0d253d",
          bodyColor: "#64748d",
          padding: 12,
          cornerRadius: 8,
          titleFont: { size: 14, weight: "bold" },
          bodyFont: { size: 13 },
          borderColor: "#e3e8ee",
          borderWidth: 1,
        },
      },
      scales: {
        y: {
          beginAtZero: false,
          grid: { color: "#e3e8ee" },
          ticks: { font: { size: 12 }, color: "#64748d" },
        },
        x: {
          grid: { display: false },
          ticks: { font: { size: 12, weight: "500" }, color: "#64748d" },
        },
      },
    },
  });
}

onMounted(buildChart);
watch(() => [props.data, props.showCount], buildChart);
</script>

<template>
  <div class="bg-white rounded-2xl border border-[#e3e8ee] p-6 shadow-sm card-stripe">
    <div class="flex items-center gap-3 mb-5">
      <div class="w-10 h-10 rounded-xl bg-[#f6f9fc] flex items-center justify-center">
        <svg class="w-5 h-5 text-[#533afd]" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/></svg>
      </div>
      <h3 class="text-base font-bold text-[#0d253d]">{{ title }}</h3>
    </div>
    <div class="relative h-80">
      <canvas ref="canvas"></canvas>
    </div>
  </div>
</template>
