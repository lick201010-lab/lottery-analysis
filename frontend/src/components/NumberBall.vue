<script setup>
const props = defineProps({
  number: { type: Number, required: true },
  size: { type: String, default: "md" }, // sm, md, lg, xl
  isSpecial: { type: Boolean, default: false },
  lotteryType: { type: String, default: "marksix" }, // marksix | ssq
});

const sizeMap = {
  sm: "w-7 h-7 text-xs",
  md: "w-9 h-9 text-sm",
  lg: "w-11 h-11 text-base",
  xl: "w-14 h-14 text-lg",
};

// Color schemes by lottery type
const colorSchemes = {
  marksix: {
    normal: "bg-gradient-to-br from-[#fcd535] via-[#f0b90b] to-[#d4a009] text-[#181a20] shadow-lg shadow-yellow-500/25",
    special: "bg-gradient-to-br from-[#f6465d] via-[#e03e54] to-[#c23347] text-white shadow-lg shadow-red-500/25",
  },
  ssq: {
    normal: "bg-gradient-to-br from-[#ef4444] via-[#dc2626] to-[#b91c1c] text-white shadow-lg shadow-red-500/25",
    special: "bg-gradient-to-br from-[#3b82f6] via-[#2563eb] to-[#1d4ed8] text-white shadow-lg shadow-blue-500/25",
  },
};

const scheme = colorSchemes[props.lotteryType] || colorSchemes.marksix;
const colorClass = props.isSpecial ? scheme.special : scheme.normal;
</script>

<template>
  <div
    :class="[
      'inline-flex items-center justify-center rounded-full font-bold select-none ball-shine transition-all duration-200 hover:scale-110 hover:shadow-xl',
      sizeMap[size],
      colorClass,
    ]"
  >
    {{ number }}
  </div>
</template>
