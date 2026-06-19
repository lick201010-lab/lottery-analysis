<script setup>
import { computed } from "vue";
import { useSEO, breadcrumb } from "../composables/useSEO.js";
import { archiveData, getArchiveIssue } from "../data/drawArchives.js";
import NumberBall from "../components/NumberBall.vue";

const props = defineProps({
  gameKey: { type: String, required: true },
  year: { type: String, required: true },
  issue: { type: String, required: true },
});

const game = computed(() => archiveData.games[props.gameKey]);
const draw = computed(() => getArchiveIssue(props.gameKey, props.year, props.issue));
const title = computed(() => `${game.value.label}${draw.value.drawNumber}期开奖结果`);
const description = computed(
  () =>
    `${game.value.label}${draw.value.drawNumber}期开奖结果归档，开奖日期 ${draw.value.drawDate}，整理正码、${game.value.issueLabel}、和值、奇偶大小等统计。仅供数据分析与娱乐参考。`,
);

const datasetJsonLd = computed(() => ({
  "@context": "https://schema.org",
  "@type": "Dataset",
  name: title.value,
  description: description.value,
  inLanguage: "zh-CN",
  creator: { "@type": "Organization", name: "弈彩 YiCai" },
  url: `https://yicai.ckl.hk${draw.value.path}`,
  datePublished: draw.value.drawDate,
  variableMeasured: ["期号", "开奖日期", "正码", game.value.issueLabel, "和值", "奇偶比", "大小比"],
}));

useSEO({
  title: title.value,
  description: description.value,
  path: draw.value.path,
  jsonLd: [
    breadcrumb([
      { name: "首页", path: "/" },
      { name: `${game.value.label}开奖归档`, path: `${game.value.basePath}/results` },
      { name: `${props.year}年`, path: `${game.value.basePath}/${props.year}` },
      { name: draw.value.drawNumber, path: draw.value.path },
    ]),
    datasetJsonLd.value,
  ],
});
</script>

<template>
  <div class="space-y-8 pb-16">
    <section class="rounded-md border border-[#e2d8ca] bg-[#fffdf8] px-6 py-8 sm:px-8 lg:px-10">
      <p class="mb-3 text-xs font-semibold tracking-[0.24em] text-[#9b7a45]">ISSUE ARCHIVE</p>
      <div class="grid gap-8 lg:grid-cols-[minmax(0,1fr)_300px] lg:items-start">
        <div>
          <h1 class="text-3xl font-semibold leading-tight text-[#173247] sm:text-4xl">{{ title }}</h1>
          <p class="mt-4 text-base leading-8 text-[#5f6868]">
            本页为{{ game.label }}第 {{ draw.drawNumber }} 期开奖结果归档，开奖日期为 {{ draw.drawDate }}。
          </p>
        </div>
        <aside class="rounded-md border border-[#eadfce] bg-[#f7f1e8] p-5">
          <p class="text-sm font-semibold text-[#233142]">{{ game.label }}开奖归档</p>
          <div class="mt-4 space-y-2 text-sm text-[#6e7373]">
            <p>年份：{{ year }}</p>
            <p>期号：{{ draw.drawNumber }}</p>
            <p>{{ game.issueLabel }}：{{ String(draw.special).padStart(2, "0") }}</p>
          </div>
        </aside>
      </div>
    </section>

    <section class="rounded-md border border-[#e2d8ca] bg-[#fffdf8] p-6 sm:p-8">
      <div class="grid gap-8 lg:grid-cols-[minmax(0,1fr)_280px]">
        <div>
          <h2 class="text-xl font-semibold text-[#1c3342]">开奖号码</h2>
          <div class="mt-5 flex flex-wrap items-center gap-3">
            <NumberBall
              v-for="number in draw.numbers"
              :key="number"
              :number="number"
              :lottery-type="gameKey"
              size="lg"
            />
            <span class="text-lg font-semibold text-[#9b7a45]">+</span>
            <div class="flex flex-col items-center gap-2">
              <NumberBall :number="draw.special" :lottery-type="gameKey" :is-special="true" size="lg" />
              <span class="text-xs font-semibold text-[#6e7373]">
                <template v-if="gameKey === 'ssq'">蓝球 · 头奖条件</template>
                <template v-else>特码 · 辅助判断</template>
              </span>
            </div>
          </div>
          <p class="mt-5 text-sm leading-7 text-[#6e7373]">{{ game.issueNote }}。页面只整理历史数据，不提供任何结果判断。</p>
        </div>

        <div class="rounded-md border border-[#eadfce] bg-[#fffaf3] p-5">
          <h2 class="text-base font-semibold text-[#233142]">基础统计</h2>
          <dl class="mt-4 grid grid-cols-2 gap-4 text-sm">
            <div>
              <dt class="text-[#8a8f8c]">和值</dt>
              <dd class="mt-1 text-lg font-semibold text-[#233142]">{{ draw.sumTotal }}</dd>
            </div>
            <div>
              <dt class="text-[#8a8f8c]">奇偶比</dt>
              <dd class="mt-1 text-lg font-semibold text-[#233142]">{{ draw.oddCount }}:{{ draw.evenCount }}</dd>
            </div>
            <div>
              <dt class="text-[#8a8f8c]">大小比</dt>
              <dd class="mt-1 text-lg font-semibold text-[#233142]">{{ draw.smallCount }}:{{ draw.bigCount }}</dd>
            </div>
            <div>
              <dt class="text-[#8a8f8c]">连号</dt>
              <dd class="mt-1 text-lg font-semibold text-[#233142]">{{ draw.hasConsecutive ? "有" : "无" }}</dd>
            </div>
          </dl>
        </div>
      </div>
    </section>

    <section class="grid gap-6 lg:grid-cols-2">
      <router-link
        :to="`${game.basePath}/${year}`"
        class="rounded-md border border-[#e2d8ca] bg-[#fffdf8] p-5 transition hover:border-[#d0b98f]"
      >
        <p class="text-sm font-semibold text-[#233142]">查看{{ year }}年归档</p>
        <p class="mt-2 text-sm text-[#6e7373]">返回同一年份的更多期开奖记录。</p>
      </router-link>
      <router-link
        :to="`${game.basePath}/frequency`"
        class="rounded-md border border-[#e2d8ca] bg-[#fffdf8] p-5 transition hover:border-[#d0b98f]"
      >
        <p class="text-sm font-semibold text-[#233142]">查看号码频率</p>
        <p class="mt-2 text-sm text-[#6e7373]">继续查看历史出现次数、冷热和遗漏。</p>
      </router-link>
    </section>

    <section class="rounded-md border border-[#eadfce] bg-[#fffaf3] p-5">
      <h2 class="text-base font-semibold text-[#233142]">合规说明</h2>
      <p class="mt-2 text-sm leading-7 text-[#6e7373]">
        本页内容仅供数据分析与娱乐参考。开奖结果具有随机性，历史数据不能保证未来结果；请以官方公告为准，理性娱乐。
      </p>
    </section>
  </div>
</template>
