<script setup>
import { useSEO } from "../composables/useSEO.js";

useSEO({
  title: "隐私政策",
  description: "弈彩 YiCai 的数据收集范围、Cookie 使用、第三方分析与广告（Google AdSense）说明、用户权利与联系方式。",
});
</script>

<template>
  <div class="ref-card p-8">
    <h1 class="text-2xl font-semibold text-[#1c3342] mb-4">隐私政策</h1>
    <div class="prose prose-sm text-[#5f6868] space-y-4">
      <p>我们非常重视您的个人信息和隐私保护。</p>
      <p><strong>信息收集：</strong>我们仅收集您主动提供的信息，用于改善用户体验。我们不会收集您的财务信息或敏感个人信息。</p>
      <p><strong>Cookie使用：</strong>我们使用Cookie来记住您的偏好设置，如彩种选择等。</p>
      <p><strong>第三方服务：</strong>我们使用 Google Analytics 等第三方分析服务来改进网站功能。</p>
      <p>
        <strong>广告与第三方 Cookie：</strong>本站使用 Google AdSense 等第三方广告服务。Google 及其合作伙伴会使用 Cookie，根据您过去对本站及其他网站的访问向您展示广告。您可以通过
        <a href="https://www.google.com/settings/ads" target="_blank" rel="noopener" class="text-[#9d6d3a] underline">Google 广告设置</a>
        管理或停用个性化广告，或访问
        <a href="https://www.aboutads.info" target="_blank" rel="noopener" class="text-[#9d6d3a] underline">www.aboutads.info</a>
        退出第三方供应商的 Cookie。面向欧洲（EEA/英国）用户，本站提供 Cookie 同意选项（Consent Management Platform）。
      </p>
      <p><strong>数据安全：</strong>我们采取合理的安全措施保护您的数据。</p>
      <p>如有任何问题，请联系我们。</p>
    </div>
  </div>
</template>