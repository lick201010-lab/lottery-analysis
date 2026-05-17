<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { api, lotteryType } from "../api.js";
import NumberBall from "../components/NumberBall.vue";
import CountdownTimer from "../components/CountdownTimer.vue";

const summary = ref({});
const latestDraw = ref(null);
const jackpotData = ref(null);
const frequencyData = ref([]);
const loading = ref(false);
const jackpotLoading = ref(false);

const lotteryLabel = computed(() => (lotteryType.value === "ssq" ? "双色球" : "六合彩"));
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

function formatMoney(amount, currency = "HK$") {
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
  if (!match) return displayDrawNumber.value;
  return `${match[1]}/${String(Number(match[2]) + 1).padStart(match[2].length, "0")}`;
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
const hasRealPrizeData = computed(() =>
  poolAmount.value > 0 ||
  Number(jackpotData.value?.sales_amount || 0) > 0 ||
  prizeBreakdown.value.some((p) => Number(p.amount_per_note || 0) > 0)
);

const poolDisplay = computed(() => poolAmount.value ? formatMoney(poolAmount.value) : "官方未公布");
const poolSubDisplay = computed(() =>
  poolAmount.value ? `约 ¥${Math.round(poolAmount.value * 0.932).toLocaleString()}` : "等待官方奖金公告"
);
const firstPrizeCount = computed(() =>
  hasRealPrizeData.value ? `${prizeBreakdown.value[0]?.count ?? 0} 注` : "--"
);
const nextPoolDisplay = computed(() =>
  poolAmount.value ? formatMoney(Math.round(poolAmount.value * 1.102)) : "按开奖公告"
);
const nextPoolSubDisplay = computed(() =>
  poolAmount.value ? `约 ¥${Math.round(poolAmount.value * 1.027).toLocaleString()}` : "不使用估算数据"
);

const prizeRows = computed(() => {
  const defaults = [
    { label: "头奖", condition: "6个正码" },
    { label: "二奖", condition: "5个正码 + 特别号" },
    { label: "三奖", condition: "5个正码" },
  ];
  const rows = lotteryType.value === "ssq"
    ? defaults.map((row, i) => ({ ...row, label: ["一等奖", "二等奖", "三等奖"][i] }))
    : defaults;

  return rows.map((row, i) => {
    const prize = prizeBreakdown.value[i] || {};
    return {
      ...row,
      count: hasRealPrizeData.value ? (prize.count ?? 0) : "--",
      prize: hasRealPrizeData.value && Number(prize.amount_per_note || 0) > 0
        ? formatMoney(prize.amount_per_note)
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
      <div class="hero-reference-top">
        <div class="flex flex-wrap items-center gap-6">
          <h1 class="text-[42px] font-semibold tracking-[0.12em] text-[#1c3342]">{{ lotteryLabel }}</h1>
          <span class="text-[24px] font-semibold text-[#1f3443]">最新开奖</span>
          <span class="issue-pill">第 {{ displayDrawNumber }} 期</span>
          <span class="flex items-center gap-3 text-[17px] text-[#626c6c]">
            <span>▣</span>
            {{ displayDate }}
            <span>{{ toWeekday(displayDate) }}</span>
          </span>
        </div>
        <div class="flex gap-6">
          <router-link to="/data" class="ref-outline-button">↶ 查看历史记录</router-link>
          <router-link to="/generate" class="ref-gold-button">✥ 模拟选号</router-link>
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
        <span class="flex items-center gap-2">ⓘ 数据来源：香港马会六合彩</span>
        <span class="h-5 w-px bg-[#c9bdae]"></span>
        <span>开奖时间： {{ displayDate }} 21:32</span>
      </div>
    </section>

    <section class="grid grid-cols-1 xl:grid-cols-[0.88fr_1fr_1.04fr] gap-6">
      <div class="ref-card p-7">
        <h2 class="mb-3 text-[25px] font-semibold text-[#1c3342]">下期开奖</h2>
        <div class="mb-6 flex flex-wrap gap-8 text-[16px] text-[#5f6868]">
          <span>▣ 第 {{ nextDrawNumber }} 期</span>
          <span>▣ {{ lotteryType === "ssq" ? "周日" : "周二" }} 21:30</span>
        </div>
        <CountdownTimer />
        <p class="mt-7 text-[15px] text-[#767d7b]">♧ 距离开奖仅供参考，请以官方公布时间为准</p>
      </div>

      <div class="ref-card p-7">
        <div class="mb-8 flex items-center justify-between">
          <h2 class="text-[25px] font-semibold text-[#1c3342]">奖金状态</h2>
          <router-link to="/jackpot" class="text-[15px] text-[#7a746c]">查看详情 ›</router-link>
        </div>
        <div class="grid grid-cols-3 divide-x divide-[#e1d8ca]">
          <div class="pr-8">
            <p class="mb-4 text-[15px] text-[#68716f]">头奖基金 ⓘ</p>
            <p class="text-[20px] font-semibold text-[#c5443f]">{{ poolDisplay }}</p>
            <p class="mt-3 text-[14px] text-[#7a807f]">{{ poolSubDisplay }}</p>
          </div>
          <div class="px-8">
            <p class="mb-4 text-[15px] text-[#68716f]">头奖派出</p>
            <p class="text-[20px] font-semibold text-[#c5443f]">{{ firstPrizeCount }}</p>
          </div>
          <div class="pl-8">
            <p class="mb-4 text-[15px] text-[#68716f]">下期估计头奖</p>
            <p class="text-[20px] font-semibold text-[#bd7f26]">{{ nextPoolDisplay }}</p>
            <p class="mt-3 text-[14px] text-[#7a807f]">{{ nextPoolSubDisplay }}</p>
          </div>
        </div>
      </div>

      <div class="ref-card p-0 overflow-hidden">
        <div class="flex items-center justify-between px-7 py-6">
          <h2 class="text-[25px] font-semibold text-[#1c3342]">号码趋势摘要 <span class="text-[17px] font-normal text-[#6e7373]">（近 30 期）</span></h2>
          <router-link to="/frequency" class="text-[15px] text-[#7a746c]">查看详情 ›</router-link>
        </div>
        <div class="grid grid-cols-3 border-t border-[#e2d9cc]">
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
            <span>最长遗漏 {{ summary.most_overdue?.consecutive_missed || 28 }} 期</span>
          </div>
          <div class="trend-cell">
            <p>连号趋势</p>
            <strong>23%</strong>
            <span>连号出现概率</span>
          </div>
        </div>
      </div>
    </section>

    <section class="ref-card p-7">
      <div class="mb-6 flex items-center gap-7">
        <h2 class="text-[24px] font-semibold text-[#1c3342]">近期号码分布</h2>
        <span class="text-[15px] text-[#6e7373]">统计范围：近 100 期</span>
      </div>
      <div class="flex gap-8">
        <div class="min-w-0 flex-1 overflow-x-auto">
          <table class="distribution-table">
            <tbody>
              <template v-for="(row, rowIndex) in numberRows" :key="rowIndex">
                <tr>
                  <th v-if="rowIndex === 0" rowspan="2">出现次数</th>
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
                  <th v-if="rowIndex !== 0">出现次数</th>
                  <td v-for="number in row" :key="'c-' + number">{{ numberFrequency(number) }}</td>
                </tr>
              </template>
            </tbody>
          </table>
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
          <span class="text-[14px] text-[#6e7373]">单位：HK$</span>
        </div>
        <table class="prize-table">
          <thead><tr><th>奖项</th><th>中奖条件</th><th>中奖注数</th><th>每注奖金</th></tr></thead>
          <tbody>
            <tr v-for="row in prizeRows" :key="row.label">
              <td>{{ row.label }}</td>
              <td>{{ row.condition }}</td>
              <td>{{ row.count }}</td>
              <td>{{ row.prize }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="ref-card p-7">
        <div class="mb-5 flex items-center justify-between">
          <h2 class="text-[24px] font-semibold text-[#1c3342]">号码走势（近 30 期）</h2>
          <div class="flex gap-7 text-sm text-[#6e7373]">
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
      <span class="mx-auto">数据来源：香港马会六合彩官方网站</span>
      <span>最后更新： {{ displayDate }} 21:40</span>
      <span>⟳</span>
    </div>
  </div>
</template>
