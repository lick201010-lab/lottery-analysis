<script setup>
import NumberBall from "./NumberBall.vue";

defineProps({
  lotteryLabel: { type: String, required: true },
  displayDrawNumber: { type: String, required: true },
  displayDate: { type: String, required: true },
  weekdayLabel: { type: String, required: true },
  drawNumbers: { type: Array, required: true },
  specialNumber: { type: Number, default: null },
  lotteryType: { type: String, required: true },
  drawSourceText: { type: String, required: true },
  displayDrawTime: { type: String, required: true },
});
</script>

<template>
  <section class="ref-card hero-reference">
    <div class="hero-reference-top flex flex-col gap-4 sm:flex-row sm:items-start">
      <div class="flex flex-wrap items-baseline gap-3">
        <h1 class="text-2xl font-semibold leading-tight tracking-[0.12em] text-[#1c3342] sm:text-[42px]">
          {{ lotteryLabel }}
        </h1>
        <span class="text-lg font-semibold text-[#1f3443] sm:text-[24px]">最新开奖</span>
      </div>
      <div class="flex flex-wrap items-center gap-3">
        <span class="issue-pill text-sm sm:text-base">第 {{ displayDrawNumber }} 期</span>
        <span class="flex items-center gap-2 text-sm text-[#626c6c] sm:text-[17px]">
          <span>▣</span>
          {{ displayDate }}
          <span class="hidden xs:inline">{{ weekdayLabel }}</span>
        </span>
      </div>
      <div class="flex gap-3 sm:ml-auto sm:gap-6">
        <router-link to="/data" class="ref-outline-button text-sm sm:text-base">↶ 历史</router-link>
        <router-link to="/generate" class="ref-gold-button text-sm sm:text-base">✥ 选号</router-link>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-7 lg:grid-cols-[1.26fr_0.42fr_0.9fr]">
      <div>
        <p class="mb-5 text-[17px] font-medium text-[#1f3443]">中奖号码</p>
        <div class="flex flex-wrap items-center gap-6">
          <NumberBall
            v-for="number in drawNumbers"
            :key="number"
            :number="number"
            size="hero"
            :lotteryType="lotteryType"
          />
        </div>
      </div>

      <div class="pl-0 lg:border-l lg:border-[#d8cec0] lg:pl-10">
        <p class="mb-5 text-[17px] font-medium text-[#1f3443]">特别号码</p>
        <NumberBall
          v-if="specialNumber"
          :number="specialNumber"
          size="hero"
          is-special
          :lotteryType="lotteryType"
        />
      </div>

      <div class="relative min-h-[145px]">
        <div class="hk-skyline" aria-hidden="true">
          <img src="/assets/hk-skyline.png" alt="" decoding="async" />
        </div>
      </div>
    </div>

    <div class="mt-8 flex flex-wrap items-center gap-7 text-[15px] text-[#68716f]">
      <span class="flex items-center gap-2">ⓘ {{ drawSourceText }}</span>
      <span class="h-5 w-px bg-[#c9bdae]"></span>
      <span>开奖时间： {{ displayDate }} {{ displayDrawTime }}</span>
    </div>
  </section>
</template>
