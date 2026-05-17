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
          borderColor: "#5f768f",
          backgroundColor: "rgba(95, 118, 143, 0.12)",
          fill: true,
          tension: 0.4,
          pointRadius: 3,
          pointHoverRadius: 6,
          pointBackgroundColor: "#5f768f",
          pointBorderColor: "#ffffff",
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
            color: "#7d867f",
          },
        },
        tooltip: {
          backgroundColor: "#ffffff",
          titleColor: "#233142",
          bodyColor: "#7d867f",
          padding: 12,
          cornerRadius: 8,
          borderColor: "#ddd4c7",
          borderWidth: 1,
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: "#ddd4c7" },
          ticks: { font: { size: 12 }, color: "#7d867f" },
        },
        x: {
          grid: { display: false },
          ticks: { maxTicksLimit: 20, maxRotation: 0, font: { size: 11 }, color: "#7d867f" },
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
  <div class="bg-white rounded-2xl border border-[#e3e8ee] p-6 shadow-sm card-stripe">
    <div class="relative h-80">
      <canvas ref="canvas"></canvas>
    </div>
  </div>
</template>
