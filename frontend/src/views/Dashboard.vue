<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { api, lotteryType } from "../api.js";
import NumberBall from "../components/NumberBall.vue";
import CountdownTimer from "../components/CountdownTimer.vue";

const summary = ref({});
const latestDraw = ref(null);
const jackpotData = ref(null);
const loading = ref(false);
const jackpotLoading = ref(false);

const lotteryLabel = computed(() => (lotteryType.value === "ssq" ? "双色球" : "六合彩"));
const mainRange = computed(() => (lotteryType.value === "ssq" ? "1-33" : "1-49"));
const specialRange = computed(() => (lotteryType.value === "ssq" ? "1-16" : "1-49"));

function hasConsecutive(sortedNums) {
  return sortedNums.some((n, i) => i > 0 && n - sortedNums[i - 1] === 1);
}

const jackpotDraw = computed(() => {
  if (!jackpotData.value?.red_balls || !jackpotData.value?.blue_ball) return null;
  const nums = String(jackpotData.value.red_balls)
    .split(",")
    .map((n) => Number(String(n).trim()))
    .filter((n) => Number.isFinite(n))
    .sort((a, b) => a - b);
  const special = Number(String(jackpotData.value.blue_ball).trim());
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
  ].filter((n) => n !== null && n !== undefined);
});

const displayJackpot = computed(() => {
  const drawLabel = jackpotData.value?.draw_number
    ? "第" + jackpotData.value.draw_number + "期"
    : "等待最新开奖";

  if (jackpotData.value && jackpotData.value.pool_amount) {
    const amt = jackpotData.value.pool_amount;
    if (amt >= 100000000) {
      return {
        amount: (amt / 100000000).toFixed(2),
        unit: "亿元",
        cashValue: (amt * 0.5 / 100000000).toFixed(2) + "亿元",
        nextDraw: drawLabel,
      };
    }
    return {
      amount: (amt / 10000).toFixed(0),
      unit: "万元",
      cashValue: (amt * 0.5 / 10000).toFixed(0) + "万元",
      nextDraw: drawLabel,
    };
  }

  if (lotteryType.value === "marksix" && jackpotData.value?.draw_number) {
    return { amount: "按开奖规则", unit: "", cashValue: "香港中奖免税", nextDraw: drawLabel };
  }

  if (lotteryType.value === "ssq") {
    return { amount: "12.8", unit: "亿元", cashValue: "6.4亿元", nextDraw: drawLabel };
  }

  return { amount: "按开奖规则", unit: "", cashValue: "香港中奖免税", nextDraw: drawLabel };
});

const prizeRules = computed(() => {
  if (lotteryType.value === "ssq") {
    return [
      { level: "一等奖", condition: "6红 + 1蓝", prize: "浮动（最高1000万）" },
      { level: "二等奖", condition: "6红 + 0蓝", prize: "浮动" },
      { level: "三等奖", condition: "5红 + 1蓝", prize: "3,000元" },
      { level: "四等奖", condition: "5红 + 0蓝 或 4红 + 1蓝", prize: "200元" },
      { level: "五等奖", condition: "4红 + 0蓝 或 3红 + 1蓝", prize: "10元" },
      { level: "六等奖", condition: "2红 + 1蓝 或 1红 + 1蓝 或 0红 + 1蓝", prize: "5元" },
    ];
  }

  return [
    { level: "头奖", condition: "6个正码", prize: "浮动（最低800万港币）" },
    { level: "二等奖", condition: "5个正码 + 特别号码", prize: "浮动" },
    { level: "三等奖", condition: "5个正码", prize: "浮动" },
    { level: "四等奖", condition: "4个正码 + 特别号码", prize: "9,600港币" },
    { level: "五等奖", condition: "4个正码", prize: "640港币" },
    { level: "六等奖", condition: "3个正码 + 特别号码", prize: "320港币" },
    { level: "七等奖", condition: "3个正码", prize: "40港币" },
  ];
});

const prizeBreakdown = computed(() => jackpotData.value?.prize_breakdown || []);

async function loadData() {
  loading.value = true;
  jackpotLoading.value = true;
  try {
    [summary.value, latestDraw.value] = await Promise.all([
      api.summary(),
      api.latestDraw(),
    ]);
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
  <div class="space-y-8 sm:space-y-10 animate-fade-in-up">
    <section class="hero-panel overflow-hidden">
      <div class="grid min-h-[500px] grid-cols-1 lg:grid-cols-[1.58fr_0.82fr]">
        <div class="flex flex-col justify-center p-7 sm:p-10 lg:p-14">
          <div class="eyebrow mb-3">{{ lotteryLabel }} 数据概览</div>
          <div class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h1 class="text-4xl sm:text-5xl lg:text-6xl font-semibold tracking-tight text-[#233142]">
                最新开奖
              </h1>
              <p v-if="activeDraw" class="mt-4 text-base sm:text-lg text-[#7d867f]">
                第 {{ activeDraw.draw_number }} 期 · {{ activeDraw.draw_date }}
              </p>
              <p v-else class="mt-3 text-sm sm:text-base text-[#7d867f]">正在读取最新数据...</p>
            </div>
            <div class="flex gap-2 sm:pb-1">
              <router-link class="btn-morandi-secondary" to="/data">历史记录</router-link>
              <router-link class="btn-morandi-primary" to="/generate">模拟选号</router-link>
            </div>
          </div>

          <div v-if="activeDraw" class="mt-10 flex flex-wrap items-center gap-4 sm:gap-5">
            <NumberBall
              v-for="number in drawNumbers"
              :key="number"
              :number="number"
              size="hero"
              :lotteryType="lotteryType"
            />
            <span class="px-1 text-3xl font-light text-[#b7aa99]">+</span>
            <NumberBall
              :number="activeDraw.special_num"
              size="hero"
              is-special
              :lotteryType="lotteryType"
            />
          </div>

          <div v-if="activeDraw" class="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div class="metric-tile">
              <span>奇偶比例</span>
              <strong>{{ activeDraw.odd_count }}:{{ activeDraw.even_count }}</strong>
            </div>
            <div class="metric-tile">
              <span>大小比例</span>
              <strong>{{ activeDraw.small_count }}:{{ activeDraw.big_count }}</strong>
            </div>
            <div class="metric-tile">
              <span>号码合计</span>
              <strong>{{ activeDraw.sum_total }}</strong>
            </div>
          </div>
        </div>

        <aside class="flex flex-col justify-center border-t border-[#ddd4c7] bg-[#efe6da] p-7 sm:p-10 lg:border-l lg:border-t-0">
          <div class="space-y-6">
            <div class="rounded-lg border border-[#d8cbbb] bg-[#fffdf8]/70 p-6 shadow-sm">
              <p class="text-xs font-semibold tracking-[0.22em] text-[#8d6f47] uppercase">Archive</p>
              <p class="mt-2 text-3xl font-semibold tabular text-[#233142]">
                {{ loading ? "..." : (summary.total_draws || 0).toLocaleString() }}
              </p>
              <p class="text-sm text-[#7d867f]">已收录历史期数</p>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div class="rounded-lg border border-[#d8cbbb] bg-[#fffdf8]/70 p-5">
                <p class="text-xs text-[#7d867f]">正码范围</p>
                <p class="mt-2 text-xl font-semibold text-[#233142]">{{ mainRange }}</p>
              </div>
              <div class="rounded-lg border border-[#d8cbbb] bg-[#fffdf8]/70 p-5">
                <p class="text-xs text-[#7d867f]">特别号</p>
                <p class="mt-2 text-xl font-semibold text-[#233142]">{{ specialRange }}</p>
              </div>
            </div>

            <div class="rounded-lg border border-[#d8cbbb] bg-[#fffdf8]/70 p-5">
              <p class="text-xs text-[#7d867f]">最新同步日期</p>
              <p class="mt-2 text-lg font-semibold text-[#233142]">
                {{ activeDraw?.draw_date || (loading ? "读取中" : (summary.latest_date || "-")) }}
              </p>
            </div>
          </div>
        </aside>
      </div>
    </section>

    <section class="grid grid-cols-1 lg:grid-cols-[0.95fr_1.05fr] gap-5">
      <div class="card-stripe p-6 sm:p-7">
        <div class="mb-5">
          <p class="eyebrow mb-2">Next Draw</p>
          <h2 class="text-2xl font-semibold text-[#233142]">下期开奖倒计时</h2>
          <p class="mt-2 text-sm text-[#7d867f]">{{ displayJackpot.nextDraw }}</p>
        </div>
        <CountdownTimer />
      </div>

      <div class="card-stripe p-6 sm:p-7">
        <div class="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p class="eyebrow mb-2">Prize Status</p>
            <h2 class="text-2xl font-semibold text-[#233142]">奖金状态</h2>
            <p class="mt-2 text-sm text-[#7d867f]">
              {{ jackpotLoading ? "正在同步奖金信息" : "来源于最新开奖与本地归档" }}
            </p>
          </div>
          <div class="rounded-lg border border-[#d8cbbb] bg-[#f8f2e8] px-5 py-4 text-right">
            <p class="text-xs text-[#7d867f]">当前显示</p>
            <p class="mt-1 text-2xl font-semibold tabular text-[#8d6f47]">
              {{ displayJackpot.amount }}<span class="text-base">{{ displayJackpot.unit }}</span>
            </p>
            <p class="text-xs text-[#7d867f]">{{ displayJackpot.cashValue }}</p>
          </div>
        </div>

        <div class="mt-6 grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div
            v-for="(prize, i) in prizeBreakdown.slice(0, 4)"
            :key="i"
            class="rounded-lg border border-[#ddd4c7] bg-[#fffdf8] p-4"
          >
            <p class="text-xs text-[#7d867f]">
              {{ lotteryType === "ssq" ? (["一等奖", "二等奖", "三等奖", "四等奖"][i] || "其他") : (["头奖", "二等奖", "三等奖", "四等奖"][i] || "其他") }}
            </p>
            <p class="mt-1 text-xl font-semibold tabular text-[#233142]">
              {{ prize.count?.toLocaleString?.() || prize.count || 0 }} 注
            </p>
          </div>
          <div v-if="!prizeBreakdown.length" class="col-span-full rounded-lg border border-dashed border-[#cfc2b2] bg-[#fffdf8] p-6 text-center text-sm text-[#7d867f]">
            暂无实时中奖明细。
          </div>
        </div>
      </div>
    </section>

    <section class="space-y-4">
      <div>
        <p class="eyebrow mb-2">Number Signals</p>
        <h2 class="text-2xl sm:text-3xl font-semibold tracking-tight text-[#233142]">号码趋势摘要</h2>
        <p class="mt-2 max-w-2xl text-sm text-[#7d867f]">
          近期数据按频率、结构与组合三条线整理，便于从不同角度复盘号码分布。
        </p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <router-link to="/frequency" class="card-stripe p-6 hover-lift">
          <div class="flex items-start justify-between gap-4">
            <div>
              <p class="text-sm font-semibold text-[#8d6f47]">高频数字</p>
              <h3 class="mt-2 text-xl font-semibold text-[#233142]">查看近期活跃号码</h3>
            </div>
            <span class="rounded-full bg-[#e7dcc7] px-3 py-1 text-sm text-[#6f5737]">频率</span>
          </div>
          <p class="mt-8 text-sm leading-6 text-[#7d867f]">
            按历史出现次数排序，适合快速检查某些号码是否持续活跃。
          </p>
        </router-link>

        <router-link to="/patterns" class="card-stripe p-6 hover-lift">
          <div class="flex items-start justify-between gap-4">
            <div>
              <p class="text-sm font-semibold text-[#7089a6]">走势结构</p>
              <h3 class="mt-2 text-xl font-semibold text-[#233142]">奇偶、大小与和值</h3>
            </div>
            <span class="rounded-full bg-[#dfe7eb] px-3 py-1 text-sm text-[#536b80]">趋势</span>
          </div>
          <p class="mt-8 text-sm leading-6 text-[#7d867f]">
            用更稳定的结构指标观察开奖分布，减少单个号码带来的噪声。
          </p>
        </router-link>

        <router-link to="/pairs" class="card-stripe p-6 hover-lift">
          <div class="flex items-start justify-between gap-4">
            <div>
              <p class="text-sm font-semibold text-[#7f9a86]">组合关系</p>
              <h3 class="mt-2 text-xl font-semibold text-[#233142]">连号、同尾与搭配</h3>
            </div>
            <span class="rounded-full bg-[#e0e7dc] px-3 py-1 text-sm text-[#566d60]">组合</span>
          </div>
          <p class="mt-8 text-sm leading-6 text-[#7d867f]">
            从成组出现的角度整理号码关系，便于做数据复盘。
          </p>
        </router-link>
      </div>
    </section>

    <section class="card-stripe overflow-hidden">
      <div class="flex flex-col gap-2 border-b border-[#ddd4c7] bg-[#f8f2e8] px-6 py-5 sm:px-7">
        <p class="eyebrow">Prize Rules</p>
        <h2 class="text-2xl font-semibold text-[#233142]">{{ lotteryLabel }} 奖金规则</h2>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full table-premium text-sm sm:text-[15px]">
          <thead>
            <tr class="border-b border-[#ddd4c7] bg-[#fffdf8]">
              <th class="px-5 py-4 text-left">奖项等级</th>
              <th class="px-5 py-4 text-left">中奖条件</th>
              <th class="px-5 py-4 text-right">奖金金额</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(rule, i) in prizeRules" :key="rule.level" class="border-b border-[#eee8dd] last:border-0">
              <td class="px-5 py-4 font-semibold text-[#233142]">{{ rule.level }}</td>
              <td class="px-5 py-4 text-[#7d867f]">{{ rule.condition }}</td>
              <td class="px-5 py-4 text-right font-semibold" :class="i === 0 ? 'text-[#b96d63]' : 'text-[#233142]'">
                {{ rule.prize }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>
