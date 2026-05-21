<script setup>
import { useSEO } from "../composables/useSEO.js";

useSEO({
  title: "走势分析专题文章",
  description: "深度文章：连号现象、区间分布、和值统计等走势特征的统计学解读。基于历史数据的科普内容。",
});
</script>

<template>
  <div class="ref-card p-8">
    <h1 class="text-2xl font-semibold text-[#1c3342] mb-4">模式分析文章</h1>
    <div class="prose prose-sm text-[#5f6868] space-y-4">
      <article>
        <h2 class="text-lg font-medium mb-2">号码出现频率分析</h2>
        <p>在彩票分析中，我们通常会统计每个号码在历史开奖中的出现频率。高频率号码被称为"热号"，低频率号码被称为"冷号"。然而，由于开奖的随机性，热号未必会在未来继续频繁出现，冷号也未必会继续保持低频率。</p>
      </article>
      <article>
        <h2 class="text-lg font-medium mb-2">连号现象研究</h2>
        <p>连号是指开奖号码中存在两个或以上连续的数字。通过分析历史数据，我们可以统计连号出现的概率。但需要注意的是，每一次开奖都是独立事件，历史数据不能预测未来结果。</p>
      </article>
      <article>
        <h2 class="text-lg font-medium mb-2">区间分布规律</h2>
        <p>将号码池划分为多个区间（如低区、中区、高区），统计开奖号码在各区间的分布情况。这种方法可以帮助我们了解号码的分散程度，但不能用于预测具体的开奖号码。</p>
      </article>
    </div>
  </div>
</template>