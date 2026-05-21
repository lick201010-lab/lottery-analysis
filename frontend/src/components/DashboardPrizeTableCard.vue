<script setup>
defineProps({
  prizeUnit: { type: String, required: true },
  prizeRows: { type: Array, required: true },
  settlementStatus: { type: Object, required: true },
  settlementMetrics: { type: Array, required: true },
  hasRealPrizeData: { type: Boolean, required: true },
});

function statusClass(tone) {
  if (tone === "ok") return "border-[#9fc8b6] bg-[#edf8f2] text-[#2e7356]";
  if (tone === "loading") return "border-[#d7c492] bg-[#fff7db] text-[#826525]";
  return "border-[#dfc4b9] bg-[#fff0ea] text-[#934b38]";
}

function rowClass(index) {
  return index < 2 ? "bg-[#fff7ec]" : "bg-transparent";
}
</script>

<template>
  <section class="ref-card p-6 sm:p-7">
    <div class="mb-5 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <h2 class="text-[24px] font-semibold leading-tight text-[#1c3342]">开奖结算状态</h2>
        <p class="mt-1 text-sm text-[#6e7373]">{{ prizeUnit }}</p>
      </div>
      <span
        class="inline-flex w-fit items-center rounded-full border px-3 py-1 text-xs font-semibold"
        :class="statusClass(settlementStatus.tone)"
      >
        {{ settlementStatus.label }}
      </span>
    </div>

    <div class="grid grid-cols-2 gap-px overflow-hidden rounded-md border border-[#e2d9cc] bg-[#e2d9cc]">
      <div
        v-for="metric in settlementMetrics"
        :key="metric.label"
        class="bg-[#fffdf8] px-3 py-3"
      >
        <p class="text-[11px] font-semibold tracking-[0.08em] text-[#8b908d]">{{ metric.label }}</p>
        <p class="mt-1 truncate text-sm font-semibold text-[#233142] sm:text-base">{{ metric.value }}</p>
      </div>
    </div>

    <div
      v-if="!hasRealPrizeData"
      class="mt-4 rounded-md border border-dashed border-[#dccabb] bg-[#fffaf3] px-4 py-3 text-sm text-[#796f62]"
    >
      {{ settlementStatus.description }}
    </div>

    <div class="mt-5 overflow-hidden rounded-md border border-[#e2d9cc]">
      <table class="w-full whitespace-nowrap text-sm">
        <thead>
          <tr class="bg-[#f6efe5] text-left text-[#5d6263]">
            <th class="px-3 py-3 font-semibold">奖项</th>
            <th class="px-3 py-3 font-semibold">条件</th>
            <th class="px-3 py-3 text-center font-semibold">注数</th>
            <th class="px-3 py-3 text-right font-semibold">每注奖金</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[#e8ddcf]">
          <tr
            v-for="(row, index) in prizeRows"
            :key="row.label"
            :class="rowClass(index)"
          >
            <td class="px-3 py-3 font-semibold text-[#233142]">{{ row.label }}</td>
            <td class="px-3 py-3 text-[#7b8585]">{{ row.condition }}</td>
            <td class="px-3 py-3 text-center text-[#4f5658]">{{ row.count }}</td>
            <td class="px-3 py-3 text-right font-semibold text-[#4f5658]">{{ row.prize }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
