<script setup>
import { useSEO } from "../composables/useSEO.js";

useSEO({
  title: "数据分析方法说明",
  description: "介绍冷热号、遗漏、连号、区间分布等数据分析指标的含义与使用方法。仅供数据分析与娱乐参考。",
});
</script>

<template>
  <div class="ref-card p-8">
    <h1 class="text-2xl font-semibold text-[#1c3342] mb-4">数据分析方法</h1>
    <div class="prose prose-sm text-[#5f6868] space-y-4">
      <p>请记住，彩票开奖是随机事件，历史数据只能帮助理解分布，不能保证未来结果。</p>
      <h2 class="text-lg font-medium">常见的分析思路</h2>
      <ul class="list-disc pl-6 space-y-2">
        <li><strong>冷热号分析：</strong>统计历史开奖中各号码的出现频率，但过去的表现不代表未来结果。</li>
        <li><strong>连号统计：</strong>记录历史中连号出现的频率和模式。</li>
        <li><strong>区间分布：</strong>将号码分成多个区间，分析开奖号码在各个区间的分布情况。</li>
        <li><strong>奇偶比例：</strong>统计开奖号码中奇数和偶数的比例分布。</li>
      </ul>
      <p class="text-[#c85d5a]">以上分析仅供参考，请勿沉迷。理性娱乐，保持在自己的承受范围内。</p>
    </div>
  </div>
</template>
