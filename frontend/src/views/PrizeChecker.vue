<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { api, lotteryType } from "../api.js";
import { getLotteryMeta } from "../lotteryMeta.js";
import { useSEO } from "../composables/useSEO.js";

useSEO({
  title: "对奖器 - 双色球、六合彩、7星彩中奖查询",
  description:
    "输入你选的号码，自动对照开奖结果，查询命中几个号码、中了第几等奖。数据对照仅供娱乐参考，最终奖级与奖金以官方公告为准。",
});

const meta = computed(() => getLotteryMeta(lotteryType.value));
const isSSQ = computed(() => lotteryType.value === "ssq");
const isQXC = computed(() => lotteryType.value === "qxc");
const isMarkSix = computed(() => lotteryType.value === "marksix");

// 号码结构（按彩种）
const mainCount = 6;
const hasSpecialInput = computed(() => isSSQ.value || isQXC.value); // 六合彩用户只选 6 个，特码是开出的
const mainRange = computed(() => {
  if (isSSQ.value) return { min: 1, max: 33, label: "红球", positional: false };
  if (isQXC.value) return { min: 0, max: 9, label: "前区", positional: true };
  return { min: 1, max: 49, label: "选号", positional: false }; // marksix
});
const specialRange = computed(() => {
  if (isSSQ.value) return { min: 1, max: 16, label: "蓝球" };
  if (isQXC.value) return { min: 0, max: 14, label: "后区" };
  return null;
});

const draws = ref([]);
const selectedKey = ref("");
const loading = ref(false);
const mainInputs = ref(["", "", "", "", "", ""]);
const specialInput = ref("");
const result = ref(null);
const inputError = ref("");

const selectedDraw = computed(() => draws.value.find((d) => d.draw_number === selectedKey.value) || null);

function drawMain(d) {
  return [d.num1, d.num2, d.num3, d.num4, d.num5, d.num6].map(Number);
}

async function loadDraws() {
  loading.value = true;
  result.value = null;
  try {
    const res = await api.draws({ page: 1, per_page: 30 });
    draws.value = res.draws || [];
    selectedKey.value = draws.value[0]?.draw_number || "";
  } catch (e) {
    console.error(e);
    draws.value = [];
  } finally {
    loading.value = false;
  }
}
onMounted(loadDraws);
watch(lotteryType, () => {
  mainInputs.value = ["", "", "", "", "", ""];
  specialInput.value = "";
  result.value = null;
  inputError.value = "";
  loadDraws();
});

// —— 判奖逻辑（按官方规则）——
function judge(type, userMain, userSpecial, draw) {
  const dm = drawMain(draw);
  const ds = Number(draw.special_num);

  if (type === "marksix") {
    // 用户选 6 个号；与 6 正码比对（集合），特码看用户号是否含开出的特码
    const zheng = userMain.filter((n) => dm.includes(n)).length;
    const te = userMain.includes(ds);
    let level = null;
    if (zheng === 6) level = 1;
    else if (zheng === 5 && te) level = 2;
    else if (zheng === 5) level = 3;
    else if (zheng === 4 && te) level = 4;
    else if (zheng === 4) level = 5;
    else if (zheng === 3 && te) level = 6;
    else if (zheng === 3) level = 7;
    const names = { 1: "头奖", 2: "二奖", 3: "三奖", 4: "四奖", 5: "五奖", 6: "六奖", 7: "七奖" };
    return { level, name: level ? names[level] : null, detail: `命中 ${zheng} 个正码${te ? " + 特别号" : ""}`, hitMain: zheng, hitSpecial: te };
  }

  if (type === "ssq") {
    const red = userMain.filter((n) => dm.includes(n)).length;
    const blue = userSpecial === ds;
    let level = null;
    if (red === 6 && blue) level = 1;
    else if (red === 6) level = 2;
    else if (red === 5 && blue) level = 3;
    else if (red === 5 || (red === 4 && blue)) level = 4;
    else if (red === 4 || (red === 3 && blue)) level = 5;
    else if (blue) level = 6; // 中蓝球即得六等奖（2/1/0 红 + 蓝）
    const names = { 1: "一等奖", 2: "二等奖", 3: "三等奖", 4: "四等奖", 5: "五等奖", 6: "六等奖" };
    return { level, name: level ? names[level] : null, detail: `命中 ${red} 个红球${blue ? " + 蓝球" : ""}`, hitMain: red, hitSpecial: blue };
  }

  // qxc：按位置比对前区 6 位 + 后区 1 位
  let front = 0;
  for (let i = 0; i < 6; i++) if (userMain[i] === dm[i]) front++;
  const back = userSpecial === ds;
  let level = null;
  if (front === 6 && back) level = 1;
  else if (front === 6) level = 2;
  else if (front === 5 && back) level = 3;
  else if (front === 5) level = 4;
  else if (front === 4 && back) level = 5;
  else if (front === 4) level = 6;
  const names = { 1: "一等奖", 2: "二等奖", 3: "三等奖", 4: "四等奖", 5: "五等奖", 6: "六等奖" };
  return { level, name: level ? names[level] : null, detail: `前区命中 ${front} 位${back ? " + 后区" : ""}`, hitMain: front, hitSpecial: back, qxc: true };
}

function check() {
  inputError.value = "";
  result.value = null;
  const d = selectedDraw.value;
  if (!d) {
    inputError.value = "请先选择开奖期号。";
    return;
  }
  const r = mainRange.value;
  const main = mainInputs.value.map((v) => Number(String(v).trim()));
  if (main.some((n) => !Number.isInteger(n) || String(mainInputs.value[main.indexOf(n)]).trim() === "")) {
    // 简单校验：6 个主号都要填
  }
  for (let i = 0; i < mainCount; i++) {
    const v = String(mainInputs.value[i]).trim();
    if (v === "" || !Number.isInteger(Number(v)) || Number(v) < r.min || Number(v) > r.max) {
      inputError.value = `请填写完整的 6 个${r.label}号码（${r.min}-${r.max}）。`;
      return;
    }
  }
  if (!r.positional) {
    const uniq = new Set(main);
    if (uniq.size !== mainCount) {
      inputError.value = `${r.label}号码不能重复。`;
      return;
    }
  }
  let special = null;
  if (hasSpecialInput.value) {
    const sv = String(specialInput.value).trim();
    const sr = specialRange.value;
    if (sv === "" || !Number.isInteger(Number(sv)) || Number(sv) < sr.min || Number(sv) > sr.max) {
      inputError.value = `请填写${sr.label}号码（${sr.min}-${sr.max}）。`;
      return;
    }
    special = Number(sv);
  }
  result.value = judge(lotteryType.value, main, special, d);
}
</script>

<template>
  <div class="space-y-6 pb-16">
    <section class="ref-card p-6 sm:p-8">
      <p class="mb-2 text-xs font-semibold tracking-[0.22em] text-[#9b7a45]">PRIZE CHECK · 对奖器</p>
      <h1 class="text-2xl font-semibold text-[#1c3342] sm:text-3xl">{{ meta.label }}对奖器</h1>
      <p class="mt-2 max-w-2xl text-sm leading-7 text-[#5f6868]">
        选择开奖期号，输入你选的号码，自动对照开奖结果，看命中几个、中了第几等奖。数据对照仅供娱乐参考，<strong>最终奖级与奖金以官方公告为准</strong>。
      </p>

      <!-- 期号选择 -->
      <div class="mt-6">
        <label class="block text-sm font-semibold text-[#233142]">对照开奖期号</label>
        <select
          v-model="selectedKey"
          class="mt-2 min-h-11 w-full max-w-xs rounded-md border border-[#d8cbb9] bg-[#fffaf2] px-3 text-sm text-[#233142] outline-none focus:border-[#b9863c] sm:w-auto"
        >
          <option v-if="loading" value="">加载中…</option>
          <option v-for="d in draws" :key="d.draw_number" :value="d.draw_number">
            {{ d.draw_number }} 期（{{ d.draw_date }}）
          </option>
        </select>
        <div v-if="selectedDraw" class="mt-3 flex flex-wrap items-center gap-2">
          <span class="text-xs text-[#7d867f]">开奖号码：</span>
          <span
            v-for="(n, i) in drawMain(selectedDraw)"
            :key="'d' + i"
            class="inline-flex h-8 min-w-8 items-center justify-center rounded-full bg-[#c85d5a] px-2 text-sm font-semibold text-white"
          >{{ isQXC ? n : String(n).padStart(2, "0") }}</span>
          <span class="px-1 text-[#9b7a45]">+</span>
          <span class="inline-flex h-8 min-w-8 items-center justify-center rounded-full bg-[#5d7d9f] px-2 text-sm font-semibold text-white">
            {{ isQXC ? selectedDraw.special_num : String(selectedDraw.special_num).padStart(2, "0") }}
          </span>
          <span class="text-xs text-[#9b7a45]">
            （{{ isSSQ ? "蓝球" : isQXC ? "后区" : "特码" }}）
          </span>
        </div>
      </div>

      <!-- 号码输入 -->
      <div class="mt-6">
        <label class="block text-sm font-semibold text-[#233142]">
          你的号码（{{ mainRange.label }} {{ mainRange.min }}-{{ mainRange.max }}{{ mainRange.positional ? "，按位置" : "" }}）
        </label>
        <div class="mt-2 flex flex-wrap items-end gap-2">
          <input
            v-for="(_, i) in mainInputs"
            :key="'m' + i"
            v-model="mainInputs[i]"
            type="number"
            :min="mainRange.min"
            :max="mainRange.max"
            inputmode="numeric"
            class="h-11 w-14 rounded-md border border-[#d8cbb9] bg-[#fffaf2] text-center text-sm font-semibold text-[#233142] outline-none focus:border-[#b9863c]"
            :placeholder="String(i + 1)"
          />
          <template v-if="hasSpecialInput">
            <span class="px-1 text-lg text-[#9b7a45]">+</span>
            <input
              v-model="specialInput"
              type="number"
              :min="specialRange.min"
              :max="specialRange.max"
              inputmode="numeric"
              class="h-11 w-14 rounded-md border border-[#5d7d9f] bg-[#eef3f8] text-center text-sm font-semibold text-[#233142] outline-none focus:border-[#3f6285]"
              :placeholder="specialRange.label"
            />
            <span class="text-xs text-[#7d867f]">{{ specialRange.label }}</span>
          </template>
        </div>
        <p v-if="isMarkSix" class="mt-2 text-xs text-[#7d867f]">
          六合彩对奖只需填你选的 6 个号码；特码由开奖产生，系统会自动判断你是否命中。
        </p>
      </div>

      <div class="mt-5 flex items-center gap-3">
        <button
          type="button"
          @click="check"
          class="min-h-11 rounded-md bg-[#233142] px-6 text-sm font-semibold text-white transition hover:bg-[#31465b]"
        >对奖</button>
        <span v-if="inputError" class="text-sm text-[#b96d63]">{{ inputError }}</span>
      </div>
    </section>

    <!-- 结果 -->
    <section v-if="result" class="ref-card p-6 sm:p-8">
      <div
        class="rounded-xl border p-5"
        :class="result.level ? 'border-[#cdab6c] bg-[#fff8ec]' : 'border-[#e2d8ca] bg-[#fffdf8]'"
      >
        <p class="text-lg font-semibold" :class="result.level ? 'text-[#9d6d3a]' : 'text-[#5f6868]'">
          {{ result.level ? `🎉 恭喜，命中 ${result.name}` : "未中奖" }}
        </p>
        <p class="mt-1 text-sm text-[#5f6868]">{{ result.detail }}</p>
        <p v-if="result.level" class="mt-2 text-xs text-[#7d867f]">
          具体奖金金额每期浮动，<strong>以官方公告为准</strong>。{{ result.qxc ? "7星彩奖级以官方奖级表为准。" : "" }}
        </p>
        <p v-else class="mt-2 text-xs text-[#7d867f]">
          本次未达到可中奖的命中条件。开奖结果具有随机性，仅供娱乐参考。
        </p>
      </div>
    </section>

    <p class="text-center text-xs leading-6 text-[#7d867f]/80">
      免责声明：对奖器仅按公开规则做号码对照，方便你自查，<strong>不构成任何投注建议，最终中奖结果与奖金以官方公告为准</strong>。开奖结果具有随机性，请理性娱乐。
    </p>
  </div>
</template>
