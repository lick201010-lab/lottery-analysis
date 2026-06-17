<script setup>
import { computed } from "vue";
import { useSEO, breadcrumb } from "../composables/useSEO.js";
import { archiveData, getArchiveYear } from "../data/drawArchives.js";
import NumberBall from "../components/NumberBall.vue";

const props = defineProps({
  gameKey: { type: String, required: true },
  year: { type: String, required: true },
});

const game = computed(() => archiveData.games[props.gameKey]);
const archiveYear = computed(() => getArchiveYear(props.gameKey, props.year));
const title = computed(() => `${game.value.label}${props.year}年开奖归档`);
const description = computed(
  () =>
    `${game.value.label}${props.year}年开奖归档，整理期号、开奖日期、开奖号码、${game.value.issueLabel}、奇偶大小与和值。仅供数据分析与娱乐参考。`,
);

const datasetJsonLd = computed(() => ({
  "@context": "https://schema.org",
  "@type": "Dataset",
  name: title.value,
  description: description.value,
  inLanguage: "zh-CN",
  creator: { "@type": "Organization", name: "弈彩 YiCai" },
  url: `https://yicai.ckl.hk${archiveYear.value.path}`,
  temporalCoverage: `${archiveYear.value.earliestDate}/${archiveYear.value.latestDate}`,
}));

useSEO({
  title: title.value,
  description: description.value,
  path: archiveYear.value.path,
  jsonLd: [
    breadcrumb([
      { name: "首页", path: "/" },
      { name: `${game.value.label}开奖归档`, path: `${game.value.basePath}/results` },
      { name: `${props.year}年`, path: archiveYear.value.path },
    ]),
    datasetJsonLd.value,
  ],
});
</script>

<template>
  <div class="space-y-8 pb-16">
    <section class="rounded-md border border-[#e2d8ca] bg-[#fffdf8] px-6 py-8 sm:px-8 lg:px-10">
      <p class="mb-3 text-xs font-semibold tracking-[0.24em] text-[#9b7a45]">DRAW ARCHIVE</p>
      <div class="grid gap-6 lg:grid-cols-[minmax(0,1fr)_280px]">
        <div>
          <h1 class="text-3xl font-semibold leading-tight text-[#173247] sm:text-4xl">{{ title }}</h1>
          <p class="mt-4 max-w-3xl text-base leading-8 text-[#5f6868]">
            本页是{{ game.label }}{{ year }}年开奖归档，按期号整理开奖日期、正码、{{ game.issueLabel }}与基础统计指标。
          </p>
        </div>
        <aside class="rounded-md border border-[#eadfce] bg-[#f7f1e8] p-5">
          <p class="text-sm font-semibold text-[#233142]">归档概览</p>
          <dl class="mt-4 grid grid-cols-2 gap-3 text-sm">
            <div>
              <dt class="text-[#8a8f8c]">收录期数</dt>
              <dd class="mt-1 font-semibold text-[#233142]">{{ archiveYear.count }}</dd>
            </div>
            <div>
              <dt class="text-[#8a8f8c]">最新日期</dt>
              <dd class="mt-1 font-semibold text-[#233142]">{{ archiveYear.latestDate }}</dd>
            </div>
          </dl>
        </aside>
      </div>
    </section>

    <section class="rounded-md border border-[#e2d8ca] bg-[#fffdf8] p-5 sm:p-6">
      <div class="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 class="text-xl font-semibold text-[#1c3342]">{{ year }}年近期归档</h2>
          <p class="mt-1 text-sm text-[#6e7373]">优先展示该年份最近期号，更多历史记录可在开奖查询页继续筛选。</p>
        </div>
        <router-link :to="`${game.basePath}/results`" class="text-sm font-semibold text-[#7c6644] hover:text-[#533f2a]">
          返回{{ game.label }}专题
        </router-link>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full min-w-[760px] text-sm">
          <thead>
            <tr class="border-b border-[#e8ddcf] bg-[#f6efe5] text-left text-[#5d6263]">
              <th class="px-3 py-3 font-semibold">期号</th>
              <th class="px-3 py-3 font-semibold">日期</th>
              <th class="px-3 py-3 text-center font-semibold">开奖号码</th>
              <th class="px-3 py-3 text-center font-semibold">{{ game.issueLabel }}</th>
              <th class="px-3 py-3 text-center font-semibold">和值</th>
              <th class="px-3 py-3 text-center font-semibold">详情</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[#eadfce]">
            <tr v-for="draw in archiveYear.sampleDraws" :key="draw.path" class="hover:bg-[#fffaf3]">
              <td class="px-3 py-3 font-semibold text-[#233142]">{{ draw.drawNumber }}</td>
              <td class="px-3 py-3 text-[#6e7373]">{{ draw.drawDate }}</td>
              <td class="px-3 py-3">
                <div class="flex justify-center gap-1.5">
                  <NumberBall
                    v-for="number in draw.numbers"
                    :key="`${draw.drawNumber}-${number}`"
                    :number="number"
                    :lottery-type="gameKey"
                    size="sm"
                  />
                </div>
              </td>
              <td class="px-3 py-3 text-center">
                <NumberBall :number="draw.special" :lottery-type="gameKey" :is-special="true" size="sm" />
              </td>
              <td class="px-3 py-3 text-center font-semibold text-[#566064]">{{ draw.sumTotal }}</td>
              <td class="px-3 py-3 text-center">
                <router-link
                  v-if="draw.hasDetail"
                  :to="draw.path"
                  class="text-xs font-semibold text-[#7c6644] hover:text-[#533f2a]"
                >
                  查看
                </router-link>
                <span v-else class="text-xs text-[#8a8f8c]">归档</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="rounded-md border border-[#eadfce] bg-[#fffaf3] p-5">
      <h2 class="text-base font-semibold text-[#233142]">合规说明</h2>
      <p class="mt-2 text-sm leading-7 text-[#6e7373]">
        本页内容仅供数据分析与娱乐参考。开奖结果具有随机性，历史数据不能保证未来结果；请以官方公告为准，理性娱乐。
      </p>
    </section>
  </div>
</template>
