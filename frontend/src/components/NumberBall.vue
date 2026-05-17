<script setup>
const props = defineProps({
  number: { type: Number, required: true },
  size: { type: String, default: "md" }, // sm, md, lg, xl
  isSpecial: { type: Boolean, default: false },
  lotteryType: { type: String, default: "marksix" }, // marksix | ssq
});

import { computed } from "vue";

const sizeMap = {
  sm: "w-7 h-7 text-xs",
  md: "w-9 h-9 text-sm",
  lg: "w-11 h-11 text-base",
  xl: "w-14 h-14 text-lg",
  hero: "w-14 h-14 sm:w-[64px] sm:h-[64px] text-xl sm:text-[28px]",
};

// MarkSix official color rules
const marksixRed = new Set([1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46]);
const marksixBlue = new Set([3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48]);
const marksixGreen = new Set([5, 6, 11, 16, 17, 21, 22, 27, 28, 32, 33, 38, 39, 43, 44, 49]);

function getMarksixColor(n) {
  if (marksixRed.has(n)) return "red";
  if (marksixBlue.has(n)) return "blue";
  if (marksixGreen.has(n)) return "green";
  return "red";
}

// Color classes
const colorClasses = {
  marksix: {
    red: "bg-gradient-to-br from-[#ff9a92] via-[#d94b43] to-[#9f2f2b] text-white",
    blue: "bg-gradient-to-br from-[#82b6e4] via-[#347dbb] to-[#1f5688] text-white",
    green: "bg-gradient-to-br from-[#91cc96] via-[#43a85a] to-[#2f7542] text-white",
  },
  ssq: {
    red: "bg-gradient-to-br from-[#ff9a92] via-[#d94b43] to-[#9f2f2b] text-white",
    blue: "bg-gradient-to-br from-[#82b6e4] via-[#347dbb] to-[#1f5688] text-white",
  },
};

const scheme = colorClasses[props.lotteryType] || colorClasses.marksix;

let colorClass;
if (props.lotteryType === "ssq") {
  // SSQ: normal balls = red, special = blue
  colorClass = props.isSpecial ? scheme.blue : scheme.red;
} else {
  // MarkSix: each number has its own color
  const colorKey = getMarksixColor(props.number);
  colorClass = scheme[colorKey];
}

const displayNumber = computed(() => String(props.number).padStart(2, "0"));
</script>

<template>
  <div
    :class="[
      'inline-flex items-center justify-center rounded-full font-bold select-none ball-shine transition-all duration-200 hover:-translate-y-0.5 hover:scale-105',
      sizeMap[size],
      colorClass,
    ]"
  >
    {{ displayNumber }}
  </div>
</template>
