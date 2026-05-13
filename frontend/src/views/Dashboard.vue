<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { api, lotteryType } from "../api.js";
import NumberBall from "../components/NumberBall.vue";

const summary = ref({});
const latestDraw = ref(null);
const loading = ref(false);
const userDrawCount = ref(0);

// Add draw modal
const showModal = ref(false);
const addLoading = ref(false);
const addError = ref("");
const newDraw = ref({
  draw_number: "",
  draw_date: new Date().toISOString().split("T")[0],
  num1: "", num2: "", num3: "", num4: "", num5: "", num6: "",
  special_num: "",
});

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
    userDrawCount.value = api.getUserDrawCount();
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
}

function openModal() {
  showModal.value = true;
  addError.value = "";
  newDraw.value = {
    draw_number: "",
    draw_date: new Date().toISOString().split("T")[0],
    num1: "", num2: "", num3: "", num4: "", num5: "", num6: "",
    special_num: "",
  };
}

function closeModal() {
  showModal.value = false;
}

function validateNumber(n, max) {
  const val = parseInt(n);
  return !isNaN(val) && val >= 1 && val <= max;
}

async function submitNewDraw() {
  addError.value = "";
  const d = newDraw.value;

  if (!d.draw_number.trim()) {
    addError.value = "请输入期号";
    return;
  }
  if (!d.draw_date) {
    addError.value = "请选择日期";
    return;
  }

  const nums = [d.num1, d.num2, d.num3, d.num4, d.num5, d.num6].map((n) => parseInt(n));
  for (let i = 0; i < nums.length; i++) {
    if (isNaN(nums[i]) || nums[i] < 1 || nums[i] > 49) {
      addError.value = `号码 ${i + 1} 必须是 1-49 之间的数字`;
      return;
    }
  }

  const special = parseInt(d.special_num);
  if (isNaN(special) || special < 1 || special > 49) {
    addError.value = "特码必须是 1-49 之间的数字";
    return;
  }

  const sortedNums = [...nums].sort((a, b) => a - b);
  const midpoint = 49 / 2;

  const draw = {
    draw_number: d.draw_number.trim(),
    draw_date: d.draw_date,
    num1: sortedNums[0],
    num2: sortedNums[1],
    num3: sortedNums[2],
    num4: sortedNums[3],
    num5: sortedNums[4],
    num6: sortedNums[5],
    special_num: special,
    odd_count: sortedNums.filter((n) => n % 2 === 1).length,
    even_count: sortedNums.filter((n) => n % 2 === 0).length,
    small_count: sortedNums.filter((n) => n <= midpoint).length,
    big_count: sortedNums.filter((n) => n > midpoint).length,
    has_consecutive: sortedNums.some((n, i) => i > 0 && n - sortedNums[i - 1] === 1),
    sum_total: sortedNums.reduce((a, b) => a + b, 0),
    lottery_type: "marksix",
  };

  addLoading.value = true;
  try {
    const added = api.addDraw(draw);
    if (!added) {
      addError.value = "该期号已存在";
      return;
    }
    closeModal();
    await loadData();
  } catch (e) {
    addError.value = "添加失败: " + e.message;
  } finally {
    addLoading.value = false;
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
      <div class="flex items-center gap-3">
        <span class="inline-flex items-center gap-2 px-4 py-2 bg-white rounded-xl border border-gray-200 text-sm text-gray-500 shadow-sm">
          <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
          主号码 {{ mainRange }} / 特码 {{ specialRange }}
        </span>
        <button
          @click="openModal"
          class="btn-premium inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-red-600 to-red-700 text-white text-sm font-bold rounded-xl hover:shadow-lg hover:shadow-red-500/25"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
          更新开奖
        </button>
      </div>
    </div>

    <!-- User draw notice -->
    <div v-if="userDrawCount > 0" class="flex items-center gap-3 px-5 py-3 bg-blue-50 border border-blue-100 rounded-xl text-sm text-blue-700">
      <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
      <span>你已手动添加 {{ userDrawCount }} 期开奖记录，所有分析数据已实时更新。</span>
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

    <!-- Add Draw Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="closeModal">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg p-6 space-y-5">
        <div class="flex items-center justify-between">
          <h3 class="text-xl font-bold text-gray-900">录入最新开奖</h3>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600 transition-colors">
            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
          </button>
        </div>

        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-semibold text-gray-600 mb-1.5">期号</label>
              <input v-model="newDraw.draw_number" type="text" placeholder="如: 26/001" class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-400" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-600 mb-1.5">开奖日期</label>
              <input v-model="newDraw.draw_date" type="date" class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-400" />
            </div>
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-600 mb-1.5">开奖号码 (1-49)</label>
            <div class="grid grid-cols-6 gap-2">
              <input v-for="i in 6" :key="i" v-model="newDraw['num' + i]" type="number" min="1" max="49" :placeholder="'号码' + i" class="w-full px-2 py-2.5 border border-gray-200 rounded-xl text-sm text-center focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-400" />
            </div>
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-600 mb-1.5">特码 (1-49)</label>
            <input v-model="newDraw.special_num" type="number" min="1" max="49" placeholder="特码" class="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-400" />
          </div>

          <div v-if="addError" class="text-sm text-red-600 bg-red-50 px-4 py-2.5 rounded-xl">{{ addError }}</div>
        </div>

        <div class="flex gap-3 pt-2">
          <button @click="closeModal" class="flex-1 px-4 py-3 border border-gray-200 rounded-xl text-sm font-bold text-gray-600 hover:bg-gray-50 transition-colors">
            取消
          </button>
          <button @click="submitNewDraw" :disabled="addLoading" class="flex-1 px-4 py-3 bg-gradient-to-r from-red-600 to-red-700 text-white rounded-xl text-sm font-bold hover:shadow-lg hover:shadow-red-500/25 disabled:opacity-50 transition-all">
            {{ addLoading ? "添加中..." : "确认添加" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
