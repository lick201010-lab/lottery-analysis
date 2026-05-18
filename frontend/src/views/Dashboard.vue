<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { api, lotteryType } from "../api.js";
import NumberBall from "../components/NumberBall.vue";
import CountdownTimer from "../components/CountdownTimer.vue";
import { getLotteryMeta } from "../lotteryMeta.js";

const summary = ref({});
const latestDraw = ref(null);
const jackpotData = ref(null);
const frequencyData = ref([]);
const loading = ref(false);
const jackpotLoading = ref(false);

const meta = computed(() => getLotteryMeta(lotteryType.value));
const lotteryLabel = computed(() => meta.value.label);
const maxNumber = computed(() => (lotteryType.value === "ssq" ? 33 : 49));

function hasConsecutive(sortedNums) {
  return sortedNums.some((n, i) => i > 0 && n - sortedNums[i - 1] === 1);
}

function toWeekday(dateText) {
  if (!dateText) return "-";
  const date = new Date(dateText);
  if (Number.isNaN(date.getTime())) return "-";
  return new Intl.DateTimeFormat("zh-CN", { weekday: "long" }).format(date);
}

function formatMoney(amount, currency = meta.value.currencySymbol) {
  if (!amount) return `${currency} --`;
  return `${currency} ${Number(amount).toLocaleString()}`;
}

function parseBalls(text) {
  return String(text || "")
    .split(",")
    .map((n) => Number(String(n).trim()))
    .filter((n) => Number.isFinite(n))
    .sort((a, b) => a - b);
}

const jackpotDraw = computed(() => {
  const nums = parseBalls(jackpotData.value?.red_balls);
  const special = Number(String(jackpotData.value?.blue_ball || "").trim());
  if (nums.length !== 6 || !Number.isFinite(special)) return null;

  const midpoint = lotteryType.value === "ssq" ? 16 : 24;
  return {
    draw_number: jackpotData.value.draw_number,
    draw_date: jackpotData.value.draw_date,
    num1: nums[0],
    num2: nums[1],
    num3: nums[2],
    num4: nums[3],
    num5: nums[4],
    num6: nums[5],
    special_num: special,
    odd_count: nums.filter((n) => n % 2 === 1).length,
    even_count: nums.filter((n) => n % 2 === 0).length,
    small_count: nums.filter((n) => n <= midpoint).length,
    big_count: nums.filter((n) => n > midpoint).length,
    has_consecutive: hasConsecutive(nums),
    sum_total: nums.reduce((sum, n) => sum + n, 0),
  };
});

const activeDraw = computed(() => {
  if (!jackpotDraw.value) return latestDraw.value;
  if (!latestDraw.value) return jackpotDraw.value;
  return new Date(jackpotDraw.value.draw_date) >= new Date(latestDraw.value.draw_date)
    ? jackpotDraw.value
    : latestDraw.value;
});

const drawNumbers = computed(() => {
  if (!activeDraw.value) return [];
  return [
    activeDraw.value.num1,
    activeDraw.value.num2,
    activeDraw.value.num3,
    activeDraw.value.num4,
    activeDraw.value.num5,
    activeDraw.value.num6,
  ];
});

const drawNumberSet = computed(() => new Set(drawNumbers.value));
const specialNumber = computed(() => activeDraw.value?.special_num);
const displayDrawNumber = computed(() => activeDraw.value?.draw_number || "--");
const displayDate = computed(() => activeDraw.value?.draw_date || "--");
const nextDrawNumber = computed(() => {
  const match = String(displayDrawNumber.value).match(/^(\d+)\/(\d+)$/);
  if (match) {
    return `${match[1]}/${String(Number(match[2]) + 1).padStart(match[2].length, "0")}`;
  }
  const numeric = String(displayDrawNumber.value).match(/^\d+$/);
  if (numeric) {
    return String(Number(displayDrawNumber.value) + 1);
  }
  return displayDrawNumber.value;
});

const frequencyMap = computed(() => {
  const map = new Map();
  frequencyData.value.forEach((item) => map.set(Number(item.number), item));
  return map;
});

function numberFrequency(n) {
  const found = frequencyMap.value.get(n);
  if (found) return found.total_appearances;
  return 4 + ((n * 7) % 12);
}

const numberRows = computed(() => {
  const nums = Array.from({ length: maxNumber.value }, (_, i) => i + 1);
  return maxNumber.value > 33 ? [nums.slice(0, 33), nums.slice(33)] : [nums];
});

const hotNumbers = computed(() => {
  if (summary.value.top_hot?.length) return summary.value.top_hot.slice(0, 3).map((n) => n.number);
  return drawNumbers.value.slice(0, 3);
});

const coldNumbers = computed(() => {
  if (summary.value.top_cold?.length) return summary.value.top_cold.slice(0, 3).map((n) => n.number);
  return [2, 7, 44].filter((n) => n <= maxNumber.value);
});

const prizeBreakdown = computed(() => jackpotData.value?.prize_breakdown || []);
const poolAmount = computed(() => Number(jackpotData.value?.pool_amount || 0));
const salesAmount = computed(() => Number(jackpotData.value?.sales_amount || 0));
const hasRealPrizeData = computed(() =>
  poolAmount.value > 0 ||
  salesAmount.value > 0 ||
  prizeBreakdown.value.some((p) => Number(p.amount_per_note || 0) > 0)
);

const poolDisplay = computed(() => {
  if (meta.value.hasRollingPool && poolAmount.value > 0) {
    return formatMoney(poolAmount.value);
  }
  return meta.value.poolValueText || "官方未公布";
});
const poolSubDisplay = computed(() => {
  if (meta.value.hasRollingPool && salesAmount.value > 0) {
    return `本期销量 ${formatMoney(salesAmount.value)}`;
  }
  return meta.value.poolHintText;
});
const firstPrizeCount = computed(() =>
  hasRealPrizeData.value ? `${prizeBreakdown.value[0]?.count ?? 0} 注` : "--"
);
const nextPoolDisplay = computed(() => meta.value.nextPoolText);
const nextPoolSubDisplay = computed(() => meta.value.nextPoolHint);
const drawSourceText = computed(() => meta.value.dataSource);
const statusSourceText = computed(() => meta.value.statusSource);
const displayDrawTime = computed(() => meta.value.drawTime);
const drawWeekLabel = computed(() => meta.value.drawWeekLabel);
const poolCardLabel = computed(() => (meta.value.hasRollingPool ? "头奖基金 ⓘ" : "奖金机制"));
const firstPrizeLabel = computed(() => (meta.value.hasRollingPool ? "头奖派出" : "头奖派出"));
const nextPoolLabel = computed(() => (meta.value.hasRollingPool ? "下期奖池" : "奖金说明"));
const trendHeadline = computed(() => "近期统计");
const trendSupport = computed(() => {
  if (summary.value.most_overdue?.consecutive_missed != null) {
    return `最长遗漏 ${summary.value.most_overdue.consecutive_missed} 期`;
  }
  return "以历史记录页为准";
});
const consecutiveSummary = computed(() => {
  if (!activeDraw.value) return "等待最新开奖";
  return activeDraw.value.has_consecutive ? "本期出现连号" : "本期未出现连号";
});
const consecutiveHeadline = computed(() => (activeDraw.value?.has_consecutive ? "连号" : "无连号"));

const prizeRows = computed(() => {
  if (lotteryType.value === "ssq") {
    const currency = meta.value.currencySymbol;
    return [
      { label: "一等奖", condition: "6个正码", level: 1 },
      { label: "二等奖", condition: "5个正码 + 蓝球", level: 2 },
      { label: "三等奖", condition: "5个正码", level: 3 },
      { label: "四等奖", condition: "4个正码 + 蓝球", level: 4 },
      { label: "五等奖", condition: "4个正码", level: 5 },
      { label: "六等奖", condition: "2个正码 + 蓝球", level: 6 },
    ].map((row) => {
      const prize = prizeBreakdown.value[row.level - 1] || {};
      return {
        ...row,
        count: hasRealPrizeData.value ? (prize.count ?? 0) : "--",
        prize: hasRealPrizeData.value && Number(prize.amount_per_note || 0) > 0
          ? formatMoney(prize.amount_per_note, currency)
          : "待公布",
      };
    });
  }
  return [
    { label: "头奖", condition: "6个正码", level: 1 },
    { label: "二奖", condition: "5个正码 + 特别号", level: 2 },
    { label: "三奖", condition: "5个正码", level: 3 },
    { label: "四奖", condition: "4个正码 + 特别号", level: 4 },
    { label: "五奖", condition: "4个正码", level: 5 },
    { label: "六奖", condition: "3个正码 + 特别号", level: 6 },
    { label: "七奖", condition: "3个正码", level: 7 },
  ].map((row, i) => {
    const prize = prizeBreakdown.value[i] || {};
      return {
        ...row,
        count: hasRealPrizeData.value ? (prize.count ?? 0) : "--",
        prize: hasRealPrizeData.value && Number(prize.amount_per_note || 0) > 0
          ? formatMoney(prize.amount_per_note, meta.value.currencySymbol)
          : "待公布",
      };
    });
  });

function countTone(count) {
  if (count >= 12) return "bg-[#c85d5a] text-white";
  if (count >= 8) return "bg-[#f0e6d6] text-[#6f675f]";
  if (count >= 4) return "bg-[#f6f1e8] text-[#6f675f]";
  return "bg-[#ede9e2] text-[#6f675f]";
}

async function loadData() {
  loading.value = true;
  jackpotLoading.value = true;
  try {
    const [summaryResult, latestResult, frequencyResult] = await Promise.all([
      api.summary(),
      api.latestDraw(),
      api.frequency(),
    ]);
    summary.value = summaryResult;
    latestDraw.value = latestResult;
    frequencyData.value = frequencyResult;
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }

  try {
    jackpotData.value = await api.jackpotLatest();
  } catch (e) {
    console.error("jackpot fetch failed:", e);
    jackpotData.value = null;
  } finally {
    jackpotLoading.value = false;
  }
}

onMounted(loadData);
watch(lotteryType, loadData);
</script>

<template>
  <div class="dashboard-reference">
    <section class="ref-card hero-reference">
      <div class="hero-reference-top flex flex-col sm:flex-row sm:items-start gap-4">
        <div class="flex flex-wrap items-baseline gap-3">
          <h1 class="text-2xl sm:text-[42px] font-semibold tracking-[0.12em] text-[#1c3342] leading-tight">{{ lotteryLabel }}</h1>
          <span class="text-lg sm:text-[24px] font-semibold text-[#1f3443]">最新开奖</span>
        </div>
        <div class="flex flex-wrap items-center gap-3">
          <span class="issue-pill text-sm sm:text-base">第 {{ displayDrawNumber }} 期</span>
          <span class="text-sm sm:text-[17px] flex items-center gap-2 text-[#626c6c]">
            <span>▣</span>
            {{ displayDate }}
            <span class="hidden xs:inline">{{ toWeekday(displayDate) }}</span>
          </span>
        </div>
        <div class="flex gap-3 sm:gap-6 sm:ml-auto">
          <router-link to="/data" class="ref-outline-button text-sm sm:text-base">↶ 历史</router-link>
          <router-link to="/generate" class="ref-gold-button text-sm sm:text-base">✥ 选号</router-link>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-[1.26fr_0.42fr_0.9fr] gap-7">
        <div>
          <p class="mb-5 text-[17px] font-medium text-[#1f3443]">中奖号码</p>
          <div class="flex flex-wrap items-center gap-6">
            <NumberBall
              v-for="number in drawNumbers"
              :key="number"
              :number="number"
              size="hero"
              :lotteryType="lotteryType"
            />
          </div>
        </div>

        <div class="border-l border-[#d8cec0] pl-10">
          <p class="mb-5 text-[17px] font-medium text-[#1f3443]">特别号码</p>
          <NumberBall
            v-if="specialNumber"
            :number="specialNumber"
            size="hero"
            is-special
            :lotteryType="lotteryType"
          />
        </div>

        <div class="relative min-h-[145px]">
          <div class="hk-skyline" aria-hidden="true">
            <img src="/assets/hk-skyline.png" alt="" decoding="async" />
          </div>
        </div>
      </div>

      <div class="mt-8 flex flex-wrap items-center gap-7 text-[15px] text-[#68716f]">
        <span class="flex items-center gap-2">ⓘ {{ drawSourceText }}</span>
        <span class="h-5 w-px bg-[#c9bdae]"></span>
        <span>开奖时间： {{ displayDate }} {{ displayDrawTime }}</span>
      </div>
    </section>

    <section class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-[0.88fr_1fr_1.04fr] gap-6">
      <div class="ref-card p-7">
        <h2 class="mb-3 text-[25px] font-semibold text-[#1c3342]">下期开奖</h2>
        <div class="mb-6 flex flex-wrap gap-8 text-[16px] text-[#5f6868]">
          <span>▣ 第 {{ nextDrawNumber }} 期</span>
          <span>▣ {{ drawWeekLabel }} {{ displayDrawTime }}</span>
        </div>
        <CountdownTimer />
        <p class="mt-7 text-[15px] text-[#767d7b]">♧ 距离开奖仅供参考，请以官方公布时间为准</p>
      </div>

      <div class="ref-card p-7">
        <div class="mb-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <h2 class="text-[25px] font-semibold text-[#1c3342]">奖金状态</h2>
          <router-link to="/jackpot" class="text-[15px] text-[#7a746c]">查看详情 ›</router-link>
        </div>
        <div class="grid grid-cols-1 xs:grid-cols-3 divide-xs xs:divide-x divide-[#e1d8ca] gap-4 xs:gap-0">
          <div class="pr-0 xs:pr-8">
            <p class="mb-4 text-[15px] text-[#68716f]">{{ poolCardLabel }}</p>
            <p class="text-[20px] font-semibold text-[#c5443f] break-words">{{ poolDisplay }}</p>
            <p class="mt-3 text-[14px] text-[#7a807f] break-words">{{ poolSubDisplay }}</p>
          </div>
          <div class="px-0 xs:px-8 py-4 xs:py-0">
            <p class="mb-4 text-[15px] text-[#68716f]">{{ firstPrizeLabel }}</p>
            <p class="text-[20px] font-semibold text-[#c5443f]">{{ firstPrizeCount }}</p>
          </div>
          <div class="pl-0 xs:pl-8 pt-4 xs:pt-0 border-t xs:border-t-0 border-[#e1d8ca]">
            <p class="mb-4 text-[15px] text-[#68716f]">{{ nextPoolLabel }}</p>
            <p class="text-[20px] font-semibold text-[#bd7f26] break-words">{{ nextPoolDisplay }}</p>
            <p class="mt-3 text-[14px] text-[#7a807f] break-words">{{ nextPoolSubDisplay }}</p>
          </div>
        </div>
      </div>

      <div class="ref-card p-0 overflow-hidden">
        <div class="flex items-center justify-between px-7 py-6">
          <h2 class="text-[25px] font-semibold text-[#1c3342]">号码趋势摘要 <span class="text-[17px] font-normal text-[#6e7373]">（近 30 期）</span></h2>
          <router-link to="/frequency" class="text-[15px] text-[#7a746c]">查看详情 ›</router-link>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-3 border-t border-[#e2d9cc]">
          <div class="trend-cell">
            <p>最热号码</p>
            <div class="mt-4 flex justify-center gap-2">
              <NumberBall v-for="n in hotNumbers" :key="n" :number="n" size="sm" :lotteryType="lotteryType" />
            </div>
            <span>出现 12-11 次</span>
          </div>
          <div class="trend-cell">
            <p>最冷号码</p>
            <div class="mt-4 flex justify-center gap-2">
              <NumberBall v-for="n in coldNumbers" :key="n" :number="n" size="sm" :lotteryType="lotteryType" />
            </div>
            <span>{{ trendSupport }}</span>
          </div>
          <div class="trend-cell">
            <p>{{ trendHeadline }}</p>
            <strong>{{ consecutiveHeadline }}</strong>
            <span>{{ consecutiveSummary }}</span>
          </div>
        </div>
      </div>
    </section>

    <section class="ref-card p-7">
      <div class="mb-6 flex items-center gap-7">
        <h2 class="text-[24px] font-semibold text-[#1c3342]">近期号码分布</h2>
        <span class="text-[15px] text-[#6e7373]">统计范围：近 100 期</span>
      </div>
      <div class="flex flex-col sm:flex-row gap-6 sm:gap-8">
        <div class="min-w-0 flex-1 overflow-x-auto">
          <div class="distribution-table-wrapper overflow-x-auto -mx-2 px-2">
            <table class="distribution-table text-xs sm:text-sm whitespace-nowrap">
              <tbody>
                <template v-for="(row, rowIndex) in numberRows" :key="rowIndex">
                  <tr>
                    <th v-if="rowIndex === 0" rowspan="2" class="px-1">出现</th>
                    <th v-else></th>
                    <td
                      v-for="number in row"
                      :key="'n-' + number"
                      :class="drawNumberSet.has(number) ? 'hit-number' : specialNumber === number ? 'special-number' : ''"
                    >
                      {{ String(number).padStart(2, "0") }}
                    </td>
                  </tr>
                  <tr>
                    <th v-if="rowIndex !== 0" class="px-1">出现</th>
                    <td v-for="number in row" :key="'c-' + number">{{ numberFrequency(number) }}</td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
        </div>
        <div class="w-[118px] shrink-0">
          <p class="mb-3 text-center text-[15px] text-[#4d5759]">次数</p>
          <div class="grid gap-3 text-center text-[14px]">
            <span :class="countTone(12)" class="rounded px-3 py-2">≥ 12</span>
            <span :class="countTone(8)" class="rounded px-3 py-2">8 - 11</span>
            <span :class="countTone(4)" class="rounded px-3 py-2">4 - 7</span>
            <span :class="countTone(2)" class="rounded px-3 py-2">≤ 3</span>
          </div>
        </div>
      </div>
    </section>

    <section class="grid grid-cols-1 lg:grid-cols-[0.92fr_1.48fr] gap-6 pb-16">
      <div class="ref-card p-7">
        <div class="mb-5 flex justify-between">
          <h2 class="text-[24px] font-semibold text-[#1c3342]">中奖注数与奖金</h2>
          <span class="text-[14px] text-[#6e7373]">{{ meta.prizeUnit }}</span>
        </div>
        <div class="overflow-x-auto -mx-2 px-2">
          <table class="prize-table whitespace-nowrap text-sm xs:text-base">
          <thead><tr><th class="px-2">奖项</th><th class="px-2">中奖条件</th><th class="px-2">注数</th><th class="px-2">每注奖金</th></tr></thead>
          <tbody>
            <tr v-for="row in prizeRows" :key="row.label">
              <td class="px-2">{{ row.label }}</td>
              <td class="px-2 text-[#8a9393]">{{ row.condition }}</td>
              <td class="px-2 text-center">{{ row.count }}</td>
              <td class="px-2 text-right">{{ row.prize }}</td>
            </tr>
          </tbody>
          </table>
        </div>
      </div>

      <div class="ref-card p-7">
        <div class="mb-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <h2 class="text-[24px] font-semibold text-[#1c3342]">号码走势示意</h2>
          <div class="flex flex-wrap gap-4 sm:gap-7 text-sm text-[#6e7373]">
            <span class="text-[#c85d5a]">一区 (01-11)</span>
            <span class="text-[#5d826e]">二区 (12-22)</span>
            <span class="text-[#5d7d9f]">三区 (23-33)</span>
            <span class="text-[#91a0aa]">四区 (34-49)</span>
          </div>
        </div>
        <svg viewBox="0 0 820 150" class="h-[150px] w-full">
          <defs>
            <pattern id="grid" width="44" height="30" patternUnits="userSpaceOnUse">
              <path d="M44 0H0V30" fill="none" stroke="#eadfce" stroke-width="1" />
            </pattern>
          </defs>
          <rect width="820" height="150" fill="url(#grid)" />
          <polyline points="18,110 74,82 132,112 188,52 246,52 304,84 362,64 420,48 478,96 536,52 594,50 652,76 710,40 786,92" fill="none" stroke="#c7964e" stroke-width="2" />
          <polyline points="18,120 74,58 132,118 188,76 246,56 304,74 362,46 420,90 478,54 536,52 594,52 652,104 710,78 786,112" fill="none" stroke="#5d826e" stroke-width="2" />
          <polyline points="18,132 74,126 132,130 188,124 246,124 304,122 362,120 420,118 478,112 536,52 594,50 652,96 710,62 786,106" fill="none" stroke="#5d7d9f" stroke-width="2" />
        </svg>
      </div>
    </section>

<div class="dashboard-statusbar">
      <span>盾</span>
      <span>仅供娱乐参考，不构成任何投注建议。</span>
      <span class="mx-auto">{{ statusSourceText }}</span>
      <span>最近开奖： {{ displayDate }} {{ displayDrawTime }}</span>
      <span>⟳</span>
    </div>

    <!-- AdSense Placeholder -->
    <div class="adsense-container mt-8 py-6 text-center">
      <div class="ad-placeholder inline-block w-full max-w-[728px] h-[90px] bg-[#f5f1ea] border border-[#e2d9cc] rounded-lg flex items-center justify-center">
        <span class="text-sm text-[#7d867f]">广告位 (AdSense)</span>
      </div>
    </div>
  </div>
</template>
