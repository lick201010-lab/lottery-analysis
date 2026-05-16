<script setup>
import { computed } from "vue";
import { lotteryType } from "../api.js";
import NumberBall from "./NumberBall.vue";

const props = defineProps({
  draws: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
});

function formatDate(d) {
  if (!d) return "";
  return new Date(d).toLocaleDateString("zh-HK");
}
</script>

<template>
  <div class="bg-white rounded-2xl border border-[#e3e8ee] shadow-sm overflow-hidden card-stripe">
    <div class="overflow-x-auto">
      <table class="w-full table-premium text-[15px]">
        <thead>
          <tr class="bg-[#f6f9fc] border-b border-[#e3e8ee]">
            <th class="px-5 py-4 text-left font-semibold text-[#64748d]">期号</th>
            <th class="px-5 py-4 text-left font-semibold text-[#64748d] hidden sm:table-cell">日期</th>
            <th class="px-5 py-4 text-center font-semibold text-[#64748d]">开奖数字</th>
            <th class="px-5 py-4 text-center font-semibold text-[#64748d]">特别号</th>
            <th class="px-5 py-4 text-center font-semibold text-[#64748d] hidden md:table-cell">单/双</th>
            <th class="px-5 py-4 text-center font-semibold text-[#64748d] hidden md:table-cell">大小</th>
            <th class="px-5 py-4 text-center font-semibold text-[#64748d] hidden md:table-cell">总和</th>
            <th class="px-5 py-4 text-center font-semibold text-[#64748d] hidden md:table-cell">连号</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="8" class="px-5 py-16 text-center text-[#64748d]">
              <svg class="w-8 h-8 mx-auto mb-2 animate-spin text-[#e3e8ee]" fill="currentColor" viewBox="0 0 24 24"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/></svg>
              加载中...
            </td>
          </tr>
          <tr v-else-if="draws.length === 0">
            <td colspan="8" class="px-5 py-16 text-center text-[#64748d]">
              <svg class="w-10 h-10 mx-auto mb-3 text-[#e3e8ee]" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
              暂无数据，请先导入数据
            </td>
          </tr>
          <tr
            v-for="draw in draws"
            :key="draw.id"
            class="border-b border-[#e3e8ee] transition-colors hover:bg-[#f6f9fc]"
          >
            <td class="px-5 py-3.5 font-bold text-[#273951]">{{ draw.draw_number }}</td>
            <td class="px-5 py-3.5 text-[#64748d] font-medium hidden sm:table-cell">{{ formatDate(draw.draw_date) }}</td>
            <td class="px-5 py-3.5">
              <div class="flex items-center justify-center gap-1.5 sm:gap-2">
                <NumberBall :number="draw.num1" :lotteryType="lotteryType" size="sm" />
                <NumberBall :number="draw.num2" :lotteryType="lotteryType" size="sm" />
                <NumberBall :number="draw.num3" :lotteryType="lotteryType" size="sm" />
                <NumberBall :number="draw.num4" :lotteryType="lotteryType" size="sm" />
                <NumberBall :number="draw.num5" :lotteryType="lotteryType" size="sm" />
                <NumberBall :number="draw.num6" :lotteryType="lotteryType" size="sm" />
              </div>
            </td>
            <td class="px-5 py-3.5 text-center">
              <NumberBall :number="draw.special_num" :lotteryType="lotteryType" size="sm" />
            </td>
            <td class="px-5 py-3.5 text-center text-[#64748d] font-medium hidden md:table-cell">
              {{ draw.odd_count }}:{{ draw.even_count }}
            </td>
            <td class="px-5 py-3.5 text-center text-[#64748d] font-medium hidden md:table-cell">
              {{ draw.small_count }}:{{ draw.big_count }}
            </td>
            <td class="px-5 py-3.5 text-center text-[#64748d] font-bold hidden md:table-cell">{{ draw.sum_total }}</td>
            <td class="px-5 py-3.5 text-center hidden md:table-cell">
              <span
                v-if="draw.has_consecutive"
                class="text-xs font-bold bg-[#533afd] text-white px-2.5 py-1 rounded-lg"
              >是</span>
              <span v-else class="text-xs text-[#64748d] font-medium">-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
