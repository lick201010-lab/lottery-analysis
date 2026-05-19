<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { api, lotteryType } from "../api.js";
import { getLotteryMeta } from "../lotteryMeta.js";
import DashboardHero from "../components/DashboardHero.vue";
import DashboardNextDrawCard from "../components/DashboardNextDrawCard.vue";
import DashboardPrizeStatusCard from "../components/DashboardPrizeStatusCard.vue";
import DashboardTrendSummaryCard from "../components/DashboardTrendSummaryCard.vue";
import DashboardDistributionCard from "../components/DashboardDistributionCard.vue";
import DashboardPrizeTableCard from "../components/DashboardPrizeTableCard.vue";
import DashboardTrendGuideCard from "../components/DashboardTrendGuideCard.vue";
import DashboardStatusBar from "../components/DashboardStatusBar.vue";

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
const specialNumber = computed(() => activeDraw.value?.special_num ?? null);
const displayDrawNumber = computed(() => activeDraw.value?.draw_number || "--");
const displayDate = computed(() => activeDraw.value?.draw_date || "--");
const weekdayLabel = computed(() => toWeekday(displayDate.value));

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

const hotSupport = computed(() => {
  if (summary.value.top_hot?.length) {
    const counts = summary.value.top_hot.slice(0, 3).map((item) => item.total_appearances);
    const high = Math.max(...counts);
    const low = Math.min(...counts);
    return `出现 ${high} - ${low} 次`;
  }
  return "以近期开奖为参考";
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
const firstPrizeLabel = computed(() => "头奖派出");
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

const chartZones = computed(() => {
  if (lotteryType.value === "ssq") {
    return [
      { label: "一区 (01-11)", color: "text-[#c85d5a]" },
      { label: "二区 (12-22)", color: "text-[#5d826e]" },
      { label: "三区 (23-33)", color: "text-[#5d7d9f]" },
    ];
  }
  return [
    { label: "一区 (01-11)", color: "text-[#c85d5a]" },
    { label: "二区 (12-22)", color: "text-[#5d826e]" },
    { label: "三区 (23-33)", color: "text-[#5d7d9f]" },
    { label: "四区 (34-49)", color: "text-[#91a0aa]" },
  ];
});

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
  ].map((row, index) => {
    const prize = prizeBreakdown.value[index] || {};
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
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }

  try {
    jackpotData.value = await api.jackpotLatest();
  } catch (error) {
    console.error("jackpot fetch failed:", error);
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
    <DashboardHero
      :lottery-label="lotteryLabel"
      :display-draw-number="displayDrawNumber"
      :display-date="displayDate"
      :weekday-label="weekdayLabel"
      :draw-numbers="drawNumbers"
      :special-number="specialNumber"
      :lottery-type="lotteryType"
      :draw-source-text="drawSourceText"
      :display-draw-time="displayDrawTime"
    />

    <section class="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-[0.88fr_1fr_1.04fr]">
      <DashboardNextDrawCard
        :next-draw-number="nextDrawNumber"
        :draw-week-label="drawWeekLabel"
        :display-draw-time="displayDrawTime"
      />

      <DashboardPrizeStatusCard
        :pool-card-label="poolCardLabel"
        :pool-display="poolDisplay"
        :pool-sub-display="poolSubDisplay"
        :first-prize-label="firstPrizeLabel"
        :first-prize-count="firstPrizeCount"
        :next-pool-label="nextPoolLabel"
        :next-pool-display="nextPoolDisplay"
        :next-pool-sub-display="nextPoolSubDisplay"
      />

      <DashboardTrendSummaryCard
        :hot-numbers="hotNumbers"
        :hot-support="hotSupport"
        :cold-numbers="coldNumbers"
        :cold-support="trendSupport"
        :trend-headline="trendHeadline"
        :consecutive-headline="consecutiveHeadline"
        :consecutive-summary="consecutiveSummary"
        :lottery-type="lotteryType"
      />
    </section>

    <DashboardDistributionCard
      :number-rows="numberRows"
      :draw-number-set="drawNumberSet"
      :special-number="specialNumber"
      :number-frequency="numberFrequency"
      :count-tone="countTone"
    />

    <section class="grid grid-cols-1 gap-6 pb-16 lg:grid-cols-[0.92fr_1.48fr]">
      <DashboardPrizeTableCard :prize-unit="meta.prizeUnit" :prize-rows="prizeRows" />
      <DashboardTrendGuideCard :chart-zones="chartZones" />
    </section>

    <DashboardStatusBar
      :status-source-text="statusSourceText"
      :display-date="displayDate"
      :display-draw-time="displayDrawTime"
    />

    <div class="adsense-container mt-8 py-6 text-center">
      <div class="ad-placeholder inline-block h-[90px] w-full max-w-[728px] items-center justify-center rounded-lg border border-[#e2d9cc] bg-[#f5f1ea] flex">
        <span class="text-sm text-[#7d867f]">广告位 (AdSense)</span>
      </div>
    </div>
  </div>
</template>
