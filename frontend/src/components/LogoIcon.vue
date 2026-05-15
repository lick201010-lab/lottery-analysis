<template>
  <svg :width="size" :height="size" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#fcd535"/>
        <stop offset="100%" stop-color="#f0b90b"/>
      </linearGradient>
    </defs>
    <!-- Outer circle -->
    <circle cx="20" cy="20" r="18" stroke="url(#logoGradient)" stroke-width="2.5" fill="none"/>
    <!-- Inner design: stylized lottery ball with data waves -->
    <circle cx="20" cy="20" r="8" fill="url(#logoGradient)"/>
    <!-- Data wave lines -->
    <path d="M8 24 Q14 20 20 24 Q26 28 32 24" stroke="url(#logoGradient)" stroke-width="2" fill="none" stroke-linecap="round"/>
    <path d="M8 28 Q14 24 20 28 Q26 32 32 28" stroke="url(#logoGradient)" stroke-width="1.5" fill="none" stroke-linecap="round" opacity="0.6"/>
    <!-- Dot accent -->
    <circle cx="20" cy="14" r="2.5" fill="#0b0e11"/>
  </svg>
</template>

<script setup>
defineProps({
  size: { type: [Number, String], default: 40 }
});
</script>
