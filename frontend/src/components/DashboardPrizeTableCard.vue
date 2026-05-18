<script setup>
defineProps({
  prizeUnit: { type: String, required: true },
  prizeRows: { type: Array, required: true },
});
</script>

<template>
  <div class="ref-card p-7">
    <div class="mb-5 flex justify-between">
      <h2 class="text-[24px] font-semibold text-[#1c3342]">中奖注数与奖金</h2>
      <span class="text-[14px] text-[#6e7373]">{{ prizeUnit }}</span>
    </div>
    <div class="-mx-2 overflow-x-auto px-2">
      <table class="prize-table whitespace-nowrap text-sm xs:text-base">
        <thead>
          <tr>
            <th class="px-2">奖项</th>
            <th class="px-2">中奖条件</th>
            <th class="px-2">注数</th>
            <th class="px-2">每注奖金</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in prizeRows" :key="row.label">
            <td class="px-2">{{ row.label }}</td>
            <td class="px-2 text-[#8a9393]">{{ row.condition }}</td>
            <td class="px-2 text-center">{{ row.count }}</td>
            <td class="px-2 text-right">{{ row.prize }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
