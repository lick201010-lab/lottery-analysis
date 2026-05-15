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
        <h1 class="text-2xl font-bold text-white tracking-tight">频率分析</h1>
        <p class="text-base text-[#707a8a] mt-1">号码出现频率、冷热分析与遗漏追踪</p>
      </div>
      <div class="flex gap-2 bg-[#1e2329] p-1.5 rounded-xl border border-[#2b3139] shadow-sm">
        <button
          v-for="n in displayOptions"
          :key="n"
          @click="displayCount = n"
          class="px-4 py-2 text-sm font-bold rounded-lg transition-all"
          :class="
            displayCount === n
              ? 'bg-[#fcd535] text-[#181a20] shadow-md shadow-[#fcd535]/20'
              : 'text-[#707a8a] hover:bg-[#2b3139]'
          "
        >
          Top {{ n }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-20 text-[#707a8a]">
      <svg class="w-10 h-10 mx-auto mb-3 animate-spin text-[#707a8a]" fill="currentColor" viewBox="0 0 24 24"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/></svg>
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
        <div class="bg-[#1e2329] rounded-2xl border border-[#2b3139] p-6 shadow-sm card-lift">
          <div class="flex items-center gap-3 mb-5">
            <div class="w-10 h-10 rounded-xl bg-[#fcd535] flex items-center justify-center shadow-lg shadow-[#fcd535]/20">
              <svg class="w-5 h-5 text-[#181a20]" fill="currentColor" viewBox="0 0 24 24"><path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/></svg>
            </div>
            <h3 class="text-base font-bold text-white">热门号码 (Top 10)</h3>
          </div>
          <div v-if="hotColdData.hot.length === 0" class="text-base text-[#707a8a] py-4">暂无数据</div>
          <div v-else class="space-y-2">
            <div
              v-for="(h, i) in hotColdData.hot"
              :key="h.number"
              class="flex items-center gap-3 py-2.5 px-3 rounded-xl hover:bg-[#2b3139]/60 transition-colors cursor-pointer group"
              @click="selectNumber(h.number)"
            >
              <span class="text-sm font-bold text-[#707a8a] w-6">{{ i + 1 }}</span>
              <NumberBall :number="h.number" :lotteryType="lotteryType" size="md" />
              <span class="text-[15px] text-[#b7bdc6] flex-1 font-medium">
                出现 {{ h.total_appearances }} 次
              </span>
              <span class="text-xs font-bold text-[#707a8a] bg-[#2b3139] px-2 py-1 rounded-lg group-hover:bg-[#2b3139] group-hover:text-[#fcd535] transition-colors">
                评分 {{ h.hotness_score }}
              </span>
            </div>
          </div>
        </div>

        <!-- Cold Numbers -->
        <div class="bg-[#1e2329] rounded-2xl border border-[#2b3139] p-6 shadow-sm card-lift">
          <div class="flex items-center gap-3 mb-5">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M16 18l2.29-2.29-4.88-4.88-4 4L2 7.41 3.41 6l6 6 4-4 6.3 6.29L22 12v6z"/></svg>
            </div>
            <h3 class="text-base font-bold text-white">冷门号码 (Bottom 10)</h3>
          </div>
          <div v-if="hotColdData.cold.length === 0" class="text-base text-[#707a8a] py-4">暂无数据</div>
          <div v-else class="space-y-2">
            <div
              v-for="(c, i) in hotColdData.cold"
              :key="c.number"
              class="flex items-center gap-3 py-2.5 px-3 rounded-xl hover:bg-[#2b3139]/60 transition-colors cursor-pointer group"
              @click="selectNumber(c.number)"
            >
              <span class="text-sm font-bold text-[#707a8a] w-6">{{ i + 1 }}</span>
              <NumberBall :number="c.number" :lotteryType="lotteryType" size="md" />
              <span class="text-[15px] text-[#b7bdc6] flex-1 font-medium">
                出现 {{ c.total_appearances }} 次
              </span>
              <span class="text-xs font-bold text-[#707a8a] bg-[#2b3139] px-2 py-1 rounded-lg group-hover:bg-[#2b3139] group-hover:text-[#fcd535] transition-colors">
                评分 {{ c.hotness_score }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Overdue Numbers -->
      <div class="bg-[#1e2329] rounded-2xl border border-[#2b3139] p-6 shadow-sm card-lift">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-amber-700 flex items-center justify-center shadow-lg shadow-amber-500/20">
            <svg class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>
          </div>
          <h3 class="text-base font-bold text-white">遗漏号码 (久未开出)</h3>
        </div>
        <div v-if="overdueData.length === 0" class="text-base text-[#707a8a] py-4">暂无数据</div>
        <div v-else class="grid grid-cols-3 sm:grid-cols-5 md:grid-cols-7 lg:grid-cols-8 gap-3">
          <div
            v-for="o in overdueData.slice(0, 24)"
            :key="o.number"
            class="flex flex-col items-center gap-1.5 p-3 rounded-xl hover:bg-[#2b3139]/60 transition-colors cursor-pointer"
            @click="selectNumber(o.number)"
          >
            <NumberBall :number="o.number" :lotteryType="lotteryType" size="lg" />
            <span class="text-xs font-semibold text-[#707a8a]">遗漏 {{ o.consecutive_missed }} 期</span>
          </div>
        </div>
      </div>

      <!-- Ranking Table -->
      <div class="bg-[#1e2329] rounded-2xl border border-[#2b3139] shadow-sm overflow-hidden card-lift">
        <div class="px-6 py-5 border-b border-[#2b3139] flex items-center gap-3">
          <div class="w-1 h-6 bg-gradient-to-b from-[#b7bdc6] to-[#707a8a] rounded-full"></div>
          <h3 class="text-base font-bold text-white">完整排名 ({{ totalBallsLabel }})</h3>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full table-premium text-[15px]">
            <thead>
              <tr class="bg-[#0b0e11]/80 border-b border-[#2b3139]">
                <th class="px-5 py-3.5 text-left text-[#707a8a] font-semibold">排名</th>
                <th class="px-5 py-3.5 text-left text-[#707a8a] font-semibold">号码</th>
                <th class="px-5 py-3.5 text-right text-[#707a8a] font-semibold">出现次数</th>
                <th class="px-5 py-3.5 text-right text-[#707a8a] font-semibold">特码次数</th>
                <th class="px-5 py-3.5 text-right text-[#707a8a] font-semibold">遗漏期数</th>
                <th class="px-5 py-3.5 text-right text-[#707a8a] font-semibold">上次出现</th>
                <th class="px-5 py-3.5 text-right text-[#707a8a] font-semibold">热度</th>
                <th class="px-5 py-3.5 text-center text-[#707a8a] font-semibold">趋势</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(r, i) in sortedByFreq"
                :key="r.number"
                class="border-b border-[#2b3139] transition-colors"
                :class="selectedNumber === r.number ? 'bg-[#fcd535]/10' : 'hover:bg-[#2b3139]/60'"
              >
                <td class="px-5 py-3 text-[#707a8a] font-bold">{{ i + 1 }}</td>
                <td class="px-5 py-3">
                  <NumberBall :number="r.number" :lotteryType="lotteryType" size="sm" />
                </td>
                <td class="px-5 py-3 text-right text-[#eaecef] font-bold">
                  {{ r.total_appearances }}
                </td>
                <td class="px-5 py-3 text-right text-[#707a8a]">
                  {{ r.special_appearances }}
                </td>
                <td class="px-5 py-3 text-right font-bold" :class="r.consecutive_missed > 30 ? 'text-[#f6465d]' : 'text-[#707a8a]'">
                  {{ r.consecutive_missed }}
                </td>
                <td class="px-5 py-3 text-right text-[#707a8a]">
                  {{ r.last_appearance_date || '-' }}
                </td>
                <td class="px-5 py-3 text-right">
                  <span class="inline-block px-2.5 py-1 rounded-lg text-xs font-bold" :class="r.hotness_score > 80 ? 'bg-[#fcd535]/20 text-[#fcd535]' : r.hotness_score > 50 ? 'bg-[#f0b90b]/20 text-[#f0b90b]' : 'bg-[#2b3139] text-[#707a8a]'">
                    {{ r.hotness_score }}
                  </span>
                </td>
                <td class="px-5 py-3 text-center">
                  <button
                    @click="selectNumber(r.number)"
                    class="text-xs font-bold px-3 py-1.5 rounded-lg border border-[#2b3139] hover:bg-[#2b3139] hover:border-[#fcd535] hover:text-[#fcd535] transition-colors"
                    :class="selectedNumber === r.number ? 'bg-[#fcd535] text-[#181a20] border-[#fcd535] hover:bg-[#f0b90b]' : 'text-[#707a8a]'"
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
      <div v-if="selectedNumber" class="bg-[#1e2329] rounded-2xl border border-[#2b3139] p-6 shadow-sm card-lift">
        <div class="flex items-center gap-3 mb-5">
          <NumberBall :number="selectedNumber" :lotteryType="lotteryType" size="lg" />
          <div>
            <div class="text-base font-bold text-white">号码 #{{ selectedNumber }} 近50期滚动频率</div>
            <div class="text-sm text-[#707a8a]">点击表格中其他号码可切换</div>
          </div>
          <button
            @click="selectedNumber = null"
            class="ml-auto inline-flex items-center gap-1.5 px-4 py-2 text-sm font-bold text-[#707a8a] hover:text-[#eaecef] hover:bg-[#2b3139] rounded-xl transition-colors"
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
