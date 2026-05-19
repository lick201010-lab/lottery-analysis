<script setup>
defineProps({
  numberRows: { type: Array, required: true },
  drawNumberSet: { type: Object, required: true },
  specialNumber: { type: Number, default: null },
  numberFrequency: { type: Function, required: true },
  countTone: { type: Function, required: true },
});
</script>

<template>
  <section class="ref-card p-7">
    <div class="mb-6 flex items-center gap-7">
      <h2 class="text-[24px] font-semibold text-[#1c3342]">近期号码分布</h2>
      <span class="text-[15px] text-[#6e7373]">统计范围：近 100 期</span>
    </div>
    <div class="flex flex-col gap-6 sm:flex-row sm:gap-8">
      <div class="min-w-0 flex-1 overflow-x-auto">
        <div class="distribution-table-wrapper -mx-2 overflow-x-auto px-2">
          <table class="distribution-table whitespace-nowrap text-xs sm:text-sm">
            <tbody>
              <template v-for="(row, rowIndex) in numberRows" :key="rowIndex">
                <tr>
                  <th v-if="rowIndex === 0" rowspan="2" class="px-1">出现</th>
                  <th v-else></th>
                  <td
                    v-for="number in row"
                    :key="'n-' + number"
                    :class="drawNumberSet.has(number) ? 'hit-number' : specialNumber === number ? 'special-number' : ''"
                  >
                    {{ String(number).padStart(2, "0") }}
                  </td>
                </tr>
                <tr>
                  <th v-if="rowIndex !== 0" class="px-1">出现</th>
                  <td v-for="number in row" :key="'c-' + number">{{ numberFrequency(number) }}</td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
      </div>
      <div class="w-[118px] shrink-0">
        <p class="mb-3 text-center text-[15px] text-[#4d5759]">次数</p>
        <div class="grid gap-3 text-center text-[14px]">
          <span :class="countTone(12)" class="rounded px-3 py-2">≥ 12</span>
          <span :class="countTone(8)" class="rounded px-3 py-2">8 - 11</span>
          <span :class="countTone(4)" class="rounded px-3 py-2">4 - 7</span>
          <span :class="countTone(2)" class="rounded px-3 py-2">≤ 3</span>
        </div>
      </div>
    </div>
  </section>
</template>
