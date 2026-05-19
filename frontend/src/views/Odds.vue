<script setup>
import { ref, computed } from "vue";
import { lotteryType } from "../api.js";

const selectedNumbers = ref([]);
const oddsData = ref({
  ssq: [
    { level: "一等奖", condition: "6红+1蓝", probability: "1/177,210,888", odds: "约500万-1000万" },
    { level: "二等奖", condition: "6红", probability: "1/11,688,053", odds: "约10万-100万" },
    { level: "三等奖", condition: "5红+1蓝", probability: "1/789,648", odds: "约3,000" },
    { level: "四等奖", condition: "5红 或 4红+1蓝", probability: "1/22,075", odds: "约200" },
    { level: "五等奖", condition: "4红", probability: "1/1,083", odds: "约10" },
    { level: "六等奖", condition: "2红+1蓝", probability: "1/672", odds: "约5" },
  ],
  lw6: [
    { level: "头奖", condition: "6个正码全中", probability: "1/13,983,816", odds: "彩池决定" },
    { level: "二奖", condition: "5个正码+特别号", probability: "1/2,330,636", odds: "彩池决定" },
    { level: "三奖", condition: "5个正码", probability: "1/55,491", odds: "约HK$10,000" },
    { level: "四奖", condition: "4个正码+特别号", probability: "1/22,197", odds: "约HK$640" },
    { level: "五奖", condition: "4个正码", probability: "1/1,083", odds: "约HK$320" },
    { level: "六奖", condition: "3个正码+特别号", probability: "1/812", odds: "约HK$130" },
    { level: "七奖", condition: "3个正码", probability: "1/81", odds: "约HK$30" },
  ]
});

const currentOdds = computed(() => lotteryType.value === "ssq" ? oddsData.value.ssq : oddsData.value.lw6);
const lotteryName = computed(() => lotteryType.value === "ssq" ? "双色球" : "香港六合彩");
</script>

<template>
  <div class="ref-card p-8">
    <h1 class="text-2xl font-semibold text-[#1c3342] mb-2">中奖概率说明</h1>
    <p class="text-sm text-[#7a807f] mb-6">{{ lotteryName }}各奖项的中奖条件与概率</p>
    
    <div class="overflow-x-auto">
      <table class="prize-table whitespace-nowrap text-sm">
        <thead>
          <tr>
            <th class="px-3 text-left">奖项</th>
            <th class="px-3 text-left">中奖条件</th>
            <th class="px-3 text-left">概率</th>
            <th class="px-3 text-left">奖金</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in currentOdds" :key="row.level">
            <td class="px-3 font-medium">{{ row.level }}</td>
            <td class="px-3 text-[#8a9393]">{{ row.condition }}</td>
            <td class="px-3 text-[#c5443f]">{{ row.probability }}</td>
            <td class="px-3">{{ row.odds }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <p class="mt-6 text-xs text-[#7d867f] border-t border-[#e2d9cc] pt-4">
      注：中奖概率为理论值，实际奖金由奖池金额和中奖注数决定。请理性投注，切勿沉迷。
    </p>
  </div>
</template>