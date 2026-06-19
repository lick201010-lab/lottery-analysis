<script setup>
import { computed } from "vue";
import { useSEO, faqPage, dataset } from "../composables/useSEO.js";
import { seoTopics, seoTopicList } from "../data/seoTopics.js";

const props = defineProps({
  topicKey: { type: String, required: true },
});

const topic = computed(() => seoTopics[props.topicKey]);

const articleJsonLd = computed(() => ({
  "@context": "https://schema.org",
  "@type": "Article",
  headline: topic.value.title,
  description: topic.value.description,
  inLanguage: "zh-CN",
  author: { "@type": "Organization", name: "弈彩 YiCai" },
  publisher: {
    "@type": "Organization",
    name: "弈彩 YiCai",
    logo: {
      "@type": "ImageObject",
      url: "https://yicai.ckl.hk/logo.png",
    },
  },
  mainEntityOfPage: `https://yicai.ckl.hk${topic.value.path}`,
}));

const jsonLdBlocks = [articleJsonLd.value, faqPage(topic.value.faq)];
if (topic.value.dataset) {
  jsonLdBlocks.push(
    dataset({
      name: topic.value.dataset.name,
      description: topic.value.dataset.description,
      path: topic.value.path,
      temporalCoverage: topic.value.dataset.temporalCoverage,
      variableMeasured: topic.value.dataset.variableMeasured,
    }),
  );
}

useSEO({
  title: topic.value.title,
  description: topic.value.description,
  path: topic.value.path,
  jsonLd: jsonLdBlocks,
});

const siblingTopics = computed(() =>
  seoTopicList.filter((item) => item.game === topic.value.game && item.path !== topic.value.path),
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
          <h2 class="text-sm font-semibold text-[#233142]">{{ topic.game }}专题</h2>
          <div class="mt-4 space-y-2">
            <router-link
              v-for="item in siblingTopics"
              :key="item.path"
              :to="item.path"
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
          <h2 class="text-base font-semibold text-[#233142]">合规说明</h2>
          <p class="mt-2 text-sm leading-7 text-[#6e7373]">
            本页内容仅供数据分析与娱乐参考。开奖结果具有随机性，历史数据不能保证未来结果；请以官方公告为准，理性娱乐。
          </p>
        </div>
      </article>

      <aside class="space-y-6">
        <div class="rounded-md border border-[#e2d8ca] bg-[#fffdf8] p-5">
          <h2 class="text-base font-semibold text-[#1c3342]">相关入口</h2>
          <div class="mt-4 space-y-2">
            <router-link
              v-for="link in topic.related"
              :key="link.path"
              :to="link.path"
              class="flex items-center justify-between rounded-md border border-[#eadfce] bg-[#fffaf3] px-3 py-2.5 text-sm text-[#5f6868] transition hover:border-[#d0b98f] hover:text-[#233142]"
            >
              <span>{{ link.label }}</span>
              <span aria-hidden="true">›</span>
            </router-link>
          </div>
        </div>

        <div class="rounded-md border border-[#e2d8ca] bg-[#fffdf8] p-5">
          <h2 class="text-base font-semibold text-[#1c3342]">常见问题</h2>
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
