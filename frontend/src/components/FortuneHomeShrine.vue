<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { api } from "../api.js";
import NumberBall from "./NumberBall.vue";

const props = defineProps({
  lotteryType: { type: String, required: true },
  lotteryLabel: { type: String, required: true },
  defaultDrawDate: { type: String, default: "" },
});

const USER_KEY_STORAGE = "yicai_fortune_user_key";
const zodiacOptions = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"];
const constellationOptions = [
  "白羊",
  "金牛",
  "双子",
  "巨蟹",
  "狮子",
  "处女",
  "天秤",
  "天蝎",
  "射手",
  "摩羯",
  "水瓶",
  "双鱼",
];
const offerings = [
  { type: "incense", label: "上香", note: "清香一柱", cost: 5, mark: "香" },
  { type: "peach", label: "桃子", note: "添一点甜", cost: 10, mark: "桃" },
  { type: "ingot", label: "元宝", note: "金气加持", cost: 30, mark: "宝" },
  { type: "pouch", label: "锦囊", note: "大运模式", cost: 60, mark: "锦" },
];

const userKey = ref("");
const profile = ref(null);
const todayResult = ref(null);
const selectedDrawDate = ref("");
const pointsBalance = ref(0);
const adRewardsRemaining = ref(0);
const adRewardPoints = ref(10);
const loading = ref(false);
const statusMessage = ref("");
const promptMode = ref(null);
const isShaking = ref(false);
const showOverlay = ref(false);
const overlayResult = ref(null);
const overlayEffect = ref({ level: 1, name: "清风小吉" });
const overlayMode = ref("result");
const adDialogOpen = ref(false);
const adSeconds = ref(0);
const adLoading = ref(false);
let adTimer = 0;

const profileComplete = computed(() => Boolean(profile.value?.zodiac && profile.value?.constellation));
const promptTitle = computed(() => (promptMode.value === "zodiac" ? "选择你的属相" : "选择你的星座"));
const promptOptions = computed(() => (promptMode.value === "zodiac" ? zodiacOptions : constellationOptions));
const hasTodayResult = computed(() => Boolean(todayResult.value));
const specialLabel = computed(() => {
  if (props.lotteryType === "ssq") return "蓝球";
  if (props.lotteryType === "qxc") return "后区";
  return "特码";
});
const mainButtonText = computed(() => {
  if (loading.value) return "正在请财神";
  if (!profile.value?.zodiac) return "填写属相";
  if (!profile.value?.constellation) return "填写星座";
  if (hasTodayResult.value) return "查看今日手气";
  return "摇一摇请财神";
});
const helperText = computed(() => {
  if (!profile.value?.zodiac) return "先填属相，财神会记住你的今日手气档案。";
  if (!profile.value?.constellation) return "再填星座，生成属于今天的一次娱乐手气。";
  if (hasTodayResult.value) return "今天已经请过财神，结果已保存，可随时查看。";
  return "选择开奖日期后轻点财神，摇出今日娱乐号码。";
});
const overlayNumbers = computed(() => overlayResult.value?.regular_numbers || []);
const overlaySpecial = computed(() => overlayResult.value?.special_number);
const overlayClass = computed(() => `effect-level-${overlayEffect.value?.level || 1}`);
const overlayTitle = computed(() => {
  if (overlayMode.value === "offering") return `${overlayEffect.value.name} · 上供回响`;
  return `${overlayEffect.value.name} · 今日手气签`;
});
const resultDisclosure = computed(() => {
  if (props.lotteryType === "ssq") return "双色球为 6 红 + 1 蓝；本结果仅供娱乐。";
  if (props.lotteryType === "qxc") return "七星彩按位生成，前 6 位可重复；本结果仅供娱乐。";
  return "六合彩头奖看 6 个正码，特码仅作娱乐参考。";
});

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

function normalizeDate(value) {
  const match = String(value || "").match(/\d{4}-\d{2}-\d{2}/);
  return match ? match[0] : todayIso();
}

function createUserKey() {
  const randomPart =
    typeof crypto !== "undefined" && crypto.randomUUID
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  return `fortune-${randomPart}`.slice(0, 80);
}

function ensureUserKey() {
  if (typeof window === "undefined") return "";
  const existing = window.localStorage.getItem(USER_KEY_STORAGE);
  if (existing) return existing;
  const created = createUserKey();
  window.localStorage.setItem(USER_KEY_STORAGE, created);
  return created;
}

function errorText(error) {
  const raw = error?.message || "操作失败，请稍后再试";
  const jsonStart = raw.indexOf("{");
  if (jsonStart >= 0) {
    try {
      const parsed = JSON.parse(raw.slice(jsonStart));
      return parsed.detail || raw;
    } catch {
      return raw;
    }
  }
  return raw.replace(/^API \d+:\s*/, "");
}

async function loadTodayStatus() {
  if (!userKey.value) return;
  try {
    const data = await api.fortuneToday({
      user_key: userKey.value,
      lottery_type: props.lotteryType,
      draw_date: selectedDrawDate.value,
    });
    profile.value = data.profile;
    todayResult.value = data.result;
    pointsBalance.value = data.points_balance || 0;
    adRewardPoints.value = data.ad_reward_points || 10;
    adRewardsRemaining.value = data.ad_rewards_remaining || 0;
    statusMessage.value = "";
  } catch (error) {
    statusMessage.value = errorText(error);
  }
}

async function savePromptChoice(value) {
  if (!userKey.value || !promptMode.value) return;
  const payload = {
    user_key: userKey.value,
    zodiac: profile.value?.zodiac,
    constellation: profile.value?.constellation,
  };
  if (promptMode.value === "zodiac") payload.zodiac = value;
  if (promptMode.value === "constellation") payload.constellation = value;
  loading.value = true;
  try {
    const data = await api.fortuneProfile(payload);
    profile.value = data.profile;
    promptMode.value = null;
    statusMessage.value = "";
  } catch (error) {
    statusMessage.value = errorText(error);
  } finally {
    loading.value = false;
  }
}

function closePrompt() {
  promptMode.value = null;
}

async function handleMainClick() {
  if (loading.value) return;
  if (!profile.value?.zodiac) {
    promptMode.value = "zodiac";
    return;
  }
  if (!profile.value?.constellation) {
    promptMode.value = "constellation";
    return;
  }
  if (todayResult.value) {
    openResultOverlay(todayResult.value);
    return;
  }
  loading.value = true;
  isShaking.value = true;
  try {
    const data = await api.fortuneGenerate({
      user_key: userKey.value,
      lottery_type: props.lotteryType,
      draw_date: selectedDrawDate.value,
      zodiac: profile.value.zodiac,
      constellation: profile.value.constellation,
    });
    profile.value = data.profile;
    todayResult.value = data.result;
    window.setTimeout(() => openResultOverlay(data.result), 520);
  } catch (error) {
    statusMessage.value = errorText(error);
  } finally {
    window.setTimeout(() => {
      isShaking.value = false;
      loading.value = false;
    }, 620);
  }
}

function openResultOverlay(result) {
  if (!result) return;
  overlayMode.value = "result";
  overlayResult.value = result;
  overlayEffect.value = {
    level: result.effect_level || 1,
    name: result.effect_name || "清风小吉",
  };
  showOverlay.value = true;
}

async function makeOffering(offering) {
  if (loading.value) return;
  if (!profileComplete.value) {
    statusMessage.value = "先完成属相和星座档案，再上供。";
    return;
  }
  loading.value = true;
  isShaking.value = true;
  try {
    const data = await api.fortuneOffering({
      user_key: userKey.value,
      offering_type: offering.type,
    });
    pointsBalance.value = data.points_balance || 0;
    overlayMode.value = "offering";
    overlayEffect.value = data.effect || { level: 1, name: "清风小吉" };
    overlayResult.value = todayResult.value;
    window.setTimeout(() => {
      showOverlay.value = true;
    }, 500);
    statusMessage.value = `${data.offering_label}已上供，积分余额 ${pointsBalance.value}`;
  } catch (error) {
    const message = errorText(error);
    statusMessage.value = message === "Insufficient points" ? "积分不足，先看广告赚一点香火积分。" : message;
  } finally {
    window.setTimeout(() => {
      isShaking.value = false;
      loading.value = false;
    }, 620);
  }
}

function startAdReward() {
  if (adLoading.value || adRewardsRemaining.value <= 0) return;
  adDialogOpen.value = true;
  adLoading.value = true;
  adSeconds.value = 15;
  if (adTimer) window.clearInterval(adTimer);
  adTimer = window.setInterval(async () => {
    if (adSeconds.value > 1) {
      adSeconds.value -= 1;
      return;
    }
    window.clearInterval(adTimer);
    adTimer = 0;
    await claimAdReward();
  }, 1000);
}

async function claimAdReward() {
  try {
    const data = await api.fortuneAdReward({ user_key: userKey.value });
    pointsBalance.value = data.points_balance || pointsBalance.value;
    adRewardsRemaining.value = data.ad_rewards_remaining || 0;
    statusMessage.value = `已获得 ${data.ad_reward_points || adRewardPoints.value} 积分。`;
  } catch (error) {
    statusMessage.value = errorText(error);
  } finally {
    adDialogOpen.value = false;
    adLoading.value = false;
    adSeconds.value = 0;
  }
}

function closeOverlay() {
  showOverlay.value = false;
}

function closeAdDialog() {
  if (adTimer) {
    window.clearInterval(adTimer);
    adTimer = 0;
  }
  adDialogOpen.value = false;
  adLoading.value = false;
  adSeconds.value = 0;
}

onMounted(() => {
  selectedDrawDate.value = normalizeDate(props.defaultDrawDate);
  userKey.value = ensureUserKey();
  loadTodayStatus();
});

watch(
  () => props.lotteryType,
  () => {
    todayResult.value = null;
    loadTodayStatus();
  }
);

watch(
  () => props.defaultDrawDate,
  (value) => {
    if (!selectedDrawDate.value || selectedDrawDate.value === normalizeDate(props.defaultDrawDate)) {
      selectedDrawDate.value = normalizeDate(value);
    }
  }
);

onBeforeUnmount(() => {
  if (adTimer && typeof window !== "undefined") window.clearInterval(adTimer);
});
</script>

<template>
  <section class="fortune-home-shrine" :class="{ 'is-shaking': isShaking }">
    <div class="shrine-main">
      <button class="mascot-button" type="button" :disabled="loading" @click="handleMainClick">
        <span class="mascot-halo" aria-hidden="true"></span>
        <img src="/caishen-mascot.png" alt="弈彩财神公仔" loading="lazy" decoding="async" />
      </button>
      <div class="shrine-copy">
        <p class="shrine-kicker">今日手气</p>
        <h3>财神摆一下</h3>
        <p>{{ helperText }}</p>
      </div>
    </div>

    <div class="profile-strip">
      <span :class="{ filled: profile?.zodiac }">{{ profile?.zodiac ? `属${profile.zodiac}` : "未填属相" }}</span>
      <span :class="{ filled: profile?.constellation }">{{ profile?.constellation ? `${profile.constellation}座` : "未填星座" }}</span>
      <label v-if="profileComplete" class="date-control">
        <span>开奖日期</span>
        <input v-model="selectedDrawDate" type="date" />
      </label>
    </div>

    <div class="shrine-actions">
      <button class="primary-shake" type="button" :disabled="loading" @click="handleMainClick">
        <span aria-hidden="true" class="button-glint"></span>
        {{ mainButtonText }}
      </button>
      <button class="ad-button" type="button" :disabled="adLoading || adRewardsRemaining <= 0" @click="startAdReward">
        看广告 +{{ adRewardPoints }} 积分
      </button>
    </div>

    <div class="offering-row" aria-label="财神上供">
      <button
        v-for="offering in offerings"
        :key="offering.type"
        type="button"
        :disabled="loading"
        @click="makeOffering(offering)"
      >
        <span class="offering-mark">{{ offering.mark }}</span>
        <span>
          <strong>{{ offering.label }}</strong>
          <small>{{ offering.cost }} 积分 · {{ offering.note }}</small>
        </span>
      </button>
    </div>

    <div class="fortune-footer">
      <span>香火积分 {{ pointsBalance }}</span>
      <span>今日广告剩余 {{ adRewardsRemaining }} 次</span>
      <span>{{ lotteryLabel }}</span>
    </div>
    <p v-if="statusMessage" class="fortune-status">{{ statusMessage }}</p>

    <Teleport to="body">
      <div v-if="promptMode" class="fortune-modal-shell" @click.self="closePrompt">
        <div class="fortune-prompt">
          <button type="button" class="modal-close" aria-label="关闭" @click="closePrompt">×</button>
          <p class="modal-kicker">请财神先认人</p>
          <h3>{{ promptTitle }}</h3>
          <div class="prompt-grid">
            <button
              v-for="item in promptOptions"
              :key="item"
              type="button"
              @click="savePromptChoice(item)"
            >
              {{ item }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="adDialogOpen" class="fortune-modal-shell" @click.self="closeAdDialog">
        <div class="fortune-prompt ad-prompt">
          <button type="button" class="modal-close" aria-label="关闭" @click="closeAdDialog">×</button>
          <p class="modal-kicker">香火积分</p>
          <h3>模拟广告播放中</h3>
          <div class="ad-dial">{{ adSeconds }}</div>
          <p>完成后获得 {{ adRewardPoints }} 积分。真实小程序版本可接激励视频广告。</p>
        </div>
      </div>

      <div v-if="showOverlay" class="fortune-effect-overlay" :class="overlayClass">
        <button type="button" class="overlay-close" aria-label="关闭" @click="closeOverlay">×</button>
        <div class="effect-orbit" aria-hidden="true">
          <span v-for="n in 18" :key="n"></span>
        </div>
        <div class="overlay-panel">
          <img class="overlay-mascot" src="/caishen-mascot.png" alt="" loading="lazy" decoding="async" />
          <p class="modal-kicker">{{ props.lotteryLabel }}</p>
          <h2>{{ overlayTitle }}</h2>
          <p class="fortune-text">
            {{ overlayResult?.fortune_text || "供品已送达，财神轻轻点头，今天就图一个开心和好彩头。" }}
          </p>
          <div v-if="overlayResult" class="result-balls">
            <NumberBall
              v-for="(number, index) in overlayNumbers"
              :key="`${index}-${number}`"
              :number="number"
              :lottery-type="props.lotteryType"
              size="lg"
            />
            <span class="result-plus">+</span>
            <NumberBall
              v-if="overlaySpecial !== null && overlaySpecial !== undefined"
              :number="overlaySpecial"
              :lottery-type="props.lotteryType"
              is-special
              size="lg"
            />
          </div>
          <p v-if="overlayResult" class="result-note">{{ specialLabel }} · {{ resultDisclosure }}</p>
          <button type="button" class="overlay-action" @click="closeOverlay">收下今日手气</button>
        </div>
      </div>
    </Teleport>
  </section>
</template>

<style scoped>
.fortune-home-shrine {
  position: relative;
  margin-top: 20px;
  padding: 18px;
  border: 1px solid rgba(207, 189, 160, 0.54);
  border-radius: 24px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.78), rgba(255, 248, 237, 0.58)),
    radial-gradient(circle at 18% 12%, rgba(216, 174, 95, 0.16), transparent 42%);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.9), 0 18px 44px rgba(52, 41, 27, 0.08);
  overflow: hidden;
}

.fortune-home-shrine::before {
  content: "";
  position: absolute;
  inset: 12px;
  border: 1px solid rgba(218, 179, 105, 0.16);
  border-radius: 20px;
  pointer-events: none;
}

.shrine-main {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 14px;
}

.mascot-button {
  position: relative;
  display: grid;
  width: 94px;
  height: 94px;
  flex: 0 0 auto;
  place-items: center;
  border: 0;
  border-radius: 28px;
  background: linear-gradient(145deg, rgba(20, 38, 51, 0.96), rgba(42, 67, 78, 0.92));
  box-shadow: 0 16px 30px rgba(20, 38, 51, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.16);
  cursor: pointer;
}

.mascot-button:disabled {
  cursor: wait;
}

.mascot-button img {
  position: relative;
  z-index: 1;
  width: 80px;
  height: 80px;
  object-fit: contain;
  transform-origin: 50% 78%;
  filter: drop-shadow(0 10px 14px rgba(34, 20, 6, 0.22));
}

.mascot-halo {
  position: absolute;
  inset: 12px;
  border-radius: 999px;
  background: radial-gradient(circle, rgba(247, 198, 96, 0.32), transparent 64%);
}

.is-shaking .mascot-button img {
  animation: shrine-shake 0.62s cubic-bezier(0.18, 0.92, 0.2, 1);
}

@keyframes shrine-shake {
  0%, 100% { transform: rotate(0deg) translateY(0); }
  18% { transform: rotate(-7deg) translateY(-2px); }
  36% { transform: rotate(6deg) translateY(0); }
  54% { transform: rotate(-4deg) translateY(-1px); }
  72% { transform: rotate(3deg) translateY(0); }
}

.shrine-copy {
  min-width: 0;
}

.shrine-kicker,
.modal-kicker {
  margin: 0 0 5px;
  color: #9b7440;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.shrine-copy h3 {
  margin: 0;
  color: #0f172a;
  font-size: 24px;
  font-weight: 900;
  letter-spacing: 0;
}

.shrine-copy p {
  margin: 6px 0 0;
  color: rgba(30, 41, 59, 0.72);
  font-size: 14px;
  line-height: 1.65;
}

.profile-strip {
  position: relative;
  z-index: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
}

.profile-strip > span,
.date-control {
  display: inline-flex;
  min-height: 34px;
  align-items: center;
  gap: 8px;
  border: 1px solid rgba(207, 189, 160, 0.42);
  border-radius: 999px;
  padding: 7px 12px;
  background: rgba(255, 255, 255, 0.62);
  color: rgba(30, 41, 59, 0.62);
  font-size: 13px;
  font-weight: 800;
}

.profile-strip > span.filled {
  border-color: rgba(159, 116, 54, 0.34);
  color: #0f172a;
  background: rgba(255, 251, 243, 0.86);
}

.date-control input {
  width: 132px;
  border: 0;
  background: transparent;
  color: #0f172a;
  font: inherit;
  outline: none;
}

.shrine-actions {
  position: relative;
  z-index: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 14px;
}

.primary-shake,
.ad-button {
  min-height: 42px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 900;
  cursor: pointer;
}

.primary-shake {
  position: relative;
  overflow: hidden;
  border: 0;
  padding: 0 22px;
  color: #fff;
  background: linear-gradient(135deg, #0f2533, #18384a 62%, #0d1b25);
  box-shadow: 0 16px 28px rgba(15, 37, 51, 0.22);
}

.button-glint {
  position: absolute;
  inset: 0;
  background: linear-gradient(105deg, transparent 22%, rgba(255, 255, 255, 0.22) 42%, transparent 58%);
  transform: translateX(-120%);
  animation: button-glint 3.2s ease-in-out infinite;
}

@keyframes button-glint {
  0%, 55% { transform: translateX(-120%); }
  82%, 100% { transform: translateX(120%); }
}

.ad-button {
  border: 1px solid rgba(15, 37, 51, 0.14);
  padding: 0 16px;
  color: #163040;
  background: rgba(255, 255, 255, 0.68);
}

.primary-shake:disabled,
.ad-button:disabled,
.offering-row button:disabled {
  opacity: 0.58;
  cursor: not-allowed;
}

.offering-row {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
  margin-top: 14px;
}

.offering-row button {
  display: flex;
  align-items: center;
  gap: 9px;
  border: 1px solid rgba(207, 189, 160, 0.42);
  border-radius: 16px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.6);
  color: #0f172a;
  text-align: left;
  cursor: pointer;
  transition: transform 0.18s ease, border-color 0.18s ease, background 0.18s ease;
}

.offering-row button:hover {
  transform: translateY(-2px);
  border-color: rgba(185, 130, 45, 0.5);
  background: rgba(255, 250, 240, 0.9);
}

.offering-mark {
  display: inline-grid;
  width: 30px;
  height: 30px;
  flex: 0 0 auto;
  place-items: center;
  border-radius: 10px;
  color: #f8df9d;
  background: linear-gradient(145deg, #132b39, #23475a);
  font-size: 13px;
  font-weight: 900;
}

.offering-row strong,
.offering-row small {
  display: block;
}

.offering-row strong {
  font-size: 13px;
  line-height: 1.2;
}

.offering-row small {
  margin-top: 2px;
  color: rgba(30, 41, 59, 0.58);
  font-size: 11px;
  line-height: 1.35;
}

.fortune-footer {
  position: relative;
  z-index: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  margin-top: 12px;
  color: rgba(30, 41, 59, 0.58);
  font-size: 12px;
  font-weight: 800;
}

.fortune-status {
  position: relative;
  z-index: 1;
  margin: 10px 0 0;
  color: #9b4d14;
  font-size: 12px;
  font-weight: 800;
}

.fortune-modal-shell,
.fortune-effect-overlay {
  position: fixed;
  inset: 0;
  z-index: 2000;
}

.fortune-modal-shell {
  display: grid;
  place-items: center;
  padding: 22px;
  background: rgba(15, 23, 42, 0.38);
  backdrop-filter: blur(10px);
}

.fortune-prompt {
  position: relative;
  width: min(520px, 100%);
  border: 1px solid rgba(219, 190, 143, 0.46);
  border-radius: 28px;
  padding: 28px;
  background: #fffaf3;
  box-shadow: 0 30px 90px rgba(15, 23, 42, 0.28);
}

.fortune-prompt h3 {
  margin: 0 0 18px;
  color: #0f172a;
  font-size: 26px;
  font-weight: 900;
}

.modal-close,
.overlay-close {
  border: 0;
  border-radius: 999px;
  cursor: pointer;
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 34px;
  height: 34px;
  color: #0f172a;
  background: rgba(15, 23, 42, 0.06);
  font-size: 22px;
}

.prompt-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.prompt-grid button {
  min-height: 44px;
  border: 1px solid rgba(207, 189, 160, 0.48);
  border-radius: 14px;
  color: #0f172a;
  background: rgba(255, 255, 255, 0.7);
  font-weight: 900;
  cursor: pointer;
}

.prompt-grid button:hover {
  border-color: rgba(15, 37, 51, 0.3);
  background: #fff;
}

.ad-prompt {
  text-align: center;
}

.ad-prompt p:last-child {
  margin: 14px auto 0;
  max-width: 320px;
  color: rgba(30, 41, 59, 0.66);
  line-height: 1.7;
}

.ad-dial {
  display: grid;
  width: 104px;
  height: 104px;
  margin: 4px auto 0;
  place-items: center;
  border-radius: 999px;
  color: #f8df9d;
  background: radial-gradient(circle at 35% 28%, #325267, #102431 68%);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.18), 0 18px 40px rgba(15, 37, 51, 0.2);
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 42px;
  font-weight: 900;
}

.fortune-effect-overlay {
  display: grid;
  place-items: center;
  overflow: hidden;
  padding: 28px;
  background:
    radial-gradient(circle at 50% 35%, rgba(255, 229, 173, 0.28), transparent 38%),
    linear-gradient(135deg, rgba(15, 23, 42, 0.93), rgba(15, 37, 51, 0.9));
}

.effect-orbit {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.effect-orbit span {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 14px;
  height: 14px;
  border-radius: 999px;
  background: linear-gradient(145deg, #ffdf91, #b97d25);
  box-shadow: 0 0 28px rgba(255, 209, 110, 0.5);
  transform: rotate(calc(var(--i, 1) * 20deg)) translateX(24vw);
  animation: coin-orbit 1.8s ease-out both;
}

.effect-orbit span:nth-child(1) { --i: 1; }
.effect-orbit span:nth-child(2) { --i: 2; }
.effect-orbit span:nth-child(3) { --i: 3; }
.effect-orbit span:nth-child(4) { --i: 4; }
.effect-orbit span:nth-child(5) { --i: 5; }
.effect-orbit span:nth-child(6) { --i: 6; }
.effect-orbit span:nth-child(7) { --i: 7; }
.effect-orbit span:nth-child(8) { --i: 8; }
.effect-orbit span:nth-child(9) { --i: 9; }
.effect-orbit span:nth-child(10) { --i: 10; }
.effect-orbit span:nth-child(11) { --i: 11; }
.effect-orbit span:nth-child(12) { --i: 12; }
.effect-orbit span:nth-child(13) { --i: 13; }
.effect-orbit span:nth-child(14) { --i: 14; }
.effect-orbit span:nth-child(15) { --i: 15; }
.effect-orbit span:nth-child(16) { --i: 16; }
.effect-orbit span:nth-child(17) { --i: 17; }
.effect-orbit span:nth-child(18) { --i: 18; }

@keyframes coin-orbit {
  0% { opacity: 0; transform: rotate(calc(var(--i) * 20deg)) translateX(0) scale(0.4); }
  28% { opacity: 1; }
  100% { opacity: 0; transform: rotate(calc(var(--i) * 20deg)) translateX(42vw) scale(1); }
}

.effect-level-1 .effect-orbit span:nth-child(n + 7),
.effect-level-2 .effect-orbit span:nth-child(n + 11),
.effect-level-3 .effect-orbit span:nth-child(n + 15) {
  display: none;
}

.overlay-close {
  position: absolute;
  top: 24px;
  right: 24px;
  z-index: 2;
  width: 44px;
  height: 44px;
  color: #fff;
  background: rgba(255, 255, 255, 0.14);
  font-size: 26px;
}

.overlay-panel {
  position: relative;
  z-index: 1;
  width: min(720px, 100%);
  border: 1px solid rgba(248, 223, 157, 0.3);
  border-radius: 34px;
  padding: 34px 28px 30px;
  background: rgba(255, 250, 243, 0.94);
  text-align: center;
  box-shadow: 0 32px 110px rgba(0, 0, 0, 0.42);
}

.overlay-mascot {
  width: 128px;
  height: 128px;
  object-fit: contain;
  margin-top: -88px;
  filter: drop-shadow(0 18px 22px rgba(34, 20, 6, 0.22));
  animation: overlay-mascot 0.82s cubic-bezier(0.18, 0.92, 0.2, 1) both;
}

@keyframes overlay-mascot {
  0% { transform: translateY(26px) scale(0.84) rotate(-5deg); opacity: 0; }
  70% { transform: translateY(-6px) scale(1.04) rotate(2deg); opacity: 1; }
  100% { transform: translateY(0) scale(1) rotate(0); }
}

.overlay-panel h2 {
  margin: 0;
  color: #0f172a;
  font-size: clamp(30px, 4vw, 48px);
  font-weight: 950;
  letter-spacing: 0;
}

.fortune-text {
  margin: 14px auto 0;
  max-width: 560px;
  color: rgba(30, 41, 59, 0.72);
  font-size: 16px;
  line-height: 1.9;
}

.result-balls {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: 22px;
}

.result-plus {
  color: #9b7440;
  font-size: 22px;
  font-weight: 900;
}

.result-note {
  margin: 14px auto 0;
  color: rgba(30, 41, 59, 0.6);
  font-size: 13px;
  font-weight: 800;
}

.overlay-action {
  margin-top: 24px;
  min-height: 46px;
  border: 0;
  border-radius: 999px;
  padding: 0 26px;
  color: #fff;
  background: linear-gradient(135deg, #0f2533, #18384a);
  font-weight: 900;
  cursor: pointer;
}

@media (max-width: 860px) {
  .fortune-home-shrine {
    border-radius: 22px;
    padding: 16px;
  }

  .shrine-main {
    align-items: flex-start;
  }

  .mascot-button {
    width: 82px;
    height: 82px;
    border-radius: 24px;
  }

  .mascot-button img {
    width: 70px;
    height: 70px;
  }

  .shrine-copy h3 {
    font-size: 21px;
  }

  .offering-row {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .prompt-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 520px) {
  .shrine-main {
    gap: 11px;
  }

  .shrine-actions,
  .profile-strip,
  .fortune-footer {
    flex-direction: column;
    align-items: stretch;
  }

  .profile-strip > span,
  .date-control,
  .primary-shake,
  .ad-button {
    width: 100%;
    justify-content: center;
  }

  .date-control input {
    width: 100%;
    max-width: 150px;
  }

  .offering-row {
    grid-template-columns: 1fr;
  }

  .fortune-effect-overlay {
    padding: 20px;
  }

  .overlay-panel {
    border-radius: 26px;
    padding: 30px 18px 24px;
  }
}
</style>
