<script setup>
defineProps({
  chartZones: { type: Array, required: true },
});
</script>

<template>
  <div class="ref-card p-7">
    <div class="mb-5 flex flex-col items-start justify-between gap-3 sm:flex-row sm:items-center">
      <h2 class="text-[24px] font-semibold text-[#1c3342]">号码走势示意</h2>
      <div class="flex flex-wrap gap-4 text-sm text-[#6e7373] sm:gap-7">
        <span
          v-for="zone in chartZones"
          :key="zone.label"
          :class="zone.color"
        >
          {{ zone.label }}
        </span>
      </div>
    </div>
    <svg viewBox="0 0 820 150" class="h-[150px] w-full">
      <defs>
        <pattern id="grid" width="44" height="30" patternUnits="userSpaceOnUse">
          <path d="M44 0H0V30" fill="none" stroke="#eadfce" stroke-width="1" />
        </pattern>
      </defs>
      <rect width="820" height="150" fill="url(#grid)" />
      <polyline points="18,110 74,82 132,112 188,52 246,52 304,84 362,64 420,48 478,96 536,52 594,50 652,76 710,40 786,92" fill="none" stroke="#c7964e" stroke-width="2" />
      <polyline points="18,120 74,58 132,118 188,76 246,56 304,74 362,46 420,90 478,54 536,52 594,52 652,104 710,78 786,112" fill="none" stroke="#5d826e" stroke-width="2" />
      <polyline points="18,132 74,126 132,130 188,124 246,124 304,122 362,120 420,118 478,112 536,52 594,50 652,96 710,62 786,106" fill="none" stroke="#5d7d9f" stroke-width="2" />
    </svg>
  </div>
</template>
