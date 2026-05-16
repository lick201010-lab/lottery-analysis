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
    <!-- Hero Section -->
    <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#f6f9fc] to-white border border-[#e3e8ee] p-6 sm:p-10">
      <div class="absolute top-0 right-0 w-72 h-72 bg-gradient-to-br from-[#665efd]/10 via-[#533afd]/5 to-transparent rounded-full blur-3xl -translate-y-1/3 translate-x-1/4"></div>
      <div class="relative z-10">
        <div class="flex items-start justify-between flex-wrap gap-4">
          <div>
            <div class="flex items-center gap-3 mb-3">
              <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#533afd]/8 border border-[#533afd]/15 text-[11px] font-semibold text-[#533afd] uppercase tracking-wider">
                <span class="w-1.5 h-1.5 rounded-full bg-[#533afd]"></span>
                {{ lotteryLabel }}
              </span>
              <span class="text-[11px] text-[#64748d] font-mono tabular">{{ mainRange }} / {{ specialRange }}</span>
            </div>
            <h1 class="text-3xl sm:text-[42px] font-light text-[#0d253d] tracking-tight leading-tight">
              <span class="gradient-text font-semibold">弈彩</span> 数据统计
            </h1>
            <p class="text-[#64748d] mt-3 text-[15px] max-w-lg font-light">
              基于 <span class="tabular font-medium text-[#0d253d]">{{ summary.total_draws?.toLocaleString() || '—' }}</span> 期历史数据的深度统计与分析
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 stagger-children">
      <div class="card-stripe p-5 relative overflow-hidden">
        <div class="text-[11px] font-semibold text-[#64748d] uppercase tracking-widest mb-3">统计期数</div>
        <div class="text-3xl font-extrabold text-[#0d253d] tabular tracking-tight">
          {{ loading ? "—" : (summary.total_draws || 0).toLocaleString() }}
        </div>
      </div>

      <div class="card-stripe p-5 relative overflow-hidden">
        <div class="text-[11px] font-semibold text-[#64748d] uppercase tracking-widest mb-3">最新一期日期</div>
        <div class="text-xl font-semibold text-[#0d253d]">
          {{ loading ? "—" : (summary.latest_date || "-") }}
        </div>
      </div>

      <div class="card-stripe p-5 relative overflow-hidden">
        <div class="text-[11px] font-semibold text-[#64748d] uppercase tracking-widest mb-3">系统状态</div>
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-[#0ecb81]"></span>
          <span class="text-lg font-semibold text-[#0d253d]">正常运行</span>
        </div>
      </div>

      <div class="card-stripe p-5 relative overflow-hidden">
        <div class="text-[11px] font-semibold text-[#64748d] uppercase tracking-widest mb-3">数据覆盖</div>
        <div class="text-xl font-semibold text-[#0d253d] tabular">{{ lotteryType === 'ssq' ? '2003-至今' : '1993-至今' }}</div>
      </div>
    </div>

    <!-- Latest Draw -->
    <div v-if="latestDraw" class="card-stripe p-6 sm:p-8 relative overflow-hidden">
      <div class="flex items-center gap-3 mb-6">
        <div class="w-10 h-10 rounded-xl bg-[#533afd]/8 flex items-center justify-center border border-[#533afd]/15">
          <svg class="w-5 h-5 text-[#533afd]" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>
        </div>
        <div>
          <h3 class="text-base font-semibold text-[#0d253d]">最新一期结果</h3>
          <p class="text-xs text-[#64748d] font-mono tabular">第 {{ latestDraw.draw_number }} 期 · {{ latestDraw.draw_date }}</p>
        </div>
      </div>

      <div class="flex items-center gap-2 sm:gap-2.5 flex-wrap">
        <NumberBall :number="latestDraw.num1" size="lg" :lotteryType="lotteryType" />
        <NumberBall :number="latestDraw.num2" size="lg" :lotteryType="lotteryType" />
        <NumberBall :number="latestDraw.num3" size="lg" :lotteryType="lotteryType" />
        <NumberBall :number="latestDraw.num4" size="lg" :lotteryType="lotteryType" />
        <NumberBall :number="latestDraw.num5" size="lg" :lotteryType="lotteryType" />
        <NumberBall :number="latestDraw.num6" size="lg" :lotteryType="lotteryType" />
        <span class="mx-1 text-[#e3e8ee] text-xl sm:text-2xl font-light">+</span>
        <NumberBall :number="latestDraw.special_num" size="lg" is-special :lotteryType="lotteryType" />
      </div>

      <div class="flex gap-3 mt-6 flex-wrap">
        <span class="inline-flex items-center gap-2 px-3 py-1.5 bg-[#f6f9fc] rounded-lg text-xs text-[#64748d] border border-[#e3e8ee]">
          奇偶 <span class="tabular font-semibold text-[#0d253d]">{{ latestDraw.odd_count }}:{{ latestDraw.even_count }}</span>
        </span>
        <span class="inline-flex items-center gap-2 px-3 py-1.5 bg-[#f6f9fc] rounded-lg text-xs text-[#64748d] border border-[#e3e8ee]">
          大小 <span class="tabular font-semibold text-[#0d253d]">{{ latestDraw.small_count }}:{{ latestDraw.big_count }}</span>
        </span>
        <span class="inline-flex items-center gap-2 px-3 py-1.5 bg-[#f6f9fc] rounded-lg text-xs text-[#64748d] border border-[#e3e8ee]">
          合计 <span class="tabular font-semibold text-[#533afd]">{{ latestDraw.sum_total }}</span>
        </span>
        <span v-if="latestDraw.has_consecutive" class="inline-flex items-center gap-2 px-3 py-1.5 bg-[#ea2261]/5 rounded-lg text-xs text-[#ea2261] border border-[#ea2261]/15 font-medium">
          含连号
        </span>
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
            <h3 class="text-sm font-semibold text-[#0d253d]">高频数字</h3>
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
            <h3 class="text-sm font-semibold text-[#0d253d]">低频数字</h3>
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
            <h3 class="text-sm font-semibold text-[#0d253d]">遗漏 & 组合</h3>
            <p class="text-[11px] text-[#64748d]">最长遗漏 & 常见组合</p>
          </div>
        </div>

        <div v-if="summary.most_overdue" class="flex items-center gap-3 p-3 bg-[#f6f9fc] rounded-lg border border-[#e3e8ee] mb-4">
          <NumberBall :number="summary.most_overdue.number" size="md" :lotteryType="lotteryType" />
          <div>
            <div class="text-sm font-semibold text-[#0d253d]">遗漏 <span class="text-[#9b6829] tabular">{{ summary.most_overdue.consecutive_missed }}</span> 期</div>
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
