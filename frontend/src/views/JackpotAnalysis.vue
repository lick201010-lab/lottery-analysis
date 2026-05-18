<script setup>
import { ref, computed } from "vue";
import { lotteryType } from "../api.js";
import { getLotteryMeta } from "../lotteryMeta.js";

const inputAmount = ref(10000000); // 默认1000万
const payoutMethod = ref("cash"); // cash | annuity

const lotteryLabel = computed(() => (lotteryType.value === "ssq" ? "双色球" : "六合彩"));
const meta = computed(() => getLotteryMeta(lotteryType.value));

// Tax rules
const taxRules = computed(() => {
  if (lotteryType.value === "ssq") {
    return {
      name: "双色球",
      currency: meta.value.currencyName,
      taxRate: 0.20,
      taxName: "个人所得税",
      taxNote: meta.value.taxNote,
      exempt: false,
      annuityAvailable: false,
    };
  }
  return {
    name: "六合彩",
    currency: meta.value.currencyName,
    taxRate: 0,
    taxName: "无税费",
    taxNote: meta.value.taxNote,
    exempt: true,
    annuityAvailable: false,
  };
});

const breakdown = computed(() => {
  const amount = Number(inputAmount.value) || 0;
  const rule = taxRules.value;
  const taxAmount = amount * rule.taxRate;
  const netAmount = amount - taxAmount;

  return {
    gross: amount,
    tax: taxAmount,
    net: netAmount,
    taxRateDisplay: (rule.taxRate * 100).toFixed(0) + "%",
  };
});

const formatMoney = (n) => {
  if (n >= 100000000) return (n / 100000000).toFixed(2) + "亿";
  if (n >= 10000) return (n / 10000).toFixed(2) + "万";
  return n.toLocaleString();
};
</script>

<template>
  <div class="space-y-8 animate-fade-in-up">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-[#0a0e27] tracking-tight">奖金分析</h1>
      <p class="text-base text-[#64748d] mt-1">输入假设中奖金额，查看税后到手金额拆解</p>
    </div>

    <!-- Input Section -->
    <div class="card-stripe p-6 sm:p-8">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <label class="block text-sm font-semibold text-[#64748d] mb-2">假设中奖金额</label>
          <div class="relative">
            <span class="absolute left-4 top-1/2 -translate-y-1/2 text-[#64748d] font-medium">{{ taxRules.currency }}</span>
            <input
              v-model.number="inputAmount"
              type="number"
              class="w-full pl-14 pr-4 py-3 bg-[#f6f9fc] border border-[#e3e8ee] rounded-xl text-[#0a0e27] font-bold text-lg tabular focus:ring-2 focus:ring-[#533afd]/20"
              placeholder="输入金额"
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-semibold text-[#64748d] mb-2">彩种</label>
          <div class="flex items-center gap-2 px-4 py-3 bg-[#f6f9fc] border border-[#e3e8ee] rounded-xl">
            <span
              class="w-3 h-3 rounded-full"
              :class="lotteryType === 'ssq' ? 'bg-gradient-to-r from-blue-500 to-red-500' : 'bg-gradient-to-r from-red-500 to-orange-500'"
            ></span>
            <span class="font-bold text-[#0a0e27]">{{ lotteryLabel }}</span>
          </div>
        </div>

        <div>
          <label class="block text-sm font-semibold text-[#64748d] mb-2">税务规则</label>
          <div class="px-4 py-3 bg-[#f6f9fc] border border-[#e3e8ee] rounded-xl">
            <span class="text-sm text-[#0a0e27] font-medium">{{ taxRules.taxName }}</span>
            <span v-if="!taxRules.exempt" class="ml-2 text-xs text-[#ea2261] font-bold">{{ taxRules.taxRateDisplay }}</span>
            <span v-else class="ml-2 text-xs text-[#0ecb81] font-bold">免税</span>
          </div>
        </div>
      </div>

      <p class="text-xs text-[#64748d] mt-4">{{ taxRules.taxNote }}</p>
    </div>

    <!-- Breakdown Table -->
    <div class="card-stripe p-6 sm:p-8 overflow-hidden">
      <h3 class="text-base font-bold text-[#0a0e27] mb-5">到手金额拆解</h3>

      <div class="overflow-x-auto">
        <table class="w-full text-[15px]">
          <tbody class="divide-y divide-[#e3e8ee]">
            <tr class="group">
              <td class="py-4 pr-4 text-[#64748d]">税前金额</td>
              <td class="py-4 text-right font-bold text-[#0a0e27] tabular text-lg">{{ formatMoney(breakdown.gross) }} {{ taxRules.currency }}</td>
            </tr>
            <tr v-if="!taxRules.exempt" class="group">
              <td class="py-4 pr-4 text-[#64748d]">
                {{ taxRules.taxName }} <span class="text-xs text-[#ea2261]">-{{ taxRules.taxRateDisplay }}</span>
              </td>
              <td class="py-4 text-right font-bold text-[#ea2261] tabular text-lg">-{{ formatMoney(breakdown.tax) }} {{ taxRules.currency }}</td>
            </tr>
            <tr v-else class="group">
              <td class="py-4 pr-4 text-[#64748d]">{{ taxRules.taxName }}</td>
              <td class="py-4 text-right font-bold text-[#0ecb81] tabular text-lg">0 {{ taxRules.currency }}</td>
            </tr>
            <tr class="bg-[#f6f9fc]">
              <td class="py-5 pr-4 text-[#0a0e27] font-bold">最终到手</td>
              <td class="py-5 text-right font-extrabold text-[#533afd] tabular text-2xl">{{ formatMoney(breakdown.net) }} {{ taxRules.currency }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Visual Bar -->
    <div class="card-stripe p-6 sm:p-8">
      <h3 class="text-base font-bold text-[#0a0e27] mb-5">金额占比可视化</h3>

      <div class="relative h-12 rounded-xl overflow-hidden flex">
        <div
          v-if="breakdown.net > 0"
          class="h-full bg-gradient-to-r from-[#533afd] to-[#665efd] flex items-center justify-center text-white font-bold text-sm transition-all duration-500"
          :style="{ width: (breakdown.net / breakdown.gross * 100) + '%' }"
        >
          到手 {{ (breakdown.net / breakdown.gross * 100).toFixed(0) }}%
        </div>
        <div
          v-if="breakdown.tax > 0"
          class="h-full bg-gradient-to-r from-[#ea2261] to-[#f96bee] flex items-center justify-center text-white font-bold text-sm transition-all duration-500"
          :style="{ width: (breakdown.tax / breakdown.gross * 100) + '%' }"
        >
          税费 {{ (breakdown.tax / breakdown.gross * 100).toFixed(0) }}%
        </div>
      </div>

      <div class="flex items-center justify-center gap-6 mt-4">
        <div class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-gradient-to-r from-[#533afd] to-[#665efd]"></span>
          <span class="text-sm text-[#64748d]">到手金额</span>
        </div>
        <div v-if="breakdown.tax > 0" class="flex items-center gap-2">
          <span class="w-3 h-3 rounded-full bg-gradient-to-r from-[#ea2261] to-[#f96bee]"></span>
          <span class="text-sm text-[#64748d]">税费</span>
        </div>
      </div>
    </div>

    <!-- Disclaimer -->
    <p class="text-sm text-[#64748d] text-center">
      免责声明：奖金分析仅供参考，实际税率以当地税务机关规定为准。请理性娱乐，切勿沉迷。
    </p>
  </div>
</template>
