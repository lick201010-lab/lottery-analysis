<script setup>
import { ref, computed } from "vue";
import { lotteryType } from "../api.js";
import { useSEO, faqPage } from "../composables/useSEO.js";
import { useI18n } from "../i18n.js";

const { t, lang } = useI18n();

const faqs = [
  {
    q: "中奖概率是什么意思？",
    a: "中奖概率是按号码组合总数计算出的理论比例，用于理解不同奖项的难度。",
  },
  {
    q: "双色球一等奖概率是多少？",
    a: "双色球一等奖需要6个红球和1个蓝球全部相符，理论概率约为1/177,210,888。",
  },
  {
    q: "六合彩头奖概率是多少？",
    a: "六合彩头奖需要6个正码全部相符，理论概率约为1/13,983,816。",
  },
  {
    q: "号码频率会改变单注概率吗？",
    a: "不会。频率统计反映历史分布，单期开奖仍是随机事件，单注理论概率不因历史频率而改变。",
  },
  {
    q: "概率表可以用于什么场景？",
    a: "概率表适合理解奖项难度与规则差异，仅供数据分析与娱乐参考。",
  },
];
const localFaqs = computed(() => faqs.map((f) => ({ q: t(f.q), a: t(f.a) })));

useSEO({
  title: computed(() => t("双色球 & 六合彩中奖概率详解")),
  description: computed(() =>
    t("详细计算各档奖项的中奖概率：双色球一等奖 1772 万分之一，二、三等奖详细说明。"),
  ),
  lang,
  hreflangBase: "/odds",
  hasEn: true,
  jsonLd: computed(() => [faqPage(localFaqs.value)]),
});

const oddsData = {
  ssq: [
    { level: "一等奖", condition: "6红+1蓝", probability: "1/177,210,888", odds: "约500万-1000万" },
    { level: "二等奖", condition: "6红", probability: "1/11,688,053", odds: "约10万-100万" },
    { level: "三等奖", condition: "5红+1蓝", probability: "1/789,648", odds: "约3,000" },
    { level: "四等奖", condition: "5红 或 4红+1蓝", probability: "1/22,075", odds: "约200" },
    { level: "五等奖", condition: "4红", probability: "1/1,083", odds: "约10" },
    { level: "六等奖", condition: "2红+1蓝", probability: "1/672", odds: "约5" },
  ],
  lw6: [
    { level: "头奖", condition: "6个正码全中", probability: "1/13,983,816", odds: "彩池决定" },
    { level: "二奖", condition: "5个正码+特别号", probability: "1/2,330,636", odds: "彩池决定" },
    { level: "三奖", condition: "5个正码", probability: "1/55,491", odds: "约HK$10,000" },
    { level: "四奖", condition: "4个正码+特别号", probability: "1/22,197", odds: "约HK$640" },
    { level: "五奖", condition: "4个正码", probability: "1/1,083", odds: "约HK$320" },
    { level: "六奖", condition: "3个正码+特别号", probability: "1/812", odds: "约HK$130" },
    { level: "七奖", condition: "3个正码", probability: "1/81", odds: "约HK$30" },
  ],
  qxc: [
    { level: "一等奖", condition: "前区 6 位 + 后区全中", probability: "以官方公告为准", odds: "浮动奖金" },
    { level: "二等奖", condition: "前区 6 位全中", probability: "以官方公告为准", odds: "浮动奖金" },
    { level: "三等奖", condition: "前区任意 5 位 + 后区", probability: "以官方公告为准", odds: "固定或浮动奖金" },
    { level: "四等奖", condition: "前区任意 5 位", probability: "以官方公告为准", odds: "以官方公告为准" },
    { level: "五等奖", condition: "按官方规则匹配", probability: "以官方公告为准", odds: "以官方公告为准" },
    { level: "六等奖", condition: "按官方规则匹配", probability: "以官方公告为准", odds: "以官方公告为准" },
  ],
};

const currentOdds = computed(() => oddsData[lotteryType.value] || oddsData.lw6);
const lotteryName = computed(() =>
  lotteryType.value === "ssq" ? "双色球" : lotteryType.value === "qxc" ? "7星彩" : "香港六合彩",
);
</script>

<template>
  <div class="ref-card p-8">
    <h1 class="text-2xl font-semibold text-[#1c3342] mb-2">{{ t("中奖概率说明") }}</h1>
    <p class="text-sm text-[#7a807f] mb-6">{{ t("{name}各奖项的中奖条件与概率", { name: t(lotteryName) }) }}</p>

    <div class="overflow-x-auto">
      <table class="prize-table whitespace-nowrap text-sm">
        <thead>
          <tr>
            <th class="px-3 text-left">{{ t("奖项") }}</th>
            <th class="px-3 text-left">{{ t("中奖条件") }}</th>
            <th class="px-3 text-left">{{ t("概率") }}</th>
            <th class="px-3 text-left">{{ t("奖金") }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in currentOdds" :key="row.level">
            <td class="px-3 font-medium">{{ t(row.level) }}</td>
            <td class="px-3 text-[#8a9393]">{{ t(row.condition) }}</td>
            <td class="px-3 text-[#c5443f]">{{ t(row.probability) }}</td>
            <td class="px-3">{{ t(row.odds) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <p class="mt-6 text-xs text-[#7d867f] border-t border-[#e2d9cc] pt-4">
      {{ t("注：中奖概率为理论值，实际奖金由奖池金额和中奖注数决定。请理性娱乐，切勿沉迷。") }}
    </p>

    <section class="mt-8 border-t border-[#e2d9cc] pt-6">
      <h2 class="mb-4 text-lg font-medium text-[#1c3342]">{{ t("常见问答") }}</h2>
      <div class="space-y-4 text-sm text-[#5f6868]">
        <div v-for="item in localFaqs" :key="item.q">
          <p class="font-medium text-[#233142]">{{ item.q }}</p>
          <p class="mt-1 leading-6">{{ item.a }}</p>
        </div>
      </div>
    </section>
  </div>
</template>
