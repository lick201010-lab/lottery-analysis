<script setup>
import { useSEO } from "../composables/useSEO.js";
import NewsletterSignup from "../components/NewsletterSignup.vue";

useSEO({
  title: "关于弈彩 - 数据来源与团队",
  description: "弈彩 YiCai 的项目定位、数据来源（lottery.hk、500.com）、更新机制与联系方式。",
});
</script>

<template>
  <div class="ref-card p-8">
    <h1 class="text-2xl font-semibold text-[#1c3342] mb-4">关于我们</h1>
    <div class="prose prose-sm text-[#5f6868]">
      <p>弈彩（YiCai）是一款专注于开奖数据整理、历史统计与趋势分析的工具平台。</p>
      <p>我们致力于为用户提供清晰的号码分布图、频率统计、走势分析等数据服务，帮助用户更好地理解彩票开奖分布。</p>
      <p>本平台所有数据均来自香港马会官方网站，开奖结果公开透明。我们仅提供数据整理服务，不参与任何投注经营。</p>
    </div>

    <section class="mt-8 rounded-lg border border-[#e2d9cc] bg-[#fffaf2]/70 p-5">
      <h2 class="text-lg font-medium text-[#1c3342]">订阅数据更新</h2>
      <p class="mt-2 text-sm leading-6 text-[#5f6868]">
        接收开奖数据更新与统计摘要，内容仅供数据分析与娱乐参考。
      </p>
      <div class="mt-4">
        <NewsletterSignup input-id="newsletter-email-about" />
      </div>
    </section>
  </div>
</template>
