<script setup>
const props = defineProps({
  number: { type: Number, required: true },
  size: { type: String, default: "md" }, // sm, md, lg, xl
  isSpecial: { type: Boolean, default: false },
});

const sizeMap = {
  sm: "w-7 h-7 text-xs",
  md: "w-9 h-9 text-sm",
  lg: "w-11 h-11 text-base",
  xl: "w-14 h-14 text-lg",
};
</script>

<template>
  <div
    :class="[
      'inline-flex items-center justify-center rounded-full font-bold select-none ball-shine transition-transform hover:scale-110',
      sizeMap[size],
      isSpecial
        ? 'bg-gradient-to-br from-[#f6465d] to-[#d43d51] text-white shadow-lg shadow-red-500/20'
        : 'bg-gradient-to-br from-[#fcd535] to-[#f0b90b] text-[#181a20] shadow-lg shadow-yellow-500/20',
    ]"
  >
    {{ number }}
  </div>
</template>
