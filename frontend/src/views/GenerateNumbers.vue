<script setup>
import { ref, computed, watch } from "vue";
import { api, lotteryType } from "../api.js";
import { getLotteryMeta } from "../lotteryMeta.js";
import NumberBall from "../components/NumberBall.vue";

const strategies = [
  {
    value: "hot",
    label: "热号优先",
    desc: "优先选择近期与历史频率都偏高的号码。",
    accent: "from-[#c88c54] to-[#9d6d3a]",
    tag: "bg-[#f3e5d3] text-[#8b6336] border-[#d9bd93]",
  },
  {
    value: "weighted_random",
    label: "加权随机",
    desc: "按历史热度给权重，但保留足够随机性。",
    accent: "from-[#aa8e97] to-[#886f78]",
    tag: "bg-[#f1e6ea] text-[#886f78] border-[#d6c1c8]",
  },
  {
    value: "overdue",
    label: "追遗漏",
    desc: "优先挑选近期较久未出现的号码，适合观察型策略。",
    accent: "from-[#c07a66] to-[#9d6251]",
    tag: "bg-[#f5e3dc] text-[#945b4b] border-[#deb5a7]",
  },
  {
    value: "layered",
    label: "分层筛选",
    desc: "四层逐步过滤号码池，输出可调大小的复式投注组合。",
    accent: "from-[#6e8c9b] to-[#3f5b6d]",
    tag: "bg-[#dfeaf0] text-[#3f5b6d] border-[#a8c1cd]",
  },
];

const strategy = ref("hot");
const count = ref(3);
const result = ref(null);
const loading = ref(false);
const freqData = ref([]);

// 分层筛选配置
const layered = ref({
  history_periods: 50,
  hot_pct: 60,
  hot_count: 3,
  cold_count: 1,
  trend_periods: 20,
  consecutive: "any",
  odd_even: "any",
  big_small: "any",
  sum_min: null,
  sum_max: null,
  pool1_size: 10,
  pool2_size: 8,
  pool3_size: 6,
});
const mustIncludeInput = ref("");
const mustExcludeInput = ref("");
const layeredResult = ref(null);
const layeredLoading = ref(false);
const layeredError = ref("");

const meta = computed(() => getLotteryMeta(lotteryType.value));
const lotteryLabel = computed(() => meta.value.label);
function boundedCount(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return 0;
  return Math.min(6, Math.max(0, Math.floor(n)));
}

const supplementCount = computed(() =>
  Math.max(0, layered.value.pool1_size - boundedCount(layered.value.hot_count) - boundedCount(layered.value.cold_count))
);
const hotColdTooLarge = computed(() =>
  boundedCount(layered.value.hot_count) + boundedCount(layered.value.cold_count) > layered.value.pool1_size
);
const poolSizeError = computed(() => {
  const p1 = layered.value.pool1_size;
  const p2 = layered.value.pool2_size;
  const p3 = layered.value.pool3_size;
  if (p1 < p2) return `第一步（${p1}）不能小于第二步（${p2}）`;
  if (p2 < p3) return `第二步（${p2}）不能小于第三步（${p3}）`;
  if (p3 < 6) return "最终号码数不能少于 6 个";
  return "";
});
const helperText = computed(() =>
  meta.value.hasRollingPool
    ? "以历史数据做模拟组合，不展示任何官方推荐。"
    : "固定奖金玩法同样只适合做模拟组合与走势观察。"
);

function strategyInfo(value) {
  return strategies.find((item) => item.value === value) || strategies[0];
}

function parseInputNumbers(text) {
  if (!text) return [];
  return text
    .split(/[,，\s]+/)
    .map((t) => parseInt(t.trim(), 10))
    .filter((n) => Number.isFinite(n) && n >= 1);
}

async function generate() {
  loading.value = true;
  try {
    const data = await api.generate(strategy.value, count.value);
    result.value = data;
    if (freqData.value.length === 0) {
      freqData.value = await api.frequency();
    }
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
}

async function runLayered() {
  const includeArr = parseInputNumbers(mustIncludeInput.value);
  const excludeArr = parseInputNumbers(mustExcludeInput.value);
  if (includeArr.length > 3) {
    layeredError.value = "胆码最多 3 个";
    return;
  }
  if (hotColdTooLarge.value) {
    layeredError.value = "热号个数 + 冷号个数不能超过第一步保留个数";
    return;
  }
  if (poolSizeError.value) {
    layeredError.value = poolSizeError.value;
    return;
  }
  layered.value.hot_count = boundedCount(layered.value.hot_count);
  layered.value.cold_count = boundedCount(layered.value.cold_count);
  layeredLoading.value = true;
  layeredError.value = "";
  try {
    const payload = {
      ...layered.value,
      must_include: includeArr,
      must_exclude: excludeArr,
    };
    layeredResult.value = await api.layeredPick(payload);
  } catch (error) {
    layeredError.value = error.message || "调用失败";
    console.error(error);
  } finally {
    layeredLoading.value = false;
  }
}

function freqForNum(number) {
  return freqData.value.find((item) => item.number === number);
}

watch(lotteryType, () => {
  result.value = null;
  layeredResult.value = null;
  freqData.value = [];
});
</script>

<template>
  <div class="space-y-8 animate-fade-in-up">
    <section class="hero-panel p-6 sm:p-8">
      <div class="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div class="max-w-2xl">
          <p class="text-sm font-medium tracking-[0.18em] text-[#8d6f47]">SIMULATED PICKS</p>
          <h1 class="mt-2 text-3xl font-semibold text-[#233142] sm:text-4xl">{{ lotteryLabel }} 模拟选号</h1>
          <p class="mt-3 text-base leading-7 text-[#66706b]">
            按历史分布、冷热程度和分层条件生成模拟组合，适合做娱乐型筛选和走势对照。
          </p>
        </div>
        <div class="rounded-lg border border-[#ddd4c7] bg-[#fffaf2] px-4 py-3 text-sm text-[#6a726d]">
          {{ helperText }}
        </div>
      </div>
    </section>

    <section class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4 stagger-children">
      <button
        v-for="item in strategies"
        :key="item.value"
        @click="strategy = item.value"
        class="card-stripe text-left p-5 transition-all duration-200"
        :class="strategy === item.value ? 'ring-2 ring-[#c3a06a] ring-offset-2 ring-offset-[#f6f0e7]' : 'hover:border-[#cdb99b]'"
      >
        <div class="mb-3 flex items-center gap-3">
          <div class="h-9 w-9 rounded-lg bg-gradient-to-br" :class="item.accent"></div>
          <div class="text-base font-semibold text-[#233142]">{{ item.label }}</div>
        </div>
        <p class="text-sm leading-6 text-[#6c7570]">{{ item.desc }}</p>
      </button>
    </section>

    <!-- 分层筛选配置面板 -->
    <section v-if="strategy === 'layered'" class="card-stripe p-6 sm:p-8 space-y-6">
      <div class="flex items-center gap-3">
        <span class="rounded-lg bg-[#dfeaf0] px-3 py-1 text-sm font-semibold text-[#3f5b6d]">分层筛选</span>
        <p class="text-sm text-[#6c7570]">每一层都可独立调参，逐层过滤号码池，最终输出复式。</p>
      </div>

      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <!-- Layer 1 -->
        <div class="rounded-xl border border-[#e3d8c4] bg-[#fffaf0] p-5 space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-base font-semibold text-[#233142]">第一层 · 大底</h3>
            <span class="text-xs text-[#8d6f47]">历史冷热</span>
          </div>
          <div>
            <label class="text-sm text-[#6c7570]">历史回顾期数</label>
            <select v-model.number="layered.history_periods" class="mt-1 w-full rounded-lg border border-[#ddd4c7] bg-white px-3 py-2 text-sm">
              <option :value="10">近 10 期</option>
              <option :value="30">近 30 期</option>
              <option :value="50">近 50 期</option>
              <option :value="100">近 100 期</option>
              <option :value="200">近 200 期</option>
            </select>
          </div>
          <div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-sm text-[#6c7570]">热号个数</label>
                <input
                  type="number"
                  min="0"
                  max="6"
                  v-model.number="layered.hot_count"
                  class="mt-1 w-full rounded-lg border border-[#ddd4c7] bg-white px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label class="text-sm text-[#6c7570]">冷号个数</label>
                <input
                  type="number"
                  min="0"
                  max="6"
                  v-model.number="layered.cold_count"
                  class="mt-1 w-full rounded-lg border border-[#ddd4c7] bg-white px-3 py-2 text-sm"
                />
              </div>
            </div>
            <p class="mt-2 text-xs" :class="hotColdTooLarge ? 'text-[#94352a]' : 'text-[#8d8d7e]'">
              其余 {{ supplementCount }} 个由中间号/趋势池补齐。
            </p>
          </div>
        </div>

        <!-- Layer 2 -->
        <div class="rounded-xl border border-[#e3d8c4] bg-[#fffaf0] p-5 space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-base font-semibold text-[#233142]">第二层 · 走势</h3>
            <span class="text-xs text-[#8d6f47]">连号特征</span>
          </div>
          <div>
            <label class="text-sm text-[#6c7570]">近期分析期数</label>
            <select v-model.number="layered.trend_periods" class="mt-1 w-full rounded-lg border border-[#ddd4c7] bg-white px-3 py-2 text-sm">
              <option :value="10">近 10 期</option>
              <option :value="20">近 20 期</option>
              <option :value="30">近 30 期</option>
              <option :value="50">近 50 期</option>
            </select>
          </div>
          <div>
            <label class="text-sm text-[#6c7570]">连号要求</label>
            <select v-model="layered.consecutive" class="mt-1 w-full rounded-lg border border-[#ddd4c7] bg-white px-3 py-2 text-sm">
              <option value="any">不限</option>
              <option value="include">偏好出现在连号场次的号</option>
              <option value="exclude">偏好出现在无连号场次的号</option>
            </select>
          </div>
        </div>

        <!-- Layer 3 -->
        <div class="rounded-xl border border-[#e3d8c4] bg-[#fffaf0] p-5 space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-base font-semibold text-[#233142]">第三层 · 统计</h3>
            <span class="text-xs text-[#8d6f47]">奇偶 / 大小 / 和值</span>
          </div>
          <div>
            <label class="text-sm text-[#6c7570]">奇偶偏好</label>
            <select v-model="layered.odd_even" class="mt-1 w-full rounded-lg border border-[#ddd4c7] bg-white px-3 py-2 text-sm">
              <option value="any">不限</option>
              <option value="more_odd">偏奇</option>
              <option value="more_even">偏偶</option>
              <option value="balanced">奇偶平衡</option>
            </select>
          </div>
          <div>
            <label class="text-sm text-[#6c7570]">大小偏好</label>
            <select v-model="layered.big_small" class="mt-1 w-full rounded-lg border border-[#ddd4c7] bg-white px-3 py-2 text-sm">
              <option value="any">不限</option>
              <option value="more_big">偏大</option>
              <option value="more_small">偏小</option>
              <option value="balanced">大小平衡</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-sm text-[#6c7570]">和值下限</label>
              <input type="number" v-model.number="layered.sum_min" placeholder="不限" class="mt-1 w-full rounded-lg border border-[#ddd4c7] bg-white px-3 py-2 text-sm" />
            </div>
            <div>
              <label class="text-sm text-[#6c7570]">和值上限</label>
              <input type="number" v-model.number="layered.sum_max" placeholder="不限" class="mt-1 w-full rounded-lg border border-[#ddd4c7] bg-white px-3 py-2 text-sm" />
            </div>
          </div>
        </div>

        <!-- Layer 4 -->
        <div class="rounded-xl border border-[#e3d8c4] bg-[#fffaf0] p-5 space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-base font-semibold text-[#233142]">第四层 · 个人</h3>
            <span class="text-xs text-[#8d6f47]">胆码 / 杀号</span>
          </div>
          <div>
            <label class="text-sm text-[#6c7570]">胆码（必含，最多 3 个，逗号或空格分隔）</label>
            <input v-model="mustIncludeInput" placeholder="例如：7, 23, 45" class="mt-1 w-full rounded-lg border border-[#ddd4c7] bg-white px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="text-sm text-[#6c7570]">杀号（必排，逗号或空格分隔）</label>
            <input v-model="mustExcludeInput" placeholder="例如：1, 13, 26" class="mt-1 w-full rounded-lg border border-[#ddd4c7] bg-white px-3 py-2 text-sm" />
          </div>
        </div>
      </div>

      <!-- 漏斗步数配置 -->
      <div class="rounded-xl border border-[#ddd4c7] bg-[#f7f2e9] p-5 space-y-4">
        <div class="flex items-center gap-2">
          <h3 class="text-sm font-semibold text-[#233142]">漏斗步数配置</h3>
          <span class="text-xs text-[#7d867f]">— 三步逐步压缩号码池</span>
        </div>
        <div class="grid grid-cols-3 gap-4">
          <div>
            <label class="text-xs font-medium text-[#6c7570]">第一步保留</label>
            <div class="flex items-center gap-2 mt-1">
              <input type="range" min="6" max="30" v-model.number="layered.pool1_size" class="flex-1" />
              <span class="w-7 text-center text-sm font-semibold text-[#233142]">{{ layered.pool1_size }}</span>
            </div>
          </div>
          <div>
            <label class="text-xs font-medium text-[#6c7570]">第二步保留</label>
            <div class="flex items-center gap-2 mt-1">
              <input type="range" min="6" max="20" v-model.number="layered.pool2_size" class="flex-1" />
              <span class="w-7 text-center text-sm font-semibold text-[#233142]">{{ layered.pool2_size }}</span>
            </div>
          </div>
          <div>
            <label class="text-xs font-medium text-[#6c7570]">最终号码数</label>
            <div class="flex items-center gap-2 mt-1">
              <input type="range" min="6" max="12" v-model.number="layered.pool3_size" class="flex-1" />
              <span class="w-7 text-center text-sm font-semibold text-[#233142]">{{ layered.pool3_size }}</span>
            </div>
          </div>
        </div>
        <div class="flex items-center justify-between">
          <p class="text-xs text-[#7d867f]">
            漏斗：49 → <strong>{{ layered.pool1_size }}</strong> → <strong>{{ layered.pool2_size }}</strong> → <strong>{{ layered.pool3_size }}</strong> 个
          </p>
          <p v-if="poolSizeError" class="text-xs text-[#94352a]">⚠ {{ poolSizeError }}</p>
        </div>
      </div>

      <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-end rounded-lg border border-[#ddd4c7] bg-[#f7f2e9] p-4">
        <button
          @click="runLayered"
          :disabled="layeredLoading || !!poolSizeError"
          class="inline-flex items-center justify-center rounded-lg bg-[#3f5b6d] px-7 py-3 text-base font-semibold text-white transition hover:bg-[#2c4250] disabled:opacity-50"
        >
          <span>{{ layeredLoading ? "筛选中..." : "运行分层漏斗" }}</span>
        </button>
      </div>
      <p v-if="layeredError" class="rounded-lg bg-[#fbe2dc] px-4 py-3 text-sm text-[#94352a]">{{ layeredError }}</p>
    </section>

    <!-- 简单策略控制区 -->
    <section v-else class="card-stripe p-6 sm:p-8">
      <div class="flex flex-col gap-5 lg:flex-row lg:items-center">
        <div class="flex items-center gap-3">
          <label class="text-sm font-semibold tracking-[0.08em] text-[#6c7570]">生成组数</label>
          <div class="flex gap-1 rounded-xl bg-[#f7f2e9] p-1">
            <button
              v-for="n in 10"
              :key="n"
              @click="count = n"
              class="h-10 w-10 rounded-lg text-sm font-semibold transition-all"
              :class="count === n ? 'bg-[#fffdf8] text-[#233142] shadow-sm' : 'text-[#7d867f] hover:text-[#233142]'"
            >
              {{ n }}
            </button>
          </div>
        </div>
        <div class="rounded-lg border border-[#ddd4c7] bg-[#f7f2e9] px-4 py-3 text-sm text-[#6d746f]">
          当前策略：{{ strategyInfo(strategy).label }}
        </div>
        <button
          @click="generate"
          :disabled="loading"
          class="ml-0 inline-flex items-center gap-2 rounded-lg bg-[#8d6f47] px-7 py-3 text-base font-semibold text-white transition hover:bg-[#6f5737] disabled:opacity-50 lg:ml-auto"
        >
          <span>{{ loading ? "生成中..." : "生成组合" }}</span>
        </button>
      </div>
    </section>

    <!-- 分层漏斗结果 -->
    <div v-if="layeredResult && strategy === 'layered'" class="space-y-4">

      <!-- Step 1: 大底 -->
      <section class="card-stripe overflow-hidden">
        <div class="flex items-center gap-3 bg-[#eaf4f0] px-6 py-3 border-b border-[#d3e9e2]">
          <span class="flex h-6 w-6 items-center justify-center rounded-full bg-[#3f7a6a] text-xs font-bold text-white">1</span>
          <span class="text-sm font-semibold text-[#233142]">大底筛选</span>
          <span class="text-xs text-[#5a8a7a]">49 → {{ layeredResult.stats.pool1_size }} 个</span>
          <span class="ml-auto text-xs text-[#7d867f]">热 {{ layeredResult.stats.hot_count }} · 冷 {{ layeredResult.stats.cold_count }} · 补 {{ layeredResult.stats.pool1_size - layeredResult.stats.hot_count - layeredResult.stats.cold_count }}</span>
        </div>
        <div class="p-5 space-y-3">
          <!-- 热/冷/补 分组展示 -->
          <div v-if="layeredResult.pool1_groups" class="flex flex-wrap gap-y-3 gap-x-5">
            <div v-if="layeredResult.pool1_groups.hot_numbers.length" class="flex items-center gap-1.5 flex-wrap">
              <span class="text-xs font-semibold text-[#c05c3a] bg-[#fde8e0] border border-[#f5c0a8] rounded px-1.5 py-0.5">热</span>
              <NumberBall v-for="n in layeredResult.pool1_groups.hot_numbers" :key="'hot-' + n" :number="n" :lotteryType="lotteryType" size="sm" />
            </div>
            <div v-if="layeredResult.pool1_groups.cold_numbers.length" class="flex items-center gap-1.5 flex-wrap">
              <span class="text-xs font-semibold text-[#3a6fbc] bg-[#e0ecfd] border border-[#a8c5f5] rounded px-1.5 py-0.5">冷</span>
              <NumberBall v-for="n in layeredResult.pool1_groups.cold_numbers" :key="'cold-' + n" :number="n" :lotteryType="lotteryType" size="sm" />
            </div>
            <div v-if="layeredResult.pool1_groups.supplement_numbers.length" class="flex items-center gap-1.5 flex-wrap">
              <span class="text-xs font-semibold text-[#5a6a5e] bg-[#eaf0eb] border border-[#c2d4c6] rounded px-1.5 py-0.5">补</span>
              <NumberBall v-for="n in layeredResult.pool1_groups.supplement_numbers" :key="'sup-' + n" :number="n" :lotteryType="lotteryType" size="sm" />
            </div>
          </div>
        </div>
        <!-- 箭头 -->
        <div class="flex items-center gap-2 px-6 py-2 bg-[#f7f2e9] border-t border-[#e6ddd0] text-xs text-[#7d867f]">
          <span>▼ 走势精选，淘汰 {{ (layeredResult.pool1_eliminated || []).length }} 个中的 {{ layeredResult.stats.pool1_size - layeredResult.stats.pool2_size }} 个</span>
        </div>
      </section>

      <!-- Step 2: 走势 -->
      <section class="card-stripe overflow-hidden">
        <div class="flex items-center gap-3 bg-[#f4f0e8] px-6 py-3 border-b border-[#e6ddd0]">
          <span class="flex h-6 w-6 items-center justify-center rounded-full bg-[#8d6f47] text-xs font-bold text-white">2</span>
          <span class="text-sm font-semibold text-[#233142]">走势精选</span>
          <span class="text-xs text-[#8d6f47]">{{ layeredResult.stats.pool1_size }} → {{ layeredResult.stats.pool2_size }} 个</span>
        </div>
        <div class="p-5 space-y-3">
          <!-- 保留号码 -->
          <div class="flex flex-wrap gap-1.5">
            <NumberBall v-for="n in layeredResult.pool2" :key="'p2-' + n" :number="n" :lotteryType="lotteryType" size="sm" />
          </div>
          <!-- 淘汰号码 -->
          <div v-if="layeredResult.pool2_eliminated?.length" class="flex items-center gap-1.5 flex-wrap">
            <span class="text-xs text-[#aaa] mr-1">淘汰：</span>
            <span
              v-for="n in layeredResult.pool2_eliminated"
              :key="'e2-' + n"
              class="inline-flex h-7 w-7 items-center justify-center rounded-full border border-[#ddd] bg-[#f5f5f5] text-xs text-[#bbb] line-through"
            >{{ n }}</span>
          </div>
        </div>
        <!-- 箭头 -->
        <div class="flex items-center gap-2 px-6 py-2 bg-[#f7f2e9] border-t border-[#e6ddd0] text-xs text-[#7d867f]">
          <span>▼ 综合得分精选，淘汰 {{ layeredResult.stats.pool2_size - layeredResult.stats.pool3_size }} 个</span>
        </div>
      </section>

      <!-- Step 3: 最终号码 -->
      <section class="card-stripe overflow-hidden">
        <div class="flex items-center gap-3 bg-[#fdf5e4] px-6 py-3 border-b border-[#f0dcac]">
          <span class="flex h-6 w-6 items-center justify-center rounded-full bg-[#c8952a] text-xs font-bold text-white">3</span>
          <span class="text-sm font-semibold text-[#233142]">最终号码</span>
          <span class="text-xs text-[#a07820]">{{ layeredResult.stats.pool2_size }} → <strong>{{ layeredResult.stats.pool3_size }}</strong> 个 ★</span>
          <span class="ml-auto rounded-full border border-[#e6c87a] bg-[#fdf0cd] px-3 py-1 text-xs font-semibold text-[#8d6220]">分层漏斗</span>
        </div>
        <div class="p-6 space-y-5">
          <!-- 最终号码大展示 -->
          <div class="flex flex-wrap items-center gap-3">
            <NumberBall
              v-for="n in layeredResult.pool3"
              :key="'p3-' + n"
              :number="n"
              :lotteryType="lotteryType"
              size="lg"
            />
            <span class="mx-1 text-2xl text-[#cfbea6]">+</span>
            <NumberBall :number="layeredResult.special_pick" :lotteryType="lotteryType" size="lg" is-special />
          </div>
          <!-- 淘汰号码 -->
          <div v-if="layeredResult.pool3_eliminated?.length" class="flex items-center gap-1.5 flex-wrap">
            <span class="text-xs text-[#aaa] mr-1">淘汰：</span>
            <span
              v-for="n in layeredResult.pool3_eliminated"
              :key="'e3-' + n"
              class="inline-flex h-7 w-7 items-center justify-center rounded-full border border-[#ddd] bg-[#f5f5f5] text-xs text-[#bbb] line-through"
            >{{ n }}</span>
          </div>
          <!-- 特别号候选 -->
          <div class="rounded-lg border border-[#e8d9b8] bg-[#fffaf0] p-4">
            <p class="text-sm font-semibold text-[#233142] mb-2">特别号候选 Top 5</p>
            <div class="flex flex-wrap gap-2">
              <NumberBall
                v-for="n in layeredResult.special_candidates"
                :key="'spc-' + n"
                :number="n"
                :lotteryType="lotteryType"
                size="md"
                is-special
              />
            </div>
          </div>
        </div>
        <div class="px-6 pb-4 text-xs text-[#8d8d7e]">分析范围：近 {{ layeredResult.stats.draws_analyzed }} 期开奖</div>
      </section>
    </div>

    <!-- 简单策略结果 -->
    <div v-if="result && strategy !== 'layered'" class="space-y-5">
      <section
        v-for="(set, idx) in result.sets"
        :key="idx"
        class="card-stripe p-6 sm:p-8"
      >
        <div class="mb-6 flex flex-wrap items-center gap-4">
          <span class="text-2xl font-semibold text-[#ccbda8]">#{{ idx + 1 }}</span>
          <span class="rounded-full border px-3 py-1.5 text-xs font-semibold" :class="strategyInfo(set.strategy).tag">
            {{ strategyInfo(set.strategy).label }}
          </span>
        </div>

        <div class="flex flex-wrap items-center gap-4">
          <NumberBall
            v-for="n in set.regular"
            :key="n"
            :number="n"
            :lotteryType="lotteryType"
            size="xl"
          />
          <span class="mx-1 text-2xl text-[#cfbea6]">+</span>
          <NumberBall :number="set.special" :lotteryType="lotteryType" size="xl" is-special />
        </div>

        <div class="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-4 xl:grid-cols-7">
          <div
            v-for="n in set.regular.concat([set.special])"
            :key="'stat-' + n"
            class="rounded-lg border border-[#e2d8ca] bg-[#faf7f0] p-4 text-center"
          >
            <NumberBall :number="n" :lotteryType="lotteryType" size="md" />
            <div class="mt-2 text-xs font-medium text-[#6f7772]">
              频次 {{ freqForNum(n)?.total_appearances || "?" }}
            </div>
            <div
              v-if="freqForNum(n)?.consecutive_missed > 0"
              class="mt-1 text-xs font-semibold"
              :class="freqForNum(n)?.consecutive_missed > 20 ? 'text-[#b96d63]' : 'text-[#7d867f]'"
            >
              遗漏 {{ freqForNum(n)?.consecutive_missed }} 期
            </div>
            <div v-else class="mt-1 text-xs font-semibold text-[#71897d]">最近出现</div>
          </div>
        </div>
      </section>
    </div>

    <!-- 空态 -->
    <section v-if="!result && !layeredResult" class="card-stripe p-12 text-center sm:p-20">
      <div class="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-[#f3e6d6] text-3xl text-[#8d6f47]">
        ✦
      </div>
      <p class="text-xl font-semibold text-[#233142]">选择策略，点击生成</p>
      <p class="mx-auto mt-2 max-w-md text-base leading-7 text-[#6f7772]">
        系统会根据所选策略生成模拟号码，并显示对应的历史频次与遗漏情况。
      </p>
    </section>

    <p class="text-center text-sm text-[#6f7772]">
      免责声明：模拟选号仅供娱乐参考，不构成任何投注建议。彩票开奖结果具有随机性，历史数据不能预测未来结果。
    </p>
  </div>
</template>
