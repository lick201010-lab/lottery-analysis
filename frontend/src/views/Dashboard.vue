<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { api, lotteryType } from "../api.js";
import NumberBall from "../components/NumberBall.vue";

const summary = ref({});
const latestDraw = ref(null);
const loading = ref(false);
const userDrawCount = ref(0);

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
const maxNum = computed(() => (lotteryType.value === "ssq" ? 33 : 49));
const maxSpecial = computed(() => (lotteryType.value === "ssq" ? 16 : 49));

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

async function submitNewDraw() {
  addError.value = "";
  const d = newDraw.value;
  const mx = maxNum.value;
  const ms = maxSpecial.value;

  if (!d.draw_number.trim()) { addError.value = "请输入期号"; return; }
  if (!d.draw_date) { addError.value = "请选择日期"; return; }

  const nums = [d.num1, d.num2, d.num3, d.num4, d.num5, d.num6].map((n) => parseInt(n));
  for (let i = 0; i < nums.length; i++) {
    if (isNaN(nums[i]) || nums[i] < 1 || nums[i] > mx) {
      addError.value = `号码 ${i + 1} 必须是 1-${mx} 之间的数字`; return;
    }
  }

  const special = parseInt(d.special_num);
  if (isNaN(special) || special < 1 || special > ms) {
    addError.value = `特码必须是 1-${ms} 之间的数字`; return;
  }

  const sortedNums = [...nums].sort((a, b) => a - b);
  const midpoint = mx / 2;

  const draw = {
    draw_number: d.draw_number.trim(),
    draw_date: d.draw_date,
    num1: sortedNums[0], num2: sortedNums[1], num3: sortedNums[2],
    num4: sortedNums[3], num5: sortedNums[4], num6: sortedNums[5],
    special_num: special,
    odd_count: sortedNums.filter((n) => n % 2 === 1).length,
    even_count: sortedNums.filter((n) => n % 2 === 0).length,
    small_count: sortedNums.filter((n) => n <= midpoint).length,
    big_count: sortedNums.filter((n) => n > midpoint).length,
    has_consecutive: sortedNums.some((n, i) => i > 0 && n - sortedNums[i - 1] === 1),
    sum_total: sortedNums.reduce((a, b) => a + b, 0),
    lottery_type: lotteryType.value,
  };

  addLoading.value = true;
  try {
    const added = api.addDraw(draw);
    if (!added) { addError.value = "该期号已存在"; return; }
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
  <div class="space-y-6 animate-fade-in-up">
    <!-- Hero Section -->
    <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#1e2329] to-[#15191e] border border-[#2b3139] p-6 sm:p-8">
      <div class="absolute top-0 right-0 w-64 h-64 bg-[#fcd535]/3 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3"></div>
      <div class="relative z-10">
        <div class="flex items-start justify-between flex-wrap gap-4">
          <div>
            <div class="flex items-center gap-3 mb-2">
              <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#fcd535]/10 border border-[#fcd535]/20 text-[11px] font-semibold text-[#fcd535] uppercase tracking-wider">
                <span class="w-1.5 h-1.5 rounded-full bg-[#fcd535] animate-pulse"></span>
                {{ lotteryLabel }}
              </span>
              <span class="text-[11px] text-[#707a8a] font-mono">{{ mainRange }} / {{ specialRange }}</span>
            </div>
            <h1 class="text-3xl sm:text-4xl font-bold text-white tracking-tight">
              欢迎回到 <span class="gradient-text">彩溯</span>
            </h1>
            <p class="text-[#707a8a] mt-2 text-sm max-w-lg">
              基于 {{ summary.total_draws?.toLocaleString() || '—' }} 期历史数据的深度分析与统计
            </p>
          </div>
          <button
            @click="openModal"
            class="btn-premium inline-flex items-center gap-2 px-5 py-2.5 bg-[#fcd535] text-[#181a20] text-sm font-bold rounded-xl hover:bg-[#f0b90b] hover:shadow-lg hover:shadow-yellow-500/20 transition-all"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
            录入开奖
          </button>
        </div>
      </div>
    </div>

    <!-- User draw notice -->
    <div v-if="userDrawCount > 0" class="flex items-center gap-3 px-4 py-3 bg-[#fcd535]/5 border border-[#fcd535]/15 rounded-xl text-sm text-[#fcd535]">
      <svg class="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
      <span>你已手动添加 {{ userDrawCount }} 期开奖记录</span>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
      <div class="card-premium rounded-xl p-5 stat-accent relative overflow-hidden">
        <div class="relative z-10">
          <div class="text-[11px] font-semibold text-[#707a8a] uppercase tracking-widest mb-3">总开奖期数</div>
          <div class="text-3xl font-extrabold text-white font-mono tracking-tight">
            {{ loading ? "—" : (summary.total_draws || 0).toLocaleString() }}
          </div>
        </div>
        <div class="absolute bottom-0 right-0 w-16 h-16 bg-[#fcd535]/5 rounded-full blur-xl"></div>
      </div>

      <div class="card-premium rounded-xl p-5 stat-accent relative overflow-hidden">
        <div class="relative z-10">
          <div class="text-[11px] font-semibold text-[#707a8a] uppercase tracking-widest mb-3">最新开奖</div>
          <div class="text-xl font-bold text-white">
            {{ loading ? "—" : (summary.latest_date || "-") }}
          </div>
        </div>
        <div class="absolute bottom-0 right-0 w-16 h-16 bg-[#f0b90b]/5 rounded-full blur-xl"></div>
      </div>

      <div class="card-premium rounded-xl p-5 stat-accent relative overflow-hidden">
        <div class="relative z-10">
          <div class="text-[11px] font-semibold text-[#707a8a] uppercase tracking-widest mb-3">系统状态</div>
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-[#0ecb81]"></span>
            <span class="text-lg font-bold text-[#0ecb81]">正常</span>
          </div>
        </div>
        <div class="absolute bottom-0 right-0 w-16 h-16 bg-[#0ecb81]/5 rounded-full blur-xl"></div>
      </div>

      <div class="card-premium rounded-xl p-5 stat-accent relative overflow-hidden">
        <div class="relative z-10">
          <div class="text-[11px] font-semibold text-[#707a8a] uppercase tracking-widest mb-3">数据覆盖</div>
          <div class="text-xl font-bold text-white font-mono">{{ lotteryType === 'ssq' ? '2003-至今' : '1993-至今' }}</div>
        </div>
        <div class="absolute bottom-0 right-0 w-16 h-16 bg-[#3b82f6]/5 rounded-full blur-xl"></div>
      </div>
    </div>

    <!-- Latest Draw -->
    <div v-if="latestDraw" class="card-premium rounded-xl p-6 relative overflow-hidden">
      <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#fcd535]/30 to-transparent"></div>
      <div class="flex items-center justify-between flex-wrap gap-4 mb-6">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-[#fcd535]/20 to-[#f0b90b]/10 flex items-center justify-center border border-[#fcd535]/20">
            <svg class="w-5 h-5 text-[#fcd535]" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>
          </div>
          <div>
            <h3 class="text-base font-bold text-white">最新一期开奖结果</h3>
            <p class="text-xs text-[#707a8a] font-mono">第 {{ latestDraw.draw_number }} 期 · {{ latestDraw.draw_date }}</p>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-2 flex-wrap justify-center sm:justify-start">
        <NumberBall :number="latestDraw.num1" size="xl" :lotteryType="lotteryType" />
        <NumberBall :number="latestDraw.num2" size="xl" :lotteryType="lotteryType" />
        <NumberBall :number="latestDraw.num3" size="xl" :lotteryType="lotteryType" />
        <NumberBall :number="latestDraw.num4" size="xl" :lotteryType="lotteryType" />
        <NumberBall :number="latestDraw.num5" size="xl" :lotteryType="lotteryType" />
        <NumberBall :number="latestDraw.num6" size="xl" :lotteryType="lotteryType" />
        <span class="mx-1 text-[#474d57] text-xl">+</span>
        <NumberBall :number="latestDraw.special_num" size="xl" is-special :lotteryType="lotteryType" />
      </div>

      <div class="flex gap-3 mt-5 flex-wrap">
        <span class="inline-flex items-center gap-2 px-3 py-1.5 bg-[#0b0e11] rounded-lg text-xs text-[#b7bdc6] border border-[#2b3139]">
          单双 <span class="font-mono font-bold text-white">{{ latestDraw.odd_count }}:{{ latestDraw.even_count }}</span>
        </span>
        <span class="inline-flex items-center gap-2 px-3 py-1.5 bg-[#0b0e11] rounded-lg text-xs text-[#b7bdc6] border border-[#2b3139]">
          大小 <span class="font-mono font-bold text-white">{{ latestDraw.small_count }}:{{ latestDraw.big_count }}</span>
        </span>
        <span class="inline-flex items-center gap-2 px-3 py-1.5 bg-[#0b0e11] rounded-lg text-xs text-[#b7bdc6] border border-[#2b3139]">
          总和 <span class="font-mono font-bold text-[#fcd535]">{{ latestDraw.sum_total }}</span>
        </span>
        <span v-if="latestDraw.has_consecutive" class="inline-flex items-center gap-2 px-3 py-1.5 bg-[#f6465d]/8 rounded-lg text-xs text-[#f6465d] border border-[#f6465d]/20 font-medium">
          含连号
        </span>
      </div>
    </div>

    <!-- Hot / Cold / Overdue -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
      <!-- Hot Numbers -->
      <div class="card-premium rounded-xl p-5 relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-[#f6465d] to-transparent opacity-60"></div>
        <div class="flex items-center gap-3 mb-5">
          <div class="w-9 h-9 rounded-lg bg-[#f6465d]/10 flex items-center justify-center border border-[#f6465d]/20">
            <svg class="w-4 h-4 text-[#f6465d]" fill="currentColor" viewBox="0 0 24 24"><path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/></svg>
          </div>
          <div>
            <h3 class="text-sm font-bold text-white">热门号码</h3>
            <p class="text-[11px] text-[#707a8a]">出现频率最高 Top 5</p>
          </div>
        </div>
        <div v-if="!summary.top_hot || summary.top_hot.length === 0" class="text-sm text-[#707a8a] py-6 text-center">暂无数据</div>
        <div v-else class="space-y-2">
          <div v-for="(h, i) in summary.top_hot.slice(0, 5)" :key="h?.number" class="flex items-center gap-3 p-2 rounded-lg hover:bg-[#2b3139]/40 transition-colors">
            <span class="text-xs font-bold text-[#f6465d] w-5 text-center font-mono">{{ i + 1 }}</span>
            <NumberBall v-if="h" :number="h.number" size="sm" :lotteryType="lotteryType" />
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between">
                <span class="text-xs text-[#b7bdc6]">{{ h.total_appearances }} 次</span>
                <span class="text-[10px] text-[#707a8a] font-mono">{{ ((h.total_appearances / (summary.total_draws || 1)) * 100).toFixed(1) }}%</span>
              </div>
              <div class="w-full h-1 bg-[#2b3139] rounded-full mt-1.5 overflow-hidden">
                <div class="h-full bg-gradient-to-r from-[#f6465d] to-[#ff6b7d] rounded-full transition-all" :style="{ width: Math.min(100, (h.total_appearances / (summary.top_hot[0]?.total_appearances || 1)) * 100) + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Cold Numbers -->
      <div class="card-premium rounded-xl p-5 relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-[#3b82f6] to-transparent opacity-60"></div>
        <div class="flex items-center gap-3 mb-5">
          <div class="w-9 h-9 rounded-lg bg-[#3b82f6]/10 flex items-center justify-center border border-[#3b82f6]/20">
            <svg class="w-4 h-4 text-[#3b82f6]" fill="currentColor" viewBox="0 0 24 24"><path d="M16 18l2.29-2.29-4.88-4.88-4 4L2 7.41 3.41 6l6 6 4-4 6.3 6.29L22 12v6z"/></svg>
          </div>
          <div>
            <h3 class="text-sm font-bold text-white">冷门号码</h3>
            <p class="text-[11px] text-[#707a8a]">出现频率最低 Top 5</p>
          </div>
        </div>
        <div v-if="!summary.top_cold || summary.top_cold.length === 0" class="text-sm text-[#707a8a] py-6 text-center">暂无数据</div>
        <div v-else class="space-y-2">
          <div v-for="(c, i) in summary.top_cold.slice(0, 5)" :key="c?.number" class="flex items-center gap-3 p-2 rounded-lg hover:bg-[#2b3139]/40 transition-colors">
            <span class="text-xs font-bold text-[#3b82f6] w-5 text-center font-mono">{{ i + 1 }}</span>
            <NumberBall v-if="c" :number="c.number" size="sm" :lotteryType="lotteryType" />
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between">
                <span class="text-xs text-[#b7bdc6]">{{ c.total_appearances }} 次</span>
                <span class="text-[10px] text-[#707a8a] font-mono">{{ ((c.total_appearances / (summary.total_draws || 1)) * 100).toFixed(1) }}%</span>
              </div>
              <div class="w-full h-1 bg-[#2b3139] rounded-full mt-1.5 overflow-hidden">
                <div class="h-full bg-gradient-to-r from-[#3b82f6] to-[#60a5fa] rounded-full transition-all" :style="{ width: Math.min(100, (c.total_appearances / (summary.top_hot?.[0]?.total_appearances || 1)) * 100) + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Overdue & Pairs -->
      <div class="card-premium rounded-xl p-5 relative overflow-hidden">
        <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-[#fcd535] to-transparent opacity-60"></div>
        <div class="flex items-center gap-3 mb-5">
          <div class="w-9 h-9 rounded-lg bg-[#fcd535]/10 flex items-center justify-center border border-[#fcd535]/20">
            <svg class="w-4 h-4 text-[#fcd535]" fill="currentColor" viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>
          </div>
          <div>
            <h3 class="text-sm font-bold text-white">遗漏 & 共现</h3>
            <p class="text-[11px] text-[#707a8a]">最久未开 & 热门组合</p>
          </div>
        </div>

        <div v-if="summary.most_overdue" class="flex items-center gap-3 p-3 bg-[#fcd535]/5 rounded-lg border border-[#fcd535]/10 mb-4">
          <NumberBall :number="summary.most_overdue.number" size="md" :lotteryType="lotteryType" />
          <div>
            <div class="text-sm font-bold text-[#eaecef]">遗漏 <span class="text-[#fcd535] font-mono">{{ summary.most_overdue.consecutive_missed }}</span> 期</div>
            <div class="text-[11px] text-[#707a8a]">最久未开出号码</div>
          </div>
        </div>

        <div v-if="summary.top_pairs && summary.top_pairs.length > 0">
          <div class="text-[11px] font-semibold text-[#707a8a] uppercase tracking-wider mb-2.5">热门共现对</div>
          <div class="space-y-1.5">
            <div v-for="p in summary.top_pairs.slice(0, 5)" :key="p?.num_a + '-' + p?.num_b" class="flex items-center gap-2 p-1.5 rounded-lg hover:bg-[#2b3139]/40 transition-colors">
              <NumberBall v-if="p" :number="p.num_a" size="sm" :lotteryType="lotteryType" />
              <span class="text-[#474d57] text-xs">+</span>
              <NumberBall v-if="p" :number="p.num_b" size="sm" :lotteryType="lotteryType" />
              <span class="ml-auto text-xs font-semibold text-[#b7bdc6] font-mono">{{ p.co_occurrences }} 次</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Draw Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="closeModal">
      <div class="bg-[#1e2329] rounded-xl border border-[#2b3139] shadow-2xl w-full max-w-lg p-6 space-y-5 relative overflow-hidden">
        <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#fcd535]/40 to-transparent"></div>
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-bold text-white">录入最新开奖</h3>
          <button @click="closeModal" class="text-[#707a8a] hover:text-white transition-colors p-1 rounded-lg hover:bg-[#2b3139]">
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
          </button>
        </div>

        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-[#707a8a] uppercase tracking-wider mb-1.5">期号</label>
              <input v-model="newDraw.draw_number" type="text" placeholder="如: 26/051" class="w-full px-3 py-2.5 bg-[#0b0e11] border border-[#2b3139] rounded-lg text-sm text-[#eaecef] focus:outline-none focus:border-[#fcd535] transition-colors" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-[#707a8a] uppercase tracking-wider mb-1.5">开奖日期</label>
              <input v-model="newDraw.draw_date" type="date" class="w-full px-3 py-2.5 bg-[#0b0e11] border border-[#2b3139] rounded-lg text-sm text-[#eaecef] focus:outline-none focus:border-[#fcd535] transition-colors" />
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-[#707a8a] uppercase tracking-wider mb-1.5">开奖号码 (1-{{ maxNum }})</label>
            <div class="grid grid-cols-6 gap-2">
              <input v-for="i in 6" :key="i" v-model="newDraw['num' + i]" type="number" min="1" :max="maxNum" :placeholder="'' + i" class="w-full px-2 py-2.5 bg-[#0b0e11] border border-[#2b3139] rounded-lg text-sm text-center text-[#eaecef] focus:outline-none focus:border-[#fcd535] transition-colors font-mono" />
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-[#707a8a] uppercase tracking-wider mb-1.5">特码 (1-{{ maxSpecial }})</label>
            <input v-model="newDraw.special_num" type="number" min="1" :max="maxSpecial" placeholder="特码" class="w-full px-3 py-2.5 bg-[#0b0e11] border border-[#2b3139] rounded-lg text-sm text-[#eaecef] focus:outline-none focus:border-[#fcd535] transition-colors font-mono" />
          </div>

          <div v-if="addError" class="text-sm text-[#f6465d] bg-[#f6465d]/8 px-4 py-2.5 rounded-lg border border-[#f6465d]/15">{{ addError }}</div>
        </div>

        <div class="flex gap-3 pt-2">
          <button @click="closeModal" class="flex-1 px-4 py-2.5 border border-[#2b3139] rounded-lg text-sm font-bold text-[#b7bdc6] hover:bg-[#2b3139] hover:text-white transition-colors">
            取消
          </button>
          <button @click="submitNewDraw" :disabled="addLoading" class="flex-1 px-4 py-2.5 bg-[#fcd535] text-[#181a20] rounded-lg text-sm font-bold hover:bg-[#f0b90b] hover:shadow-lg hover:shadow-yellow-500/20 disabled:opacity-50 transition-all">
            {{ addLoading ? "添加中..." : "确认添加" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
