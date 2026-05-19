<script setup>
defineProps({
  poolCardLabel: { type: String, required: true },
  poolDisplay: { type: String, required: true },
  poolSubDisplay: { type: String, required: true },
  firstPrizeLabel: { type: String, required: true },
  firstPrizeCount: { type: String, required: true },
  nextPoolLabel: { type: String, required: true },
  nextPoolDisplay: { type: String, required: true },
  nextPoolSubDisplay: { type: String, required: true },
});
</script>

<template>
  <div class="ref-card p-7">
    <div class="mb-8 flex flex-col items-start justify-between gap-3 sm:flex-row sm:items-center">
      <h2 class="text-[25px] font-semibold text-[#1c3342]">奖金状态</h2>
      <router-link to="/jackpot" class="text-[15px] text-[#7a746c]">查看详情 ›</router-link>
    </div>
    <div class="grid grid-cols-1 gap-4 divide-[#e1d8ca] xs:grid-cols-3 xs:gap-0 xs:divide-x">
      <div class="pr-0 xs:pr-8">
        <p class="mb-4 text-[15px] text-[#68716f]">{{ poolCardLabel }}</p>
        <p class="break-words text-[20px] font-semibold text-[#c5443f]">{{ poolDisplay }}</p>
        <p class="mt-3 break-words text-[14px] text-[#7a807f]">{{ poolSubDisplay }}</p>
      </div>
      <div class="px-0 py-4 xs:px-8 xs:py-0">
        <p class="mb-4 text-[15px] text-[#68716f]">{{ firstPrizeLabel }}</p>
        <p class="text-[20px] font-semibold text-[#c5443f]">{{ firstPrizeCount }}</p>
      </div>
      <div class="border-[#e1d8ca] pl-0 pt-4 xs:border-t-0 xs:pl-8 xs:pt-0">
        <p class="mb-4 text-[15px] text-[#68716f]">{{ nextPoolLabel }}</p>
        <p class="break-words text-[20px] font-semibold text-[#bd7f26]">{{ nextPoolDisplay }}</p>
        <p class="mt-3 break-words text-[14px] text-[#7a807f]">{{ nextPoolSubDisplay }}</p>
      </div>
    </div>
  </div>
</template>
