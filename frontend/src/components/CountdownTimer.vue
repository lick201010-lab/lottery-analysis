<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { lotteryType } from "../api.js";

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
          daysUntil = 0;
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
  lotteryType.value === "ssq"
    ? "每周二、四、日 21:15"
    : "每周二、四、六 21:30"
);
</script>

<template>
  <div>
    <div class="mb-3 text-sm text-[#7d867f]">{{ drawSchedule }}</div>
    <div class="grid grid-cols-4 gap-2 sm:gap-3">
      <div
        v-for="item in [
          { value: timeLeft.days, label: '天' },
          { value: timeLeft.hours, label: '时' },
          { value: timeLeft.minutes, label: '分' },
          { value: timeLeft.seconds, label: '秒', accent: true },
        ]"
        :key="item.label"
        class="flex flex-col items-center"
      >
        <div
          class="flex aspect-square w-full items-center justify-center rounded-lg text-xl font-semibold text-white tabular shadow-lg sm:text-2xl"
          :class="item.accent
            ? 'bg-gradient-to-br from-[#8d6f47] to-[#6f5737] shadow-[#8d6f47]/20'
            : 'bg-gradient-to-br from-[#405064] to-[#233142] shadow-[#233142]/15'"
        >
          {{ String(item.value).padStart(2, "0") }}
        </div>
        <span class="mt-1.5 text-[11px] tracking-wider text-[#7d867f]">{{ item.label }}</span>
      </div>
    </div>
  </div>
</template>
