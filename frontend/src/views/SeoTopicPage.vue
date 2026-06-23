<script setup>
import { computed } from "vue";
import { useSEO, faqPage, dataset } from "../composables/useSEO.js";
import { seoTopics, seoTopicList } from "../data/seoTopics.js";
import { seoTopicsTw, seoTopicListTw } from "../data/seoTopics.tw.js";

const props = defineProps({
  topicKey: { type: String, required: true },
  lang: { type: String, default: "zh" }, // "zh" | "tw"
});

const isTw = computed(() => props.lang === "tw");
const prefix = computed(() => (isTw.value ? "/tw" : ""));
const topic = computed(() => (isTw.value ? seoTopicsTw : seoTopics)[props.topicKey]);
const list = computed(() => (isTw.value ? seoTopicListTw : seoTopicList));

// 界面固定文案（简/繁）
const UI = {
  zh: {
    suffix: "专题",
    compliance: "合规说明",
    complianceText:
      "本页内容仅供数据分析与娱乐参考。开奖结果具有随机性，历史数据不能保证未来结果；请以官方公告为准，理性娱乐。",
    related: "相关入口",
    faq: "常见问题",
  },
  tw: {
    suffix: "專題",
    compliance: "合規說明",
    complianceText:
      "本頁內容僅供數據分析與娛樂參考。開獎結果具有隨機性，歷史數據不能保證未來結果；請以官方公告為準，理性娛樂。",
    related: "相關入口",
    faq: "常見問題",
  },
};
const ui = computed(() => (isTw.value ? UI.tw : UI.zh));

const articleJsonLd = computed(() => ({
  "@context": "https://schema.org",
  "@type": "Article",
  headline: topic.value.title,
  description: topic.value.description,
  inLanguage: isTw.value ? "zh-Hant" : "zh-CN",
  author: { "@type": "Organization", name: "弈彩 YiCai" },
  publisher: {
    "@type": "Organization",
    name: "弈彩 YiCai",
    logo: { "@type": "ImageObject", url: "https://yicai.ckl.hk/logo.png" },
  },
  mainEntityOfPage: `https://yicai.ckl.hk${prefix.value}${topic.value.path}`,
}));

const jsonLdBlocks = computed(() => {
  const blocks = [articleJsonLd.value, faqPage(topic.value.faq)];
  if (topic.value.dataset) {
    blocks.push(
      dataset({
        name: topic.value.dataset.name,
        description: topic.value.dataset.description,
        path: `${prefix.value}${topic.value.path}`,
        temporalCoverage: topic.value.dataset.temporalCoverage,
        variableMeasured: topic.value.dataset.variableMeasured,
      }),
    );
  }
  return blocks;
});

useSEO({
  title: computed(() => topic.value.title),
  description: computed(() => topic.value.description),
  path: computed(() => `${prefix.value}${topic.value.path}`),
  lang: computed(() => props.lang),
  hreflangBase: computed(() => topic.value.path),
  jsonLd: jsonLdBlocks,
});

const siblingTopics = computed(() =>
  list.value.filter((item) => item.game === topic.value.game && item.path !== topic.value.path),
);
</script>

<template>
  <div class="space-y-8 pb-16">
    <section class="rounded-md border border-[#e2d8ca] bg-[#fffdf8] px-6 py-8 sm:px-8 lg:px-10">
      <p class="mb-3 text-xs font-semibold tracking-[0.24em] text-[#9b7a45]">{{ topic.eyebrow }}</p>
      <div class="grid gap-8 lg:grid-cols-[minmax(0,1fr)_300px] lg:items-start">
        <div>
          <h1 class="max-w-3xl text-3xl font-semibold leading-tight text-[#173247] sm:text-4xl">
            {{ topic.title }}
          </h1>
          <p class="mt-4 max-w-3xl text-base leading-8 text-[#5f6868]">{{ topic.summary }}</p>
          <div class="mt-6 flex flex-wrap gap-2">
            <span
              v-for="point in topic.keyPoints"
              :key="point"
              class="rounded-full border border-[#ded2c0] bg-[#fff8ec] px-3 py-1.5 text-xs font-semibold text-[#725b36]"
            >
              {{ point }}
            </span>
          </div>
        </div>

        <aside class="rounded-md border border-[#eadfce] bg-[#f7f1e8] p-5">
          <h2 class="text-sm font-semibold text-[#233142]">{{ topic.game }}{{ ui.suffix }}</h2>
          <div class="mt-4 space-y-2">
            <router-link
              v-for="item in siblingTopics"
              :key="item.path"
              :to="`${prefix}${item.path}`"
              class="block rounded-md px-3 py-2 text-sm text-[#68706f] transition hover:bg-white hover:text-[#233142]"
            >
              {{ item.title }}
            </router-link>
          </div>
        </aside>
      </div>
    </section>

    <section class="grid gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
      <article class="rounded-md border border-[#e2d8ca] bg-[#fffdf8] p-6 sm:p-8">
        <div class="space-y-7">
          <section v-for="section in topic.sections" :key="section.heading">
            <h2 class="text-xl font-semibold text-[#1c3342]">{{ section.heading }}</h2>
            <p class="mt-3 text-[15px] leading-8 text-[#5f6868]">{{ section.body }}</p>
          </section>
        </div>

        <div class="mt-8 rounded-md border border-[#eadfce] bg-[#fffaf3] p-5">
          <h2 class="text-base font-semibold text-[#233142]">{{ ui.compliance }}</h2>
          <p class="mt-2 text-sm leading-7 text-[#6e7373]">{{ ui.complianceText }}</p>
        </div>
      </article>

      <aside class="space-y-6">
        <div class="rounded-md border border-[#e2d8ca] bg-[#fffdf8] p-5">
          <h2 class="text-base font-semibold text-[#1c3342]">{{ ui.related }}</h2>
          <div class="mt-4 space-y-2">
            <router-link
              v-for="lk in topic.related"
              :key="lk.path"
              :to="`${prefix}${lk.path}`"
              class="flex items-center justify-between rounded-md border border-[#eadfce] bg-[#fffaf3] px-3 py-2.5 text-sm text-[#5f6868] transition hover:border-[#d0b98f] hover:text-[#233142]"
            >
              <span>{{ lk.label }}</span>
              <span aria-hidden="true">›</span>
            </router-link>
          </div>
        </div>

        <div class="rounded-md border border-[#e2d8ca] bg-[#fffdf8] p-5">
          <h2 class="text-base font-semibold text-[#1c3342]">{{ ui.faq }}</h2>
          <div class="mt-4 space-y-4">
            <div v-for="item in topic.faq" :key="item.q">
              <h3 class="text-sm font-semibold text-[#233142]">{{ item.q }}</h3>
              <p class="mt-1 text-sm leading-6 text-[#6e7373]">{{ item.a }}</p>
            </div>
          </div>
        </div>
      </aside>
    </section>
  </div>
</template>
