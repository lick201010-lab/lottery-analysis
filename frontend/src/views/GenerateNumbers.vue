<script setup>
import { ref, computed, watch, nextTick } from "vue";
import { api, lotteryType } from "../api.js";
import { getLotteryMeta } from "../lotteryMeta.js";
import { useSEO } from "../composables/useSEO.js";
import NumberBall from "../components/NumberBall.vue";

useSEO({
  title: "模拟选号器（娱乐型）",
  description: "提供热号优先、加权随机、追遗漏、分层漏斗 4 种娱乐型模拟选号方式。仅供娱乐，不构成任何投注建议。",
});

const simpleStrategies = [
  {
    value: "hot",
    label: "热号优先",
    desc: "选近期与历史频率都偏高的号码",
    accent: "from-[#c88c54] to-[#9d6d3a]",
    tag: "bg-[#f3e5d3] text-[#8b6336] border-[#d9bd93]",
  },
  {
    value: "weighted_random",
    label: "加权随机",
    desc: "按热度权重抽取，保留随机性",
    accent: "from-[#aa8e97] to-[#886f78]",
    tag: "bg-[#f1e6ea] text-[#886f78] border-[#d6c1c8]",
  },
  {
    value: "overdue",
    label: "追遗漏",
    desc: "挑选近期较久未出现的号码",
    accent: "from-[#c07a66] to-[#9d6251]",
    tag: "bg-[#f5e3dc] text-[#945b4b] border-[#deb5a7]",
  },
];

const layeredStrategy = {
  value: "layered",
  label: "分层筛选漏斗",
  desc: "综合冷热 / 走势 / 统计逐步精选，自动给出多组 6 号推荐",
  tag: "bg-[#dfeaf0] text-[#3f5b6d] border-[#a8c1cd]",
};

// 兼容 strategyInfo 查找
const strategies = [...simpleStrategies, layeredStrategy];

const strategy = ref("hot");
const showAdvanced = ref(false);
const count = ref(3);
const result = ref(null);
const loading = ref(false);
const freqData = ref([]);

// 分层筛选配置
const defaultLayered = () => ({
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
  qxc_pool1_size: 5,
  qxc_pool2_size: 4,
  qxc_pool3_size: 3,
  count: 5,
});
const layered = ref(defaultLayered());
const mustIncludeInput = ref("");
const mustExcludeInput = ref("");
const layeredResult = ref(null);
const layeredLoading = ref(false);
const layeredError = ref("");

const meta = computed(() => getLotteryMeta(lotteryType.value));
const lotteryLabel = computed(() => meta.value.label);
const isSSQ = computed(() => lotteryType.value === "ssq");
const isQXC = computed(() => lotteryType.value === "qxc");
const canUseLayered = computed(() => ["marksix", "ssq", "qxc"].includes(lotteryType.value));
const specialLabel = computed(() => (isSSQ.value ? "蓝球" : isQXC.value ? "后区" : "特码"));
const pageDescription = computed(() =>
  isQXC.value
    ? "按位置热度、历史频率、遗漏和后区候选生成可重复数字组合，适合做娱乐型观察。"
    : "按历史分布、冷热程度和分层条件生成模拟组合，适合做娱乐型筛选和走势对照。"
);
function boundedCount(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return 0;
  return Math.min(6, Math.max(0, Math.floor(n)));
}

const supplementCount = computed(() =>
  Math.max(0, activePool1Size.value - boundedCount(layered.value.hot_count) - boundedCount(layered.value.cold_count))
);
const hotColdTooLarge = computed(() =>
  boundedCount(layered.value.hot_count) + boundedCount(layered.value.cold_count) > activePool1Size.value
);
const activePool1Size = computed(() => (isQXC.value ? layered.value.qxc_pool1_size : layered.value.pool1_size));
const activePool2Size = computed(() => (isQXC.value ? layered.value.qxc_pool2_size : layered.value.pool2_size));
const activePool3Size = computed(() => (isQXC.value ? layered.value.qxc_pool3_size : layered.value.pool3_size));
const layeredIntro = computed(() =>
  isQXC.value
    ? "按 6 个位置分别筛选 0-9，再独立筛选后区 0-14，保留位置与重复数字。"
    : layeredStrategy.desc
);
const layeredFlowText = computed(() =>
  isQXC.value
    ? `每位 10 → ${layered.value.qxc_pool1_size} → ${layered.value.qxc_pool2_size} → ${layered.value.qxc_pool3_size} 个 · 输出最多 ${layered.value.count} 组`
    : `漏斗：49 → ${layered.value.pool1_size} → ${layered.value.pool2_size} → ${layered.value.pool3_size} 个 · 输出最多 5 组 6 号推荐`
);
const isQxcLayeredResult = computed(() => layeredResult.value?.mode === "qxc_position_layered");
const poolSizeError = computed(() => {
  const p1 = activePool1Size.value;
  const p2 = activePool2Size.value;
  const p3 = activePool3Size.value;
  if (p1 < p2) return `第一步（${p1}）不能小于第二步（${p2}）`;
  if (p2 < p3) return `第二步（${p2}）不能小于第三步（${p3}）`;
  if (isQXC.value && p3 < 1) return "七星彩每位最终候选不能少于 1 个";
  if (isQXC.value) return "";
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

function scrollToStrategyControls(value) {
  if (typeof window === "undefined") return;
  if (!window.matchMedia("(max-width: 768px)").matches) return;
  const selector = value === "layered" ? ".generate-layered-config" : ".generate-simple-controls";
  nextTick(() => {
    document.querySelector(selector)?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  });
}

function selectStrategy(value) {
  strategy.value = value;
  layeredError.value = "";
  if (value === "layered") {
    result.value = null;
  } else {
    layeredResult.value = null;
  }
  scrollToStrategyControls(value);
}

function parseInputNumbers(text) {
  if (!text) return [];
  const minNumber = isQXC.value ? 0 : 1;
  return text
    .split(/[,，\s]+/)
    .map((t) => parseInt(t.trim(), 10))
    .filter((n) => Number.isFinite(n) && n >= minNumber);
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

function resetSimulation() {
  strategy.value = "hot";
  showAdvanced.value = false;
  count.value = 3;
  result.value = null;
  layeredResult.value = null;
  layeredError.value = "";
  layeredLoading.value = false;
  loading.value = false;
  layered.value = defaultLayered();
  mustIncludeInput.value = "";
  mustExcludeInput.value = "";
}

function statBalls(set) {
  if (lotteryType.value === "marksix") {
    return set.regular.map((number) => ({ number, special: false }));
  }
  return [
    ...set.regular.map((number) => ({ number, special: false })),
    { number: set.special, special: true },
  ];
}

watch(lotteryType, () => {
  result.value = null;
  layeredResult.value = null;
  freqData.value = [];
});
</script>

<template>
  <div class="generate-page space-y-8 animate-fade-in-up">
    <section class="hero-panel p-6 sm:p-8">
      <div class="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div class="max-w-2xl">
          <p class="text-sm font-medium tracking-[0.18em] text-[#8d6f47]">SIMULATED PICKS</p>
          <h1 class="mt-2 text-3xl font-semibold text-[#233142] sm:text-4xl">{{ lotteryLabel }} 模拟选号</h1>
          <p class="mt-3 text-base leading-7 text-[#66706b]">
            {{ pageDescription }}
          </p>
        </div>
        <div class="rounded-lg border border-[#ddd4c7] bg-[#fffaf2] px-4 py-3 text-sm text-[#6a726d]">
          {{ helperText }}
        </div>
      </div>
    </section>

    <!-- 简单策略 3 个小卡 -->
    <section>
      <p class="mb-3 text-xs font-semibold tracking-[0.2em] text-[#8d6f47]">基础策略</p>
      <div class="grid grid-cols-1 gap-3 sm:grid-cols-3 stagger-children">
        <button
          v-for="item in simpleStrategies"
          :key="item.value"
          type="button"
          :aria-pressed="strategy === item.value"
          @click="selectStrategy(item.value)"
          class="generate-strategy-choice card-stripe text-left p-4 transition-all duration-200"
          :class="strategy === item.value ? 'ring-2 ring-[#c3a06a] ring-offset-2 ring-offset-[#f6f0e7]' : 'hover:border-[#cdb99b]'"
        >
          <div class="mb-2 flex items-center gap-2.5">
            <div class="generate-strategy-icon h-7 w-7 rounded-lg bg-gradient-to-br" :class="item.accent"></div>
            <div class="text-sm font-semibold text-[#233142]">{{ item.label }}</div>
          </div>
          <p class="text-xs leading-5 text-[#6c7570]">{{ item.desc }}</p>
        </button>
      </div>
    </section>

    <!-- 分层筛选 featured 大卡 -->
    <section v-if="canUseLayered">
      <p class="mb-3 text-xs font-semibold tracking-[0.2em] text-[#8d6f47]">进阶策略 · 推荐</p>
      <button
        type="button"
        :aria-pressed="strategy === layeredStrategy.value"
        @click="selectStrategy(layeredStrategy.value)"
        class="generate-strategy-choice card-stripe w-full text-left p-6 transition-all duration-200 relative overflow-hidden"
        :class="strategy === layeredStrategy.value ? 'ring-2 ring-[#3f5b6d] ring-offset-2 ring-offset-[#f6f0e7] bg-gradient-to-br from-[#f4faff] to-[#eef3f7]' : 'hover:border-[#3f5b6d]'"
      >
        <div class="pointer-events-none absolute right-4 top-4 text-[#3f5b6d] opacity-30 text-5xl font-bold">★</div>
        <div class="flex flex-col sm:flex-row sm:items-center gap-4">
          <div class="generate-layered-icon flex-shrink-0 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-[#6e8c9b] to-[#3f5b6d] text-2xl text-white shadow-md"></div>
          <div class="flex-1">
            <div class="flex items-center gap-2 flex-wrap">
              <h3 class="text-lg font-bold text-[#233142]">{{ layeredStrategy.label }}</h3>
              <span class="rounded-full border border-[#a8c1cd] bg-[#dfeaf0] px-2 py-0.5 text-[10px] font-semibold tracking-wider text-[#3f5b6d]">智能推荐</span>
            </div>
            <p class="mt-1 text-sm leading-6 text-[#6c7570]">{{ layeredIntro }}</p>
            <p class="mt-1.5 text-xs text-[#8d6f47]">
              {{ layeredFlowText }}
            </p>
          </div>
          <div class="flex-shrink-0 hidden sm:block">
            <span v-if="strategy === layeredStrategy.value" class="inline-flex items-center gap-1 rounded-lg bg-[#3f5b6d] px-3 py-1.5 text-xs font-semibold text-white">
              ✓ 已选
            </span>
            <span v-else class="inline-flex items-center gap-1 text-sm font-semibold text-[#3f5b6d]">
              点击使用 →
            </span>
          </div>
        </div>
      </button>
    </section>

    <!-- 分层筛选配置面板 -->
    <section v-if="strategy === 'layered' && canUseLayered" class="generate-layered-config card-stripe p-6 sm:p-8 space-y-5">
      <div class="flex items-start gap-3">
        <div class="generate-config-icon flex-shrink-0 flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-[#6e8c9b] to-[#3f5b6d] text-lg text-white"></div>
        <div>
          <h3 class="text-base font-semibold text-[#233142]">分层筛选配置</h3>
          <p class="mt-0.5 text-xs text-[#6c7570]">先调核心 4 项，进阶选项可保持默认</p>
        </div>
      </div>

      <!-- 核心配置 -->
      <div class="rounded-xl border border-[#e3d8c4] bg-[#fffaf0] p-5 space-y-5">
        <div class="flex items-center gap-2">
          <span class="rounded-md bg-[#fde8c8] px-2 py-0.5 text-[11px] font-bold text-[#8d6220]">核心</span>
          <h4 class="text-sm font-semibold text-[#233142]">必填配置</h4>
        </div>

        <!-- 历史 / 热 / 冷 -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <label class="text-sm font-medium text-[#233142]"><span class="generate-field-icon history"></span>历史回顾期数</label>
            <p class="mt-0.5 text-[11px] text-[#9a9385]">看多少期历史来判断冷热</p>
            <select v-model.number="layered.history_periods" class="mt-2 w-full rounded-lg border border-[#ddd4c7] bg-white px-3 py-2 text-sm">
              <option :value="10">近 10 期</option>
              <option :value="30">近 30 期</option>
              <option :value="50">近 50 期（推荐）</option>
              <option :value="100">近 100 期</option>
              <option :value="200">近 200 期</option>
            </select>
          </div>
          <div>
            <label class="text-sm font-medium text-[#233142]"><span class="generate-field-icon hot"></span>热号个数</label>
            <p class="mt-0.5 text-[11px] text-[#9a9385]">{{ isQXC ? "每个位置优先保留的热数字" : "出现频率最高的 N 个" }}</p>
            <input type="number" min="0" max="6" v-model.number="layered.hot_count" class="mt-2 w-full rounded-lg border border-[#ddd4c7] bg-white px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="text-sm font-medium text-[#233142]"><span class="generate-field-icon cold"></span>冷号个数</label>
            <p class="mt-0.5 text-[11px] text-[#9a9385]">{{ isQXC ? "每个位置纳入的冷数字" : "最久没出现的 N 个" }}</p>
            <input type="number" min="0" max="6" v-model.number="layered.cold_count" class="mt-2 w-full rounded-lg border border-[#ddd4c7] bg-white px-3 py-2 text-sm" />
          </div>
        </div>
        <p class="text-xs" :class="hotColdTooLarge ? 'text-[#94352a]' : 'text-[#8d8d7e]'">
          剩余 {{ supplementCount }} 个名额会由次热号补齐
        </p>

        <!-- 漏斗步数 -->
        <div class="rounded-lg border border-[#ddd4c7] bg-white p-4 space-y-3">
          <div class="flex items-center justify-between">
            <div>
              <span class="text-sm font-medium text-[#233142]"><span class="generate-field-icon funnel"></span>漏斗步数</span>
              <p class="text-[11px] text-[#9a9385]">
                {{ isQXC ? "每个位置独立压缩数字池，保留重复和位置顺序" : "三步逐步压缩号码池，最终保留 N 个作为推荐组合源" }}
              </p>
            </div>
            <div class="text-xs font-mono text-[#3f5b6d] bg-[#dfeaf0] rounded px-2 py-1">
              {{ isQXC ? "每位 10" : "49" }} → <strong>{{ activePool1Size }}</strong> → <strong>{{ activePool2Size }}</strong> → <strong class="text-[#8d6220]">{{ activePool3Size }}</strong>
            </div>
          </div>
          <div v-if="isQXC" class="grid grid-cols-1 gap-3 sm:grid-cols-4">
            <div>
              <label class="text-xs text-[#6c7570]">第一层/每位</label>
              <div class="flex items-center gap-2 mt-1">
                <input type="range" min="2" max="10" v-model.number="layered.qxc_pool1_size" class="flex-1" />
                <span class="w-8 text-center text-sm font-semibold text-[#233142]">{{ layered.qxc_pool1_size }}</span>
              </div>
            </div>
            <div>
              <label class="text-xs text-[#6c7570]">第二层/每位</label>
              <div class="flex items-center gap-2 mt-1">
                <input type="range" min="2" max="8" v-model.number="layered.qxc_pool2_size" class="flex-1" />
                <span class="w-8 text-center text-sm font-semibold text-[#233142]">{{ layered.qxc_pool2_size }}</span>
              </div>
            </div>
            <div>
              <label class="text-xs text-[#6c7570]">最终/每位</label>
              <div class="flex items-center gap-2 mt-1">
                <input type="range" min="1" max="6" v-model.number="layered.qxc_pool3_size" class="flex-1" />
                <span class="w-8 text-center text-sm font-semibold text-[#8d6220]">{{ layered.qxc_pool3_size }}</span>
              </div>
            </div>
            <div>
              <label class="text-xs text-[#6c7570]">输出组数</label>
              <div class="flex items-center gap-2 mt-1">
                <input type="range" min="1" max="10" v-model.number="layered.count" class="flex-1" />
                <span class="w-8 text-center text-sm font-semibold text-[#233142]">{{ layered.count }}</span>
              </div>
            </div>
          </div>
          <div v-else class="grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div>
              <label class="text-xs text-[#6c7570]">第一步保留</label>
              <div class="flex items-center gap-2 mt-1">
                <input type="range" min="6" max="30" v-model.number="layered.pool1_size" class="flex-1" />
                <span class="w-8 text-center text-sm font-semibold text-[#233142]">{{ layered.pool1_size }}</span>
              </div>
            </div>
            <div>
              <label class="text-xs text-[#6c7570]">第二步保留</label>
              <div class="flex items-center gap-2 mt-1">
                <input type="range" min="6" max="20" v-model.number="layered.pool2_size" class="flex-1" />
                <span class="w-8 text-center text-sm font-semibold text-[#233142]">{{ layered.pool2_size }}</span>
              </div>
            </div>
            <div>
              <label class="text-xs text-[#6c7570]">最终保留</label>
              <div class="flex items-center gap-2 mt-1">
                <input type="range" min="6" max="12" v-model.number="layered.pool3_size" class="flex-1" />
                <span class="w-8 text-center text-sm font-semibold text-[#8d6220]">{{ layered.pool3_size }}</span>
              </div>
            </div>
          </div>
          <p v-if="poolSizeError" class="text-xs text-[#94352a]"><span class="generate-inline-alert"></span>{{ poolSizeError }}</p>
          <p v-else-if="isQXC" class="text-xs text-[#5a8a7a]">
            ✓ 每位最终池 {{ layered.qxc_pool3_size }} 个数字，按位置生成 {{ layered.count }} 组可重复组合
          </p>
          <p v-else-if="layered.pool3_size > 6" class="text-xs text-[#5a8a7a]">
            ✓ 最终池 {{ layered.pool3_size }} 个号码，将自动产生多组 6 选组合推荐
          </p>
          <p v-else class="text-xs text-[#7d867f]">
            最终池 6 个号码 = 单组推荐；调大可获多组组合
          </p>
        </div>
      </div>

      <!-- 进阶选项（折叠） -->
      <div class="rounded-xl border border-[#e3d8c4] bg-[#fdfaf3]">
        <button
          type="button"
          @click="showAdvanced = !showAdvanced"
          class="generate-advanced-toggle w-full flex items-center justify-between gap-4 px-5 py-3 text-left hover:bg-[#fff7e8] transition"
        >
          <div class="flex min-w-0 flex-1 flex-wrap items-center gap-2">
            <span class="rounded-md bg-[#e8e0cc] px-2 py-0.5 text-[11px] font-bold text-[#7a6740]">进阶</span>
            <span class="text-sm font-semibold text-[#233142]">高级筛选条件</span>
            <span class="text-xs text-[#9a9385]">（走势、奇偶、大小、和值、胆码、杀号）</span>
          </div>
          <span class="shrink-0 text-[#8d6f47] transition-transform" :class="showAdvanced ? 'rotate-180' : ''">▾</span>
        </button>
        <div v-if="showAdvanced" class="px-5 pb-5 space-y-4 border-t border-[#e3d8c4]">
          <div class="grid grid-cols-1 gap-4 lg:grid-cols-2 mt-4">
            <!-- 走势 -->
            <div>
              <label class="text-sm font-medium text-[#233142]"><span class="generate-field-icon trend"></span>近期走势期数</label>
              <select v-model.number="layered.trend_periods" class="mt-1 w-full rounded-lg border border-[#ddd4c7] bg-white px-3 py-2 text-sm">
                <option :value="10">近 10 期</option>
                <option :value="20">近 20 期</option>
                <option :value="30">近 30 期</option>
                <option :value="50">近 50 期</option>
              </select>
            </div>
            <div v-if="!isQXC">
              <label class="text-sm font-medium text-[#233142]"><span class="generate-field-icon link"></span>连号要求</label>
              <select v-model="layered.consecutive" class="mt-1 w-full rounded-lg border border-[#ddd4c7] bg-white px-3 py-2 text-sm">
                <option value="any">不限</option>
                <option value="include">偏好出现在连号场次的号</option>
                <option value="exclude">偏好出现在无连号场次的号</option>
              </select>
            </div>
            <!-- 统计 -->
            <div>
              <label class="text-sm font-medium text-[#233142]"><span class="generate-field-icon balance"></span>奇偶偏好</label>
              <select v-model="layered.odd_even" class="mt-1 w-full rounded-lg border border-[#ddd4c7] bg-white px-3 py-2 text-sm">
                <option value="any">不限</option>
                <option value="more_odd">偏奇</option>
                <option value="more_even">偏偶</option>
                <option value="balanced">奇偶平衡</option>
              </select>
            </div>
            <div>
              <label class="text-sm font-medium text-[#233142]"><span class="generate-field-icon measure"></span>大小偏好</label>
              <select v-model="layered.big_small" class="mt-1 w-full rounded-lg border border-[#ddd4c7] bg-white px-3 py-2 text-sm">
                <option value="any">不限</option>
                <option value="more_big">{{ isQXC ? "偏大（5-9）" : "偏大（>24）" }}</option>
                <option value="more_small">{{ isQXC ? "偏小（0-4）" : "偏小（≤24）" }}</option>
                <option value="balanced">大小平衡</option>
              </select>
            </div>
            <!-- 和值 -->
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="text-sm font-medium text-[#233142]">和值下限</label>
                <input type="number" v-model.number="layered.sum_min" :placeholder="isQXC ? '前 6 位和值，不限' : '不限'" class="mt-1 w-full rounded-lg border border-[#ddd4c7] bg-white px-3 py-2 text-sm" />
              </div>
              <div>
                <label class="text-sm font-medium text-[#233142]">和值上限</label>
                <input type="number" v-model.number="layered.sum_max" :placeholder="isQXC ? '前 6 位和值，不限' : '不限'" class="mt-1 w-full rounded-lg border border-[#ddd4c7] bg-white px-3 py-2 text-sm" />
              </div>
            </div>
            <div></div>
            <!-- 胆码 / 杀号 -->
            <div>
              <label class="text-sm font-medium text-[#233142]"><span class="generate-field-icon include"></span>胆码（必含）</label>
              <p class="text-[11px] text-[#9a9385]">{{ isQXC ? "0-9 数字，最多 3 个，系统会分配到位置池" : "最多 3 个，逗号或空格分隔" }}</p>
              <input v-model="mustIncludeInput" :placeholder="isQXC ? '例如：0, 7, 9' : '例如：7, 23, 45'" class="mt-1 w-full rounded-lg border border-[#ddd4c7] bg-white px-3 py-2 text-sm" />
            </div>
            <div>
              <label class="text-sm font-medium text-[#233142]"><span class="generate-field-icon exclude"></span>杀号（必排）</label>
              <p class="text-[11px] text-[#9a9385]">{{ isQXC ? "0-9 数字，所有位置都会排除" : "逗号或空格分隔" }}</p>
              <input v-model="mustExcludeInput" :placeholder="isQXC ? '例如：1, 3, 6' : '例如：1, 13, 26'" class="mt-1 w-full rounded-lg border border-[#ddd4c7] bg-white px-3 py-2 text-sm" />
            </div>
          </div>
        </div>
      </div>

      <!-- 运行按钮 -->
      <div class="flex flex-wrap items-center justify-end gap-3">
        <button
          type="button"
          @click="resetSimulation"
          class="generate-reset-btn inline-flex items-center justify-center rounded-lg px-6 py-3 text-base font-semibold transition"
        >
          重置
        </button>
        <button
          type="button"
          @click="runLayered"
          :disabled="layeredLoading || !!poolSizeError"
          class="inline-flex items-center justify-center rounded-lg bg-[#3f5b6d] px-8 py-3 text-base font-semibold text-white transition hover:bg-[#2c4250] disabled:opacity-50 shadow-md"
        >
          <span>{{ layeredLoading ? "筛选中..." : (layeredResult ? "再来一次" : "运行分层漏斗") }}</span>
        </button>
      </div>
      <p v-if="layeredError" class="rounded-lg bg-[#fbe2dc] px-4 py-3 text-sm text-[#94352a]">{{ layeredError }}</p>
    </section>

    <!-- 简单策略控制区 -->
    <section v-else class="generate-simple-controls card-stripe p-6 sm:p-8">
      <div class="flex flex-col gap-5 lg:flex-row lg:items-center">
        <div class="generate-count-row flex flex-col gap-3 sm:flex-row sm:items-center">
          <label class="whitespace-nowrap text-sm font-semibold tracking-[0.08em] text-[#6c7570]">生成组数</label>
          <div class="generate-count-picker grid grid-cols-5 gap-1 rounded-xl bg-[#f7f2e9] p-1 sm:flex">
            <button
              v-for="n in 10"
              :key="n"
              type="button"
              :aria-pressed="count === n"
              @click="count = n"
              class="h-10 min-w-0 rounded-lg text-sm font-semibold transition-all sm:w-10"
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
          type="button"
          @click="resetSimulation"
          class="generate-reset-btn ml-0 inline-flex items-center gap-2 rounded-lg px-6 py-3 text-base font-semibold transition lg:ml-auto"
        >
          重置
        </button>
        <button
          type="button"
          @click="generate"
          :disabled="loading"
          class="ml-0 inline-flex items-center gap-2 rounded-lg bg-[#8d6f47] px-7 py-3 text-base font-semibold text-white transition hover:bg-[#6f5737] disabled:opacity-50"
        >
          <span>{{ loading ? "生成中..." : (result ? "再来一次" : "生成组合") }}</span>
        </button>
      </div>
    </section>

    <!-- 七彩彩票位置分层结果 -->
    <div v-if="isQxcLayeredResult && strategy === 'layered'" class="space-y-4">
      <section class="card-stripe overflow-hidden">
        <div class="flex flex-wrap items-center gap-3 border-b border-[#e6ddd0] bg-[#f7f2e9] px-6 py-4">
          <span class="flex h-7 w-7 items-center justify-center rounded-full bg-[#3f5b6d] text-xs font-bold text-white">7</span>
          <div>
            <h2 class="text-base font-bold text-[#233142]">七星彩位置漏斗</h2>
            <p class="text-xs text-[#7d867f]">每一位独立筛选 0-9，保留位置顺序与重复数字。</p>
          </div>
          <span class="ml-auto rounded-full border border-[#bdd0da] bg-[#eaf4f7] px-3 py-1 text-xs font-semibold text-[#3f5b6d]">
            近 {{ layeredResult.stats.draws_analyzed }} 期开奖
          </span>
        </div>
        <div class="grid grid-cols-1 gap-px bg-[#eadfce] sm:grid-cols-2 xl:grid-cols-3">
          <div
            v-for="pool in layeredResult.position_pools"
            :key="'qxc-position-' + pool.position"
            class="bg-[#fffaf2] p-5"
          >
            <div class="mb-3 flex items-center justify-between gap-3">
              <div>
                <p class="text-xs font-semibold tracking-[0.14em] text-[#8d6f47]">POSITION {{ pool.position }}</p>
                <h3 class="mt-1 text-base font-semibold text-[#233142]">第 {{ pool.position }} 位候选</h3>
              </div>
              <span class="rounded-full bg-[#edf3f6] px-2.5 py-1 text-xs font-semibold text-[#3f5b6d]">
                {{ pool.pool1.length }} → {{ pool.pool2.length }} → {{ pool.pool3.length }}
              </span>
            </div>
            <div class="flex flex-wrap gap-1.5">
              <NumberBall
                v-for="(n, numberIndex) in pool.pool3"
                :key="`qxc-p${pool.position}-final-${numberIndex}-${n}`"
                :number="n"
                :lotteryType="lotteryType"
                size="md"
              />
            </div>
            <div class="mt-3 grid grid-cols-2 gap-2 text-[11px] text-[#7d867f]">
              <div class="rounded-lg bg-white/70 px-3 py-2">
                <span class="font-semibold text-[#c05c3a]">热</span>
                <span class="ml-1">{{ (pool.hot_numbers || []).join("、") || "-" }}</span>
              </div>
              <div class="rounded-lg bg-white/70 px-3 py-2">
                <span class="font-semibold text-[#3f5b6d]">冷</span>
                <span class="ml-1">{{ (pool.cold_numbers || []).join("、") || "-" }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="card-stripe p-5">
        <div class="flex flex-col gap-4 lg:flex-row lg:items-center">
          <div class="flex-1">
            <p class="text-sm font-semibold text-[#233142]">{{ specialLabel }}候选</p>
            <p class="mt-1 text-xs text-[#7d867f]">后区从 0-14 独立筛选，不参与前 6 位去重。</p>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-xs text-[#7d867f]">推荐</span>
            <NumberBall :number="layeredResult.back_zone?.pick ?? layeredResult.special_pick" :lotteryType="lotteryType" size="md" is-special />
            <span class="ml-2 text-xs text-[#7d867f]">候选</span>
            <NumberBall
              v-for="(n, idx) in (layeredResult.back_zone?.pool3 || layeredResult.special_candidates || [])"
              :key="'qxc-special-' + idx + '-' + n"
              :number="n"
              :lotteryType="lotteryType"
              size="sm"
              is-special
            />
          </div>
        </div>
      </section>

      <section class="card-stripe overflow-hidden">
        <div class="flex flex-wrap items-center gap-3 border-b border-[#f0dcac] bg-gradient-to-r from-[#fdf5e4] to-[#fffaeb] px-6 py-4">
          <span class="generate-result-icon"></span>
          <div>
            <h2 class="text-base font-bold text-[#233142]">位置组合</h2>
            <p class="text-xs text-[#8d6220]">前 6 位可重复，后区独立生成；每组保留原始位置顺序。</p>
          </div>
          <span class="ml-auto rounded-full border border-[#e6c87a] bg-[#fdf0cd] px-3 py-1 text-xs font-semibold text-[#8d6220]">专用漏斗</span>
        </div>
        <div class="p-5 space-y-3">
          <div
            v-for="(combo, idx) in layeredResult.combinations"
            :key="'qxc-combo-' + idx"
            class="flex flex-col gap-3 rounded-lg border border-[#e3d8c4] bg-[#fffaf0] px-4 py-4 transition hover:border-[#c8952a] sm:flex-row sm:items-center"
          >
            <span class="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-[#3f5b6d] text-xs font-bold text-white">{{ idx + 1 }}</span>
            <div class="flex flex-1 flex-wrap items-center gap-2">
              <NumberBall
                v-for="(n, ballIndex) in combo.regular"
                :key="`qxc-c-${idx}-${ballIndex}-${n}`"
                :number="n"
                :lotteryType="lotteryType"
                size="md"
              />
              <span class="mx-1 text-lg text-[#cfbea6]">+</span>
              <NumberBall :number="combo.special" :lotteryType="lotteryType" size="md" is-special />
            </div>
            <div class="grid grid-cols-3 gap-2 text-center text-xs text-[#7d867f] sm:min-w-[220px]">
              <div class="rounded-md bg-white/70 px-2 py-1">和值 <strong class="text-[#233142]">{{ combo.sum }}</strong></div>
              <div class="rounded-md bg-white/70 px-2 py-1">重复 <strong class="text-[#233142]">{{ combo.repeated_count }}</strong></div>
              <div class="rounded-md bg-white/70 px-2 py-1">跨度 <strong class="text-[#233142]">{{ combo.span }}</strong></div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- 分层漏斗结果 -->
    <div v-else-if="layeredResult && strategy === 'layered'" class="space-y-4">

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

      <!-- Step 3: 最终池 -->
      <section class="card-stripe overflow-hidden">
        <div class="flex items-center gap-3 bg-[#fdf5e4] px-6 py-3 border-b border-[#f0dcac]">
          <span class="flex h-6 w-6 items-center justify-center rounded-full bg-[#c8952a] text-xs font-bold text-white">3</span>
          <span class="text-sm font-semibold text-[#233142]">最终号码池</span>
          <span class="text-xs text-[#a07820]">{{ layeredResult.stats.pool2_size }} → <strong>{{ layeredResult.stats.pool3_size }}</strong> 个</span>
        </div>
        <div class="p-5 space-y-3">
          <div class="flex flex-wrap gap-1.5">
            <NumberBall v-for="n in layeredResult.pool3" :key="'p3-' + n" :number="n" :lotteryType="lotteryType" size="sm" />
          </div>
          <div v-if="layeredResult.pool3_eliminated?.length" class="flex items-center gap-1.5 flex-wrap">
            <span class="text-xs text-[#aaa] mr-1">淘汰：</span>
            <span
              v-for="n in layeredResult.pool3_eliminated"
              :key="'e3-' + n"
              class="inline-flex h-7 w-7 items-center justify-center rounded-full border border-[#ddd] bg-[#f5f5f5] text-xs text-[#bbb] line-through"
            >{{ n }}</span>
          </div>
        </div>
      </section>

      <!-- 推荐组合（多组）-->
      <section class="card-stripe overflow-hidden">
        <div class="flex items-center gap-3 bg-gradient-to-r from-[#fdf5e4] to-[#fffaeb] px-6 py-4 border-b border-[#f0dcac]">
          <span class="generate-result-icon"></span>
          <div>
            <h2 class="text-base font-bold text-[#233142]">推荐组合</h2>
            <p class="text-xs text-[#8d6220]">
              从最终池按综合得分排出 Top {{ (layeredResult.combinations || []).length }} 组
              <span v-if="isSSQ">（6 红 + 1 蓝）</span>
              <span v-else>6 号（红色为主号）</span>
            </p>
          </div>
          <span class="ml-auto rounded-full border border-[#e6c87a] bg-[#fdf0cd] px-3 py-1 text-xs font-semibold text-[#8d6220]">分层漏斗</span>
        </div>
        <div class="p-5 space-y-3">
          <div
            v-for="(combo, idx) in layeredResult.combinations"
            :key="'combo-' + idx"
            class="flex items-center gap-3 rounded-lg border border-[#e3d8c4] bg-[#fffaf0] px-4 py-3 hover:border-[#c8952a] transition"
          >
            <span class="flex-shrink-0 w-7 h-7 flex items-center justify-center rounded-full bg-[#c8952a] text-xs font-bold text-white">{{ idx + 1 }}</span>
            <div class="flex flex-wrap items-center gap-1.5 flex-1">
              <NumberBall v-for="n in combo.numbers" :key="'c-' + idx + '-' + n" :number="n" :lotteryType="lotteryType" size="md" />
              <!-- SSQ: 每组组合后跟一个蓝球（用推荐蓝球） -->
              <template v-if="isSSQ">
                <span class="mx-1 text-lg text-[#cfbea6]">+</span>
                <NumberBall :number="layeredResult.special_pick" :lotteryType="lotteryType" size="md" is-special />
              </template>
            </div>
            <div class="flex-shrink-0 text-right text-xs text-[#7d867f]">
              <div>和值 <strong class="text-[#233142]">{{ combo.sum }}</strong></div>
              <div class="text-[10px] text-[#aaa]">得分 {{ combo.score }}</div>
            </div>
          </div>
          <p v-if="!layeredResult.combinations || layeredResult.combinations.length === 0" class="text-sm text-[#94352a]">
            没有符合和值范围的组合，请放宽和值过滤。
          </p>
        </div>
      </section>

      <!-- 蓝球 / 特码 信息卡（根据彩种切换语义） -->
      <section class="card-stripe p-5">
        <div class="flex items-start gap-4">
          <div
            class="flex-shrink-0 flex h-12 w-12 items-center justify-center rounded-xl text-xl"
            :class="isSSQ ? 'bg-[#dde9f7]' : 'bg-[#dfeaf0]'"
          ></div>
          <div class="flex-1">
            <div class="flex items-center gap-2">
              <p class="text-sm font-semibold text-[#233142]">
                {{ isSSQ ? "蓝球推荐（头奖必含）" : "特码辅助参考" }}
              </p>
              <span
                v-if="!isSSQ"
                class="text-[10px] text-[#9a9385] bg-[#f3eee2] rounded px-1.5 py-0.5"
              >仅供参考</span>
              <span
                v-else
                class="text-[10px] text-[#3a6fbc] bg-[#e0ecfd] rounded px-1.5 py-0.5 border border-[#a8c5f5]"
              >6红+1蓝=一等奖</span>
            </div>
            <p class="text-xs text-[#7d867f] mt-0.5">
              {{ isSSQ
                ? "蓝球与红球独立开奖，按近期出现频次排序"
                : "特码不影响头奖，按近期出现频次排序" }}
            </p>
            <div class="mt-3 flex items-center gap-2 flex-wrap">
              <span class="text-xs text-[#7d867f]">推荐：</span>
              <NumberBall :number="layeredResult.special_pick" :lotteryType="lotteryType" size="md" is-special />
              <span class="text-xs text-[#7d867f] ml-3">其他候选：</span>
              <NumberBall
                v-for="n in (layeredResult.special_candidates || []).filter(n => n !== layeredResult.special_pick)"
                :key="'spc-' + n"
                :number="n"
                :lotteryType="lotteryType"
                size="sm"
                is-special
              />
            </div>
          </div>
        </div>
      </section>

      <p class="text-xs text-center text-[#8d8d7e]">分析范围：近 {{ layeredResult.stats.draws_analyzed }} 期开奖</p>
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

        <!-- SSQ/QXC: 前区 + 后区同行；MarkSix 特码仅作辅助显示 -->
        <div v-if="isSSQ || isQXC" class="flex flex-wrap items-center gap-4">
          <NumberBall
            v-for="(n, ballIndex) in set.regular"
            :key="`regular-${idx}-${ballIndex}`"
            :number="n"
            :lotteryType="lotteryType"
            size="xl"
          />
          <span class="mx-1 text-2xl text-[#cfbea6]">+</span>
          <NumberBall :number="set.special" :lotteryType="lotteryType" size="xl" is-special />
        </div>

        <!-- MarkSix: 主号 6 个，特码移到辅助小行 -->
        <template v-else>
          <div class="flex flex-wrap items-center gap-4">
            <NumberBall
              v-for="n in set.regular"
              :key="n"
              :number="n"
              :lotteryType="lotteryType"
              size="xl"
            />
          </div>
          <div class="mt-4 flex items-center gap-2 rounded-lg bg-[#f7f2e9] px-4 py-2 text-xs text-[#7d867f]">
            <span>特码辅助：</span>
            <NumberBall :number="set.special" :lotteryType="lotteryType" size="sm" is-special />
            <span class="text-[10px] text-[#9a9385]">（仅供参考，不影响头奖）</span>
          </div>
        </template>

        <div class="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-6">
          <div
            v-for="(ball, statIndex) in statBalls(set)"
            :key="`stat-${idx}-${statIndex}`"
            class="rounded-lg border border-[#e2d8ca] bg-[#faf7f0] p-3 text-center"
          >
            <NumberBall
              :number="ball.number"
              :lotteryType="lotteryType"
              size="md"
              :is-special="ball.special"
            />
            <div class="mt-2 text-xs font-medium text-[#6f7772]">
              频次 {{ freqForNum(ball.number)?.total_appearances || "?" }}
            </div>
            <div
              v-if="freqForNum(ball.number)?.consecutive_missed > 0"
              class="mt-1 text-xs font-semibold"
              :class="freqForNum(ball.number)?.consecutive_missed > 20 ? 'text-[#b96d63]' : 'text-[#7d867f]'"
            >
              遗漏 {{ freqForNum(ball.number)?.consecutive_missed }} 期
            </div>
            <div v-else class="mt-1 text-xs font-semibold text-[#71897d]">最近出现</div>
          </div>
        </div>
      </section>
    </div>

    <!-- 空态 -->
    <section v-if="!result && !layeredResult" class="card-stripe p-12 text-center sm:p-20">
      <div class="generate-empty-icon mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-[#f3e6d6] text-3xl text-[#8d6f47]">
        ✦
      </div>
      <p class="text-xl font-semibold text-[#233142]">选择策略，点击生成</p>
      <p class="mx-auto mt-2 max-w-md text-base leading-7 text-[#6f7772]">
        系统会根据所选策略生成模拟号码，并显示对应的历史频次与遗漏情况。
      </p>
    </section>

    <p class="text-center text-sm text-[#6f7772]">
      免责声明：模拟选号仅供娱乐参考，不构成任何参与建议。彩票开奖结果具有随机性，历史数据不能保证未来结果。
    </p>
  </div>
</template>
