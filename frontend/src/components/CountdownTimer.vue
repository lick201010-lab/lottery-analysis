<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { lotteryType } from "../api.js";

const timeLeft = ref({ days: 0, hours: 0, minutes: 0, seconds: 0 });
let timer = null;

function getNextDrawDate() {
  const now = new Date();
  const currentDay = now.getDay(); // 0=Sunday, 1=Monday, ...
  const currentHour = now.getHours();
  const currentMinute = now.getMinutes();

  const config =
    lotteryType.value === "ssq"
      ? { days: [2, 4, 0], hour: 21, minute: 15 } // 双色球: 周二、四、日
      : { days: [2, 4, 6], hour: 21, minute: 30 }; // 六合彩: 周二、四、六

  // Find next draw day
  let daysUntil = 0;
  let found = false;

  for (let i = 0; i < 7; i++) {
    const checkDay = (currentDay + i) % 7;
    if (config.days.includes(checkDay)) {
      if (i === 0) {
        // Same day - check if draw time has passed
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

  if (!found) daysUntil = 1; // fallback

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
  <div class="text-center">
    <div class="text-xs text-[#64748d] mb-3">{{ drawSchedule }}</div>
    <div class="grid grid-cols-4 gap-2">
      <div class="flex flex-col items-center">
        <div class="w-full aspect-square rounded-xl bg-gradient-to-br from-[#0d253d] to-[#1a365d] text-white flex items-center justify-center text-xl sm:text-2xl font-bold tabular shadow-lg">
          {{ String(timeLeft.days).padStart(2, "0") }}
        </div>
        <span class="text-[10px] text-[#64748d] mt-1.5 uppercase tracking-wider">天</span>
      </div>
      <div class="flex flex-col items-center">
        <div class="w-full aspect-square rounded-xl bg-gradient-to-br from-[#0d253d] to-[#1a365d] text-white flex items-center justify-center text-xl sm:text-2xl font-bold tabular shadow-lg">
          {{ String(timeLeft.hours).padStart(2, "0") }}
        </div>
        <span class="text-[10px] text-[#64748d] mt-1.5 uppercase tracking-wider">时</span>
      </div>
      <div class="flex flex-col items-center">
        <div class="w-full aspect-square rounded-xl bg-gradient-to-br from-[#0d253d] to-[#1a365d] text-white flex items-center justify-center text-xl sm:text-2xl font-bold tabular shadow-lg">
          {{ String(timeLeft.minutes).padStart(2, "0") }}
        </div>
        <span class="text-[10px] text-[#64748d] mt-1.5 uppercase tracking-wider">分</span>
      </div>
      <div class="flex flex-col items-center">
        <div class="w-full aspect-square rounded-xl bg-gradient-to-br from-[#533afd] to-[#4434d4] text-white flex items-center justify-center text-xl sm:text-2xl font-bold tabular shadow-lg shadow-[#533afd]/30">
          {{ String(timeLeft.seconds).padStart(2, "0") }}
        </div>
        <span class="text-[10px] text-[#64748d] mt-1.5 uppercase tracking-wider">秒</span>
      </div>
    </div>
  </div>
</template>
