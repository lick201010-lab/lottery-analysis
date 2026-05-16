<template>
  <svg :width="size" :height="size" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="logoGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#665efd"/>
        <stop offset="50%" stop-color="#533afd"/>
        <stop offset="100%" stop-color="#4434d4"/>
      </linearGradient>
      <linearGradient id="logoGrad2" x1="100%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#f96bee"/>
        <stop offset="100%" stop-color="#533afd"/>
      </linearGradient>
    </defs>
    <!-- Outer ring -->
    <circle cx="20" cy="20" r="18" stroke="url(#logoGrad1)" stroke-width="3" fill="none"/>
    <!-- Inner twisted ring (Mobius strip style) -->
    <path d="M20 6 C28 6, 34 12, 34 20 C34 26, 30 30, 26 30 C22 30, 20 26, 20 20 C20 14, 24 10, 28 10 C32 10, 34 14, 34 20" 
          stroke="url(#logoGrad2)" stroke-width="3" fill="none" stroke-linecap="round"/>
    <!-- Center dot -->
    <circle cx="20" cy="20" r="4" fill="url(#logoGrad1)"/>
  </svg>
</template>

<script setup>
defineProps({
  size: { type: [Number, String], default: 40 }
});
</script>
