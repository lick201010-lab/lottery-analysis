<script setup>
const props = defineProps({
  number: { type: Number, required: true },
  size: { type: String, default: "md", validator: (v) => ["sm", "md", "lg", "xl"].includes(v) },
});

const colors = {
  red: new Set([1, 2, 7, 8, 12, 13, 18, 19, 23, 24, 29, 30, 34, 35, 40, 45, 46]),
  blue: new Set([3, 4, 9, 10, 14, 15, 20, 25, 26, 31, 36, 37, 41, 42, 47, 48]),
  green: new Set([5, 6, 11, 16, 17, 21, 22, 27, 28, 32, 33, 38, 39, 43, 44, 49]),
};

function ballColor(n) {
  if (colors.red.has(n)) return "from-red-500 to-red-700 ring-red-400/30";
  if (colors.blue.has(n)) return "from-blue-500 to-blue-700 ring-blue-400/30";
  return "from-emerald-500 to-emerald-700 ring-emerald-400/30";
}

const sizeClasses = {
  sm: "w-8 h-8 text-[13px]",
  md: "w-10 h-10 text-[15px]",
  lg: "w-14 h-14 text-xl",
  xl: "w-[72px] h-[72px] text-2xl",
};
</script>

<template>
  <span
    class="ball-shine inline-flex items-center justify-center rounded-full text-white font-bold shadow-lg bg-gradient-to-b ring-2 ring-offset-1 ring-offset-white/0 transition-transform duration-200 hover:scale-110"
    :class="[ballColor(props.number), sizeClasses[props.size] || sizeClasses.md]"
  >
    {{ props.number }}
  </span>
</template>
