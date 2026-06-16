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
</script>

<template>
  <div>
    <div class="mb-5 flex items-center gap-2 text-[15px] text-[#6e7373]">
      <span>▣</span>
      <span>{{ drawSchedule }}</span>
    </div>
    <div class="grid grid-cols-4 gap-6">
      <div
        v-for="item in [
          { value: timeLeft.days, label: '天' },
          { value: timeLeft.hours, label: '时' },
          { value: timeLeft.minutes, label: '分' },
          { value: timeLeft.seconds, label: '秒' },
        ]"
        :key="item.label"
        class="text-center"
      >
        <div class="countdown-box">
          {{ String(item.value).padStart(2, "0") }}
        </div>
        <div class="mt-2 text-[14px] text-[#7a807f]">{{ item.label }}</div>
      </div>
    </div>
  </div>
</template>
