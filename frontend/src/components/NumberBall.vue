<script setup>
const props = defineProps({
  number: { type: Number, required: true },
  size: { type: String, default: "md" }, // sm, md, lg, xl
  isSpecial: { type: Boolean, default: false },
  lotteryType: { type: String, default: "marksix" }, // marksix | ssq | qxc
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
  qxc: {
    regular: "bg-gradient-to-br from-[#718aa0] via-[#29465d] to-[#122838] text-white shadow-[inset_0_1px_8px_rgba(255,255,255,0.22),0_8px_18px_rgba(18,40,56,0.22)]",
    special: "bg-gradient-to-br from-[#f0d69a] via-[#c5943f] to-[#7b5523] text-white shadow-[inset_0_1px_8px_rgba(255,255,255,0.25),0_8px_18px_rgba(123,85,35,0.22)]",
  },
};

const scheme = colorClasses[props.lotteryType] || colorClasses.marksix;

let colorClass;
if (props.lotteryType === "ssq") {
  // SSQ: normal balls = red, special = blue
  colorClass = props.isSpecial ? scheme.blue : scheme.red;
} else if (props.lotteryType === "qxc") {
  // QXC: six positional front-zone digits + one amber back-zone digit.
  colorClass = props.isSpecial ? scheme.special : scheme.regular;
} else {
  // MarkSix: each number has its own color
  const colorKey = getMarksixColor(props.number);
  colorClass = scheme[colorKey];
}

const displayNumber = computed(() =>
  props.lotteryType === "qxc" ? String(props.number) : String(props.number).padStart(2, "0")
);
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
