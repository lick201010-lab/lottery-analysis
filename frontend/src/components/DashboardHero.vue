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
            v-for="(number, index) in drawNumbers"
            :key="`hero-${index}`"
            :number="number"
            size="hero"
            :lotteryType="lotteryType"
          />
        </div>
      </div>

      <div class="pl-0 lg:border-l lg:border-[#d8cec0] lg:pl-10">
        <p class="mb-5 text-[17px] font-medium text-[#1f3443]">特别号码</p>
        <NumberBall
          v-if="specialNumber !== null && specialNumber !== undefined"
          :number="specialNumber"
          size="hero"
          is-special
          :lotteryType="lotteryType"
        />
      </div>

      <div class="relative min-h-[145px]">
        <div class="hk-skyline" aria-hidden="true">
          <svg
            v-if="lotteryType === 'ssq'"
            class="mainland-skyline-svg"
            viewBox="0 0 900 210"
            focusable="false"
          >
            <g fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round" stroke-linecap="round">
              <path d="M26 178H874" />
              <path d="M62 178v-30h68v30M48 148h96l-22-17H70zM72 131h48l-14-12H86z" />
              <path d="M186 178v-34h96v34M170 144h128l-28-18h-72zM204 126h60l-18-13h-24z" />
              <path d="M356 178c0-40 42-70 94-70s94 30 94 70M386 178c0-28 28-50 64-50s64 22 64 50M412 128l38-46 38 46" />
              <path d="M606 178v-38h86v38M588 140h122l-30-20h-62zM622 120h54l-16-12h-22z" />
              <path d="M744 178v-28h92v28M730 150h120l-26-17h-68zM760 133h58l-17-12h-24z" />
              <path d="M40 178c50-12 94-12 144 0M304 178c48-11 96-11 144 0M534 178c52-12 104-12 156 0M704 178c48-10 92-10 140 0" />
            </g>
          </svg>
          <img v-else src="/assets/hk-skyline.png" alt="" decoding="async" />
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
