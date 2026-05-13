<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { api, lotteryType } from "../api.js";
import NumberBall from "../components/NumberBall.vue";

const summary = ref({});
const latestDraw = ref(null);
const loading = ref(false);

const lotteryLabel = computed(() => (lotteryType.value === "ssq" ? "双色球" : "六合彩"));
const mainRange = computed(() => (lotteryType.value === "ssq" ? "1-33" : "1-49"));
const specialRange = computed(() => (lotteryType.value === "ssq" ? "1-16" : "1-49"));

async function loadData() {
  loading.value = true;
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
}

onMounted(loadData);
watch(lotteryType, loadData);
</script>

<template>
  <div class="space-y-8 animate-fade-in-up">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 tracking-tight">{{ lotteryLabel }} 仪表盘</h1>
        <p class="text-base text-gray-400 mt-1">实时数据概览与统计分析</p>
      </div>
      <span class="inline-flex items-center gap-2 px-4 py-2 bg-white rounded-xl border border-gray-200 text-sm text-gray-500 shadow-sm">
        <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
        主号码 {{ mainRange }} / 特码 {{ specialRange }}
      </span>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
      <div class="bg-white rounded-2xl border border-gray-200/80 p-6 card-lift shadow-sm">
        <div class="flex items-center justify-between mb-3">
          <div class="text-sm font-semibold text-gray-400 uppercase tracking-wider">总开奖期数</div>
          <div class="w-10 h-10 rounded-xl bg-red-50 flex items-center justify-center">
            <svg class="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
          </div>
        </div>
        <div class="text-4xl font-extrabold text-gray-900 tracking-tight">
          {{ loading ? "—" : (summary.total_draws || 0).toLocaleString() }}
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-gray-200/80 p-6 card-lift shadow-sm">
        <div class="flex items-center justify-between mb-3">
          <div class="text-sm font-semibold text-gray-400 uppercase tracking-wider">最新开奖日期</div>
          <div class="w-10 h-10 rounded-xl bg-amber-50 flex items-center justify-center">
            <svg class="w-5 h-5 text-amber-500" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM9 10H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2zm-8 4H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2z"/></svg>
          </div>
        </div>
        <div class="text-2xl font-bold text-gray-900">
          {{ loading ? "—" : (summary.latest_date || "-") }}
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-gray-200/80 p-6 card-lift shadow-sm">
        <div class="flex items-center justify-between mb-3">
          <div class="text-sm font-semibold text-gray-400 uppercase tracking-wider">系统状态</div>
          <div class="w-10 h-10 rounded-xl bg-green-50 flex items-center justify-center">
            <svg class="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
          </div>
        </div>
        <div class="text-2xl font-bold text-green-600">运行正常</div>
      </div>

      <div class="bg-white rounded-2xl border border-gray-200/80 p-6 card-lift shadow-sm">
        <div class="flex items-center justify-between mb-3">
          <div class="text-sm font-semibold text-gray-400 uppercase tracking-wider">号码范围</div>
          <div class="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center">
            <svg class="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/></svg>
          </div>
        </div>
        <div class="text-2xl font-bold text-gray-900">{{ mainRange }} / {{ specialRange }}</div>
      </div>
    </div>

    <!-- Latest Draw -->
    <div v-if="latestDraw" class="bg-white rounded-2xl border border-gray-200/80 p-8 shadow-sm card-lift">
      <div class="flex items-center gap-3 mb-6">
        <div class="w-1 h-8 bg-gradient-to-b from-red-500 to-red-700 rounded-full"></div>
        <div>
          <h3 class="text-lg font-bold text-gray-900">最新一期开奖结果</h3>
          <p class="text-sm text-gray-400">第 {{ latestDraw.draw_number }} 期 · {{ latestDraw.draw_date }}</p>
        </div>
      </div>
      <div class="flex items-center gap-3 flex-wrap">
        <NumberBall :number="latestDraw.num1" size="xl" />
        <NumberBall :number="latestDraw.num2" size="xl" />
        <NumberBall :number="latestDraw.num3" size="xl" />
        <NumberBall :number="latestDraw.num4" size="xl" />
        <NumberBall :number="latestDraw.num5" size="xl" />
        <NumberBall :number="latestDraw.num6" size="xl" />
        <span class="mx-3 text-gray-300 text-3xl font-light">+</span>
        <NumberBall :number="latestDraw.special_num" size="xl" />
      </div>
      <div class="flex gap-6 mt-6 text-sm text-gray-500 flex-wrap">
        <span class="inline-flex items-center gap-2 px-3 py-1.5 bg-gray-50 rounded-lg">
          <span class="w-1.5 h-1.5 rounded-full bg-gray-400"></span>
          单双比 {{ latestDraw.odd_count }}:{{ latestDraw.even_count }}
        </span>
        <span class="inline-flex items-center gap-2 px-3 py-1.5 bg-gray-50 rounded-lg">
          <span class="w-1.5 h-1.5 rounded-full bg-gray-400"></span>
          大小比 {{ latestDraw.small_count }}:{{ latestDraw.big_count }}
        </span>
        <span class="inline-flex items-center gap-2 px-3 py-1.5 bg-gray-50 rounded-lg">
          <span class="w-1.5 h-1.5 rounded-full bg-gray-400"></span>
          总和 {{ latestDraw.sum_total }}
        </span>
        <span v-if="latestDraw.has_consecutive" class="inline-flex items-center gap-2 px-3 py-1.5 bg-amber-50 text-amber-700 rounded-lg font-medium">
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>
          含连号
        </span>
      </div>
    </div>

    <!-- Hot / Cold / Overdue -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
      <div class="bg-white rounded-2xl border border-gray-200/80 p-6 shadow-sm card-lift">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-red-500 to-red-700 flex items-center justify-center shadow-lg shadow-red-500/20">
            <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/></svg>
          </div>
          <h3 class="text-base font-bold text-gray-900">热门号码 Top 5</h3>
        </div>
        <div v-if="!summary.top_hot || summary.top_hot.length === 0" class="text-sm text-gray-400 py-4">暂无数据</div>
        <div v-else class="space-y-3">
          <div v-for="(h, i) in summary.top_hot.slice(0, 5)" :key="h?.number" class="flex items-center gap-3 p-2.5 rounded-xl hover:bg-red-50/50 transition-colors">
            <span class="text-sm font-bold text-gray-300 w-5">{{ i + 1 }}</span>
            <NumberBall v-if="h" :number="h.number" size="md" />
            <div class="flex-1">
              <div class="text-sm font-semibold text-gray-700">出现 {{ h.total_appearances }} 次</div>
              <div class="w-full h-1.5 bg-gray-100 rounded-full mt-1.5 overflow-hidden">
                <div class="h-full bg-gradient-to-r from-red-400 to-red-600 rounded-full" :style="{ width: Math.min(100, (h.total_appearances / (summary.top_hot[0]?.total_appearances || 1)) * 100) + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-gray-200/80 p-6 shadow-sm card-lift">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M16 18l2.29-2.29-4.88-4.88-4 4L2 7.41 3.41 6l6 6 4-4 6.3 6.29L22 12v6z"/></svg>
          </div>
          <h3 class="text-base font-bold text-gray-900">冷门号码 Top 5</h3>
        </div>
        <div v-if="!summary.top_cold || summary.top_cold.length === 0" class="text-sm text-gray-400 py-4">暂无数据</div>
        <div v-else class="space-y-3">
          <div v-for="(c, i) in summary.top_cold.slice(0, 5)" :key="c?.number" class="flex items-center gap-3 p-2.5 rounded-xl hover:bg-blue-50/50 transition-colors">
            <span class="text-sm font-bold text-gray-300 w-5">{{ i + 1 }}</span>
            <NumberBall v-if="c" :number="c.number" size="md" />
            <div class="flex-1">
              <div class="text-sm font-semibold text-gray-700">出现 {{ c.total_appearances }} 次</div>
              <div class="w-full h-1.5 bg-gray-100 rounded-full mt-1.5 overflow-hidden">
                <div class="h-full bg-gradient-to-r from-blue-400 to-blue-600 rounded-full" :style="{ width: Math.min(100, (c.total_appearances / (summary.top_hot?.[0]?.total_appearances || 1)) * 100) + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-gray-200/80 p-6 shadow-sm card-lift">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-amber-700 flex items-center justify-center shadow-lg shadow-amber-500/20">
            <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>
          </div>
          <h3 class="text-base font-bold text-gray-900">最久未开 & 热门共现</h3>
        </div>
        <div v-if="summary.most_overdue" class="flex items-center gap-3 p-3 bg-amber-50/60 rounded-xl mb-4">
          <NumberBall :number="summary.most_overdue.number" size="md" />
          <div>
            <div class="text-sm font-bold text-gray-800">遗漏 {{ summary.most_overdue.consecutive_missed }} 期</div>
            <div class="text-xs text-gray-400">最久未开出号码</div>
          </div>
        </div>
        <div v-else class="text-sm text-gray-400 py-4">暂无数据</div>

        <div v-if="summary.top_pairs && summary.top_pairs.length > 0" class="mt-4">
          <div class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">热门共现</div>
          <div class="space-y-2.5">
            <div v-for="p in summary.top_pairs.slice(0, 5)" :key="p?.num_a + '-' + p?.num_b" class="flex items-center gap-2 p-2 rounded-xl hover:bg-gray-50 transition-colors">
              <NumberBall v-if="p" :number="p.num_a" size="sm" />
              <span class="text-gray-300 text-sm">+</span>
              <NumberBall v-if="p" :number="p.num_b" size="sm" />
              <span class="ml-auto text-sm font-semibold text-gray-600">{{ p.co_occurrences }} 次</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
