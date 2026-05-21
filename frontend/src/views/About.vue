<script setup>
import { useSEO } from "../composables/useSEO.js";

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
      <p>我们致力于为用户提供清晰的号码分布图、频率统计、走势分析等数据服务，帮助用户更好地理解彩票开奖规律。</p>
      <p>本平台所有数据均来自香港马会官方网站，开奖结果公开透明。我们仅提供数据整理服务，不参与任何投注经营。</p>
    </div>
  </div>
</template>