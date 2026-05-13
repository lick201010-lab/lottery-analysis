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
          borderColor: "#dc2626",
          backgroundColor: "rgba(220, 38, 38, 0.08)",
          fill: true,
          tension: 0.4,
          pointRadius: 3,
          pointHoverRadius: 6,
          pointBackgroundColor: "#dc2626",
          pointBorderColor: "#fff",
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
          },
        },
        tooltip: {
          backgroundColor: "rgba(17, 24, 39, 0.9)",
          padding: 12,
          cornerRadius: 8,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: "#f3f4f6" },
          ticks: { font: { size: 12 } },
        },
        x: {
          grid: { display: false },
          ticks: { maxTicksLimit: 20, maxRotation: 0, font: { size: 11 } },
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
  <div class="bg-white rounded-2xl border border-gray-200/80 p-6 shadow-sm">
    <div class="relative h-80">
      <canvas ref="canvas"></canvas>
    </div>
  </div>
</template>
