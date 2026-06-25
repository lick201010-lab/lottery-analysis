<script setup>
import { computed } from "vue";
import { useSEO } from "../composables/useSEO.js";
import { useI18n } from "../i18n.js";

const { t, lang } = useI18n();

useSEO({
  title: computed(() => t("隐私政策")),
  description: computed(() =>
    t("弈彩 YiCai 的数据收集范围、Cookie 使用、第三方分析与广告（Google AdSense）说明、用户权利与联系方式。"),
  ),
  lang,
  hreflangBase: "/privacy",
  hasEn: true,
});
</script>

<template>
  <div class="ref-card p-8">
    <h1 class="text-2xl font-semibold text-[#1c3342] mb-4">{{ t("隐私政策") }}</h1>
    <div class="prose prose-sm text-[#5f6868] space-y-4">
      <p>{{ t("我们非常重视您的个人信息和隐私保护。") }}</p>
      <p v-html="t('<strong>信息收集：</strong>我们仅收集您主动提供的信息，用于改善用户体验。我们不会收集您的财务信息或敏感个人信息。')"></p>
      <p v-html="t('<strong>Cookie使用：</strong>我们使用Cookie来记住您的偏好设置，如彩种选择等。')"></p>
      <p v-html="t('<strong>第三方服务：</strong>我们使用 Google Analytics 等第三方分析服务来改进网站功能。')"></p>
      <p>
        <strong>{{ t("广告与第三方 Cookie：") }}</strong>{{ t("本站使用 Google AdSense 等第三方广告服务。Google 及其合作伙伴会使用 Cookie，根据您过去对本站及其他网站的访问向您展示广告。您可以通过") }}
        <a href="https://www.google.com/settings/ads" target="_blank" rel="noopener" class="text-[#9d6d3a] underline">{{ t("Google 广告设置") }}</a>
        {{ t("管理或停用个性化广告，或访问") }}
        <a href="https://www.aboutads.info" target="_blank" rel="noopener" class="text-[#9d6d3a] underline">www.aboutads.info</a>
        {{ t("退出第三方供应商的 Cookie。面向欧洲（EEA/英国）用户，本站提供 Cookie 同意选项（Consent Management Platform）。") }}
      </p>
      <p v-html="t('<strong>数据安全：</strong>我们采取合理的安全措施保护您的数据。')"></p>
      <p>{{ t("如有任何问题，请联系我们。") }}</p>
    </div>
  </div>
</template>
