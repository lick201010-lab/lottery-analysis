<script setup>
import { computed } from "vue";
import { useSEO } from "../composables/useSEO.js";
import { useI18n } from "../i18n.js";

const { t, lang } = useI18n();

const advertisingPrivacyCopy = computed(() => {
  if (lang.value === "en") {
    return "YiCai only permits contextual, non-personalized advertising on lottery-data pages. We keep ad personalization and advertising user-data signals disabled, including after cookie consent, and do not use visits to lottery pages to build an advertising profile. Google and its partners may still use cookies for ad delivery, security, fraud prevention, frequency capping, and aggregated measurement where consent and local law permit.";
  }
  if (lang.value === "tw") {
    return "弈彩在彩票數據頁面僅允許情境式、非個人化廣告。即使你同意 Cookie，我們仍會關閉廣告個人化及廣告使用者資料訊號，不會根據你瀏覽彩票頁面的行為建立廣告興趣檔案。Google 及其合作夥伴仍可能在取得同意且符合當地法律的前提下，使用 Cookie 完成廣告投放、安全防護、反詐欺、頻次控制與匯總成效衡量。";
  }
  return "弈彩在彩票数据页面仅允许情境式、非个性化广告。即使你同意 Cookie，我们仍会关闭广告个性化及广告用户数据信号，不会根据你浏览彩票页面的行为建立广告兴趣档案。Google 及其合作伙伴仍可能在取得同意且符合当地法律的前提下，使用 Cookie 完成广告投放、安全防护、反欺诈、频次控制与汇总成效衡量。";
});

const advertisingSettingsIntro = computed(() => {
  if (lang.value === "en") return "You can review your preferences in ";
  if (lang.value === "tw") return "你可以前往";
  return "你可以前往";
});

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
        <strong>{{ t("广告与第三方 Cookie：") }}</strong>{{ advertisingPrivacyCopy }}
        {{ advertisingSettingsIntro }}
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
