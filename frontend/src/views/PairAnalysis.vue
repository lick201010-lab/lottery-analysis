<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { api, lotteryType } from "../api.js";
import NumberBall from "../components/NumberBall.vue";

const loading = ref(false);
const allPairs = ref([]);
const selectedNumber = ref(null);
const pairDetails = ref([]);
const loadingDetails = ref(false);

const maxRegular = computed(() => (lotteryType.value === "ssq" ? 33 : 49));
const numberGrid = computed(() => {
  const nums = [];
  for (let i = 1; i <= maxRegular.value; i++) {
    nums.push(i);
  }
  return nums;
});

async function loadAllPairs() {
  loading.value = true;
  try {
    const res = await api.pairs();
    allPairs.value = res.pairs || res.data || res || [];
  } catch (e) {
    console.error(e);
    allPairs.value = [];
  } finally {
    loading.value = false;
  }
}

async function selectNumberHandler(n) {
  if (selectedNumber.value === n) {
    selectedNumber.value = null;
    pairDetails.value = [];
    return;
  }
  selectedNumber.value = n;
  loadingDetails.value = true;
  try {
    const res = await api.pairDetails(n);
    pairDetails.value = res.pairs || res.data || res || [];
  } catch (e) {
    console.error(e);
    pairDetails.value = [];
  } finally {
    loadingDetails.value = false;
  }
}

onMounted(loadAllPairs);
watch(lotteryType, () => {
  selectedNumber.value = null;
  pairDetails.value = [];
  loadAllPairs();
});
</script>

<template>
  <div class="space-y-8 animate-fade-in-up">
    <div>
      <h1 class="text-2xl font-bold text-gray-900 tracking-tight">号码对分析</h1>
      <p class="text-base text-gray-400 mt-1">探索号码之间的共现关系与最佳配对</p>
    </div>

    <!-- Number Selector Grid -->
    <div class="bg-white rounded-2xl border border-gray-200/80 p-6 shadow-sm card-lift">
      <div class="flex items-center justify-between mb-5">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center">
            <svg class="w-5 h-5 text-gray-600" fill="currentColor" viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z"/></svg>
          </div>
          <div>
            <h3 class="text-base font-bold text-gray-900">号码选择器</h3>
            <p class="text-sm text-gray-400">点击号码查看其最佳配对</p>
          </div>
        </div>
        <div v-if="selectedNumber" class="flex items-center gap-2 px-4 py-2 bg-red-50 rounded-xl">
          <span class="text-sm font-bold text-gray-500">当前选中</span>
          <NumberBall :number="selectedNumber" size="sm" />
        </div>
      </div>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="n in numberGrid"
          :key="n"
          @click="selectNumberHandler(n)"
          class="transition-transform hover:scale-110 focus:outline-none"
          :class="selectedNumber === n ? 'ring-2 ring-red-400 ring-offset-2 rounded-full' : ''"
        >
          <NumberBall :number="n" size="sm" />
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <!-- Top Pairs Overall -->
      <div class="bg-white rounded-2xl border border-gray-200/80 shadow-sm overflow-hidden card-lift">
        <div class="px-6 py-5 border-b border-gray-100 flex items-center gap-3">
          <div class="w-1 h-6 bg-gradient-to-b from-red-500 to-red-700 rounded-full"></div>
          <h3 class="text-base font-bold text-gray-900">
            {{ selectedNumber ? `与 #${selectedNumber} 的最佳配对` : '热门共现号码对 (Top 50)' }}
          </h3>
        </div>
        <div v-if="loading || (selectedNumber && loadingDetails)" class="px-6 py-20 text-center text-gray-400">
          <svg class="w-8 h-8 mx-auto mb-2 animate-spin text-gray-300" fill="currentColor" viewBox="0 0 24 24"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/></svg>
          加载中...
        </div>
        <div v-else class="overflow-x-auto max-h-[500px] overflow-y-auto">
          <table class="w-full table-premium text-[15px]">
            <thead class="sticky top-0 bg-white/95 backdrop-blur-sm z-10">
              <tr class="border-b border-gray-200">
                <th class="px-5 py-3 text-left text-gray-400 font-semibold">排名</th>
                <th class="px-5 py-3 text-left text-gray-400 font-semibold">号码 A</th>
                <th class="px-5 py-3 text-left text-gray-400 font-semibold">号码 B</th>
                <th class="px-5 py-3 text-right text-gray-400 font-semibold">共现次数</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(p, i) in ((selectedNumber ? pairDetails : allPairs).slice(0, 50))"
                :key="(p.num_a || p.number_a) + '-' + (p.num_b || p.number_b) + '-' + i"
                class="border-b border-gray-100 transition-colors"
              >
                <td class="px-5 py-3 text-gray-400 font-bold">{{ i + 1 }}</td>
                <td class="px-5 py-3">
                  <button
                    @click="selectNumberHandler(p.num_a || p.number_a)"
                    class="hover:scale-110 transition-transform focus:outline-none"
                  >
                    <NumberBall :number="p.num_a || p.number_a" size="sm" />
                  </button>
                </td>
                <td class="px-5 py-3">
                  <button
                    @click="selectNumberHandler(p.num_b || p.number_b)"
                    class="hover:scale-110 transition-transform focus:outline-none"
                  >
                    <NumberBall :number="p.num_b || p.number_b" size="sm" />
                  </button>
                </td>
                <td class="px-5 py-3 text-right font-bold text-gray-800 text-base">
                  {{ p.co_occurrences || p.count || p.total || 0 }}
                </td>
              </tr>
              <tr v-if="(selectedNumber ? pairDetails : allPairs).length === 0">
                <td colspan="4" class="px-5 py-16 text-center text-gray-400">
                  暂无数据
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Pair Details Panel -->
      <div v-if="selectedNumber" class="bg-white rounded-2xl border border-gray-200/80 p-6 shadow-sm card-lift">
        <div class="flex items-center gap-3 mb-5">
          <div class="w-10 h-10 rounded-xl bg-red-100 flex items-center justify-center">
            <svg class="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
          </div>
          <h3 class="text-base font-bold text-gray-900">配对分析概览</h3>
        </div>
        <div class="space-y-4">
          <div class="flex items-center gap-4 p-5 bg-gradient-to-br from-red-50 to-white rounded-xl border border-red-100">
            <NumberBall :number="selectedNumber" size="lg" />
            <div>
              <div class="text-lg font-bold text-gray-800">号码 #{{ selectedNumber }}</div>
              <div class="text-sm text-gray-400">
                共有 {{ pairDetails.length }} 个与之配对的号码记录
              </div>
            </div>
          </div>

          <div v-if="!loadingDetails && pairDetails.length > 0" class="mt-4">
            <div class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">最佳配对 Top 5</div>
            <div class="space-y-3">
              <div
                v-for="(p, i) in pairDetails.slice(0, 5)"
                :key="i"
                class="flex items-center gap-3 p-3 bg-gray-50 rounded-xl border border-gray-100"
              >
                <span class="text-sm font-bold text-gray-300 w-5">{{ i + 1 }}</span>
                <NumberBall :number="p.num_a || p.number_a" size="md" />
                <span class="text-gray-300 text-sm">+</span>
                <NumberBall :number="p.num_b || p.number_b" size="md" />
                <span class="ml-auto text-base font-bold text-gray-800">
                  {{ p.co_occurrences || p.count || p.total }} 次
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty state for right panel when no selection -->
      <div v-else class="bg-white rounded-2xl border border-gray-200/80 p-12 shadow-sm flex flex-col items-center justify-center text-center">
        <div class="w-16 h-16 rounded-2xl bg-gray-50 flex items-center justify-center mb-4">
          <svg class="w-8 h-8 text-gray-300" fill="currentColor" viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z"/></svg>
        </div>
        <p class="text-gray-500 font-medium text-lg">选择号码查看详细配对</p>
        <p class="text-gray-400 text-sm mt-1">点击上方号码球或左侧表格中的号码</p>
      </div>
    </div>
  </div>
</template>
