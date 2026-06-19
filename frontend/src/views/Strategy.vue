<script setup>
import { useSEO, faqPage } from "../composables/useSEO.js";

const faq = [
  {
    q: "号码统计和冷热号能预测下一期吗？",
    a: "不能。号码统计、冷热号、遗漏和走势都是对历史开奖样本的描述，开奖结果具有随机性，历史数据不能预测或保证未来结果。",
  },
  {
    q: "遗漏值越大是不是越容易开出？",
    a: "不是。遗漏只表示某号码距离上次出现间隔了多少期，间隔长短不会改变下一期的开奖概率。",
  },
  {
    q: "这些数据分析能作为参与建议吗？",
    a: "不能。本页所有指标仅用于理解历史数据分布，不构成任何参与建议。请理性娱乐。",
  },
];

useSEO({
  title: "数据分析方法说明",
  description:
    "介绍冷热号、遗漏、连号、区间分布、走势等数据分析指标的含义与边界。所有指标仅供数据分析与娱乐参考，不构成建议。",
  jsonLd: [faqPage(faq)],
});
</script>

<template>
  <div class="ref-card p-8">
    <h1 class="text-2xl font-semibold text-[#1c3342] mb-4">数据分析方法</h1>
    <div class="prose prose-sm text-[#5f6868] space-y-4">
      <p>
        弈彩的所有分析指标都建立在一个前提上：<strong>彩票开奖是随机事件，历史数据只能帮助理解分布，不能预测或保证未来结果</strong>。下列方法仅用于复盘和理解历史开奖，<strong>不构成任何参与建议</strong>。
      </p>
      <h2 class="text-lg font-medium">常见的分析指标</h2>
      <ul class="list-disc pl-6 space-y-2">
        <li><strong>冷热号：</strong>统计各号码在历史开奖中的出现频率。热号是近期或长期出现较多的号码，冷号反之；过去表现不代表未来结果。</li>
        <li><strong>遗漏：</strong>记录某号码距离上次出现间隔了多少期。遗漏只反映历史间隔，不会改变下一期的开奖概率。</li>
        <li><strong>走势：</strong>把历次开奖号码按期排列观察分布变化。走势图是历史数据的可视化，不是结果走向的指示。</li>
        <li><strong>连号统计：</strong>记录历史中连号出现的频率和模式。</li>
        <li><strong>区间分布：</strong>将号码分成多个区间，观察开奖号码在各区间的分布情况。</li>
        <li><strong>奇偶比例：</strong>统计开奖号码中奇数和偶数的比例分布。</li>
      </ul>
      <h2 class="text-lg font-medium">如何正确理解这些指标</h2>
      <p>
        以上指标都是对<strong>已发生</strong>开奖结果的统计描述，适合用于查询、复盘和理解号码分布，不能用来判断或预测下一期开奖。任何单期开奖都可能与历史分布不同。
      </p>
      <p class="text-[#c85d5a]">所有分析仅供数据分析与娱乐参考，请勿沉迷。理性娱乐，保持在自己的承受范围内。</p>
    </div>

    <section class="mt-8 rounded-lg border border-[#e2d9cc] bg-[#fffaf2]/70 p-5">
      <h2 class="text-lg font-medium text-[#1c3342]">常见问题</h2>
      <div class="mt-3 space-y-4">
        <div v-for="item in faq" :key="item.q">
          <h3 class="text-sm font-semibold text-[#233142]">{{ item.q }}</h3>
          <p class="mt-1 text-sm leading-6 text-[#6e7373]">{{ item.a }}</p>
        </div>
      </div>
    </section>
  </div>
</template>
