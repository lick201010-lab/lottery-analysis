<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { api, lotteryType } from "../api.js";
import { getLotteryMeta } from "../lotteryMeta.js";
import { useSEO } from "../composables/useSEO.js";
import DashboardNextDrawCard from "../components/DashboardNextDrawCard.vue";
import DashboardPrizeStatusCard from "../components/DashboardPrizeStatusCard.vue";
import DashboardDistributionCard from "../components/DashboardDistributionCard.vue";
import DashboardPrizeTableCard from "../components/DashboardPrizeTableCard.vue";
import DashboardTrendGuideCard from "../components/DashboardTrendGuideCard.vue";
import DashboardStatusBar from "../components/DashboardStatusBar.vue";

useSEO({
  title: "弈彩 YiCai - 彩票开奖数据、号码统计与走势分析平台",
  description: "弈彩 YiCai 提供彩票开奖数据、历史开奖记录、号码频率、冷热遗漏、走势分析与模拟选号。数据每期更新，仅供数据分析与娱乐参考。",
});

const summary = ref({});
const latestDraw = ref(null);
const jackpotData = ref(null);
const frequencyData = ref([]);
const recentDraws = ref([]);
const loading = ref(false);
const jackpotLoading = ref(false);

const meta = computed(() => getLotteryMeta(lotteryType.value));
const lotteryLabel = computed(() => meta.value.label);
const maxNumber = computed(() => {
  if (lotteryType.value === "ssq") return 33;
  if (lotteryType.value === "qxc") return 14;
  return 49;
});

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

function parseBalls(text, shouldSort = true) {
  const values = String(text || "")
    .split(",")
    .map((n) => Number(String(n).trim()))
    .filter((n) => Number.isFinite(n));
  return shouldSort ? values.sort((a, b) => a - b) : values;
}

const jackpotDraw = computed(() => {
  const nums = parseBalls(jackpotData.value?.red_balls, lotteryType.value !== "qxc");
  const special = Number(String(jackpotData.value?.blue_ball ?? "").trim());
  if (nums.length !== 6 || !Number.isFinite(special)) return null;

  const midpoint = lotteryType.value === "ssq" ? 16 : lotteryType.value === "qxc" ? 4 : 24;
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

const numberStats = computed(() => {
  const start = lotteryType.value === "qxc" ? 0 : 1;
  const stats = Array.from({ length: maxNumber.value - start + 1 }, (_, i) => {
    const number = i + start;
    const found = frequencyMap.value.get(number);
    return {
      number,
      hasData: Boolean(found),
      total: Number(found?.total_appearances ?? 0),
      missed: Number(found?.consecutive_missed ?? 0),
      hotness: Number(found?.hotness_score ?? 0),
      isDrawn: drawNumberSet.value.has(number),
      isSpecial: specialNumber.value === number,
    };
  });

  const totals = stats.map((item) => item.total).sort((a, b) => a - b);
  const misses = stats.map((item) => item.missed).sort((a, b) => a - b);
  const hotThreshold = totals[Math.max(0, Math.floor(totals.length * 0.78))] || 0;
  const coldThreshold = misses[Math.max(0, Math.floor(misses.length * 0.72))] || 0;

  return stats.map((item) => {
    let tone = "neutral";
    if (item.isDrawn) tone = "hit";
    else if (item.isSpecial) tone = "special";
    else if (item.missed >= coldThreshold && item.missed > 0) tone = "cold";
    else if (item.total >= hotThreshold && item.total > 0) tone = "hot";

    return {
      ...item,
      tone,
      countLabel: item.hasData ? item.total : "--",
      missLabel: item.hasData ? (item.missed > 0 ? item.missed : "近出") : "--",
    };
  });
});

const hotNumbers = computed(() => {
  if (summary.value.top_hot?.length) return summary.value.top_hot.slice(0, 3).map((n) => n.number);
  return drawNumbers.value.slice(0, 3);
});

const coldNumbers = computed(() => {
  if (summary.value.top_cold?.length) return summary.value.top_cold.slice(0, 3).map((n) => n.number);
  return [2, 7, 44].filter((n) => n <= maxNumber.value);
});

const observationGroups = computed(() => {
  const stats = numberStats.value;
  const available = stats.filter((item) => item.hasData);
  const topHot = [...available].sort((a, b) => b.total - a.total || a.number - b.number).slice(0, 6);
  const topCold = [...available].sort((a, b) => b.missed - a.missed || a.number - b.number).slice(0, 6);
  const recovered = stats
    .filter((item) => item.hasData && (item.isDrawn || item.isSpecial))
    .sort((a, b) => b.missed - a.missed || a.number - b.number)
    .slice(0, 6);
  const active = [...available]
    .sort((a, b) => b.hotness - a.hotness || b.total - a.total || a.missed - b.missed)
    .slice(0, 6);

  return [
    { label: "热号 Top 6", hint: "近百期出现靠前", tone: "hot", numbers: topHot },
    { label: "冷号 Top 6", hint: "遗漏期数靠前", tone: "cold", numbers: topCold },
    { label: "回补观察", hint: "最新开奖命中", tone: "hit", numbers: recovered },
    { label: "连续活跃", hint: "综合热度较高", tone: "active", numbers: active },
  ];
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
  if (poolAmount.value > 0) {
    return formatMoney(poolAmount.value);
  }
  return meta.value.poolValueText || "官方未公布";
});

const poolSubDisplay = computed(() => {
  if (lotteryType.value === "marksix" && poolAmount.value > 0) {
    return "预计头奖基金 · lottery.hk 抓取";
  }
  if (salesAmount.value > 0) {
    return `本期销量 ${formatMoney(salesAmount.value)}`;
  }
  return meta.value.poolHintText;
});

const settlementStatus = computed(() => {
  if (jackpotLoading.value) {
    return {
      label: "抓取中",
      tone: "loading",
      description: "正在读取最新奖金与注数",
    };
  }
  if (hasRealPrizeData.value) {
    return {
      label: "已更新",
      tone: "ok",
      description: `${drawSourceText.value.replace("数据来源：", "")}`,
    };
  }
  return {
    label: "待公布",
    tone: "empty",
    description: "接口暂未返回真实奖金，先展示奖项规则",
  };
});

const settlementMetrics = computed(() => [
  { label: "期号", value: displayDrawNumber.value },
  { label: "开奖日期", value: displayDate.value },
  { label: meta.value.hasRollingPool ? "奖池" : "头奖", value: poolAmount.value > 0 ? formatMoney(poolAmount.value) : "--" },
  { label: "销售额", value: salesAmount.value > 0 ? formatMoney(salesAmount.value) : "--" },
]);

const nextPoolDisplay = computed(() => meta.value.nextPoolText);
const nextPoolSubDisplay = computed(() => meta.value.nextPoolHint);
const drawSourceText = computed(() => meta.value.dataSource);
const statusSourceText = computed(() => meta.value.statusSource);
const displayDrawTime = computed(() => meta.value.drawTime);
const drawWeekLabel = computed(() => meta.value.drawWeekLabel);
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
      { key: "zone1", label: "一区", range: "01-11", min: 1, max: 11, color: "#c85d5a", text: "text-[#c85d5a]" },
      { key: "zone2", label: "二区", range: "12-22", min: 12, max: 22, color: "#5d826e", text: "text-[#5d826e]" },
      { key: "zone3", label: "三区", range: "23-33", min: 23, max: 33, color: "#5d7d9f", text: "text-[#5d7d9f]" },
    ];
  }
  if (lotteryType.value === "qxc") {
    return [
      { label: "前区 (0-4)", color: "text-[#5d826e]" },
      { label: "前区 (5-9)", color: "text-[#5d7d9f]" },
      { label: "后区 (0-14)", color: "text-[#c7964e]" },
    ];
  }
  return [
    { key: "zone1", label: "一区", range: "01-11", min: 1, max: 11, color: "#c85d5a", text: "text-[#c85d5a]" },
    { key: "zone2", label: "二区", range: "12-22", min: 12, max: 22, color: "#5d826e", text: "text-[#5d826e]" },
    { key: "zone3", label: "三区", range: "23-33", min: 23, max: 33, color: "#5d7d9f", text: "text-[#5d7d9f]" },
    { key: "zone4", label: "四区", range: "34-49", min: 34, max: 49, color: "#91a0aa", text: "text-[#91a0aa]" },
  ];
});

function drawRegularNumbers(draw) {
  if (!draw) return [];
  return [draw.num1, draw.num2, draw.num3, draw.num4, draw.num5, draw.num6]
    .map((n) => Number(n))
    .filter((n) => Number.isFinite(n));
}

const zoneTrendBars = computed(() => {
  const draws = [...recentDraws.value].reverse().slice(-16);
  return draws.map((draw) => {
    const nums = drawRegularNumbers(draw);
    const segments = chartZones.value.map((zone) => {
      const count = nums.filter((n) => n >= zone.min && n <= zone.max).length;
      return {
        key: zone.key,
        label: zone.label,
        count,
        height: `${(count / 6) * 100}%`,
        color: zone.color,
      };
    });
    return {
      drawNumber: draw.draw_number,
      date: draw.draw_date,
      segments,
    };
  });
});

const zoneInsights = computed(() => {
  const totals = chartZones.value.map((zone) => {
    const count = recentDraws.value.reduce((sum, draw) => {
      return sum + drawRegularNumbers(draw).filter((n) => n >= zone.min && n <= zone.max).length;
    }, 0);
    return { ...zone, count };
  });
  if (!totals.length || !recentDraws.value.length) {
    return [
      { label: "等待数据", value: "暂无近期开奖" },
      { label: "分层参考", value: "10 → 8 → 6" },
    ];
  }

  const hotZone = [...totals].sort((a, b) => b.count - a.count)[0];
  const coldZone = [...totals].sort((a, b) => a.count - b.count)[0];
  const recentNums = recentDraws.value.flatMap(drawRegularNumbers);
  const midpoint = lotteryType.value === "ssq" ? 16 : 24;
  const bigCount = recentNums.filter((n) => n > midpoint).length;
  const smallCount = recentNums.length - bigCount;
  const structure = Math.abs(bigCount - smallCount) <= 4
    ? "结构均衡"
    : bigCount > smallCount
      ? "轻微偏大"
      : "轻微偏小";

  return [
    { label: `${hotZone.label}偏热`, value: `${hotZone.range} · ${hotZone.count} 次` },
    { label: `${coldZone.label}回补观察`, value: `${coldZone.range} · ${coldZone.count} 次` },
    { label: "大小结构", value: structure },
    { label: "分层选号参考", value: "10 → 8 → 6" },
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

  if (lotteryType.value === "qxc") {
    return [
      { label: "一等奖", condition: "前区 6 位 + 后区全中", level: 1 },
      { label: "二等奖", condition: "前区 6 位全中", level: 2 },
      { label: "三等奖", condition: "前区任意 5 位 + 后区", level: 3 },
      { label: "四等奖", condition: "前区任意 5 位", level: 4 },
      { label: "五等奖", condition: "按官方规则匹配", level: 5 },
      { label: "六等奖", condition: "按官方规则匹配", level: 6 },
    ].map((row) => {
      const prize = prizeBreakdown.value[row.level - 1] || {};
      return {
        ...row,
        count: hasRealPrizeData.value && Number(prize.count || 0) > 0 ? prize.count : "--",
        prize: hasRealPrizeData.value && Number(prize.amount_per_note || 0) > 0
          ? formatMoney(prize.amount_per_note, meta.value.currencySymbol)
          : "以官方公告为准",
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

async function loadData() {
  loading.value = true;
  jackpotLoading.value = true;

  try {
    const [summaryResult, latestResult, frequencyResult, recentResult] = await Promise.all([
      api.summary(),
      api.latestDraw(),
      api.frequency(),
      api.draws({ page: 1, per_page: 20 }),
    ]);
    summary.value = summaryResult;
    latestDraw.value = latestResult;
    frequencyData.value = frequencyResult;
    recentDraws.value = recentResult.draws || [];
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

    <DashboardPrizeStatusCard
      :lottery-label="lotteryLabel"
      :lottery-type="lotteryType"
      :display-draw-number="displayDrawNumber"
      :display-date="displayDate"
      :draw-numbers="drawNumbers"
      :special-number="specialNumber"
      :pool-display="poolDisplay"
      :pool-sub-display="poolSubDisplay"
      :next-pool-display="nextPoolDisplay"
      :next-pool-sub-display="nextPoolSubDisplay"
      :draw-source-text="drawSourceText"
      :display-draw-time="displayDrawTime"
      :has-rolling-pool="meta.hasRollingPool"
    />

    <div class="mt-6">
      <DashboardNextDrawCard
        :next-draw-number="nextDrawNumber"
        :draw-week-label="drawWeekLabel"
        :display-draw-time="displayDrawTime"
        :display-draw-number="displayDrawNumber"
        :pool-display="poolDisplay"
        :display-date="displayDate"
        :lottery-type="lotteryType"
      />
    </div>

    <div class="mt-6">
      <DashboardDistributionCard
        :number-stats="numberStats"
        :observation-groups="observationGroups"
        :lottery-type="lotteryType"
      />
    </div>

    <section class="mt-6 grid grid-cols-1 gap-6 pb-16 lg:grid-cols-[0.92fr_1.48fr]">
      <DashboardPrizeTableCard
        :prize-unit="meta.prizeUnit"
        :prize-rows="prizeRows"
        :settlement-status="settlementStatus"
        :settlement-metrics="settlementMetrics"
        :has-real-prize-data="hasRealPrizeData"
      />
      <DashboardTrendGuideCard
        :chart-zones="chartZones"
        :zone-trend-bars="zoneTrendBars"
        :zone-insights="zoneInsights"
      />
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
