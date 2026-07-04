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
  { type: "incense", label: "上香", note: "点香一次", cost: 5, mark: "香", boost: 28 },
  { type: "peach", label: "桃子", note: "摇一摇", cost: 10, mark: "桃", boost: 36 },
  { type: "ingot", label: "元宝", note: "讨个口彩", cost: 30, mark: "宝", boost: 18 },
  { type: "pouch", label: "锦囊", note: "大吉锦囊", cost: 60, mark: "锦", boost: 30 },
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
    <div class="fortune-stage-shell">
      <div class="shrine-portrait">
        <div class="portrait-arch">
          <span class="portrait-plaque">财源广进</span>
          <span class="portrait-glow"></span>
          <button class="mascot-button" type="button" :disabled="loading" @click="handleMainClick">
            <span class="mascot-halo" aria-hidden="true"></span>
            <span class="mascot-orbit" aria-hidden="true"></span>
            <img src="/caishen-mascot.png" alt="弈彩财神公仔" loading="lazy" decoding="async" />
          </button>
          <span class="portrait-base"></span>
          <span class="portrait-candle left"></span>
          <span class="portrait-candle right"></span>
        </div>
      </div>

      <div class="stage-content">
        <div class="stage-topline">
          <p class="shrine-kicker">今日手气</p>
          <label v-if="profileComplete" class="date-control">
            <span>开奖日期</span>
            <input v-model="selectedDrawDate" type="date" />
          </label>
        </div>

        <div class="stage-heading">
          <h3>财神摆一下</h3>
          <p>{{ helperText }}</p>
        </div>

        <div class="profile-strip">
          <span :class="{ filled: profile?.zodiac }">{{ profile?.zodiac ? `属${profile.zodiac}` : "未填属相" }}</span>
          <span :class="{ filled: profile?.constellation }">{{ profile?.constellation ? `${profile.constellation}座` : "未填星座" }}</span>
          <span class="lucky-chip">幸运号：08, 29</span>
          <button class="shuffle-link" type="button" :disabled="loading" @click="handleMainClick">换一换</button>
        </div>

        <div class="shrine-actions">
          <button class="primary-shake" type="button" :disabled="loading" @click="handleMainClick">
            <span aria-hidden="true" class="button-glint"></span>
            <span class="button-sigil" aria-hidden="true">福</span>
            {{ mainButtonText }}
          </button>
          <div class="incense-still" aria-hidden="true">
            <span class="incense-smoke"></span>
            <span class="incense-stick"></span>
            <span class="incense-bowl"></span>
            <span class="peach-still"></span>
          </div>
        </div>

      </div>

      <div class="shrine-offerings" aria-label="财神上供">
        <button
          v-for="offering in offerings"
          :key="offering.type"
          type="button"
          :disabled="loading"
          @click="makeOffering(offering)"
        >
          <span class="offering-mark">{{ offering.mark }}</span>
          <span class="offering-copy">
            <strong>{{ offering.label }}</strong>
            <small>{{ offering.cost }} 积分 · {{ offering.note }}</small>
          </span>
        </button>
      </div>

      <div class="stage-meter" aria-label="财神状态">
        <span>香火积分 <strong>{{ pointsBalance }}</strong></span>
        <span>今日广告剩余 <strong>{{ adRewardsRemaining }}</strong> 次</span>
        <span>{{ lotteryLabel }}</span>
      </div>
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
          <div class="overlay-hero" aria-hidden="true">
            <span class="hero-ring"></span>
            <span class="hero-ring second"></span>
            <span class="hero-smoke left"></span>
            <span class="hero-smoke right"></span>
            <span class="hero-jade one"></span>
            <span class="hero-jade two"></span>
            <img class="overlay-mascot" src="/caishen-mascot.png" alt="" loading="lazy" decoding="async" />
          </div>

          <div class="overlay-scroll">
            <p class="modal-kicker">今日手气签</p>
            <div class="overlay-title-row">
              <h2>{{ overlayTitle }}</h2>
              <span v-if="profile?.zodiac">属{{ profile.zodiac }}</span>
              <span v-if="profile?.constellation">{{ profile.constellation }}座</span>
            </div>
            <p class="fortune-text">
              {{ overlayResult?.fortune_text || "诚心上供，财神庇佑，今天就图一个开心和好彩头。" }}
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
            <div class="overlay-actions">
              <button type="button" class="overlay-action" @click="closeOverlay">收下今日手气</button>
              <router-link class="overlay-action secondary" to="/generate" @click="closeOverlay">去模拟选号</router-link>
            </div>
          </div>

          <div class="overlay-offering-dock">
            <div class="dock-header">
              <div>
                <span>上供回响</span>
                <strong>诚心上供，财神庇佑，运势加持</strong>
              </div>
              <button
                type="button"
                class="dock-ad-button"
                :disabled="adLoading || adRewardsRemaining <= 0"
                @click="startAdReward"
              >
                去赚积分
              </button>
            </div>
            <div class="dock-offerings" aria-label="财神上供">
              <button
                v-for="offering in offerings"
                :key="offering.type"
                type="button"
                :disabled="loading"
                @click="makeOffering(offering)"
              >
                <span class="offering-boost">+{{ offering.boost }}</span>
                <span class="offering-mark">{{ offering.mark }}</span>
                <span>
                  <strong>{{ offering.label }}</strong>
                  <small>{{ offering.cost }} 积分 · {{ offering.note }}</small>
                </span>
              </button>
            </div>
            <p v-if="statusMessage" class="dock-status">{{ statusMessage }}</p>
          </div>

          <div class="overlay-point-bar">
            <span>香火积分</span>
            <strong>{{ pointsBalance }}</strong>
            <span>今日广告剩余 {{ adRewardsRemaining }} 次</span>
          </div>
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

/* V2: low-luxury homepage stage + cinematic result dock */
.fortune-home-shrine {
  padding: 0;
  border: 0;
  border-radius: 30px;
  background:
    radial-gradient(circle at 16% 22%, rgba(226, 188, 111, 0.24), transparent 28%),
    linear-gradient(135deg, rgba(255, 253, 247, 0.88), rgba(244, 236, 225, 0.58));
  box-shadow: inset 0 0 0 1px rgba(210, 184, 139, 0.38), 0 22px 54px rgba(40, 31, 22, 0.1);
}

.fortune-home-shrine::before {
  inset: 1px;
  border-radius: 29px;
  border-color: rgba(255, 255, 255, 0.68);
  background:
    linear-gradient(110deg, transparent 0 44%, rgba(255, 255, 255, 0.5) 48%, transparent 54%),
    radial-gradient(circle at 92% 18%, rgba(15, 37, 51, 0.08), transparent 24%);
  opacity: 0.72;
}

.fortune-stage-shell {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 118px minmax(0, 1fr);
  gap: 18px;
  min-height: 228px;
  padding: 18px;
}

.fortune-stage-shell::after {
  content: "";
  position: absolute;
  left: 110px;
  top: 28px;
  bottom: 28px;
  width: 1px;
  background: linear-gradient(transparent, rgba(190, 151, 83, 0.48), transparent);
}

.mascot-button {
  align-self: stretch;
  width: 118px;
  height: auto;
  min-height: 168px;
  border-radius: 27px;
  background:
    radial-gradient(circle at 50% 20%, rgba(252, 218, 141, 0.28), transparent 34%),
    linear-gradient(160deg, #0e2330 0%, #183748 54%, #0a1821 100%);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.16),
    inset 0 -24px 54px rgba(0, 0, 0, 0.22),
    0 22px 44px rgba(15, 37, 51, 0.22);
}

.mascot-button::after {
  content: "";
  position: absolute;
  left: 18px;
  right: 18px;
  bottom: 18px;
  height: 18px;
  border-radius: 999px;
  background: radial-gradient(ellipse, rgba(0, 0, 0, 0.28), transparent 70%);
}

.mascot-button img {
  width: 96px;
  height: 118px;
  object-fit: contain;
  transform: translateY(4px);
  filter: drop-shadow(0 20px 20px rgba(5, 13, 18, 0.38));
}

.mascot-halo {
  inset: 14px 12px auto;
  height: 104px;
  border: 1px solid rgba(246, 205, 124, 0.28);
  background:
    radial-gradient(circle, rgba(246, 205, 124, 0.24), transparent 58%),
    conic-gradient(from 20deg, transparent, rgba(246, 205, 124, 0.34), transparent 34%);
  animation: fortune-halo-drift 8s linear infinite;
}

.mascot-orbit {
  position: absolute;
  inset: 20px 16px 48px;
  border-radius: 999px;
  border: 1px dashed rgba(246, 205, 124, 0.28);
  opacity: 0.68;
  transform: rotate(-14deg);
}

@keyframes fortune-halo-drift {
  to { transform: rotate(360deg); }
}

.stage-content {
  display: flex;
  min-width: 0;
  flex-direction: column;
  justify-content: space-between;
  padding: 6px 0 2px;
}

.stage-heading {
  max-width: 540px;
}

.shrine-kicker,
.modal-kicker {
  color: #a0712f;
  letter-spacing: 0.18em;
}

.stage-heading h3,
.shrine-copy h3 {
  margin: 0;
  color: #0f172a;
  font-size: clamp(24px, 2.2vw, 34px);
  font-weight: 950;
  line-height: 1.05;
  text-wrap: balance;
}

.stage-heading p:last-child {
  margin: 8px 0 0;
  max-width: 520px;
  color: rgba(30, 41, 59, 0.68);
  font-size: 14px;
  line-height: 1.7;
  text-wrap: pretty;
}

.profile-strip {
  margin-top: 16px;
}

.profile-strip > span,
.date-control {
  min-height: 32px;
  border-color: rgba(188, 152, 88, 0.26);
  background: rgba(255, 255, 255, 0.46);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.62);
  font-size: 12px;
}

.profile-strip > span.filled {
  border-color: rgba(160, 113, 47, 0.38);
  background: rgba(255, 249, 236, 0.86);
}

.shrine-actions {
  align-items: center;
  margin-top: 16px;
}

.primary-shake {
  min-height: 46px;
  padding: 0 24px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background:
    radial-gradient(circle at 22% 0%, rgba(255, 218, 135, 0.18), transparent 34%),
    linear-gradient(135deg, #0c1e2a, #17374a 58%, #081720);
  box-shadow: 0 18px 34px rgba(15, 37, 51, 0.26), inset 0 1px 0 rgba(255, 255, 255, 0.16);
}

.primary-shake:hover {
  transform: translateY(-1px);
  box-shadow: 0 22px 40px rgba(15, 37, 51, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.primary-shake:active {
  transform: translateY(1px) scale(0.99);
}

.stage-inline-note {
  color: rgba(30, 41, 59, 0.56);
  font-size: 12px;
  font-weight: 800;
}

.stage-meter {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1px;
  overflow: hidden;
  border: 1px solid rgba(196, 160, 96, 0.22);
  border-radius: 18px;
  background: rgba(196, 160, 96, 0.18);
}

.stage-meter span {
  display: flex;
  min-height: 38px;
  align-items: center;
  justify-content: center;
  gap: 5px;
  background: rgba(255, 252, 245, 0.66);
  color: rgba(30, 41, 59, 0.62);
  font-size: 12px;
  font-weight: 850;
}

.stage-meter strong {
  color: #0f172a;
  font-variant-numeric: tabular-nums;
}

.fortune-status {
  margin: 0;
  padding: 0 18px 16px;
}

.fortune-effect-overlay {
  align-items: center;
  overflow-y: auto;
  background:
    radial-gradient(circle at 50% 22%, rgba(224, 173, 78, 0.22), transparent 30%),
    radial-gradient(circle at 15% 84%, rgba(57, 111, 119, 0.25), transparent 28%),
    linear-gradient(135deg, rgba(7, 17, 24, 0.96), rgba(13, 33, 46, 0.94));
}

.fortune-effect-overlay::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.035) 1px, transparent 1px);
  background-size: 64px 64px;
  mask-image: radial-gradient(circle at 50% 42%, black, transparent 72%);
}

.overlay-panel {
  width: min(820px, 100%);
  margin: 54px auto 22px;
  border-color: rgba(247, 205, 124, 0.34);
  border-radius: 36px;
  padding: 42px 34px 30px;
  background:
    radial-gradient(circle at 50% 0%, rgba(255, 232, 180, 0.68), transparent 26%),
    linear-gradient(180deg, rgba(255, 252, 245, 0.96), rgba(246, 239, 226, 0.94));
  box-shadow:
    0 42px 130px rgba(0, 0, 0, 0.52),
    inset 0 1px 0 rgba(255, 255, 255, 0.86);
}

.overlay-panel::before {
  content: "";
  position: absolute;
  inset: 14px;
  border: 1px solid rgba(193, 148, 70, 0.18);
  border-radius: 28px;
  pointer-events: none;
}

.overlay-mascot {
  width: 150px;
  height: 150px;
  margin-top: -110px;
  filter: drop-shadow(0 24px 24px rgba(21, 16, 8, 0.32));
}

.overlay-panel h2 {
  margin-top: 4px;
  font-size: clamp(32px, 4.4vw, 54px);
  line-height: 1.04;
  text-wrap: balance;
}

.fortune-text {
  max-width: 610px;
  color: rgba(30, 41, 59, 0.7);
}

.result-balls {
  gap: 12px;
  margin-top: 24px;
}

.overlay-offering-dock {
  margin-top: 24px;
  border: 1px solid rgba(190, 151, 83, 0.28);
  border-radius: 24px;
  padding: 14px;
  background:
    radial-gradient(circle at 5% 0%, rgba(240, 205, 138, 0.2), transparent 32%),
    rgba(255, 251, 243, 0.72);
  text-align: left;
}

.dock-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 2px 2px 12px;
}

.dock-header span {
  display: block;
  color: #a0712f;
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.14em;
}

.dock-header strong {
  display: block;
  margin-top: 2px;
  color: rgba(30, 41, 59, 0.68);
  font-size: 13px;
  font-weight: 850;
}

.dock-ad-button {
  min-height: 34px;
  flex: 0 0 auto;
  border: 1px solid rgba(15, 37, 51, 0.16);
  border-radius: 999px;
  padding: 0 13px;
  color: #0f2533;
  background: rgba(255, 255, 255, 0.72);
  font-size: 12px;
  font-weight: 900;
  cursor: pointer;
}

.dock-ad-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.dock-offerings {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 9px;
}

.dock-offerings button {
  display: flex;
  align-items: center;
  gap: 9px;
  min-width: 0;
  border: 1px solid rgba(207, 189, 160, 0.38);
  border-radius: 17px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.66);
  color: #0f172a;
  text-align: left;
  cursor: pointer;
  transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease, box-shadow 0.2s ease;
}

.dock-offerings button:hover {
  transform: translateY(-2px);
  border-color: rgba(185, 130, 45, 0.55);
  background: #fffaf0;
  box-shadow: 0 14px 28px rgba(102, 72, 28, 0.1);
}

.dock-offerings button:active {
  transform: translateY(0) scale(0.99);
}

.dock-offerings button:disabled {
  opacity: 0.56;
  cursor: not-allowed;
}

.dock-offerings strong,
.dock-offerings small {
  display: block;
}

.dock-offerings strong {
  font-size: 13px;
  font-weight: 950;
}

.dock-offerings small {
  margin-top: 2px;
  color: rgba(30, 41, 59, 0.58);
  font-size: 11px;
  line-height: 1.35;
}

.dock-status {
  margin: 10px 2px 0;
  color: #9b4d14;
  font-size: 12px;
  font-weight: 850;
}

.overlay-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  margin-top: 22px;
}

.overlay-action {
  display: inline-flex;
  min-height: 46px;
  align-items: center;
  justify-content: center;
  margin-top: 0;
  text-decoration: none;
}

.overlay-action.secondary {
  border: 1px solid rgba(15, 37, 51, 0.14);
  color: #0f2533;
  background: rgba(255, 255, 255, 0.72);
}

@media (max-width: 860px) {
  .fortune-stage-shell {
    grid-template-columns: 92px minmax(0, 1fr);
    gap: 14px;
    min-height: 0;
    padding: 15px;
  }

  .fortune-stage-shell::after {
    display: none;
  }

  .mascot-button {
    width: 92px;
    min-height: 136px;
    border-radius: 24px;
  }

  .mascot-button img {
    width: 82px;
    height: 104px;
  }

  .stage-meter {
    grid-template-columns: 1fr;
  }

  .stage-meter span {
    min-height: 32px;
  }

  .dock-offerings {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 520px) {
  .fortune-stage-shell {
    grid-template-columns: 1fr;
  }

  .mascot-button {
    width: 100%;
    min-height: 122px;
  }

  .mascot-button img {
    width: 98px;
    height: 110px;
  }

  .stage-heading {
    text-align: center;
  }

  .shrine-actions {
    align-items: stretch;
  }

  .stage-inline-note {
    text-align: center;
  }

  .dock-header {
    align-items: stretch;
    flex-direction: column;
  }

  .dock-ad-button {
    width: 100%;
  }

  .dock-offerings {
    grid-template-columns: 1fr;
  }

  .overlay-actions {
    flex-direction: column;
  }

  .overlay-action {
    width: 100%;
  }
}

/* V3 reference match: premium Caishen stage + cinematic full-screen blessing */
.fortune-home-shrine {
  margin-top: 28px;
  padding: 0;
  border: 1px solid rgba(214, 183, 135, 0.72);
  border-radius: 18px;
  background:
    radial-gradient(circle at 28% 16%, rgba(231, 202, 151, 0.2), transparent 32%),
    linear-gradient(100deg, rgba(255, 252, 245, 0.94), rgba(249, 242, 231, 0.72) 54%, rgba(255, 252, 246, 0.9));
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.88),
    0 28px 72px rgba(55, 43, 29, 0.1);
}

.fortune-home-shrine::before {
  inset: 0;
  border-radius: 18px;
  border: 0;
  background:
    linear-gradient(90deg, rgba(169, 121, 56, 0.12), transparent 30%),
    radial-gradient(circle at 90% 42%, rgba(255, 255, 255, 0.7), transparent 34%);
  opacity: 1;
}

.fortune-stage-shell {
  display: grid;
  grid-template-columns: minmax(250px, 34%) minmax(0, 1fr);
  gap: 0;
  min-height: 352px;
  padding: 0;
}

.fortune-stage-shell::after {
  display: none;
}

.shrine-portrait {
  position: relative;
  min-height: 278px;
  border-radius: 17px 0 0 0;
  overflow: hidden;
  background:
    linear-gradient(90deg, rgba(185, 143, 83, 0.18), transparent 24%),
    radial-gradient(circle at 54% 24%, rgba(255, 244, 218, 0.72), transparent 45%),
    linear-gradient(135deg, #e9dbc6, #fff8eb 58%, #eadbc5);
}

.shrine-portrait::before {
  content: "";
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, rgba(154, 111, 57, 0.18), transparent 18%, transparent 78%, rgba(255, 255, 255, 0.58)),
    repeating-linear-gradient(90deg, rgba(159, 116, 58, 0.06) 0 1px, transparent 1px 42px);
  pointer-events: none;
}

.portrait-arch {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: end center;
}

.portrait-arch::before {
  content: "";
  position: absolute;
  left: 50%;
  top: 34px;
  width: min(245px, 76%);
  height: 260px;
  border: 1px solid rgba(195, 147, 79, 0.28);
  border-bottom: 0;
  border-radius: 999px 999px 18px 18px;
  transform: translateX(-50%);
  background:
    radial-gradient(circle at 50% 25%, rgba(255, 250, 236, 0.88), transparent 42%),
    linear-gradient(180deg, rgba(255, 247, 229, 0.58), rgba(217, 185, 134, 0.18));
  box-shadow: inset 0 0 32px rgba(255, 255, 255, 0.6);
}

.portrait-glow {
  position: absolute;
  left: 50%;
  top: 92px;
  width: 180px;
  height: 180px;
  border-radius: 999px;
  transform: translateX(-50%);
  background: radial-gradient(circle, rgba(255, 222, 151, 0.34), transparent 68%);
  filter: blur(4px);
}

.portrait-plaque {
  position: absolute;
  left: 18px;
  top: 96px;
  z-index: 2;
  display: grid;
  width: 34px;
  min-height: 126px;
  place-items: center;
  border: 1px solid rgba(181, 130, 58, 0.34);
  border-radius: 8px;
  padding: 9px 4px;
  color: #9b6a2d;
  background: rgba(255, 242, 211, 0.72);
  box-shadow: 0 12px 30px rgba(121, 80, 28, 0.08);
  font-size: 13px;
  font-weight: 900;
  line-height: 1.2;
  text-align: center;
  writing-mode: vertical-rl;
  letter-spacing: 0.18em;
}

.mascot-button {
  position: relative;
  z-index: 3;
  align-self: end;
  width: 206px;
  min-height: 238px;
  margin-bottom: 22px;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}

.mascot-button::after {
  left: 24px;
  right: 24px;
  bottom: 14px;
  height: 28px;
  background: radial-gradient(ellipse, rgba(65, 45, 18, 0.32), transparent 72%);
}

.mascot-button img {
  width: 170px;
  height: 216px;
  object-fit: contain;
  transform: translateY(3px);
  filter: drop-shadow(0 22px 18px rgba(87, 57, 22, 0.24));
}

.mascot-button:hover img {
  transform: translateY(-1px) rotate(-1deg);
}

.mascot-halo {
  inset: auto;
  top: 18px;
  left: 50%;
  width: 138px;
  height: 138px;
  border: 1px solid rgba(212, 163, 79, 0.24);
  transform: translateX(-50%);
  background:
    radial-gradient(circle, rgba(255, 228, 168, 0.22), transparent 62%),
    conic-gradient(from 20deg, transparent, rgba(212, 163, 79, 0.34), transparent 36%);
}

.mascot-orbit {
  inset: auto;
  top: 54px;
  left: 50%;
  width: 170px;
  height: 58px;
  border: 1px solid rgba(212, 163, 79, 0.24);
  transform: translateX(-50%) rotate(-9deg);
}

.portrait-base {
  position: absolute;
  left: 50%;
  bottom: 21px;
  width: 190px;
  height: 36px;
  border: 1px solid rgba(161, 112, 47, 0.28);
  border-radius: 50%;
  transform: translateX(-50%);
  background: linear-gradient(180deg, #d4c095, #8c784d);
  box-shadow: inset 0 5px 10px rgba(255, 255, 255, 0.32), 0 12px 24px rgba(64, 43, 16, 0.18);
}

.portrait-candle {
  position: absolute;
  bottom: 34px;
  width: 12px;
  height: 32px;
  border-radius: 8px 8px 3px 3px;
  background: linear-gradient(#f1d198, #b9823d);
  box-shadow: 0 0 18px rgba(255, 208, 103, 0.48);
}

.portrait-candle::before {
  content: "";
  position: absolute;
  left: 50%;
  top: -12px;
  width: 11px;
  height: 16px;
  border-radius: 999px 999px 999px 0;
  background: #ffdc86;
  transform: translateX(-50%) rotate(45deg);
  filter: blur(0.2px);
}

.portrait-candle.left { left: 22px; }
.portrait-candle.right { right: 26px; opacity: 0.45; }

.stage-content {
  position: relative;
  display: flex;
  min-width: 0;
  flex-direction: column;
  justify-content: flex-start;
  padding: 28px 30px 0;
}

.stage-content::after {
  content: "";
  position: absolute;
  right: 24px;
  top: 54px;
  width: 220px;
  height: 150px;
  border-radius: 999px;
  background: radial-gradient(ellipse, rgba(255, 255, 255, 0.72), transparent 72%);
  pointer-events: none;
}

.stage-topline {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.shrine-kicker,
.modal-kicker {
  margin: 0;
  color: #9b6a2d;
  font-size: 17px;
  font-weight: 950;
  letter-spacing: 0.08em;
}

.date-control {
  min-height: 38px;
  border: 1px solid rgba(202, 166, 105, 0.42);
  border-radius: 999px;
  padding: 0 12px;
  background: rgba(255, 251, 242, 0.82);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.78);
}

.date-control span {
  display: none;
}

.date-control input {
  color: #8a6535;
  font-size: 13px;
  font-weight: 850;
}

.stage-heading {
  position: relative;
  z-index: 1;
  max-width: 560px;
  margin-top: 16px;
}

.stage-heading h3,
.shrine-copy h3 {
  color: #172637;
  font-size: clamp(32px, 3.1vw, 44px);
  font-weight: 950;
  letter-spacing: 0.01em;
}

.stage-heading p:last-child {
  max-width: 470px;
  margin-top: 12px;
  color: rgba(46, 55, 63, 0.62);
  font-size: 15px;
  line-height: 1.8;
}

.profile-strip {
  position: relative;
  z-index: 2;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 9px;
  margin-top: 16px;
}

.profile-strip > span,
.shuffle-link {
  min-height: 36px;
  border: 1px solid rgba(210, 178, 126, 0.34);
  border-radius: 12px;
  padding: 0 15px;
  background: rgba(255, 250, 240, 0.86);
  color: #906730;
  box-shadow: 0 8px 18px rgba(91, 62, 26, 0.06);
  font-size: 14px;
  font-weight: 850;
}

.profile-strip > span.filled,
.profile-strip .lucky-chip {
  border-color: rgba(199, 154, 81, 0.42);
  background: rgba(255, 246, 226, 0.94);
}

.shuffle-link {
  border: 0;
  background: transparent;
  box-shadow: none;
  cursor: pointer;
}

.shuffle-link:hover {
  color: #0f2533;
}

.shrine-actions {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(220px, 330px) minmax(170px, 1fr);
  align-items: end;
  gap: 22px;
  margin-top: 22px;
}

.primary-shake {
  min-height: 62px;
  border: 1px solid rgba(239, 206, 144, 0.42);
  border-radius: 999px;
  padding: 0 30px;
  color: #f7d794;
  background:
    linear-gradient(90deg, rgba(255, 225, 157, 0.14), transparent 24%),
    linear-gradient(135deg, #102333, #0b1d2d 58%, #071725);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.18),
    inset 0 0 0 2px rgba(8, 17, 25, 0.38),
    0 16px 34px rgba(15, 37, 51, 0.2);
  font-size: 18px;
}

.button-sigil {
  position: relative;
  z-index: 1;
  display: inline-grid;
  width: 28px;
  height: 28px;
  margin-right: 9px;
  place-items: center;
  border: 1px solid rgba(247, 215, 148, 0.46);
  border-radius: 999px;
  color: #102333;
  background: linear-gradient(180deg, #f5d28a, #b88334);
  font-size: 14px;
}

.incense-still {
  position: relative;
  height: 96px;
  min-width: 190px;
}

.incense-stick {
  position: absolute;
  right: 94px;
  top: 8px;
  width: 2px;
  height: 62px;
  background: linear-gradient(#7f5630, #3b2b1c);
}

.incense-smoke {
  position: absolute;
  right: 78px;
  top: -4px;
  width: 58px;
  height: 48px;
  border-radius: 999px;
  border-left: 2px solid rgba(173, 158, 137, 0.18);
  border-top: 1px solid rgba(173, 158, 137, 0.12);
  filter: blur(0.2px);
  animation: incense-drift 4s ease-in-out infinite;
}

@keyframes incense-drift {
  0%, 100% { opacity: 0.36; transform: translateY(4px) translateX(0) scale(0.92); }
  50% { opacity: 0.7; transform: translateY(-8px) translateX(-8px) scale(1.06); }
}

.incense-bowl {
  position: absolute;
  right: 64px;
  bottom: 20px;
  width: 86px;
  height: 28px;
  border-radius: 0 0 999px 999px;
  background: linear-gradient(180deg, #87937e, #516e63 68%, #304c45);
  box-shadow: inset 0 4px 10px rgba(255, 255, 255, 0.2), 0 8px 18px rgba(40, 31, 20, 0.18);
}

.peach-still {
  position: absolute;
  right: 26px;
  bottom: 23px;
  width: 33px;
  height: 42px;
  border-radius: 60% 60% 54% 54%;
  background:
    radial-gradient(circle at 28% 22%, rgba(255, 255, 255, 0.7), transparent 26%),
    linear-gradient(145deg, #ffc9b8, #e78e7e 54%, #f1b77c);
  box-shadow: 0 9px 20px rgba(145, 80, 40, 0.16);
}

.shrine-offerings {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin: 24px -30px 0;
  padding: 14px 16px;
  border-top: 1px solid rgba(202, 166, 105, 0.22);
  background: rgba(255, 252, 246, 0.7);
}

.shrine-offerings button {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
  min-height: 74px;
  border: 1px solid rgba(209, 176, 123, 0.42);
  border-radius: 15px;
  padding: 13px 16px;
  background: rgba(255, 255, 255, 0.56);
  color: #172637;
  text-align: left;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease, background 0.18s ease;
}

.shrine-offerings button:hover {
  transform: translateY(-2px);
  border-color: rgba(185, 130, 45, 0.58);
  background: rgba(255, 251, 241, 0.92);
  box-shadow: 0 14px 28px rgba(84, 59, 27, 0.1);
}

.offering-mark {
  width: 42px;
  height: 42px;
  border-radius: 999px;
  color: #fff8df;
  background:
    radial-gradient(circle at 32% 24%, rgba(255, 255, 255, 0.55), transparent 24%),
    linear-gradient(145deg, #e7c178, #b68134 64%, #8b5d23);
  box-shadow: 0 10px 20px rgba(151, 102, 32, 0.22);
}

.offering-copy strong,
.offering-copy small {
  display: block;
}

.offering-copy strong {
  color: #172637;
  font-size: 15px;
  font-weight: 950;
}

.offering-copy small {
  margin-top: 4px;
  color: rgba(46, 55, 63, 0.58);
  font-size: 12px;
}

.stage-meter {
  grid-column: 1 / -1;
  display: flex;
  min-height: 47px;
  align-items: center;
  gap: 22px;
  padding: 0 24px;
  border: 0;
  border-top: 1px solid rgba(202, 166, 105, 0.22);
  border-radius: 0;
  background: rgba(255, 248, 235, 0.48);
}

.stage-meter span {
  display: inline-flex;
  min-height: 0;
  justify-content: flex-start;
  background: transparent;
  color: rgba(46, 55, 63, 0.58);
  font-size: 13px;
}

.stage-meter strong {
  color: #9b6a2d;
  font-size: 15px;
}

.fortune-status {
  margin: 0;
  padding: 10px 22px 16px;
  color: #9b4d14;
}

.fortune-effect-overlay {
  display: grid;
  place-items: center;
  overflow-y: auto;
  padding: 46px 24px;
  background:
    radial-gradient(circle at 50% 18%, rgba(235, 183, 93, 0.16), transparent 30%),
    linear-gradient(rgba(4, 12, 19, 0.82), rgba(7, 16, 24, 0.86));
  backdrop-filter: blur(10px);
}

.fortune-effect-overlay::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(circle at 24% 44%, rgba(255, 255, 255, 0.06), transparent 26%),
    radial-gradient(circle at 78% 44%, rgba(255, 255, 255, 0.04), transparent 28%),
    linear-gradient(90deg, rgba(255, 221, 148, 0.05), transparent 20%, transparent 80%, rgba(255, 221, 148, 0.04));
}

.overlay-close {
  top: max(32px, 4vh);
  right: calc(50% - min(430px, 45vw));
  z-index: 6;
  width: 54px;
  height: 54px;
  border: 1px solid rgba(248, 215, 148, 0.64);
  color: #fff7d8;
  background: rgba(11, 27, 39, 0.88);
  box-shadow: 0 0 0 4px rgba(248, 215, 148, 0.08), 0 10px 24px rgba(0, 0, 0, 0.28);
}

.overlay-panel {
  position: relative;
  z-index: 1;
  width: min(860px, calc(100vw - 42px));
  margin: 0 auto;
  border: 1px solid rgba(220, 169, 79, 0.8);
  border-radius: 22px 22px 18px 18px;
  padding: 0 18px 18px;
  overflow: visible;
  background:
    linear-gradient(180deg, rgba(13, 28, 42, 0.98), rgba(8, 20, 31, 0.98));
  box-shadow:
    0 38px 120px rgba(0, 0, 0, 0.6),
    inset 0 0 0 1px rgba(255, 240, 188, 0.1);
  text-align: center;
}

.overlay-panel::before {
  inset: 5px;
  border: 1px solid rgba(235, 183, 93, 0.26);
  border-radius: 18px;
}

.overlay-hero {
  position: relative;
  min-height: 315px;
  margin: 0 -18px;
  border-radius: 21px 21px 10px 10px;
  overflow: hidden;
  background:
    radial-gradient(circle at 50% 72%, rgba(255, 196, 83, 0.28), transparent 24%),
    radial-gradient(circle at 50% 22%, rgba(255, 216, 132, 0.14), transparent 30%),
    linear-gradient(180deg, #101e2c, #07131f 80%);
}

.overlay-hero::before,
.overlay-hero::after {
  content: "";
  position: absolute;
  left: 50%;
  bottom: 22px;
  width: 520px;
  height: 88px;
  border: 1px solid rgba(244, 191, 89, 0.36);
  border-radius: 50%;
  transform: translateX(-50%);
  box-shadow: 0 0 34px rgba(246, 185, 65, 0.22), inset 0 0 24px rgba(246, 185, 65, 0.18);
}

.overlay-hero::after {
  width: 330px;
  height: 54px;
  bottom: 50px;
  opacity: 0.76;
}

.hero-ring {
  position: absolute;
  left: 50%;
  top: 24px;
  width: 188px;
  height: 188px;
  border: 2px solid rgba(255, 213, 124, 0.74);
  border-radius: 999px;
  transform: translateX(-50%);
  box-shadow: 0 0 36px rgba(255, 204, 91, 0.34), inset 0 0 36px rgba(255, 204, 91, 0.13);
}

.hero-ring::before {
  content: "福";
  position: absolute;
  inset: 18px;
  display: grid;
  place-items: center;
  border: 1px dashed rgba(255, 222, 150, 0.46);
  border-radius: 999px;
  color: rgba(255, 220, 143, 0.26);
  font-size: 70px;
  font-weight: 950;
}

.hero-ring.second {
  top: 46px;
  width: 142px;
  height: 142px;
  opacity: 0.42;
  animation: fortune-halo-drift 14s linear infinite reverse;
}

.hero-smoke {
  position: absolute;
  top: 154px;
  width: 260px;
  height: 82px;
  border-top: 2px solid rgba(220, 225, 221, 0.12);
  border-radius: 50%;
  filter: blur(1px);
}

.hero-smoke.left {
  left: -36px;
  transform: rotate(-7deg);
}

.hero-smoke.right {
  right: -42px;
  transform: rotate(8deg);
}

.hero-jade {
  position: absolute;
  width: 19px;
  height: 24px;
  border-radius: 8px;
  background: linear-gradient(145deg, #c8f2dd, #7db49d 58%, #376e61);
  box-shadow: 0 0 18px rgba(136, 222, 187, 0.36);
}

.hero-jade.one { left: 104px; top: 72px; transform: rotate(-22deg); }
.hero-jade.two { right: 126px; top: 112px; transform: rotate(17deg); }

.overlay-mascot {
  position: absolute;
  left: 50%;
  bottom: 30px;
  z-index: 2;
  width: 250px;
  height: 268px;
  margin: 0;
  object-fit: contain;
  transform: translateX(-50%);
  filter: drop-shadow(0 26px 22px rgba(0, 0, 0, 0.36));
}

.overlay-scroll {
  position: relative;
  z-index: 3;
  margin: -34px auto 0;
  width: min(720px, calc(100% - 38px));
  border: 1px solid rgba(222, 173, 86, 0.66);
  border-radius: 24px;
  padding: 24px 26px 20px;
  background:
    radial-gradient(circle at 50% 0%, rgba(255, 213, 124, 0.14), transparent 38%),
    linear-gradient(180deg, rgba(15, 31, 45, 0.98), rgba(7, 19, 31, 0.98));
  box-shadow: 0 20px 70px rgba(0, 0, 0, 0.34), inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.overlay-scroll .modal-kicker {
  color: #efd191;
  font-size: 12px;
  letter-spacing: 0.18em;
}

.overlay-title-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 11px;
}

.overlay-title-row h2 {
  margin: 0 8px 0 0;
  color: #f5d99d;
  font-size: clamp(38px, 5vw, 64px);
  font-weight: 950;
  letter-spacing: 0.04em;
  text-shadow: 0 0 24px rgba(246, 197, 98, 0.2);
}

.overlay-title-row span {
  display: inline-flex;
  min-height: 34px;
  align-items: center;
  border: 1px solid rgba(235, 199, 130, 0.44);
  border-radius: 999px;
  padding: 0 16px;
  color: #e7c078;
  font-size: 14px;
  font-weight: 900;
}

.fortune-text {
  max-width: 610px;
  margin: 8px auto 0;
  color: rgba(234, 223, 204, 0.72);
  font-size: 14px;
  line-height: 1.8;
}

.result-balls {
  gap: 12px;
  margin-top: 18px;
}

.result-balls :deep(.ball-shine) {
  width: 64px;
  height: 64px;
  border: 1px solid rgba(255, 229, 165, 0.35);
  box-shadow:
    inset 0 8px 12px rgba(255, 255, 255, 0.22),
    inset 0 -12px 18px rgba(0, 0, 0, 0.22),
    0 0 0 4px rgba(244, 185, 82, 0.1),
    0 14px 24px rgba(0, 0, 0, 0.3);
  font-size: 24px;
}

.result-plus {
  color: #f0cd86;
  font-size: 28px;
  text-shadow: 0 0 16px rgba(245, 195, 88, 0.4);
}

.result-note {
  color: rgba(234, 223, 204, 0.58);
}

.overlay-actions {
  gap: 18px;
  margin-top: 22px;
}

.overlay-action {
  min-width: 206px;
  min-height: 58px;
  border: 1px solid rgba(255, 238, 183, 0.6);
  border-radius: 999px;
  padding: 0 32px;
  color: #553915;
  background: linear-gradient(180deg, #fff3d3, #e3b96e);
  box-shadow: 0 12px 28px rgba(211, 156, 56, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.72);
  font-size: 17px;
  text-decoration: none;
}

.overlay-action.secondary {
  border-color: rgba(98, 132, 155, 0.52);
  color: #e8f2f8;
  background: linear-gradient(180deg, #1b354a, #0d2233);
}

.overlay-offering-dock {
  position: relative;
  z-index: 2;
  width: min(650px, calc(100% - 70px));
  margin: 18px auto 0;
  border: 1px solid rgba(205, 145, 55, 0.46);
  border-radius: 16px;
  padding: 14px 18px 16px;
  background:
    linear-gradient(90deg, rgba(242, 185, 81, 0.08), transparent 20%, transparent 80%, rgba(242, 185, 81, 0.08)),
    rgba(8, 21, 32, 0.82);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.overlay-offering-dock::before {
  content: "";
  position: absolute;
  left: 50%;
  bottom: -27px;
  width: calc(100% + 160px);
  height: 48px;
  border: 1px solid rgba(207, 146, 54, 0.44);
  border-radius: 0 0 26px 26px;
  transform: translateX(-50%);
  background: linear-gradient(180deg, rgba(24, 34, 42, 0.95), rgba(9, 20, 31, 0.98));
  pointer-events: none;
}

.dock-header {
  justify-content: center;
  padding: 0 0 10px;
  text-align: center;
}

.dock-header span {
  color: #f0cd86;
  font-size: 18px;
  letter-spacing: 0.12em;
}

.dock-header strong {
  color: rgba(234, 223, 204, 0.66);
  font-size: 13px;
}

.dock-ad-button {
  position: absolute;
  right: 14px;
  bottom: -20px;
  z-index: 2;
  min-height: 34px;
  border: 1px solid rgba(238, 201, 128, 0.42);
  color: #f3d693;
  background: linear-gradient(180deg, #163247, #0a1e2e);
}

.dock-offerings {
  position: relative;
  z-index: 1;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.dock-offerings button {
  position: relative;
  flex-direction: column;
  justify-content: flex-end;
  min-height: 118px;
  border-color: rgba(216, 162, 66, 0.24);
  border-radius: 16px;
  padding: 26px 8px 10px;
  background:
    radial-gradient(circle at 50% 40%, rgba(235, 198, 126, 0.16), transparent 42%),
    rgba(4, 14, 23, 0.38);
  text-align: center;
}

.dock-offerings button:hover {
  background:
    radial-gradient(circle at 50% 40%, rgba(235, 198, 126, 0.24), transparent 44%),
    rgba(11, 28, 41, 0.72);
}

.dock-offerings .offering-mark {
  width: 52px;
  height: 52px;
  font-size: 17px;
}

.offering-boost {
  position: absolute;
  top: 8px;
  right: 10px;
  color: #f3c46b;
  font-size: 14px;
  font-weight: 950;
  text-shadow: 0 0 12px rgba(239, 185, 82, 0.4);
}

.dock-offerings strong {
  color: #f7e4b6;
}

.dock-offerings small {
  color: rgba(234, 223, 204, 0.58);
}

.dock-status {
  position: relative;
  z-index: 2;
  text-align: center;
}

.overlay-point-bar {
  position: relative;
  z-index: 3;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  width: min(630px, calc(100% - 96px));
  min-height: 48px;
  margin: 28px auto 0;
  border: 1px solid rgba(216, 162, 66, 0.44);
  border-radius: 12px;
  background: linear-gradient(180deg, #102a3d, #071824);
  color: #e7c078;
  box-shadow: 0 16px 34px rgba(0, 0, 0, 0.32);
}

.overlay-point-bar strong {
  min-width: 96px;
  color: #fff0bf;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 30px;
  line-height: 1;
}

@media (max-width: 940px) {
  .fortune-stage-shell {
    grid-template-columns: 1fr;
  }

  .shrine-portrait {
    min-height: 250px;
    border-radius: 17px 17px 0 0;
  }

  .stage-content {
    padding: 24px 22px 0;
  }

  .shrine-actions {
    grid-template-columns: 1fr;
  }

  .incense-still {
    display: none;
  }

  .shrine-offerings {
    margin-inline: -22px;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .fortune-effect-overlay {
    padding: 36px 12px 22px;
  }

  .overlay-close {
    right: 18px;
    top: 18px;
  }

  .overlay-hero {
    min-height: 238px;
  }

  .overlay-mascot {
    width: 190px;
    height: 210px;
  }

  .hero-ring {
    width: 142px;
    height: 142px;
  }

  .overlay-scroll,
  .overlay-offering-dock,
  .overlay-point-bar {
    width: calc(100% - 12px);
  }

  .overlay-title-row h2 {
    width: 100%;
    margin-right: 0;
    font-size: 36px;
  }

  .result-balls :deep(.ball-shine) {
    width: 48px;
    height: 48px;
    font-size: 18px;
  }

  .dock-offerings {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .overlay-point-bar {
    grid-template-columns: 1fr;
    gap: 3px;
    padding: 8px 0;
  }
}

@media (max-width: 520px) {
  .fortune-home-shrine {
    border-radius: 18px;
  }

  .stage-heading {
    text-align: left;
  }

  .stage-topline {
    align-items: flex-start;
    flex-direction: column;
  }

  .primary-shake {
    width: 100%;
  }

  .shrine-offerings {
    grid-template-columns: 1fr;
  }

  .stage-meter {
    align-items: flex-start;
    flex-direction: column;
    gap: 6px;
    padding: 12px 18px;
  }
}

/* Reference-image final pass: warm shrine band + cinematic result altar */
.fortune-home-shrine {
  margin-top: 0;
  border-radius: 18px;
  overflow: visible;
}

.fortune-stage-shell {
  min-height: 392px;
  grid-template-columns: minmax(260px, 31%) minmax(0, 1fr);
  border-radius: 18px;
  border-color: rgba(218, 190, 150, 0.82);
  background:
    radial-gradient(circle at 22% 16%, rgba(229, 190, 121, .22), transparent 32%),
    linear-gradient(90deg, rgba(244, 228, 197, .88) 0%, rgba(255, 253, 248, .94) 41%, rgba(255, 253, 248, .78) 100%);
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.72),
    0 22px 58px rgba(76, 56, 28, .08);
}

.fortune-stage-shell::before {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(90deg, rgba(190, 145, 75, .08), transparent 32%),
    repeating-linear-gradient(90deg, rgba(154, 112, 60, .05) 0 1px, transparent 1px 72px);
}

.shrine-portrait {
  min-height: 345px;
  border-radius: 18px 0 0 0;
}

.portrait-arch {
  min-height: 345px;
  height: 100%;
  border-radius: 18px 0 0 0;
  background:
    radial-gradient(ellipse at 52% 44%, rgba(255, 250, 228, .9), transparent 42%),
    linear-gradient(180deg, rgba(242, 217, 173, .8), rgba(228, 194, 134, .48));
}

.portrait-arch::before {
  left: 58px;
  right: 34px;
  top: 44px;
  bottom: 34px;
  border-color: rgba(196, 149, 75, .28);
  box-shadow:
    inset 0 0 80px rgba(255, 247, 224, .54),
    0 16px 40px rgba(131, 88, 35, .08);
}

.portrait-plaque {
  left: 28px;
  top: 116px;
  width: 33px;
  min-height: 116px;
  border-color: rgba(203, 162, 93, .72);
  background: rgba(255, 244, 217, .8);
  color: #956733;
  font-size: 13px;
}

.mascot-button {
  left: 53%;
  bottom: 58px;
  width: 238px;
  height: 248px;
  transform: translateX(-50%);
}

.mascot-button img {
  width: 230px;
  height: 246px;
  filter: drop-shadow(0 20px 26px rgba(94, 61, 25, .28));
}

.mascot-halo {
  width: 188px;
  height: 188px;
  opacity: .62;
}

.portrait-base {
  left: 52%;
  bottom: 35px;
  width: 246px;
  height: 42px;
  transform: translateX(-50%);
}

.portrait-candle {
  bottom: 38px;
  opacity: .86;
}

.portrait-candle.left {
  left: 50px;
}

.portrait-candle.right {
  right: 38px;
}

.stage-content {
  min-height: 345px;
  padding: 31px 30px 0;
}

.stage-topline {
  align-items: center;
}

.shrine-kicker {
  font-size: 18px;
  letter-spacing: .11em;
}

.date-control {
  min-width: 168px;
  justify-content: center;
}

.stage-heading {
  max-width: 530px;
  margin-top: 14px;
}

.stage-heading h3 {
  font-size: clamp(34px, 3.4vw, 46px);
  letter-spacing: .02em;
}

.stage-heading p:last-child {
  max-width: 520px;
  margin-top: 12px;
}

.profile-strip {
  margin-top: 18px;
}

.profile-strip > span,
.shuffle-link {
  min-height: 35px;
  border-radius: 12px;
  padding: 0 16px;
}

.shrine-actions {
  grid-template-columns: minmax(260px, 340px) minmax(170px, 1fr);
  gap: 24px;
  margin-top: 24px;
}

.primary-shake {
  min-height: 66px;
  border-width: 2px;
  font-size: 19px;
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.18),
    inset 0 0 0 2px rgba(8,17,25,.48),
    0 18px 38px rgba(15,37,51,.24);
}

.incense-still {
  height: 108px;
}

.shrine-offerings {
  margin: 20px -30px 0;
  padding: 13px 12px;
  gap: 10px;
  background: rgba(255, 251, 244, .72);
}

.shrine-offerings button {
  min-height: 72px;
  border-radius: 13px;
  background: rgba(255,255,255,.5);
}

.stage-meter {
  min-height: 45px;
  padding: 0 26px;
}

.fortune-effect-overlay {
  padding: 42px 20px;
  background:
    radial-gradient(circle at 50% 22%, rgba(237, 184, 86, .18), transparent 28%),
    radial-gradient(circle at 28% 44%, rgba(255,255,255,.05), transparent 24%),
    linear-gradient(rgba(4, 12, 19, .86), rgba(6, 15, 23, .9));
}

.overlay-panel {
  width: min(838px, calc(100vw - 48px));
  border-radius: 20px;
  border-color: rgba(224, 174, 82, .82);
  padding: 0 18px 16px;
  background:
    radial-gradient(circle at 50% 10%, rgba(233, 179, 76, .08), transparent 32%),
    linear-gradient(180deg, rgba(13, 28, 42, .99), rgba(7, 18, 29, .99));
}

.overlay-hero {
  min-height: 302px;
  border-radius: 19px 19px 8px 8px;
}

.overlay-mascot {
  bottom: 28px;
  width: 268px;
  height: 286px;
}

.hero-ring {
  top: 18px;
  width: 198px;
  height: 198px;
}

.hero-ring.second {
  top: 42px;
}

.overlay-scroll {
  position: relative;
  z-index: 3;
  width: calc(100% - 78px);
  margin: -34px auto 0;
  padding: 34px 34px 24px;
  border-radius: 20px;
  border: 1px solid rgba(223, 172, 82, .52);
  background:
    radial-gradient(circle at 50% 20%, rgba(242, 198, 113, .1), transparent 42%),
    linear-gradient(180deg, rgba(16, 34, 49, .98), rgba(9, 22, 34, .98));
  box-shadow:
    0 20px 45px rgba(0,0,0,.34),
    inset 0 1px 0 rgba(255,255,255,.08);
}

.overlay-title-row {
  justify-content: center;
}

.overlay-title-row h2 {
  flex: none;
  width: auto;
  color: #f4d391;
  font-size: clamp(48px, 5vw, 64px);
  letter-spacing: .1em;
  text-shadow: 0 2px 0 rgba(55, 32, 6, .38), 0 0 24px rgba(229, 178, 82, .28);
}

.overlay-title-row span {
  border-color: rgba(231, 187, 98, .38);
  color: #f2d18d;
  background: rgba(255, 232, 165, .06);
}

.fortune-text {
  max-width: 610px;
  margin: 10px auto 0;
}

.result-balls {
  margin-top: 18px;
}

.result-balls :deep(.ball-shine) {
  width: 64px;
  height: 64px;
  font-size: 24px;
  box-shadow: 0 16px 22px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.28);
}

.result-plus {
  color: #e5bd72;
  font-size: 28px;
}

.overlay-actions {
  margin-top: 22px;
}

.overlay-action {
  min-width: 218px;
  min-height: 54px;
  border-radius: 999px;
}

.overlay-offering-dock {
  width: calc(100% - 86px);
  margin: 16px auto 0;
  padding: 15px 18px 13px;
  border-radius: 14px;
  border: 1px solid rgba(206, 154, 68, .4);
  background:
    radial-gradient(circle at 50% 0%, rgba(226, 166, 69, .12), transparent 40%),
    rgba(9, 20, 30, .72);
}

.dock-header {
  margin-bottom: 12px;
}

.dock-offerings {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.dock-offerings button {
  min-height: 94px;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 8px;
  padding: 10px 8px;
  text-align: center;
  border-color: rgba(219, 170, 80, .34);
  background: rgba(255, 236, 181, .06);
}

.dock-offerings .offering-mark {
  width: 44px;
  height: 44px;
}

.overlay-point-bar {
  width: calc(100% - 86px);
  margin: 12px auto 0;
}

@media (max-width: 940px) {
  .fortune-stage-shell {
    grid-template-columns: 1fr;
  }

  .shrine-portrait {
    min-height: 280px;
  }

  .portrait-arch {
    min-height: 280px;
  }

  .mascot-button {
    width: 210px;
    height: 220px;
  }

  .mascot-button img {
    width: 205px;
    height: 220px;
  }

  .stage-content {
    min-height: 0;
  }
}

@media (max-width: 720px) {
  .overlay-scroll,
  .overlay-offering-dock,
  .overlay-point-bar {
    width: calc(100% - 12px);
  }

  .overlay-title-row h2 {
    font-size: 38px;
  }

  .dock-offerings {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

/* Bottom offering rail spans the full shrine, matching the reference card. */
.fortune-stage-shell {
  grid-template-rows: minmax(345px, auto) auto auto;
}

.shrine-offerings {
  grid-column: 1 / -1;
  margin: 0;
  padding: 12px 14px;
  border-top: 1px solid rgba(202, 166, 105, 0.22);
}

.shrine-offerings button {
  min-height: 72px;
  padding: 12px 18px;
}

@media (max-width: 940px) {
  .fortune-stage-shell {
    grid-template-rows: auto auto auto auto;
  }

  .shrine-offerings {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 520px) {
  .shrine-offerings {
    grid-template-columns: 1fr;
  }
}

/* Keep the full ceremonial overlay inside a desktop viewport. */
.overlay-panel {
  width: min(820px, calc(100vw - 48px));
  padding: 0 16px 12px;
}

.overlay-hero {
  min-height: 258px;
}

.overlay-mascot {
  left: 50%;
  bottom: 12px;
  width: 236px;
  height: 252px;
  transform: translateX(-50%);
  animation: none;
}

.hero-ring {
  top: 16px;
  width: 170px;
  height: 170px;
}

.hero-ring.second {
  top: 36px;
  width: 128px;
  height: 128px;
}

.overlay-scroll {
  width: calc(100% - 82px);
  margin-top: -24px;
  padding: 22px 30px 18px;
}

.overlay-scroll .modal-kicker {
  font-size: 10px;
}

.overlay-title-row {
  gap: 8px;
}

.overlay-title-row h2 {
  font-size: clamp(40px, 4vw, 50px);
  line-height: 1.04;
}

.overlay-title-row span {
  min-height: 28px;
  padding: 0 13px;
  font-size: 12px;
}

.fortune-text {
  margin-top: 7px;
  font-size: 12.5px;
  line-height: 1.58;
}

.result-balls {
  gap: 10px;
  margin-top: 12px;
}

.result-balls :deep(.ball-shine) {
  width: 56px;
  height: 56px;
  font-size: 21px;
}

.result-note {
  margin-top: 8px;
  font-size: 12px;
}

.overlay-actions {
  gap: 14px;
  margin-top: 14px;
}

.overlay-action {
  min-width: 198px;
  min-height: 48px;
  padding: 0 26px;
  font-size: 15px;
}

.overlay-offering-dock {
  width: calc(100% - 92px);
  margin-top: 12px;
  padding: 10px 14px 10px;
}

.overlay-offering-dock::before {
  bottom: -20px;
  height: 38px;
}

.dock-header {
  padding-bottom: 7px;
}

.dock-header span {
  font-size: 15px;
}

.dock-header strong {
  font-size: 11px;
}

.dock-ad-button {
  bottom: -14px;
  min-height: 30px;
  padding: 0 14px;
  font-size: 11px;
}

.dock-offerings {
  gap: 8px;
}

.dock-offerings button {
  min-height: 78px;
  border-radius: 13px;
  padding: 18px 6px 8px;
}

.dock-offerings .offering-mark {
  width: 38px;
  height: 38px;
  font-size: 14px;
}

.offering-boost {
  top: 5px;
  right: 8px;
  font-size: 12px;
}

.dock-offerings strong {
  font-size: 13px;
}

.dock-offerings small {
  font-size: 10px;
}

.overlay-point-bar {
  width: calc(100% - 100px);
  min-height: 42px;
  margin-top: 18px;
}

.overlay-point-bar strong {
  font-size: 24px;
}

@media (max-width: 720px) {
  .fortune-home-shrine {
    overflow: hidden;
  }

  .mascot-halo {
    width: 142px;
    height: 142px;
  }

  .fortune-effect-overlay {
    align-items: flex-start;
    padding: 18px 10px 26px;
  }

  .overlay-close {
    top: 14px;
    right: 14px;
    width: 56px;
    height: 56px;
  }

  .overlay-panel {
    width: calc(100vw - 20px);
    max-width: calc(100vw - 20px);
    margin: 0 auto;
    overflow: hidden;
  }

  .overlay-hero {
    min-height: 224px;
  }

  .overlay-mascot {
    bottom: 2px;
    width: 202px;
    height: 222px;
  }

  .hero-ring {
    width: 150px;
    height: 150px;
  }

  .hero-ring.second {
    width: 112px;
    height: 112px;
  }

  .overlay-scroll {
    width: calc(100% - 20px);
    margin-top: -16px;
    padding: 18px 16px 16px;
  }

  .overlay-title-row h2 {
    width: 100%;
    max-width: 100%;
    margin: 0;
    font-size: 34px;
    line-height: 1.12;
    letter-spacing: .04em;
    white-space: normal;
    overflow-wrap: anywhere;
  }

  .fortune-text {
    font-size: 13px;
  }

  .result-balls {
    max-width: 282px;
    flex-wrap: wrap;
    justify-content: center;
    margin-inline: auto;
  }

  .result-balls :deep(.ball-shine) {
    width: 50px;
    height: 50px;
    font-size: 18px;
  }

  .result-plus {
    width: 22px;
    text-align: center;
  }

  .overlay-actions {
    flex-direction: column;
    gap: 10px;
  }

  .overlay-action {
    width: 100%;
  }

  .overlay-offering-dock,
  .overlay-point-bar {
    width: calc(100% - 20px);
  }

  .dock-offerings {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
