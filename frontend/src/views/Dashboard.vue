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

// Real or fallback jackpot display
const displayJackpot = computed(() => {
  const drawLabel = jackpotData.value?.draw_number
    ? "第" + jackpotData.value.draw_number + "期"
    : (lotteryType.value === "ssq" ? "等待最新开奖" : "等待最新开奖");

  if (jackpotData.value && jackpotData.value.pool_amount) {
    const amt = jackpotData.value.pool_amount;
    if (amt >= 100000000) {
      return { amount: (amt / 100000000).toFixed(2), unit: "亿元", cashValue: (amt * 0.5 / 100000000).toFixed(2) + "亿元", nextDraw: drawLabel };
    }
    return { amount: (amt / 10000).toFixed(0), unit: "万元", cashValue: (amt * 0.5 / 10000).toFixed(0) + "万元", nextDraw: drawLabel };
  }
  if (lotteryType.value === "marksix" && jackpotData.value?.draw_number) {
    return { amount: "按开奖规则", unit: "", cashValue: "香港中奖免税", nextDraw: drawLabel };
  }
  // Fallback demo data
  if (lotteryType.value === "ssq") {
    return { amount: "12.8", unit: "亿元", cashValue: "6.4亿元", nextDraw: drawLabel };
  }
  return { amount: "按开奖规则", unit: "", cashValue: "香港中奖免税", nextDraw: drawLabel };
});

// Prize rules data
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
  <div class="space-y-8 animate-fade-in-up">
    <!-- Hero: Three-column cards -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5 stagger-children">
      <!-- Left: Latest Winning Numbers -->
      <div class="card-stripe p-6 relative overflow-hidden">
        <div class="text-center mb-5">
          <h3 class="text-lg font-bold text-[#0a0e27]">最新一期开奖</h3>
          <p v-if="latestDraw" class="text-sm text-[#64748d] mt-1">
            第 {{ latestDraw.draw_number }} 期 · {{ latestDraw.draw_date }}
          </p>
          <p v-else class="text-sm text-[#64748d] mt-1">加载中...</p>
        </div>

        <div v-if="latestDraw" class="flex items-center justify-center gap-2 flex-wrap mb-5">
          <NumberBall :number="latestDraw.num1" size="lg" :lotteryType="lotteryType" />
          <NumberBall :number="latestDraw.num2" size="lg" :lotteryType="lotteryType" />
          <NumberBall :number="latestDraw.num3" size="lg" :lotteryType="lotteryType" />
          <NumberBall :number="latestDraw.num4" size="lg" :lotteryType="lotteryType" />
          <NumberBall :number="latestDraw.num5" size="lg" :lotteryType="lotteryType" />
          <NumberBall :number="latestDraw.num6" size="lg" :lotteryType="lotteryType" />
          <span class="mx-1 text-[#e3e8ee] font-light">+</span>
          <NumberBall :number="latestDraw.special_num" size="lg" is-special :lotteryType="lotteryType" />
        </div>

        <div v-if="latestDraw" class="flex gap-2 justify-center flex-wrap">
          <span class="inline-flex items-center gap-1.5 px-2.5 py-1 bg-[#f6f9fc] rounded-lg text-xs text-[#64748d] border border-[#e3e8ee]">
            奇偶 <span class="font-semibold text-[#0a0e27]">{{ latestDraw.odd_count }}:{{ latestDraw.even_count }}</span>
          </span>
          <span class="inline-flex items-center gap-1.5 px-2.5 py-1 bg-[#f6f9fc] rounded-lg text-xs text-[#64748d] border border-[#e3e8ee]">
            大小 <span class="font-semibold text-[#0a0e27]">{{ latestDraw.small_count }}:{{ latestDraw.big_count }}</span>
          </span>
          <span class="inline-flex items-center gap-1.5 px-2.5 py-1 bg-[#f6f9fc] rounded-lg text-xs text-[#64748d] border border-[#e3e8ee]">
            合计 <span class="font-semibold text-[#533afd]">{{ latestDraw.sum_total }}</span>
          </span>
        </div>

        <router-link
          to="/data"
          class="mt-5 block w-full text-center py-3 bg-[#0d253d] text-white text-sm font-bold rounded-xl hover:bg-[#1a365d] transition-colors"
        >
          查看历史记录
        </router-link>
      </div>

      <!-- Center: Countdown -->
      <div class="card-stripe p-6 relative overflow-hidden">
        <div class="text-center mb-5">
          <h3 class="text-lg font-bold text-[#0a0e27]">下期开奖倒计时</h3>
          <p class="text-sm text-[#64748d] mt-1">{{ displayJackpot.nextDraw }}</p>
        </div>

        <CountdownTimer />

        <div class="mt-5 text-center">
          <div class="inline-block px-4 py-2 bg-gradient-to-r from-amber-500/10 to-yellow-500/10 border border-amber-500/20 rounded-xl">
            <span class="text-xs text-[#64748d] block mb-0.5">预计头奖</span>
            <span class="text-lg font-extrabold text-amber-600 tabular">{{ displayJackpot.amount }}</span>
            <span class="text-sm font-semibold text-amber-600">{{ displayJackpot.unit }}</span>
          </div>
        </div>

        <div class="mt-4 text-center">
          <span class="text-xs text-[#64748d]">现金价值约 {{ displayJackpot.cashValue }}</span>
        </div>

        <router-link
          to="/generate"
          class="mt-5 block w-full text-center py-3 bg-gradient-to-r from-[#533afd] to-[#4434d4] text-white text-sm font-bold rounded-xl hover:shadow-lg hover:shadow-[#533afd]/20 transition-all"
        >
          模拟选号
        </router-link>
      </div>

      <!-- Right: Winners / Stats -->
      <div class="card-stripe p-6 relative overflow-hidden">
        <div class="text-center mb-5">
          <h3 class="text-lg font-bold text-[#0a0e27]">中奖统计</h3>
          <p class="text-sm text-[#64748d] mt-1">{{ lotteryLabel }} 各等级中奖情况</p>
        </div>

        <div class="space-y-3">
          <div v-if="jackpotData?.prize_breakdown?.length" class="space-y-3">
            <div
              v-for="(prize, i) in jackpotData.prize_breakdown.slice(0, 4)"
              :key="i"
              class="flex items-center justify-between p-3 bg-[#f6f9fc] rounded-xl border border-[#e3e8ee]"
            >
              <span class="text-sm font-medium text-[#0a0e27]">
                {{ lotteryType === 'ssq' ? (['一等奖','二等奖','三等奖','四等奖'][i] || '其他') : (['头奖','二等奖','三等奖','四等奖'][i] || '其他') }}
              </span>
              <span class="text-sm font-bold" :class="i === 0 ? 'text-[#ea2261]' : 'text-[#0a0e27]'">
                {{ prize.count?.toLocaleString?.() || prize.count || 0 }} 注
              </span>
            </div>
          </div>
          <div v-else class="space-y-3">
            <div class="flex items-center justify-between p-3 bg-[#f6f9fc] rounded-xl border border-[#e3e8ee]">
              <span class="text-sm font-medium text-[#0a0e27]">一等奖/头奖</span>
              <span class="text-sm font-bold text-[#ea2261]">-- 注</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-[#f6f9fc] rounded-xl border border-[#e3e8ee]">
              <span class="text-sm font-medium text-[#0a0e27]">二等奖</span>
              <span class="text-sm font-bold text-[#533afd]">-- 注</span>
            </div>
            <div class="flex items-center justify-between p-3 bg-[#f6f9fc] rounded-xl border border-[#e3e8ee]">
              <span class="text-sm font-medium text-[#0a0e27]">三等奖</span>
              <span class="text-sm font-bold text-[#0a0e27]">-- 注</span>
            </div>
            <div class="text-center text-xs text-[#64748d] py-2">暂无实时中奖数据</div>
          </div>
        </div>

        <router-link
          to="/frequency"
          class="mt-5 block w-full text-center py-3 bg-[#0d253d] text-white text-sm font-bold rounded-xl hover:bg-[#1a365d] transition-colors"
        >
          号码统计分析
        </router-link>
      </div>
    </div>

    <!-- Prize Rules -->
    <div class="card-stripe p-6 sm:p-8 relative overflow-hidden">
      <div class="flex items-center gap-3 mb-6">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center shadow-lg shadow-amber-500/20">
          <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1.41 16.09V20h-2.67v-1.93c-1.71-.36-3.16-1.46-3.27-3.4h1.96c.1 1.05.82 1.87 2.65 1.87 1.96 0 2.4-.98 2.4-1.59 0-.83-.44-1.61-2.67-2.14-2.48-.6-4.18-1.62-4.18-3.67 0-1.72 1.39-2.84 3.11-3.21V4h2.67v1.95c1.86.45 2.79 1.86 2.85 3.39H14.3c-.05-1.11-.64-1.87-2.22-1.87-1.5 0-2.4.68-2.4 1.64 0 .84.65 1.39 2.67 1.91s4.18 1.39 4.18 3.91c-.01 1.83-1.38 2.83-3.12 3.16z"/></svg>
        </div>
        <div>
          <h3 class="text-base font-bold text-[#0a0e27]">{{ lotteryLabel }} 奖金规则</h3>
          <p class="text-xs text-[#64748d]">各中奖等级对应的奖金金额</p>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full table-premium text-[15px]">
          <thead>
            <tr class="bg-[#f6f9fc] border-b border-[#e3e8ee]">
              <th class="px-5 py-3.5 text-left text-[#64748d] font-semibold">奖项等级</th>
              <th class="px-5 py-3.5 text-left text-[#64748d] font-semibold">中奖条件</th>
              <th class="px-5 py-3.5 text-right text-[#64748d] font-semibold">奖金金额</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(rule, i) in prizeRules"
              :key="rule.level"
              class="border-b border-[#e3e8ee] transition-colors hover:bg-[#f6f9fc]"
            >
              <td class="px-5 py-3 font-bold text-[#0a0e27]">{{ rule.level }}</td>
              <td class="px-5 py-3 text-[#64748d]">{{ rule.condition }}</td>
              <td class="px-5 py-3 text-right font-bold" :class="i === 0 ? 'text-[#ea2261]' : 'text-[#0a0e27]'">{{ rule.prize }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 stagger-children">
      <div class="card-stripe p-5 relative overflow-hidden">
        <div class="text-[11px] font-semibold text-[#64748d] uppercase tracking-widest mb-3">统计期数</div>
        <div class="text-3xl font-extrabold text-[#0a0e27] tabular tracking-tight">
          {{ loading ? "—" : (summary.total_draws || 0).toLocaleString() }}
        </div>
      </div>

      <div class="card-stripe p-5 relative overflow-hidden">
        <div class="text-[11px] font-semibold text-[#64748d] uppercase tracking-widest mb-3">最新一期日期</div>
        <div class="text-xl font-semibold text-[#0a0e27]">
          {{ loading ? "—" : (summary.latest_date || "-") }}
        </div>
      </div>

      <div class="card-stripe p-5 relative overflow-hidden">
        <div class="text-[11px] font-semibold text-[#64748d] uppercase tracking-widest mb-3">系统状态</div>
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-[#0ecb81]"></span>
          <span class="text-lg font-semibold text-[#0a0e27]">正常运行</span>
        </div>
      </div>

      <div class="card-stripe p-5 relative overflow-hidden">
        <div class="text-[11px] font-semibold text-[#64748d] uppercase tracking-widest mb-3">数据覆盖</div>
        <div class="text-xl font-semibold text-[#0a0e27] tabular">{{ lotteryType === 'ssq' ? '2003-至今' : '1993-至今' }}</div>
      </div>
    </div>

    <!-- Hot / Cold / Overdue -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 stagger-children">
      <!-- Hot Numbers -->
      <div class="card-stripe p-5 relative overflow-hidden">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-9 h-9 rounded-lg bg-[#ea2261]/8 flex items-center justify-center border border-[#ea2261]/15">
            <svg class="w-4 h-4 text-[#ea2261]" fill="currentColor" viewBox="0 0 24 24"><path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/></svg>
          </div>
          <div>
            <h3 class="text-sm font-semibold text-[#0a0e27]">高频数字</h3>
            <p class="text-[11px] text-[#64748d]">出现频率最高 Top 5</p>
          </div>
        </div>
        <div v-if="!summary.top_hot || summary.top_hot.length === 0" class="text-sm text-[#64748d] py-6 text-center">暂无数据</div>
        <div v-else class="space-y-2">
          <div v-for="(h, i) in summary.top_hot.slice(0, 5)" :key="h?.number" class="flex items-center gap-3 p-2 rounded-lg hover:bg-[#f6f9fc] transition-colors">
            <span class="text-xs font-bold text-[#ea2261] w-5 text-center tabular">{{ i + 1 }}</span>
            <NumberBall v-if="h" :number="h.number" size="sm" :lotteryType="lotteryType" />
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between">
                <span class="text-xs text-[#64748d]">{{ h.total_appearances }} 次</span>
                <span class="text-[10px] text-[#64748d] tabular">{{ ((h.total_appearances / (summary.total_draws || 1)) * 100).toFixed(1) }}%</span>
              </div>
              <div class="w-full h-1 bg-[#e3e8ee] rounded-full mt-1.5 overflow-hidden">
                <div class="h-full bg-gradient-to-r from-[#ea2261] to-[#f96bee] rounded-full" :style="{ width: Math.min(100, (h.total_appearances / (summary.top_hot[0]?.total_appearances || 1)) * 100) + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Cold Numbers -->
      <div class="card-stripe p-5 relative overflow-hidden">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-9 h-9 rounded-lg bg-[#533afd]/8 flex items-center justify-center border border-[#533afd]/15">
            <svg class="w-4 h-4 text-[#533afd]" fill="currentColor" viewBox="0 0 24 24"><path d="M16 18l2.29-2.29-4.88-4.88-4 4L2 7.41 3.41 6l6 6 4-4 6.3 6.29L22 12v6z"/></svg>
          </div>
          <div>
            <h3 class="text-sm font-semibold text-[#0a0e27]">低频数字</h3>
            <p class="text-[11px] text-[#64748d]">出现频率最低 Top 5</p>
          </div>
        </div>
        <div v-if="!summary.top_cold || summary.top_cold.length === 0" class="text-sm text-[#64748d] py-6 text-center">暂无数据</div>
        <div v-else class="space-y-2">
          <div v-for="(c, i) in summary.top_cold.slice(0, 5)" :key="c?.number" class="flex items-center gap-3 p-2 rounded-lg hover:bg-[#f6f9fc] transition-colors">
            <span class="text-xs font-bold text-[#533afd] w-5 text-center tabular">{{ i + 1 }}</span>
            <NumberBall v-if="c" :number="c.number" size="sm" :lotteryType="lotteryType" />
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between">
                <span class="text-xs text-[#64748d]">{{ c.total_appearances }} 次</span>
                <span class="text-[10px] text-[#64748d] tabular">{{ ((c.total_appearances / (summary.total_draws || 1)) * 100).toFixed(1) }}%</span>
              </div>
              <div class="w-full h-1 bg-[#e3e8ee] rounded-full mt-1.5 overflow-hidden">
                <div class="h-full bg-gradient-to-r from-[#533afd] to-[#665efd] rounded-full" :style="{ width: Math.min(100, (c.total_appearances / (summary.top_hot?.[0]?.total_appearances || 1)) * 100) + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Overdue & Pairs -->
      <div class="card-stripe p-5 relative overflow-hidden">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-9 h-9 rounded-lg bg-[#9b6829]/10 flex items-center justify-center border border-[#9b6829]/20">
            <svg class="w-4 h-4 text-[#9b6829]" fill="currentColor" viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>
          </div>
          <div>
            <h3 class="text-sm font-semibold text-[#0a0e27]">遗漏 & 组合</h3>
            <p class="text-[11px] text-[#64748d]">最长遗漏 & 常见组合</p>
          </div>
        </div>

        <div v-if="summary.most_overdue" class="flex items-center gap-3 p-3 bg-[#f6f9fc] rounded-lg border border-[#e3e8ee] mb-4">
          <NumberBall :number="summary.most_overdue.number" size="md" :lotteryType="lotteryType" />
          <div>
            <div class="text-sm font-semibold text-[#0a0e27]">遗漏 <span class="text-[#9b6829] tabular">{{ summary.most_overdue.consecutive_missed }}</span> 期</div>
            <div class="text-[11px] text-[#64748d]">最长未开出数字</div>
          </div>
        </div>

        <div v-if="summary.top_pairs && summary.top_pairs.length > 0">
          <div class="text-[11px] font-semibold text-[#64748d] uppercase tracking-wider mb-2.5">常见组合</div>
          <div class="space-y-1.5">
            <div v-for="p in summary.top_pairs.slice(0, 5)" :key="p?.num_a + '-' + p?.num_b" class="flex items-center gap-2 p-1.5 rounded-lg hover:bg-[#f6f9fc] transition-colors">
              <NumberBall v-if="p" :number="p.num_a" size="sm" :lotteryType="lotteryType" />
              <span class="text-[#e3e8ee] text-sm">+</span>
              <NumberBall v-if="p" :number="p.num_b" size="sm" :lotteryType="lotteryType" />
              <span class="ml-auto text-xs font-semibold text-[#64748d] tabular">{{ p.co_occurrences }} 次</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
