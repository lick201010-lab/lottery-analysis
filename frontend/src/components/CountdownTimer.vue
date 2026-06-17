<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { lotteryType } from "../api.js";
import { getLotteryMeta } from "../lotteryMeta.js";

const timeLeft = ref({ days: 0, hours: 0, minutes: 0, seconds: 0 });
let timer = null;

function getNextDrawDate() {
  const now = new Date();
  const currentDay = now.getDay();
  const currentHour = now.getHours();
  const currentMinute = now.getMinutes();
  const config =
    lotteryType.value === "ssq"
      ? { days: [2, 4, 0], hour: 21, minute: 15 }
      : lotteryType.value === "qxc"
        ? { days: [2, 5, 0], hour: 21, minute: 25 }
        : { days: [2, 4, 6], hour: 21, minute: 30 };

  let daysUntil = 0;
  let found = false;
  for (let i = 0; i < 7; i++) {
    const checkDay = (currentDay + i) % 7;
    if (config.days.includes(checkDay)) {
      if (i === 0) {
        const drawTime = config.hour * 60 + config.minute;
        const nowTime = currentHour * 60 + currentMinute;
        if (nowTime < drawTime) {
          found = true;
          break;
        }
      } else {
        daysUntil = i;
        found = true;
        break;
      }
    }
  }
  if (!found) daysUntil = 1;

  const next = new Date(now);
  next.setDate(now.getDate() + daysUntil);
  next.setHours(config.hour, config.minute, 0, 0);
  return next;
}

function updateCountdown() {
  const next = getNextDrawDate();
  const diff = next.getTime() - Date.now();
  if (diff <= 0) {
    timeLeft.value = { days: 0, hours: 0, minutes: 0, seconds: 0 };
    return;
  }
  timeLeft.value = {
    days: Math.floor(diff / (1000 * 60 * 60 * 24)),
    hours: Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
    minutes: Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60)),
    seconds: Math.floor((diff % (1000 * 60)) / 1000),
  };
}

onMounted(() => {
  updateCountdown();
  timer = setInterval(updateCountdown, 1000);
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
});

const drawSchedule = computed(() =>
  getLotteryMeta(lotteryType.value).drawSchedule
);

const countdownItems = computed(() => [
  { value: timeLeft.value.days, label: "天", short: "D" },
  { value: timeLeft.value.hours, label: "时", short: "H" },
  { value: timeLeft.value.minutes, label: "分", short: "M" },
  { value: timeLeft.value.seconds, label: "秒", short: "S" },
]);
</script>

<template>
  <div class="v62-countdown-module">
    <div class="v62-countdown-schedule">
      <span aria-hidden="true"></span>
      <strong>{{ drawSchedule }}</strong>
    </div>
    <div class="v62-countdown-units" aria-label="下期开奖倒计时">
      <div
        v-for="item in countdownItems"
        :key="item.label"
        class="v62-countdown-unit"
      >
        <div class="countdown-box">
          <span class="v62-countdown-short">{{ item.short }}</span>
          <span class="v62-countdown-value">{{ String(item.value).padStart(2, "0") }}</span>
        </div>
        <div class="v62-countdown-label">{{ item.label }}</div>
      </div>
    </div>
  </div>
</template>
