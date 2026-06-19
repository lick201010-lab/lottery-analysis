<script setup>
import { useSEO } from "../composables/useSEO.js";
import NewsletterSignup from "../components/NewsletterSignup.vue";

const organizationJsonLd = {
  "@context": "https://schema.org",
  "@type": "Organization",
  name: "弈彩 YiCai",
  alternateName: "YiCai Lottery Data",
  url: "https://yicai.ckl.hk",
  logo: "https://yicai.ckl.hk/logo.png",
  email: "lick201010@gmail.com",
  description:
    "弈彩 YiCai 是一个彩票开奖数据统计平台，提供六合彩、双色球、7星彩的历史开奖记录、号码频率、冷热遗漏与走势分析，内容仅供数据分析与娱乐参考。",
  knowsAbout: ["彩票开奖数据", "历史开奖记录", "号码频率统计", "走势分析"],
};

useSEO({
  title: "关于弈彩 YiCai - 彩票开奖数据统计平台",
  description:
    "弈彩 YiCai 是彩票开奖数据统计平台，介绍平台定位、各彩种数据来源、更新机制与合规免责说明。",
  jsonLd: [organizationJsonLd],
});
</script>

<template>
  <div class="ref-card p-8">
    <h1 class="text-2xl font-semibold text-[#1c3342] mb-4">关于弈彩 YiCai</h1>
    <div class="prose prose-sm text-[#5f6868] space-y-3">
      <p>
        <strong>弈彩（YiCai）是一个彩票开奖数据统计平台</strong>，专注于开奖数据整理、历史记录、号码统计与走势分析。
      </p>
      <p>
        我们为用户提供清晰的号码分布、频率统计、冷热遗漏与走势分析等数据服务，帮助用户理解开奖数据的历史分布。弈彩仅提供数据整理与统计分析，<strong>不参与任何投注经营，也不提供任何投注或购彩渠道</strong>。
      </p>
    </div>

    <section class="mt-8 rounded-lg border border-[#e2d9cc] bg-[#fffaf2]/70 p-5">
      <h2 class="text-lg font-medium text-[#1c3342]">数据来源</h2>
      <p class="mt-2 text-sm leading-6 text-[#5f6868]">
        各彩种数据均整理自公开开奖资料；若与官方公告存在差异，请以官方公告为准：
      </p>
      <ul class="mt-3 space-y-2 text-sm leading-6 text-[#5f6868]">
        <li><strong>六合彩：</strong>参考香港赛马会公开开奖资料（lottery.hk）整理。</li>
        <li><strong>双色球：</strong>参考中国福利彩票开奖公告（500.com）整理。</li>
        <li><strong>7星彩：</strong>参考中国体育彩票开奖公告（500.com）整理。</li>
      </ul>
    </section>

    <section class="mt-6 rounded-lg border border-[#e2d9cc] bg-[#fffaf2]/70 p-5">
      <h2 class="text-lg font-medium text-[#1c3342]">更新机制</h2>
      <p class="mt-2 text-sm leading-6 text-[#5f6868]">
        数据通常在每期开奖后同步整理。开奖时间因彩种而异（六合彩每周二、四、六；双色球每周二、四、日；7星彩每周二、五、日），具体更新时间受官方公告发布时间与数据同步状态影响。
      </p>
    </section>

    <section class="mt-6 rounded-lg border border-[#e2d9cc] bg-[#fffaf2]/70 p-5">
      <h2 class="text-lg font-medium text-[#1c3342]">免责声明</h2>
      <p class="mt-2 text-sm leading-6 text-[#5f6868]">
        本平台所有内容仅供数据分析与娱乐参考。开奖结果具有随机性，历史数据不能保证或预示未来结果；号码统计、冷热、遗漏与走势分析均不构成任何参与建议。请理性娱乐，并以官方公告为准。
      </p>
    </section>

    <section class="mt-6 rounded-lg border border-[#e2d9cc] bg-[#fffaf2]/70 p-5">
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
