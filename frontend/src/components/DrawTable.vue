<script setup>
import { computed } from "vue";
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
  <div class="bg-white rounded-2xl border border-gray-200/80 shadow-sm overflow-hidden card-lift">
    <div class="overflow-x-auto">
      <table class="w-full table-premium text-[15px]">
        <thead>
          <tr class="bg-gray-50/80 border-b border-gray-200">
            <th class="px-5 py-4 text-left font-semibold text-gray-500">期号</th>
            <th class="px-5 py-4 text-left font-semibold text-gray-500">日期</th>
            <th class="px-5 py-4 text-center font-semibold text-gray-500">号码</th>
            <th class="px-5 py-4 text-center font-semibold text-gray-500">特码</th>
            <th class="px-5 py-4 text-center font-semibold text-gray-500">单/双</th>
            <th class="px-5 py-4 text-center font-semibold text-gray-500">大小</th>
            <th class="px-5 py-4 text-center font-semibold text-gray-500">总和</th>
            <th class="px-5 py-4 text-center font-semibold text-gray-500">连号</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="8" class="px-5 py-16 text-center text-gray-400">
              <svg class="w-8 h-8 mx-auto mb-2 animate-spin text-gray-300" fill="currentColor" viewBox="0 0 24 24"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/></svg>
              加载中...
            </td>
          </tr>
          <tr v-else-if="draws.length === 0">
            <td colspan="8" class="px-5 py-16 text-center text-gray-400">
              <svg class="w-10 h-10 mx-auto mb-3 text-gray-200" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
              暂无数据，请先导入数据
            </td>
          </tr>
          <tr
            v-for="draw in draws"
            :key="draw.id"
            class="border-b border-gray-100 transition-colors"
          >
            <td class="px-5 py-3.5 font-bold text-gray-800">{{ draw.draw_number }}</td>
            <td class="px-5 py-3.5 text-gray-500 font-medium">{{ formatDate(draw.draw_date) }}</td>
            <td class="px-5 py-3.5">
              <div class="flex items-center justify-center gap-2">
                <NumberBall :number="draw.num1" size="sm" />
                <NumberBall :number="draw.num2" size="sm" />
                <NumberBall :number="draw.num3" size="sm" />
                <NumberBall :number="draw.num4" size="sm" />
                <NumberBall :number="draw.num5" size="sm" />
                <NumberBall :number="draw.num6" size="sm" />
              </div>
            </td>
            <td class="px-5 py-3.5 text-center">
              <NumberBall :number="draw.special_num" size="sm" />
            </td>
            <td class="px-5 py-3.5 text-center text-gray-600 font-medium">
              {{ draw.odd_count }}:{{ draw.even_count }}
            </td>
            <td class="px-5 py-3.5 text-center text-gray-600 font-medium">
              {{ draw.small_count }}:{{ draw.big_count }}
            </td>
            <td class="px-5 py-3.5 text-center text-gray-600 font-bold">{{ draw.sum_total }}</td>
            <td class="px-5 py-3.5 text-center">
              <span
                v-if="draw.has_consecutive"
                class="text-xs font-bold bg-amber-100 text-amber-700 px-2.5 py-1 rounded-lg"
              >是</span>
              <span v-else class="text-xs text-gray-300 font-medium">-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
