<script setup>
import { computed } from "vue";
import { useSEO, faqPage } from "../composables/useSEO.js";
import { useI18n } from "../i18n.js";

const { t, lang } = useI18n();

const faqs = [
  {
    q: "彩票可以当作投资吗？",
    a: "不可以。彩票应被视为娱乐消费，不应被当作投资、收入来源或财务计划。",
  },
  {
    q: "怎样判断自己需要暂停？",
    a: "如果购买彩票影响生活预算、工作休息或情绪状态，就应立即暂停并寻求家人或专业机构帮助。",
  },
  {
    q: "使用数据分析工具要注意什么？",
    a: "数据分析只能帮助理解历史分布，不能保证未来结果，应始终保持娱乐心态。",
  },
  {
    q: "未成年人可以使用弈彩吗？",
    a: "不可以。访问和使用本网站代表用户已年满18周岁，并理解彩票相关风险。",
  },
];
const localFaqs = computed(() => faqs.map((f) => ({ q: t(f.q), a: t(f.a) })));

useSEO({
  title: computed(() => t("理性娱乐指南")),
  description: computed(() =>
    t("彩票是娱乐不是投资。识别问题性赌博的信号，了解负责任的娱乐原则与求助渠道。"),
  ),
  lang,
  hreflangBase: "/responsible",
  hasEn: true,
  jsonLd: computed(() => [faqPage(localFaqs.value)]),
});
</script>

<template>
  <div class="ref-card p-8">
    <h1 class="text-2xl font-semibold text-[#1c3342] mb-4">{{ t("理性娱乐") }}</h1>
    <div class="prose prose-sm text-[#5f6868] space-y-4">
      <div class="bg-[#fef9f0] border border-[#e8dcc8] rounded-lg p-4 mb-6">
        <p class="font-medium text-[#c5443f]">{{ t("重要提示") }}</p>
        <p class="mt-2">{{ t("彩票是一种娱乐方式，而非赚钱手段。请务必理性娱乐，切勿沉迷。") }}</p>
      </div>

      <h2 class="text-lg font-medium">{{ t("健康娱乐原则") }}</h2>
      <ul class="list-disc pl-6 space-y-2">
        <li v-html="t('<strong>设定预算：</strong>只为娱乐目的而参与，绝不动用必要的生活费用。')"></li>
        <li v-html="t('<strong>控制时间：</strong>不要让彩票影响您的正常工作和生活。')"></li>
        <li v-html="t('<strong>接受输赢：</strong>把投注视为娱乐消费，中奖是惊喜，不中亦属正常。')"></li>
        <li v-html="t('<strong>拒绝借贷：</strong>绝不借钱参与，不影响正常家庭财务。')"></li>
        <li v-html="t('<strong>及时求助：</strong>如发现自己有投注问题，请及时寻求专业帮助。')"></li>
      </ul>

      <h2 class="text-lg font-medium mt-6">{{ t("常见问题") }}</h2>
      <div class="space-y-3">
        <div v-for="item in localFaqs" :key="item.q">
          <p><strong>Q: {{ item.q }}</strong></p>
          <p>A: {{ item.a }}</p>
        </div>
      </div>

      <div class="mt-6 p-4 bg-[#f5f5f5] rounded text-xs text-[#7d867f]">
        <p>{{ t("如需帮助，请联系当地心理健康服务热线或相关戒赌机构。") }}</p>
      </div>
    </div>
  </div>
</template>
