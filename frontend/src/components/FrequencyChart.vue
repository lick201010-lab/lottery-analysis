<script setup>
import { ref, onMounted, watch } from "vue";
import { Chart, registerables } from "chart.js";
import NumberBall from "./NumberBall.vue";

Chart.register(...registerables);

const props = defineProps({
  data: { type: Array, default: () => [] },
  title: { type: String, default: "号码频率" },
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
            return `rgba(252, 213, 53, ${alpha})`;
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
          backgroundColor: "rgba(30, 35, 41, 0.95)",
          titleColor: "#eaecef",
          bodyColor: "#b7bdc6",
          padding: 12,
          cornerRadius: 8,
          titleFont: { size: 14, weight: "bold" },
          bodyFont: { size: 13 },
          borderColor: "#2b3139",
          borderWidth: 1,
        },
      },
      scales: {
        y: {
          beginAtZero: false,
          grid: { color: "#2b3139" },
          ticks: { font: { size: 12 }, color: "#707a8a" },
        },
        x: {
          grid: { display: false },
          ticks: { font: { size: 12, weight: "500" }, color: "#707a8a" },
        },
      },
    },
  });
}

onMounted(buildChart);
watch(() => [props.data, props.showCount], buildChart);
</script>

<template>
  <div class="bg-[#1e2329] rounded-2xl border border-[#2b3139] p-6 shadow-sm card-lift">
    <div class="flex items-center gap-3 mb-5">
      <div class="w-10 h-10 rounded-xl bg-[#2b3139] flex items-center justify-center">
        <svg class="w-5 h-5 text-[#fcd535]" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/></svg>
      </div>
      <h3 class="text-base font-bold text-white">{{ title }}</h3>
    </div>
    <div class="relative h-80">
      <canvas ref="canvas"></canvas>
    </div>
  </div>
</template>
