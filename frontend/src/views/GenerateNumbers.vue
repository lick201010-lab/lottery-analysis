<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { api, lotteryType } from "../api.js";
import NumberBall from "../components/NumberBall.vue";

const strategies = [
  {
    value: "hot",
    label: "热门号码",
    desc: "优先选择历史出现频率最高的号码",
    icon: "red",
    gradient: "from-[#f6465d] to-[#d63050]",
    light: "bg-[#2b3139] text-[#f6465d] border-[#f6465d]",
  },
  {
    value: "cold",
    label: "冷门号码",
    desc: "选择历史出现频率最低的号码",
    icon: "blue",
    gradient: "from-blue-500 to-blue-700",
    light: "bg-[#2b3139] text-blue-400 border-blue-400",
  },
  {
    value: "balanced",
    label: "均衡混合",
    desc: "混合热门、中等、冷门号码，分布更均匀",
    icon: "green",
    gradient: "from-[#0ecb81] to-[#0ab46e]",
    light: "bg-[#2b3139] text-[#0ecb81] border-[#0ecb81]",
  },
  {
    value: "weighted_random",
    label: "加权随机",
    desc: "按热度权重随机抽取，热门号码更易被选中但不固定",
    icon: "purple",
    gradient: "from-purple-500 to-purple-700",
    light: "bg-[#2b3139] text-purple-400 border-purple-400",
  },
  {
    value: "pair_chain",
    label: "号码链",
    desc: "从最热号码开始，逐个挑选经常共现的号码，形成搭配链",
    icon: "amber",
    gradient: "from-[#fcd535] to-[#f0b90b]",
    light: "bg-[#2b3139] text-[#fcd535] border-[#fcd535]",
  },
  {
    value: "overdue",
    label: "追遗漏",
    desc: "选择最久未开出的号码，适合追号策略",
    icon: "orange",
    gradient: "from-orange-500 to-orange-700",
    light: "bg-[#2b3139] text-orange-400 border-orange-400",
  },
];

const strategy = ref("hot");
const count = ref(3);
const result = ref(null);
const loading = ref(false);
const freqData = ref([]);

const lotteryLabel = computed(() =>
  lotteryType.value === "ssq" ? "双色球" : "六合彩"
);

function strategyInfo(s) {
  return strategies.find((x) => x.value === s) || strategies[0];
}

async function generate() {
  loading.value = true;
  try {
    const data = await api.generate(strategy.value, count.value);
    result.value = data;
    if (freqData.value.length === 0) {
      freqData.value = await api.frequency();
    }
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
}

function freqForNum(n) {
  return freqData.value.find((f) => f.number === n);
}

watch(lotteryType, () => {
  result.value = null;
  freqData.value = [];
});
</script>

<template>
  <div class="space-y-8 animate-fade-in-up">
    <div>
      <h1 class="text-2xl font-bold text-[#0d253d] tracking-tight">{{ lotteryLabel }} 模拟选号</h1>
      <p class="text-base text-[#64748d] mt-1">基于历史数据分析，智能生成号码组合</p>
    </div>

    <!-- Strategy Selection -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 stagger-children">
      <button
        v-for="s in strategies"
        :key="s.value"
        @click="strategy = s.value"
        class="text-left p-5 rounded-2xl border-2 transition-all duration-200"
        :class="
          strategy === s.value
            ? s.light + ' shadow-md scale-[1.02]'
            : 'border-[#e3e8ee] bg-white hover:border-[#64748d] hover:shadow-sm text-[#64748d]'
        "
      >
        <div class="flex items-center gap-3 mb-2">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-br" :class="s.gradient" v-if="strategy === s.value"></div>
          <div class="w-8 h-8 rounded-lg bg-[#f6f9fc]" v-else></div>
          <div class="font-bold text-base">{{ s.label }}</div>
        </div>
        <div class="text-sm opacity-70 leading-relaxed">{{ s.desc }}</div>
      </button>
    </div>

    <!-- Controls -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center gap-4 sm:gap-6 bg-white rounded-2xl border border-[#e3e8ee] p-6 shadow-sm card-lift card-stripe">
      <div class="flex items-center gap-3">
        <label class="text-base font-semibold text-[#64748d]">生成组数</label>
        <div class="flex gap-1 bg-[#f6f9fc] p-1 rounded-xl overflow-x-auto">
          <button
            v-for="n in 10"
            :key="n"
            @click="count = n"
            class="w-10 h-10 rounded-lg text-sm font-bold transition-all"
            :class="count === n ? 'bg-white text-[#533afd] shadow-sm' : 'text-[#64748d] hover:text-[#273951]'"
          >
            {{ n }}
          </button>
        </div>
      </div>
      <button
        @click="generate"
        :disabled="loading"
        class="btn-premium ml-auto inline-flex items-center gap-2 px-8 py-3.5 bg-[#533afd] text-white text-base font-bold rounded-xl hover:shadow-lg disabled:opacity-50"
      >
        <svg v-if="!loading" class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z"/></svg>
        <svg v-else class="w-5 h-5 animate-spin" fill="currentColor" viewBox="0 0 24 24"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/></svg>
        {{ loading ? "生成中..." : "生成号码" }}
      </button>
    </div>

    <!-- Generated Results -->
    <div v-if="result" class="space-y-5">
      <div
        v-for="(set, idx) in result.sets"
        :key="idx"
        class="bg-white rounded-2xl border border-[#e3e8ee] p-8 shadow-sm card-lift card-stripe"
      >
        <div class="flex items-center gap-4 mb-6">
          <span class="text-2xl font-extrabold text-[#e3e8ee]">#{{ idx + 1 }}</span>
          <span
            class="text-xs font-bold px-3 py-1.5 rounded-full border-2"
            :class="strategyInfo(set.strategy).light"
          >
            {{ strategyInfo(set.strategy).label }}
          </span>
        </div>

        <!-- Regular Numbers -->
        <div class="flex items-center gap-4 flex-wrap">
          <NumberBall
            v-for="n in set.regular"
            :key="n"
            :number="n"
            :lotteryType="lotteryType"
            size="xl"
          />
          <span class="text-3xl text-[#e3e8ee] mx-3 font-light">+</span>
          <NumberBall :number="set.special" :lotteryType="lotteryType" size="xl" is-special />
        </div>

        <!-- Number Stats -->
        <div class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-3 mt-8">
          <div
            v-for="n in set.regular.concat([set.special])"
            :key="'stat-' + n"
            class="text-center p-4 rounded-xl bg-[#f6f9fc] border border-[#f6f9fc] hover:border-[#e3e8ee] transition-colors"
          >
            <NumberBall :number="n" :lotteryType="lotteryType" size="md" />
            <div class="text-xs text-[#64748d] mt-2 font-medium">
              频次 {{ freqForNum(n)?.total_appearances || "?" }}
            </div>
            <div
              v-if="freqForNum(n)?.consecutive_missed > 0"
              class="text-xs font-bold mt-1"
              :class="
                freqForNum(n)?.consecutive_missed > 20
                  ? 'text-[#ea2261]'
                  : 'text-[#64748d]'
              "
            >
              遗漏 {{ freqForNum(n)?.consecutive_missed }} 期
            </div>
            <div v-else class="text-xs text-[#0ecb81] font-bold mt-1">最新出现</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div
      v-if="!result"
      class="bg-white rounded-2xl border border-[#e3e8ee] p-20 text-center shadow-sm card-lift card-stripe"
    >
      <div class="w-20 h-20 rounded-2xl bg-gradient-to-br from-[#f6f9fc] to-[#e3e8ee] flex items-center justify-center mx-auto mb-6">
        <svg class="w-10 h-10 text-[#533afd]" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z"/></svg>
      </div>
      <p class="text-xl font-bold text-[#273951]">选择策略，点击「生成号码」</p>
      <p class="text-base text-[#64748d] mt-2 max-w-md mx-auto">
        系统将基于历史数据统计分析，按所选策略为你生成数字组合
      </p>
    </div>

    <!-- Disclaimer -->
    <p class="text-sm text-[#64748d] text-center">
      免责声明：号码生成仅供娱乐参考，不构成任何投注建议。彩票开奖结果为随机事件，历史数据不能预测未来结果。
    </p>
  </div>
</template>
