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
    value: "cold",
    label: "冷号观察",
    desc: "观察长期较少出现的号码，做均衡补位。",
    accent: "from-[#7a8f9c] to-[#576c79]",
    tag: "bg-[#e5edf0] text-[#4f6775] border-[#b7cad3]",
  },
  {
    value: "balanced",
    label: "冷热均衡",
    desc: "混合热号、中位号与冷号，保持分布自然。",
    accent: "from-[#7b9273] to-[#5c7155]",
    tag: "bg-[#e7efe4] text-[#5c7254] border-[#c3d2bd]",
  },
  {
    value: "overdue",
    label: "追遗漏",
    desc: "优先挑选近期较久未出现的号码，适合观察型策略。",
    accent: "from-[#c07a66] to-[#9d6251]",
    tag: "bg-[#f5e3dc] text-[#945b4b] border-[#deb5a7]",
  },
];

const strategy = ref("hot");
const count = ref(3);
const result = ref(null);
const loading = ref(false);
const freqData = ref([]);

const meta = computed(() => getLotteryMeta(lotteryType.value));
const lotteryLabel = computed(() => meta.value.label);
const helperText = computed(() =>
  meta.value.hasRollingPool
    ? "以历史数据做模拟组合，不展示任何官方推荐。"
    : "固定奖金玩法同样只适合做模拟组合与走势观察。"
);

function strategyInfo(value) {
  return strategies.find((item) => item.value === value) || strategies[0];
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

function freqForNum(number) {
  return freqData.value.find((item) => item.number === number);
}

watch(lotteryType, () => {
  result.value = null;
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
            按历史分布、冷热程度和常见搭配生成模拟组合，适合做娱乐型筛选和走势对照。
          </p>
        </div>
        <div class="rounded-lg border border-[#ddd4c7] bg-[#fffaf2] px-4 py-3 text-sm text-[#6a726d]">
          {{ helperText }}
        </div>
      </div>
    </section>

    <section class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3 stagger-children">
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

    <section class="card-stripe p-6 sm:p-8">
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

    <div v-if="result" class="space-y-5">
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

    <section v-else class="card-stripe p-12 text-center sm:p-20">
      <div class="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-[#f3e6d6] text-3xl text-[#8d6f47]">
        ✦
      </div>
      <p class="text-xl font-semibold text-[#233142]">选择策略，点击“生成组合”</p>
      <p class="mx-auto mt-2 max-w-md text-base leading-7 text-[#6f7772]">
        系统会根据所选策略生成一组可供观察的模拟号码，并显示对应的历史频次与遗漏情况。
      </p>
    </section>

    <p class="text-center text-sm text-[#6f7772]">
      免责声明：模拟选号仅供娱乐参考，不构成任何投注建议。彩票开奖结果具有随机性，历史数据不能预测未来结果。
    </p>
  </div>
</template>
