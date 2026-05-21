<script setup>
import { useSEO, faqPage } from "../composables/useSEO.js";

const faqs = [
  {
    q: "双色球一注号码由哪些部分组成？",
    a: "双色球一注由6个红球和1个蓝球组成，红球范围为01-33，蓝球范围为01-16。",
  },
  {
    q: "六合彩正码和特别号码有什么区别？",
    a: "六合彩每期开出6个正码和1个特别号码，头奖只看6个正码，特别号码主要用于部分奖等条件。",
  },
  {
    q: "弈彩的数据适合做什么？",
    a: "弈彩用于查看历史开奖、号码频率、冷热遗漏和走势分布，所有内容仅供数据分析与娱乐参考。",
  },
  {
    q: "历史数据能保证未来结果吗？",
    a: "不能。彩票开奖具有随机性，历史数据只能帮助理解分布情况，不能保证未来结果。",
  },
  {
    q: "开奖时间以哪里为准？",
    a: "开奖时间与结果应以官方开奖公告为准，弈彩会尽量及时同步并整理展示。",
  },
];

useSEO({
  title: "双色球 & 六合彩玩法规则详解",
  description: "一文讲清双色球红蓝球玩法、六合彩 6+1 规则、各档奖项条件、开奖时间表与常见问答。",
  jsonLd: [faqPage(faqs)],
});
</script>

<template>
  <div class="ref-card p-8">
    <h1 class="text-2xl font-semibold text-[#1c3342] mb-4">玩法指南</h1>
    <div class="prose prose-sm text-[#5f6868] space-y-4">
      <h2 class="text-lg font-medium">双色球玩法</h2>
      <p>双色球每注投注号码由6个红色球号码和1个蓝色球号码组成。红色球号码从01-33中选择6个，蓝色球号码从01-16中选择1个。</p>
      <h2 class="text-lg font-medium">香港六合彩玩法</h2>
      <p>香港六合彩每注投注号码由6个正码和1个特别号码组成。正码从01-49中选择6个，特别号码从剩余号码中选择1个。</p>
      <h2 class="text-lg font-medium">奖项设置</h2>
      <p>根据选中号码的数量和中奖情况，分为头奖、二奖、三奖等多个奖项。具体奖金金额以当期开奖公告为准。</p>
      <h2 class="text-lg font-medium">常见问答</h2>
      <div class="space-y-3">
        <div v-for="item in faqs" :key="item.q">
          <p class="font-medium text-[#233142]">{{ item.q }}</p>
          <p>{{ item.a }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
