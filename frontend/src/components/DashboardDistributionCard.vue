<script setup>
defineProps({
  numberStats: { type: Array, required: true },
  observationGroups: { type: Array, required: true },
  lotteryType: { type: String, required: true },
});

function ballToneClass(item) {
  if (item.tone === "hit") return "border-[#c85d5a] bg-[#c85d5a] text-white shadow-sm";
  if (item.tone === "special") return "border-[#6288ad] bg-[#6288ad] text-white shadow-sm";
  if (item.tone === "hot") return "border-[#dfaaa4] bg-[#fff0ed] text-[#9f3834]";
  if (item.tone === "cold") return "border-[#b3c9df] bg-[#eef6fb] text-[#315f86]";
  return "border-[#e4d9c9] bg-[#fffdf8] text-[#435056]";
}

function groupToneClass(tone) {
  if (tone === "hot") return "text-[#b8473f]";
  if (tone === "cold") return "text-[#356a92]";
  if (tone === "hit") return "text-[#7a653f]";
  return "text-[#476555]";
}
</script>

<template>
  <section class="ref-card p-6 sm:p-7">
    <div class="mb-5 flex flex-col gap-2 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <h2 class="text-[24px] font-semibold leading-tight text-[#1c3342]">近期号码观察</h2>
        <p class="mt-1 text-sm text-[#6e7373]">近 100 期 · 出现次数 / 遗漏 / 冷热指数</p>
      </div>
      <div class="flex flex-wrap gap-2 text-xs font-semibold text-[#6b706e]">
        <span class="rounded border border-[#dfaaa4] bg-[#fff0ed] px-2.5 py-1 text-[#9f3834]">热</span>
        <span class="rounded border border-[#b3c9df] bg-[#eef6fb] px-2.5 py-1 text-[#315f86]">冷</span>
        <span class="rounded border border-[#c85d5a] bg-[#c85d5a] px-2.5 py-1 text-white">最新命中</span>
      </div>
    </div>

    <div class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_300px]">
      <div class="min-w-0">
        <div class="grid grid-cols-7 gap-2 sm:grid-cols-11 md:grid-cols-11 lg:grid-cols-11 xl:grid-cols-11">
          <div
            v-for="item in numberStats"
            :key="item.number"
            class="min-h-[58px] rounded-md border px-1.5 py-1.5 text-center transition hover:-translate-y-0.5 hover:shadow-sm"
            :class="ballToneClass(item)"
          >
            <div class="text-[15px] font-bold leading-none">{{ String(item.number).padStart(2, "0") }}</div>
            <div class="mt-1 text-[10px] leading-tight opacity-80">出 {{ item.countLabel }}</div>
            <div class="text-[10px] leading-tight opacity-75">遗 {{ item.missLabel }}</div>
          </div>
        </div>
      </div>

      <aside class="border-t border-[#e5dacb] pt-4 xl:border-l xl:border-t-0 xl:pl-5 xl:pt-0">
        <div class="mb-3 flex items-center justify-between">
          <h3 class="text-base font-semibold text-[#1c3342]">观察结论</h3>
          <router-link to="/generate" class="text-xs font-semibold text-[#7c6644] hover:text-[#533f2a]">
            去分层选号
          </router-link>
        </div>

        <div class="divide-y divide-[#eadfce]">
          <div
            v-for="group in observationGroups"
            :key="group.label"
            class="py-3 first:pt-0"
          >
            <div class="mb-2 flex items-baseline justify-between gap-3">
              <p class="text-sm font-semibold" :class="groupToneClass(group.tone)">{{ group.label }}</p>
              <span class="text-[11px] text-[#8a8f8c]">{{ group.hint }}</span>
            </div>
            <div class="flex flex-wrap gap-1.5">
              <span
                v-for="item in group.numbers"
                :key="group.label + '-' + item.number"
                class="inline-grid h-8 w-8 place-items-center rounded-full border text-xs font-bold"
                :class="ballToneClass(item)"
              >
                {{ String(item.number).padStart(2, "0") }}
              </span>
              <span v-if="group.numbers.length === 0" class="text-sm text-[#8a8f8c]">
                等待频率数据
              </span>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </section>
</template>
