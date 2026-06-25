<script setup>
import { ref, computed } from "vue";
import { lotteryType } from "../api.js";
import { getLotteryMeta } from "../lotteryMeta.js";
import { useSEO, faqPage } from "../composables/useSEO.js";
import { useI18n } from "../i18n.js";

const { t, lang } = useI18n();

const faqs = [
  {
    q: "双色球中奖奖金需要缴税吗？",
    a: "中国内地彩票单注中奖金额超过规定门槛时通常需要缴纳个人所得税，页面计算仅作规则理解参考。",
  },
  {
    q: "香港六合彩奖金是否需要缴税？",
    a: "香港六合彩奖金通常按香港本地规则处理，本页面以免税口径展示，实际以官方与当地规定为准。",
  },
  {
    q: "页面里的奖金金额一定准确吗？",
    a: "奖金会受奖池、中奖注数和官方公告影响，弈彩展示的计算结果仅供数据分析与娱乐参考。",
  },
  {
    q: "税后金额怎么计算？",
    a: "税后金额按输入金额扣除对应税率后估算，用于帮助理解不同彩票规则下的金额差异。",
  },
];
const localFaqs = computed(() => faqs.map((f) => ({ q: t(f.q), a: t(f.a) })));

useSEO({
  title: computed(() => t("双色球 & 六合彩奖金税务计算器")),
  description: computed(() =>
    t("输入中奖金额查看税后到手数额。双色球 20% 个税，香港六合彩免税，含各档奖项金额详解。"),
  ),
  lang,
  hreflangBase: "/jackpot",
  hasEn: true,
  jsonLd: computed(() => [faqPage(localFaqs.value)]),
});

const inputAmount = ref(10000000);

const meta = computed(() => getLotteryMeta(lotteryType.value));
const lotteryLabel = computed(() => meta.value.label);

const taxRules = computed(() => {
  if (lotteryType.value === "ssq" || lotteryType.value === "qxc") {
    return {
      name: meta.value.label,
      currency: meta.value.currencyName,
      taxRate: 0.2,
      taxName: "个人所得税",
      taxNote: meta.value.taxNote,
      exempt: false,
    };
  }

  return {
    name: "六合彩",
    currency: meta.value.currencyName,
    taxRate: 0,
    taxName: "无税费",
    taxNote: meta.value.taxNote,
    exempt: true,
  };
});

const breakdown = computed(() => {
  const amount = Number(inputAmount.value) || 0;
  const taxAmount = amount * taxRules.value.taxRate;
  const netAmount = amount - taxAmount;

  return {
    gross: amount,
    tax: taxAmount,
    net: netAmount,
    taxRateDisplay: `${(taxRules.value.taxRate * 100).toFixed(0)}%`,
  };
});

function formatMoney(value) {
  if (lang.value === "en") {
    if (value >= 1e9) return `${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `${(value / 1e6).toFixed(2)}M`;
    if (value >= 1e3) return `${(value / 1e3).toFixed(2)}K`;
    return value.toLocaleString();
  }
  if (value >= 100000000) return `${(value / 100000000).toFixed(2)} ${t("亿")}`;
  if (value >= 10000) return `${(value / 10000).toFixed(2)} ${t("万")}`;
  return value.toLocaleString();
}

const keepRatio = computed(() => (breakdown.value.gross ? (breakdown.value.net / breakdown.value.gross) * 100 : 0));
const taxRatio = computed(() => (breakdown.value.gross ? (breakdown.value.tax / breakdown.value.gross) * 100 : 0));
</script>

<template>
  <div class="space-y-8 animate-fade-in-up">
    <section class="hero-panel p-6 sm:p-8">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div class="max-w-2xl">
          <p class="text-sm font-medium tracking-[0.18em] text-[#8d6f47]">PAYOUT ESTIMATE</p>
          <h1 class="mt-2 text-3xl font-semibold text-[#233142] sm:text-4xl">{{ t("奖金分析") }}</h1>
          <p class="mt-3 text-base leading-7 text-[#66706b]">
            {{ t("输入假设中奖金额，查看 {label} 在当前规则下的大致到手金额与税费拆解。", { label: t(lotteryLabel) }) }}
          </p>
        </div>
        <div class="rounded-lg border border-[#ddd4c7] bg-[#fffaf2] px-4 py-3 text-sm text-[#6c7570]">
          {{ t(taxRules.taxNote) }}
        </div>
      </div>
    </section>

    <section class="card-stripe p-6 sm:p-8">
      <div class="grid grid-cols-1 gap-6 md:grid-cols-3">
        <div>
          <label class="mb-2 block text-sm font-semibold tracking-[0.08em] text-[#6c7570]">{{ t("假设中奖金额") }}</label>
          <div class="relative">
            <span class="absolute left-4 top-1/2 -translate-y-1/2 text-[#7d867f]">{{ t(taxRules.currency) }}</span>
            <input
              v-model.number="inputAmount"
              type="number"
              class="w-full rounded-lg border border-[#ddd4c7] bg-[#faf7f0] py-3 pl-16 pr-4 text-lg font-semibold text-[#233142] tabular"
              :placeholder="t('输入金额')"
            />
          </div>
        </div>

        <div>
          <label class="mb-2 block text-sm font-semibold tracking-[0.08em] text-[#6c7570]">{{ t("彩种") }}</label>
          <div class="flex items-center gap-3 rounded-lg border border-[#ddd4c7] bg-[#faf7f0] px-4 py-3">
            <span
              class="h-3 w-3 rounded-full"
              :class="lotteryType === 'ssq' ? 'bg-[#5f768f]' : lotteryType === 'qxc' ? 'bg-[#c5943f]' : 'bg-[#b96d63]'"
            ></span>
            <span class="font-semibold text-[#233142]">{{ t(lotteryLabel) }}</span>
          </div>
        </div>

        <div>
          <label class="mb-2 block text-sm font-semibold tracking-[0.08em] text-[#6c7570]">{{ t("税务规则") }}</label>
          <div class="rounded-lg border border-[#ddd4c7] bg-[#faf7f0] px-4 py-3">
            <span class="text-sm font-semibold text-[#233142]">{{ t(taxRules.taxName) }}</span>
            <span v-if="taxRules.exempt" class="ml-2 text-xs font-semibold text-[#71897d]">{{ t("免税") }}</span>
            <span v-else class="ml-2 text-xs font-semibold text-[#b96d63]">{{ breakdown.taxRateDisplay }}</span>
          </div>
        </div>
      </div>
    </section>

    <section class="card-stripe p-6 sm:p-8">
      <h2 class="mb-5 text-[22px] font-semibold text-[#233142]">{{ t("到手金额拆解") }}</h2>
      <div class="overflow-x-auto">
        <table class="w-full text-[15px]">
          <tbody class="divide-y divide-[#e3d9cb]">
            <tr>
              <td class="py-4 pr-4 text-[#6f7772]">{{ t("税前金额") }}</td>
              <td class="py-4 text-right text-lg font-semibold text-[#233142] tabular">
                {{ formatMoney(breakdown.gross) }} {{ t(taxRules.currency) }}
              </td>
            </tr>
            <tr v-if="!taxRules.exempt">
              <td class="py-4 pr-4 text-[#6f7772]">
                {{ t(taxRules.taxName) }} <span class="text-xs text-[#b96d63]">-{{ breakdown.taxRateDisplay }}</span>
              </td>
              <td class="py-4 text-right text-lg font-semibold text-[#b96d63] tabular">
                -{{ formatMoney(breakdown.tax) }} {{ t(taxRules.currency) }}
              </td>
            </tr>
            <tr v-else>
              <td class="py-4 pr-4 text-[#6f7772]">{{ t(taxRules.taxName) }}</td>
              <td class="py-4 text-right text-lg font-semibold text-[#71897d] tabular">0 {{ t(taxRules.currency) }}</td>
            </tr>
            <tr class="bg-[#faf7f0]">
              <td class="py-5 pr-4 font-semibold text-[#233142]">{{ t("最终到手") }}</td>
              <td class="py-5 text-right text-2xl font-semibold text-[#8d6f47] tabular">
                {{ formatMoney(breakdown.net) }} {{ t(taxRules.currency) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="card-stripe p-6 sm:p-8">
      <h2 class="mb-5 text-[22px] font-semibold text-[#233142]">{{ t("金额占比") }}</h2>
      <div class="overflow-hidden rounded-xl border border-[#ddd4c7] bg-[#f3ede3]">
        <div class="flex h-12">
          <div
            class="flex h-full items-center justify-center bg-[#8d6f47] text-sm font-semibold text-white transition-all duration-500"
            :style="{ width: `${keepRatio}%` }"
          >
            {{ t("到手") }} {{ keepRatio.toFixed(0) }}%
          </div>
          <div
            v-if="breakdown.tax > 0"
            class="flex h-full items-center justify-center bg-[#b96d63] text-sm font-semibold text-white transition-all duration-500"
            :style="{ width: `${taxRatio}%` }"
          >
            {{ t("税费") }} {{ taxRatio.toFixed(0) }}%
          </div>
        </div>
      </div>

      <div class="mt-4 flex flex-wrap items-center gap-6 text-sm text-[#6f7772]">
        <div class="flex items-center gap-2">
          <span class="h-3 w-3 rounded-full bg-[#8d6f47]"></span>
          <span>{{ t("到手金额") }}</span>
        </div>
        <div v-if="breakdown.tax > 0" class="flex items-center gap-2">
          <span class="h-3 w-3 rounded-full bg-[#b96d63]"></span>
          <span>{{ t("税费") }}</span>
        </div>
      </div>
    </section>

    <section class="ref-card p-6 sm:p-8">
      <h2 class="text-xl font-semibold text-[#233142]">{{ t("奖金税务常见问答") }}</h2>
      <div class="mt-5 grid gap-4 md:grid-cols-2">
        <div v-for="item in localFaqs" :key="item.q" class="rounded-lg border border-[#e2d9cc] bg-[#fffaf2]/70 p-4">
          <p class="font-medium text-[#233142]">{{ item.q }}</p>
          <p class="mt-2 text-sm leading-6 text-[#66706b]">{{ item.a }}</p>
        </div>
      </div>
    </section>

    <p class="text-center text-sm text-[#6f7772]">
      {{ t("免责声明：奖金分析仅供参考，实际税率与规则以当地主管机构公布信息为准。") }}
    </p>
  </div>
</template>
