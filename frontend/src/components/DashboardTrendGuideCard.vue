<script setup>
import { computed } from "vue";

const props = defineProps({
  chartZones: { type: Array, required: true },
  zoneTrendBars: { type: Array, required: true },
  zoneInsights: { type: Array, required: true },
});

const zoneTotals = computed(() => {
  const totalDraws = Math.max(props.zoneTrendBars.length, 1);
  return props.chartZones.map((zone) => {
    const total = props.zoneTrendBars.reduce((sum, bar) => {
      const segment = bar.segments.find((item) => item.key === zone.key);
      return sum + Number(segment?.count || 0);
    }, 0);
    const average = total / totalDraws;
    return {
      ...zone,
      total,
      average: average.toFixed(1),
      share: `${Math.max(4, (total / (totalDraws * 6)) * 100)}%`,
    };
  });
});

const recentStructures = computed(() =>
  props.zoneTrendBars.slice(-5).reverse().map((bar) => ({
    ...bar,
    label: String(bar.drawNumber).split("/").pop(),
    summary: bar.segments
      .filter((segment) => segment.count > 0)
      .map((segment) => `${segment.label}${segment.count}`)
      .join(" · "),
  }))
);
</script>

<template>
  <section class="v62-glass-surface flex h-full flex-col p-6 sm:p-7">
    <div class="mb-5 flex flex-col items-start justify-between gap-3 xl:flex-row xl:items-start">
      <div>
        <h2 class="text-[24px] font-semibold leading-tight text-[#1c3342]">分区结构走势</h2>
        <p class="mt-1 text-sm text-[#6e7373]">近 20 期分区占比 · 用于辅助分层选号</p>
      </div>
      <div class="flex flex-wrap gap-x-4 gap-y-2 text-xs font-semibold">
        <span
          v-for="zone in chartZones"
          :key="zone.key"
          class="inline-flex items-center gap-1.5 text-[#626968]"
        >
          <i class="h-2.5 w-2.5 rounded-sm" :style="{ backgroundColor: zone.color }"></i>
          {{ zone.label }} ({{ zone.range }})
        </span>
      </div>
    </div>

    <div class="grid flex-1 gap-6 xl:grid-cols-[minmax(0,1fr)_260px]">
      <div class="flex min-w-0 flex-col">
        <div
          v-if="zoneTrendBars.length"
          class="grid h-[250px] grid-cols-8 items-end gap-2 border-b border-l border-[#eadfce] px-3 pb-3 sm:grid-cols-12 lg:grid-cols-16"
        >
          <div
            v-for="bar in zoneTrendBars"
            :key="bar.drawNumber"
            class="flex h-full min-w-0 flex-col justify-end gap-1"
            :title="`${bar.drawNumber} · ${bar.date}`"
          >
            <div class="flex h-[184px] flex-col justify-end overflow-hidden rounded-t border border-[#eadfce] bg-[#fffaf3]">
              <span
                v-for="segment in bar.segments"
                :key="bar.drawNumber + '-' + segment.key"
                class="block w-full"
                :style="{ height: segment.height, backgroundColor: segment.color, opacity: segment.count ? 0.92 : 0.16 }"
              ></span>
            </div>
            <span class="truncate text-center text-[10px] text-[#8a8f8c]">{{ String(bar.drawNumber).split('/').pop() }}</span>
          </div>
        </div>
        <div
          v-else
          class="grid h-[250px] place-items-center border-b border-l border-[#eadfce] bg-[#fffaf3]/70 text-sm text-[#7d867f]"
        >
          等待近期开奖数据
        </div>
        <p class="mt-3 text-xs text-[#8a8f8c]">每根柱代表一期正码结构，颜色占比越高表示该区号码越集中。</p>

        <div class="v62-zone-support mt-5 grid gap-5 lg:grid-cols-[1.1fr_0.9fr]">
          <div class="v62-zone-panel">
            <div class="mb-3 flex items-center justify-between">
              <h4 class="text-sm font-semibold text-[#233142]">近 20 期分区汇总</h4>
              <span class="text-[11px] text-[#8a8f8c]">按正码统计</span>
            </div>
            <div class="space-y-3">
              <div
                v-for="zone in zoneTotals"
                :key="'total-' + zone.key"
                class="grid grid-cols-[74px_minmax(0,1fr)_58px] items-center gap-3"
              >
                <span class="text-xs font-semibold text-[#566064]">{{ zone.label }}</span>
                <span class="h-2.5 overflow-hidden rounded-full bg-[#eee6dc]">
                  <i class="block h-full rounded-full" :style="{ width: zone.share, backgroundColor: zone.color }"></i>
                </span>
                <span class="text-right text-xs text-[#6e7373]">{{ zone.total }} 次</span>
              </div>
            </div>
          </div>

          <div class="v62-zone-panel">
            <div class="mb-3 flex items-center justify-between">
              <h4 class="text-sm font-semibold text-[#233142]">最近 5 期结构</h4>
              <span class="text-[11px] text-[#8a8f8c]">快速复盘</span>
            </div>
            <div class="space-y-2">
              <div
                v-for="item in recentStructures"
                :key="'recent-' + item.drawNumber"
                class="v62-recent-structure"
              >
                <span class="text-xs font-semibold text-[#233142]">{{ item.label }}</span>
                <span class="truncate text-right text-xs text-[#6e7373]">{{ item.summary || "暂无结构" }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <aside class="flex flex-col border-t border-[#e5dacb] pt-4 xl:border-l xl:border-t-0 xl:pl-5 xl:pt-0">
        <div class="mb-3 flex items-center justify-between">
          <h3 class="text-base font-semibold text-[#1c3342]">结构判断</h3>
          <router-link to="/generate" class="text-xs font-semibold text-[#7c6644] hover:text-[#533f2a]">
            套入漏斗
          </router-link>
        </div>
        <div class="divide-y divide-[#eadfce]">
          <div
            v-for="item in zoneInsights"
            :key="item.label"
            class="py-3 first:pt-0"
          >
            <p class="text-sm font-semibold text-[#233142]">{{ item.label }}</p>
            <p class="mt-1 text-sm text-[#6e7373]">{{ item.value }}</p>
          </div>
        </div>

        <div class="v62-pick-note mt-auto">
          <p class="text-sm font-semibold text-[#233142]">选号落点</p>
          <p class="mt-2 text-sm leading-6 text-[#6e7373]">
            先用分区偏热/回补判断大方向，再回到分层选号用 10 → 8 → 6 收敛。
          </p>
        </div>
      </aside>
    </div>
  </section>
</template>
