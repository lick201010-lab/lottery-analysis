<script setup>
import { ref, onMounted, computed, watch } from "vue";
import { api, lotteryType } from "../api.js";
import NumberBall from "../components/NumberBall.vue";
import FrequencyChart from "../components/FrequencyChart.vue";
import TrendChart from "../components/TrendChart.vue";

const frequencyData = ref([]);
const hotColdData = ref({ hot: [], cold: [] });
const overdueData = ref([]);
const trendData = ref([]);
const selectedNumber = ref(null);
const loading = ref(false);
const displayCount = ref(20);

const maxRegularNumber = computed(() => (lotteryType.value === "ssq" ? 33 : 49));
const totalBallsLabel = computed(() => `${maxRegularNumber.value}球`);

const sortedByFreq = computed(() => {
  return [...frequencyData.value].sort((a, b) => b.total_appearances - a.total_appearances);
});

const sortedByMissed = computed(() => {
  return [...frequencyData.value].sort((a, b) => b.consecutive_missed - a.consecutive_missed);
});

const displayOptions = computed(() => {
  const max = maxRegularNumber.value;
  return [10, 20, max].filter((v, i, arr) => arr.indexOf(v) === i);
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
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 tracking-tight">频率分析</h1>
        <p class="text-base text-gray-400 mt-1">号码出现频率、冷热分析与遗漏追踪</p>
      </div>
      <div class="flex gap-2 bg-white p-1.5 rounded-xl border border-gray-200 shadow-sm">
        <button
          v-for="n in displayOptions"
          :key="n"
          @click="displayCount = n"
          class="px-4 py-2 text-sm font-bold rounded-lg transition-all"
          :class="
            displayCount === n
              ? 'bg-red-600 text-white shadow-md shadow-red-500/20'
              : 'text-gray-500 hover:bg-gray-50'
          "
        >
          Top {{ n }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-20 text-gray-400">
      <svg class="w-10 h-10 mx-auto mb-3 animate-spin text-gray-300" fill="currentColor" viewBox="0 0 24 24"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/></svg>
      加载中...
    </div>

    <template v-else>
      <!-- Frequency Bar Chart -->
      <FrequencyChart
        :data="sortedByFreq"
        :showCount="displayCount"
        title="号码出现频率排名"
      />

      <!-- Hot & Cold Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        <!-- Hot Numbers -->
        <div class="bg-white rounded-2xl border border-gray-200/80 p-6 shadow-sm card-lift">
          <div class="flex items-center gap-3 mb-5">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-red-500 to-red-700 flex items-center justify-center shadow-lg shadow-red-500/20">
              <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/></svg>
            </div>
            <h3 class="text-base font-bold text-gray-900">热门号码 (Top 10)</h3>
          </div>
          <div v-if="hotColdData.hot.length === 0" class="text-base text-gray-400 py-4">暂无数据</div>
          <div v-else class="space-y-2">
            <div
              v-for="(h, i) in hotColdData.hot"
              :key="h.number"
              class="flex items-center gap-3 py-2.5 px-3 rounded-xl hover:bg-red-50/60 transition-colors cursor-pointer group"
              @click="selectNumber(h.number)"
            >
              <span class="text-sm font-bold text-gray-300 w-6">{{ i + 1 }}</span>
              <NumberBall :number="h.number" size="md" />
              <span class="text-[15px] text-gray-600 flex-1 font-medium">
                出现 {{ h.total_appearances }} 次
              </span>
              <span class="text-xs font-bold text-gray-400 bg-gray-100 px-2 py-1 rounded-lg group-hover:bg-red-100 group-hover:text-red-600 transition-colors">
                评分 {{ h.hotness_score }}
              </span>
            </div>
          </div>
        </div>

        <!-- Cold Numbers -->
        <div class="bg-white rounded-2xl border border-gray-200/80 p-6 shadow-sm card-lift">
          <div class="flex items-center gap-3 mb-5">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M16 18l2.29-2.29-4.88-4.88-4 4L2 7.41 3.41 6l6 6 4-4 6.3 6.29L22 12v6z"/></svg>
            </div>
            <h3 class="text-base font-bold text-gray-900">冷门号码 (Bottom 10)</h3>
          </div>
          <div v-if="hotColdData.cold.length === 0" class="text-base text-gray-400 py-4">暂无数据</div>
          <div v-else class="space-y-2">
            <div
              v-for="(c, i) in hotColdData.cold"
              :key="c.number"
              class="flex items-center gap-3 py-2.5 px-3 rounded-xl hover:bg-blue-50/60 transition-colors cursor-pointer group"
              @click="selectNumber(c.number)"
            >
              <span class="text-sm font-bold text-gray-300 w-6">{{ i + 1 }}</span>
              <NumberBall :number="c.number" size="md" />
              <span class="text-[15px] text-gray-600 flex-1 font-medium">
                出现 {{ c.total_appearances }} 次
              </span>
              <span class="text-xs font-bold text-gray-400 bg-gray-100 px-2 py-1 rounded-lg group-hover:bg-blue-100 group-hover:text-blue-600 transition-colors">
                评分 {{ c.hotness_score }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Overdue Numbers -->
      <div class="bg-white rounded-2xl border border-gray-200/80 p-6 shadow-sm card-lift">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-amber-700 flex items-center justify-center shadow-lg shadow-amber-500/20">
            <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>
          </div>
          <h3 class="text-base font-bold text-gray-900">遗漏号码 (久未开出)</h3>
        </div>
        <div v-if="overdueData.length === 0" class="text-base text-gray-400 py-4">暂无数据</div>
        <div v-else class="grid grid-cols-3 sm:grid-cols-5 md:grid-cols-7 lg:grid-cols-8 gap-3">
          <div
            v-for="o in overdueData.slice(0, 24)"
            :key="o.number"
            class="flex flex-col items-center gap-1.5 p-3 rounded-xl hover:bg-amber-50/60 transition-colors cursor-pointer"
            @click="selectNumber(o.number)"
          >
            <NumberBall :number="o.number" size="lg" />
            <span class="text-xs font-semibold text-gray-400">遗漏 {{ o.consecutive_missed }} 期</span>
          </div>
        </div>
      </div>

      <!-- Ranking Table -->
      <div class="bg-white rounded-2xl border border-gray-200/80 shadow-sm overflow-hidden card-lift">
        <div class="px-6 py-5 border-b border-gray-100 flex items-center gap-3">
          <div class="w-1 h-6 bg-gradient-to-b from-gray-400 to-gray-600 rounded-full"></div>
          <h3 class="text-base font-bold text-gray-900">完整排名 ({{ totalBallsLabel }})</h3>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full table-premium text-[15px]">
            <thead>
              <tr class="bg-gray-50/80 border-b border-gray-200">
                <th class="px-5 py-3.5 text-left text-gray-400 font-semibold">排名</th>
                <th class="px-5 py-3.5 text-left text-gray-400 font-semibold">号码</th>
                <th class="px-5 py-3.5 text-right text-gray-400 font-semibold">出现次数</th>
                <th class="px-5 py-3.5 text-right text-gray-400 font-semibold">特码次数</th>
                <th class="px-5 py-3.5 text-right text-gray-400 font-semibold">遗漏期数</th>
                <th class="px-5 py-3.5 text-right text-gray-400 font-semibold">上次出现</th>
                <th class="px-5 py-3.5 text-right text-gray-400 font-semibold">热度</th>
                <th class="px-5 py-3.5 text-center text-gray-400 font-semibold">趋势</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(r, i) in sortedByFreq"
                :key="r.number"
                class="border-b border-gray-100 transition-colors"
                :class="selectedNumber === r.number ? 'bg-red-50/60' : 'hover:bg-gray-50/60'"
              >
                <td class="px-5 py-3 text-gray-400 font-bold">{{ i + 1 }}</td>
                <td class="px-5 py-3">
                  <NumberBall :number="r.number" size="sm" />
                </td>
                <td class="px-5 py-3 text-right text-gray-800 font-bold">
                  {{ r.total_appearances }}
                </td>
                <td class="px-5 py-3 text-right text-gray-500">
                  {{ r.special_appearances }}
                </td>
                <td class="px-5 py-3 text-right font-bold" :class="r.consecutive_missed > 30 ? 'text-red-600' : 'text-gray-500'">
                  {{ r.consecutive_missed }}
                </td>
                <td class="px-5 py-3 text-right text-gray-400">
                  {{ r.last_appearance_date || '-' }}
                </td>
                <td class="px-5 py-3 text-right">
                  <span class="inline-block px-2.5 py-1 rounded-lg text-xs font-bold" :class="r.hotness_score > 80 ? 'bg-red-100 text-red-700' : r.hotness_score > 50 ? 'bg-orange-100 text-orange-700' : 'bg-gray-100 text-gray-600'">
                    {{ r.hotness_score }}
                  </span>
                </td>
                <td class="px-5 py-3 text-center">
                  <button
                    @click="selectNumber(r.number)"
                    class="text-xs font-bold px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-red-50 hover:border-red-300 hover:text-red-700 transition-colors"
                    :class="selectedNumber === r.number ? 'bg-red-600 text-white border-red-600 hover:bg-red-700' : 'text-gray-500'"
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
      <div v-if="selectedNumber" class="bg-white rounded-2xl border border-gray-200/80 p-6 shadow-sm card-lift">
        <div class="flex items-center gap-3 mb-5">
          <NumberBall :number="selectedNumber" size="lg" />
          <div>
            <div class="text-base font-bold text-gray-900">号码 #{{ selectedNumber }} 近50期滚动频率</div>
            <div class="text-sm text-gray-400">点击表格中其他号码可切换</div>
          </div>
          <button
            @click="selectedNumber = null"
            class="ml-auto inline-flex items-center gap-1.5 px-4 py-2 text-sm font-bold text-gray-500 hover:text-gray-800 hover:bg-gray-100 rounded-xl transition-colors"
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
