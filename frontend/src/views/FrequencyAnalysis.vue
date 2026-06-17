<script setup>
import { ref, onMounted, computed, watch } from "vue";
import { api, lotteryType } from "../api.js";
import { useSEO } from "../composables/useSEO.js";
import NumberBall from "../components/NumberBall.vue";
import FrequencyChart from "../components/FrequencyChart.vue";
import TrendChart from "../components/TrendChart.vue";

useSEO({
  title: "双色球冷热号统计 & 六合彩号码频率分析",
  description: "实时统计号码在历史开奖中的出现频率、热号冷号排行、遗漏期数。数据仅供统计参考，不构成投注建议。",
});

const frequencyData = ref([]);
const hotColdData = ref({ hot: [], cold: [] });
const overdueData = ref([]);
const trendData = ref([]);
const selectedNumber = ref(null);
const loading = ref(false);
const displayCount = ref(20);

const maxRegularNumber = computed(() => {
  if (lotteryType.value === "ssq") return 33;
  if (lotteryType.value === "qxc") return 14;
  return 49;
});
const totalBallsLabel = computed(() =>
  lotteryType.value === "qxc" ? "0-14" : `${maxRegularNumber.value}球`
);

const sortedByFreq = computed(() => {
  return [...frequencyData.value].sort((a, b) => b.total_appearances - a.total_appearances);
});

const sortedByMissed = computed(() => {
  return [...frequencyData.value].sort((a, b) => b.consecutive_missed - a.consecutive_missed);
});

const displayOptions = computed(() => {
  const max = maxRegularNumber.value;
  return [10, 20, max].filter((v, i, arr) => v <= max && arr.indexOf(v) === i);
});

async function loadAll() {
  loading.value = true;
  try {
    const [freq, hc, ov] = await Promise.all([
      api.frequency(),
      api.hotCold(10),
      api.overdue(),
    ]);
    frequencyData.value = freq;
    hotColdData.value = hc;
    overdueData.value = ov;
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
}

async function selectNumber(n) {
  selectedNumber.value = n;
  try {
    const res = await api.trend(n, 50);
    trendData.value = res.data;
  } catch (e) {
    console.error(e);
  }
}

onMounted(loadAll);
watch(lotteryType, () => {
  selectedNumber.value = null;
  trendData.value = [];
  loadAll();
});
</script>

<template>
  <div class="space-y-8 animate-fade-in-up">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-[#0d253d] tracking-tight">号码统计</h1>
        <p class="text-base text-[#64748d] mt-1">数字出现频率、冷热分析与遗漏追踪</p>
      </div>
      <div class="flex gap-2 bg-[#f6f9fc] p-1.5 rounded-xl border border-[#e3e8ee] shadow-sm overflow-x-auto">
        <button
          v-for="n in displayOptions"
          :key="n"
          @click="displayCount = n"
          class="px-4 py-2 text-sm font-bold rounded-lg transition-all"
          :class="
            displayCount === n
              ? 'bg-[#533afd] text-white shadow-md'
              : 'text-[#64748d] hover:bg-white'
          "
        >
          Top {{ n }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-20 text-[#64748d]">
      <svg class="w-10 h-10 mx-auto mb-3 animate-spin text-[#64748d]" fill="currentColor" viewBox="0 0 24 24"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/></svg>
      加载中...
    </div>

    <template v-else>
      <!-- Frequency Bar Chart -->
      <FrequencyChart
        :data="sortedByFreq"
        :showCount="displayCount"
        title="数字出现频率排名"
      />

      <!-- Hot & Cold Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5 stagger-children">
        <!-- Hot Numbers -->
        <div class="bg-white rounded-2xl border border-[#e3e8ee] p-6 shadow-sm card-stripe">
          <div class="flex items-center gap-3 mb-5">
            <div class="w-10 h-10 rounded-xl bg-[#533afd] flex items-center justify-center shadow-md shadow-[#533afd]/10">
              <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/></svg>
            </div>
            <h3 class="text-base font-bold text-[#0d253d]">高频数字 (Top 10)</h3>
          </div>
          <div v-if="hotColdData.hot.length === 0" class="text-base text-[#64748d] py-4">暂无数据</div>
          <div v-else class="space-y-2">
            <div
              v-for="(h, i) in hotColdData.hot"
              :key="h.number"
              class="flex items-center gap-3 py-2.5 px-3 rounded-xl hover:bg-[#f6f9fc] transition-colors cursor-pointer group"
              @click="selectNumber(h.number)"
            >
              <span class="text-sm font-bold text-[#64748d] w-6">{{ i + 1 }}</span>
              <NumberBall :number="h.number" :lotteryType="lotteryType" size="md" />
              <span class="text-[15px] text-[#273951] flex-1 font-medium">
                出现 {{ h.total_appearances }} 次
              </span>
              <span class="text-xs font-bold text-[#64748d] bg-[#f6f9fc] px-2 py-1 rounded-lg group-hover:bg-[#f6f9fc] group-hover:text-[#533afd] transition-colors">
                评分 {{ h.hotness_score }}
              </span>
            </div>
          </div>
        </div>

        <!-- Cold Numbers -->
        <div class="bg-white rounded-2xl border border-[#e3e8ee] p-6 shadow-sm card-stripe">
          <div class="flex items-center gap-3 mb-5">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M16 18l2.29-2.29-4.88-4.88-4 4L2 7.41 3.41 6l6 6 4-4 6.3 6.29L22 12v6z"/></svg>
            </div>
            <h3 class="text-base font-bold text-[#0d253d]">低频数字 (Bottom 10)</h3>
          </div>
          <div v-if="hotColdData.cold.length === 0" class="text-base text-[#64748d] py-4">暂无数据</div>
          <div v-else class="space-y-2">
            <div
              v-for="(c, i) in hotColdData.cold"
              :key="c.number"
              class="flex items-center gap-3 py-2.5 px-3 rounded-xl hover:bg-[#f6f9fc] transition-colors cursor-pointer group"
              @click="selectNumber(c.number)"
            >
              <span class="text-sm font-bold text-[#64748d] w-6">{{ i + 1 }}</span>
              <NumberBall :number="c.number" :lotteryType="lotteryType" size="md" />
              <span class="text-[15px] text-[#273951] flex-1 font-medium">
                出现 {{ c.total_appearances }} 次
              </span>
              <span class="text-xs font-bold text-[#64748d] bg-[#f6f9fc] px-2 py-1 rounded-lg group-hover:bg-[#f6f9fc] group-hover:text-[#533afd] transition-colors">
                评分 {{ c.hotness_score }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Overdue Numbers -->
      <div class="bg-white rounded-2xl border border-[#e3e8ee] p-6 shadow-sm card-stripe">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-amber-700 flex items-center justify-center shadow-lg shadow-amber-500/20">
            <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>
          </div>
          <h3 class="text-base font-bold text-[#0d253d]">遗漏数字 (久未开出)</h3>
        </div>
        <div v-if="overdueData.length === 0" class="text-base text-[#64748d] py-4">暂无数据</div>
        <div v-else class="grid grid-cols-3 sm:grid-cols-5 md:grid-cols-7 lg:grid-cols-8 gap-3">
          <div
            v-for="o in overdueData.slice(0, 24)"
            :key="o.number"
            class="flex flex-col items-center gap-1.5 p-3 rounded-xl hover:bg-[#f6f9fc] transition-colors cursor-pointer"
            @click="selectNumber(o.number)"
          >
            <NumberBall :number="o.number" :lotteryType="lotteryType" size="lg" />
            <span class="text-xs font-semibold text-[#64748d]">遗漏 {{ o.consecutive_missed }} 期</span>
          </div>
        </div>
      </div>

      <!-- Ranking Table -->
      <div class="bg-white rounded-2xl border border-[#e3e8ee] shadow-sm overflow-hidden card-stripe">
        <div class="px-6 py-5 border-b border-[#e3e8ee] flex items-center gap-3">
          <div class="w-1 h-6 bg-gradient-to-b from-[#b9b9f9] to-[#533afd] rounded-full"></div>
          <h3 class="text-base font-bold text-[#0d253d]">完整排名 ({{ totalBallsLabel }})</h3>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full table-premium text-[15px]">
            <thead>
              <tr class="bg-[#f6f9fc] border-b border-[#e3e8ee]">
                <th class="px-5 py-3.5 text-left text-[#64748d] font-semibold">排名</th>
                <th class="px-5 py-3.5 text-left text-[#64748d] font-semibold">数字</th>
                <th class="px-5 py-3.5 text-right text-[#64748d] font-semibold">出现次数</th>
                <th class="px-5 py-3.5 text-right text-[#64748d] font-semibold hidden sm:table-cell">特别号次数</th>
                <th class="px-5 py-3.5 text-right text-[#64748d] font-semibold">遗漏期数</th>
                <th class="px-5 py-3.5 text-right text-[#64748d] font-semibold hidden lg:table-cell">上次出现</th>
                <th class="px-5 py-3.5 text-right text-[#64748d] font-semibold hidden md:table-cell">热度</th>
                <th class="px-5 py-3.5 text-center text-[#64748d] font-semibold">趋势</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(r, i) in sortedByFreq"
                :key="r.number"
                class="border-b border-[#e3e8ee] transition-colors"
                :class="selectedNumber === r.number ? 'bg-[#533afd]/8' : 'hover:bg-[#f6f9fc]'"
              >
                <td class="px-5 py-3 text-[#64748d] font-bold">{{ i + 1 }}</td>
                <td class="px-5 py-3">
                  <NumberBall :number="r.number" :lotteryType="lotteryType" size="sm" />
                </td>
                <td class="px-5 py-3 text-right text-[#0d253d] font-bold">
                  {{ r.total_appearances }}
                </td>
                <td class="px-5 py-3 text-right text-[#64748d] hidden sm:table-cell">
                  {{ r.special_appearances }}
                </td>
                <td class="px-5 py-3 text-right font-bold" :class="r.consecutive_missed > 30 ? 'text-[#ea2261]' : 'text-[#64748d]'">
                  {{ r.consecutive_missed }}
                </td>
                <td class="px-5 py-3 text-right text-[#64748d] hidden lg:table-cell">
                  {{ r.last_appearance_date || '-' }}
                </td>
                <td class="px-5 py-3 text-right hidden md:table-cell">
                  <span class="inline-block px-2.5 py-1 rounded-lg text-xs font-bold" :class="r.hotness_score > 80 ? 'bg-[#533afd]/10 text-[#533afd]' : r.hotness_score > 50 ? 'bg-[#9b6829]/10 text-[#9b6829]' : 'bg-[#f6f9fc] text-[#64748d]'">
                    {{ r.hotness_score }}
                  </span>
                </td>
                <td class="px-5 py-3 text-center">
                  <button
                    @click="selectNumber(r.number)"
                    class="text-xs font-bold px-3 py-1.5 rounded-lg border border-[#e3e8ee] hover:bg-[#f6f9fc] hover:border-[#533afd] hover:text-[#533afd] transition-colors"
                    :class="selectedNumber === r.number ? 'bg-[#533afd] text-white border-[#533afd] hover:bg-[#4434d4]' : 'text-[#64748d]'"
                  >
                    {{ selectedNumber === r.number ? '已选' : '查看' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Trend Chart -->
      <div v-if="selectedNumber" class="bg-white rounded-2xl border border-[#e3e8ee] p-6 shadow-sm card-stripe">
        <div class="flex items-center gap-3 mb-5">
          <NumberBall :number="selectedNumber" :lotteryType="lotteryType" size="lg" />
          <div>
            <div class="text-base font-bold text-[#0d253d]">数字 #{{ selectedNumber }} 近50期滚动频率</div>
            <div class="text-sm text-[#64748d]">点击表格中其他数字可切换</div>
          </div>
          <button
            @click="selectedNumber = null"
            class="ml-auto inline-flex items-center gap-1.5 px-4 py-2 text-sm font-bold text-[#64748d] hover:text-[#0d253d] hover:bg-[#f6f9fc] rounded-xl transition-colors"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
            关闭
          </button>
        </div>
        <TrendChart :data="trendData" :number="selectedNumber" />
      </div>
    </template>
  </div>
</template>
