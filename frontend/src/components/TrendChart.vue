<script setup>
import { ref, onMounted, watch, nextTick } from "vue";
import { Chart, registerables } from "chart.js";

Chart.register(...registerables);

const props = defineProps({
  data: { type: Array, default: () => [] },
  number: { type: Number, default: 1 },
});

const canvas = ref(null);
let chart = null;

function buildChart() {
  if (!canvas.value) return;
  if (chart) chart.destroy();

  const labels = props.data.map((d) => d.draw_number);
  const values = props.data.map((d) => d.count);

  chart = new Chart(canvas.value, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: `#${props.number} 滚动频率 (50期窗口)`,
          data: values,
          borderColor: "#fcd535",
          backgroundColor: "rgba(252, 213, 53, 0.08)",
          fill: true,
          tension: 0.4,
          pointRadius: 3,
          pointHoverRadius: 6,
          pointBackgroundColor: "#fcd535",
          pointBorderColor: "#0b0e11",
          pointBorderWidth: 2,
          borderWidth: 3,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: "top",
          labels: {
            font: { size: 13, weight: "bold" },
            usePointStyle: true,
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
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: "#2b3139" },
          ticks: { font: { size: 12 }, color: "#707a8a" },
        },
        x: {
          grid: { display: false },
          ticks: { maxTicksLimit: 20, maxRotation: 0, font: { size: 11 }, color: "#707a8a" },
        },
      },
    },
  });
}

onMounted(() => {
  nextTick(buildChart);
});
watch(
  () => [props.data, props.number],
  () => nextTick(buildChart)
);
</script>

<template>
  <div class="bg-[#1e2329] rounded-2xl border border-[#2b3139] p-6 shadow-sm">
    <div class="relative h-80">
      <canvas ref="canvas"></canvas>
    </div>
  </div>
</template>
