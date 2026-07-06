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
const offeringSummary = ref({ count: 0, spent: 0, boost_score: 0 });
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
  if (hasTodayResult.value) return "查看今日手气";
  return "打开财神阁";
});
const helperText = computed(() => {
  if (hasTodayResult.value) return "今天已经请过财神，结果已保存，可随时查看。";
  if (profileComplete.value) return "档案已备好，可进入财神阁先上供加持，再摇出今日娱乐号码。";
  return "进入全屏财神阁后填写属相和星座，先上供加持，再摇出今日娱乐号码。";
});
const overlayNumbers = computed(() => overlayResult.value?.regular_numbers || []);
const overlaySpecial = computed(() => overlayResult.value?.special_number);
const overlayClass = computed(() => {
  const level = overlayEffect.value?.level || 1;
  const boostClass = offeringSummary.value.count > 0 ? "has-offering-boost" : "no-offering-boost";
  return `effect-level-${level} ${boostClass}`;
});
const overlayTitle = computed(() => {
  if (!overlayResult.value) return "财神显灵";
  return "财神显灵";
});
const overlayBadgeText = computed(() => {
  if (!profile.value?.zodiac) return "请财神先认人";
  if (!profile.value?.constellation) return "请财神看星座";
  if (!overlayResult.value) return "先上供 · 再请财神";
  return `${overlayEffect.value.name} · 今日手气签`;
});
const offeringSummaryText = computed(() => {
  const count = offeringSummary.value.count || 0;
  const spent = offeringSummary.value.spent || 0;
  if (!count) return "尚未上供，可先赚积分再加持。";
  return `今日已上供 ${count} 次 · 已加持 ${spent} 积分`;
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
    offeringSummary.value = data.offering_summary || { count: 0, spent: 0, boost_score: 0 };
    statusMessage.value = "";
  } catch (error) {
    statusMessage.value = errorText(error);
  }
}

async function saveProfileChoice(mode, value) {
  if (!userKey.value || !mode) return;
  const payload = {
    user_key: userKey.value,
    zodiac: profile.value?.zodiac,
    constellation: profile.value?.constellation,
  };
  if (mode === "zodiac") payload.zodiac = value;
  if (mode === "constellation") payload.constellation = value;
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

async function savePromptChoice(value) {
  if (!promptMode.value) return;
  await saveProfileChoice(promptMode.value, value);
}

function closePrompt() {
  promptMode.value = null;
}

function openCeremonyOverlay() {
  overlayMode.value = todayResult.value ? "result" : "setup";
  overlayResult.value = todayResult.value || null;
  overlayEffect.value = todayResult.value
    ? {
        level: Math.max(4, todayResult.value.effect_level || 1),
        name: todayResult.value.effect_name || "清风小吉",
      }
    : { level: 4, name: "开阁请神" };
  statusMessage.value = "";
  showOverlay.value = true;
}

async function saveOverlayChoice(mode, value) {
  await saveProfileChoice(mode, value);
}

async function handleMainClick() {
  if (loading.value) return;
  if (!profile.value?.zodiac) {
    openCeremonyOverlay();
    return;
  }
  if (!profile.value?.constellation) {
    openCeremonyOverlay();
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
    offeringSummary.value = data.offering_summary || offeringSummary.value;
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
    level: Math.max(4, result.effect_level || 1),
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
    offeringSummary.value = data.offering_summary || offeringSummary.value;
    overlayMode.value = "offering";
    overlayEffect.value = data.effect || { level: 1, name: "清风小吉" };
    overlayResult.value = todayResult.value || null;
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
      <button class="mascot-button" type="button" :disabled="loading" @click="openCeremonyOverlay">
        <span class="mascot-halo" aria-hidden="true"></span>
        <span class="mascot-orbit" aria-hidden="true"></span>
        <img src="/caishen-mascot.png" alt="弈彩财神公仔" loading="lazy" decoding="async" />
      </button>

      <div class="stage-content">
        <div class="stage-heading">
          <p class="shrine-kicker">今日手气</p>
          <h3>财神摆一下</h3>
          <p>{{ helperText }}</p>
        </div>

        <div class="profile-strip home-entry-strip">
          <span>全屏请神</span>
          <span>先上供再摇</span>
          <span>每日一次</span>
        </div>

        <div class="shrine-actions">
          <button class="primary-shake" type="button" :disabled="loading" @click="openCeremonyOverlay">
            <span aria-hidden="true" class="button-glint"></span>
            {{ mainButtonText }}
          </button>
          <span class="stage-inline-note">{{ hasTodayResult ? "今日手气已保存" : "每日限请一次" }}</span>
        </div>
      </div>

      <div class="stage-meter" aria-label="财神状态">
        <span>香火积分 <strong>{{ pointsBalance }}</strong></span>
        <span>今日一次 <strong>{{ hasTodayResult ? "已用" : "待请" }}</strong></span>
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
        <div
          class="overlay-panel cinematic-panel"
          :class="{
            'is-setup': !overlayResult,
            'is-pre-shake': profileComplete && !overlayResult,
            'is-result': overlayResult,
          }"
        >
          <div class="cinematic-art" aria-hidden="true">
            <img src="/assets/caishen-cinematic-shrine.png" alt="" loading="eager" decoding="async" />
            <span class="art-glow art-glow-left"></span>
            <span class="art-glow art-glow-right"></span>
          </div>

          <div class="overlay-scroll">
            <p class="modal-kicker">{{ overlayBadgeText }}</p>
            <h2>{{ overlayTitle }}</h2>

            <div v-if="!profile?.zodiac" class="overlay-setup-panel">
              <p class="fortune-text">先告诉财神你的属相，今日手气签只会为这台设备保存一次。</p>
              <div class="overlay-choice-grid" aria-label="选择属相">
                <button
                  v-for="item in zodiacOptions"
                  :key="item"
                  type="button"
                  @click="saveOverlayChoice('zodiac', item)"
                >
                  {{ item }}
                </button>
              </div>
            </div>

            <div v-else-if="!profile?.constellation" class="overlay-setup-panel">
              <p class="fortune-text">再选择星座，系统会结合开奖日生成今日娱乐手气分析。</p>
              <div class="overlay-choice-grid constellation" aria-label="选择星座">
                <button
                  v-for="item in constellationOptions"
                  :key="item"
                  type="button"
                  @click="saveOverlayChoice('constellation', item)"
                >
                  {{ item }}
                </button>
              </div>
            </div>

            <div v-else-if="!overlayResult" class="overlay-date-card">
              <p class="fortune-text">选择开奖日期，可先上供加持，再轻点请财神摇出今日手气签。每台设备每天只生成一次。</p>
              <label class="overlay-date-control">
                <span>开奖日期</span>
                <input v-model="selectedDrawDate" type="date" />
              </label>
              <button class="overlay-shake-button" type="button" :disabled="loading" @click="handleMainClick">
                <span class="button-sigil" aria-hidden="true">福</span>
                {{ loading ? "正在请财神" : "摇一摇请财神" }}
              </button>
              <p class="pre-shake-summary">{{ offeringSummaryText }}</p>
            </div>

            <div v-else class="overlay-result-block">
              <p class="fortune-text">
                {{ overlayResult?.fortune_text || "诚心上供，财神庇佑，今天就图一个开心和好彩头。" }}
              </p>
              <p class="result-boost-summary">{{ offeringSummaryText }} · 本次手气签已结算</p>
              <div class="result-balls">
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
              <p class="result-note">{{ specialLabel }} · {{ resultDisclosure }}</p>
              <div class="overlay-actions">
                <button type="button" class="overlay-action" @click="closeOverlay">收下今日手气</button>
                <router-link class="overlay-action secondary" to="/generate" @click="closeOverlay">去模拟选号</router-link>
              </div>
            </div>
          </div>

          <div v-if="profileComplete && !overlayResult" class="overlay-offering-dock pre-offering-dock">
            <div class="dock-header">
              <div>
                <span>先上供 · 再请财神</span>
                <strong>上供会计入今日加持，影响本次手气签的特效权重</strong>
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
                :disabled="loading || !profileComplete"
                @click="makeOffering(offering)"
              >
                <span class="offering-mark">{{ offering.mark }}</span>
                <span>
                  <strong>{{ offering.label }}</strong>
                  <small>{{ offering.cost }} 积分 · {{ offering.note }}</small>
                </span>
              </button>
            </div>
            <p v-if="statusMessage" class="dock-status">{{ statusMessage }}</p>
          </div>

          <div v-if="profileComplete && !overlayResult" class="overlay-point-bar">
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

/* Cinematic Caishen overlay: asset-led visual pass matching the selected Image 2 direction. */
.home-entry-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1px;
  overflow: hidden;
  width: min(560px, 100%);
  border: 1px solid rgba(175, 135, 77, 0.17);
  border-radius: 16px;
  background: rgba(175, 135, 77, 0.14);
}

.home-entry-strip span {
  display: inline-flex;
  min-height: 44px;
  align-items: center;
  justify-content: center;
  padding: 0 12px;
  color: rgba(45, 58, 67, 0.78);
  background: rgba(255, 253, 248, 0.72);
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.fortune-effect-overlay {
  display: block;
  align-items: flex-start;
  box-sizing: border-box;
  padding: 26px 16px 44px;
  overflow-y: auto;
  background:
    radial-gradient(circle at 50% 15%, rgba(246, 199, 103, 0.22), transparent 28%),
    radial-gradient(circle at 24% 52%, rgba(195, 222, 214, 0.12), transparent 24%),
    radial-gradient(circle at 76% 52%, rgba(195, 222, 214, 0.1), transparent 24%),
    linear-gradient(180deg, rgba(2, 10, 17, 0.94), rgba(4, 13, 21, 0.98));
  backdrop-filter: blur(16px) saturate(1.12);
}

.fortune-effect-overlay::before {
  opacity: 0.95;
  background:
    radial-gradient(ellipse at 50% 28%, rgba(255, 207, 119, 0.22), transparent 25%),
    radial-gradient(ellipse at 22% 58%, rgba(223, 234, 229, 0.09), transparent 22%),
    radial-gradient(ellipse at 78% 58%, rgba(223, 234, 229, 0.09), transparent 22%);
}

.cinematic-panel {
  position: relative;
  display: flex;
  isolation: isolate;
  width: min(1050px, calc(100vw - 36px));
  min-height: 0;
  flex-direction: column;
  align-items: center;
  margin: 0 auto;
  padding: 0 0 26px;
  border: 1px solid rgba(234, 185, 93, 0.82);
  border-radius: 30px;
  background:
    radial-gradient(circle at 50% 4%, rgba(255, 213, 124, 0.2), transparent 26%),
    radial-gradient(circle at 50% 80%, rgba(12, 39, 54, 0.9), transparent 52%),
    linear-gradient(180deg, rgba(11, 27, 41, 0.98), rgba(4, 13, 23, 0.98));
  box-shadow:
    0 40px 140px rgba(0, 0, 0, 0.66),
    0 0 0 1px rgba(255, 236, 177, 0.16),
    0 0 80px rgba(218, 151, 43, 0.16),
    inset 0 1px 0 rgba(255, 255, 255, 0.12);
  overflow: visible;
}

.cinematic-panel::before {
  content: "";
  position: absolute;
  inset: 12px;
  z-index: 1;
  border: 1px solid rgba(241, 190, 94, 0.24);
  border-radius: 20px;
  pointer-events: none;
}

.cinematic-panel::after {
  content: "";
  position: absolute;
  left: -38px;
  right: -38px;
  bottom: 58px;
  z-index: 1;
  height: 74px;
  border: 1px solid rgba(199, 130, 35, 0.42);
  border-radius: 0 0 42px 42px;
  background:
    linear-gradient(180deg, rgba(12, 28, 41, 0.98), rgba(4, 14, 23, 0.98)),
    radial-gradient(circle at 50% 0%, rgba(235, 181, 85, 0.18), transparent 46%);
  box-shadow: 0 26px 56px rgba(0, 0, 0, 0.44), inset 0 1px 0 rgba(255, 235, 178, 0.1);
  pointer-events: none;
}

.cinematic-art {
  position: relative;
  z-index: 0;
  width: 100%;
  height: clamp(390px, 44vw, 515px);
  min-height: 0;
  overflow: hidden;
  border-radius: 29px 29px 0 0;
  background: #071722;
}

.cinematic-art img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
  object-position: center top;
  filter: saturate(1.08) contrast(1.05);
}

.art-glow {
  position: absolute;
  top: 42%;
  width: 210px;
  height: 110px;
  border-radius: 999px;
  opacity: 0.8;
  filter: blur(24px);
  pointer-events: none;
}

.art-glow-left {
  left: 8%;
  background: rgba(218, 228, 224, 0.14);
}

.art-glow-right {
  right: 8%;
  background: rgba(218, 228, 224, 0.13);
}

.effect-orbit {
  inset: 0;
  z-index: 1;
  pointer-events: none;
}

.effect-orbit span {
  width: 24px;
  height: 24px;
  border: 1px solid rgba(255, 221, 153, 0.78);
  border-radius: 50%;
  opacity: 0.92;
  background:
    radial-gradient(circle at 35% 28%, rgba(255, 248, 210, 0.86), transparent 22%),
    radial-gradient(circle at 50% 50%, #ecc375, #b67822 66%, #6b3c10);
  box-shadow:
    0 0 18px rgba(236, 182, 83, 0.35),
    inset 0 -5px 8px rgba(67, 34, 5, 0.32);
  animation: ceremony-token-float 5.4s ease-in-out infinite both;
  transform: translate3d(0, 0, 0) rotate(var(--rot, -16deg));
}

.effect-orbit span:nth-child(3n) {
  border-radius: 8px;
  background: linear-gradient(145deg, rgba(206, 249, 226, 0.95), rgba(81, 159, 135, 0.92) 58%, rgba(27, 78, 68, 0.95));
  box-shadow: 0 0 22px rgba(130, 223, 184, 0.34);
}

.effect-orbit span:nth-child(1) { left: 31%; top: 15%; --dx: 14px; --dy: -18px; --rot: -18deg; }
.effect-orbit span:nth-child(2) { left: 67%; top: 14%; --dx: -12px; --dy: -15px; --rot: 22deg; }
.effect-orbit span:nth-child(3) { left: 28%; top: 28%; --dx: 9px; --dy: 16px; --rot: -12deg; }
.effect-orbit span:nth-child(4) { left: 72%; top: 28%; --dx: -10px; --dy: 14px; --rot: 12deg; }
.effect-orbit span:nth-child(5) { left: 23%; top: 43%; --dx: 16px; --dy: -8px; --rot: 28deg; }
.effect-orbit span:nth-child(6) { left: 77%; top: 42%; --dx: -14px; --dy: -10px; --rot: -24deg; }
.effect-orbit span:nth-child(7) { left: 35%; top: 55%; --dx: 10px; --dy: 13px; --rot: 8deg; }
.effect-orbit span:nth-child(8) { left: 65%; top: 56%; --dx: -8px; --dy: 12px; --rot: -14deg; }
.effect-orbit span:nth-child(9) { left: 19%; top: 63%; --dx: 12px; --dy: -16px; --rot: 20deg; }
.effect-orbit span:nth-child(10) { left: 81%; top: 64%; --dx: -12px; --dy: -14px; --rot: -18deg; }
.effect-orbit span:nth-child(n+11) { display: none; }

@keyframes ceremony-token-float {
  0% { opacity: 0.54; transform: translate3d(0, 0, 0) rotate(var(--rot, -16deg)) scale(0.88); }
  50% { opacity: 1; transform: translate3d(var(--dx, 10px), var(--dy, -14px), 0) rotate(calc(var(--rot, -16deg) + 26deg)) scale(1.08); }
  100% { opacity: 0.72; transform: translate3d(0, 0, 0) rotate(var(--rot, -16deg)) scale(0.92); }
}

.overlay-scroll {
  position: relative;
  z-index: 3;
  width: min(790px, calc(100% - 70px));
  margin-top: -174px;
  border: 1px solid rgba(241, 190, 94, 0.82);
  border-radius: 28px;
  padding: 28px 34px 26px;
  background:
    radial-gradient(circle at 50% 0%, rgba(255, 218, 134, 0.2), transparent 38%),
    linear-gradient(180deg, rgba(18, 36, 51, 0.98), rgba(6, 18, 29, 0.98));
  box-shadow:
    0 24px 70px rgba(0, 0, 0, 0.32),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  text-align: center;
}

.overlay-scroll .modal-kicker {
  color: #d7a64f;
}

.overlay-scroll h2 {
  margin: 0;
  color: #f4d693;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(42px, 5vw, 68px);
  font-weight: 900;
  letter-spacing: 0.08em;
  text-shadow: 0 0 26px rgba(236, 181, 80, 0.24);
}

.cinematic-panel.is-pre-shake .cinematic-art {
  height: clamp(315px, 34vw, 385px);
}

.cinematic-panel.is-pre-shake .overlay-scroll {
  margin-top: -118px;
  padding-block: 22px 20px;
}

.cinematic-panel.is-pre-shake .overlay-scroll h2 {
  font-size: clamp(38px, 4vw, 54px);
}

.cinematic-panel.is-pre-shake .fortune-text {
  margin-top: 8px;
  line-height: 1.62;
}

.fortune-text {
  max-width: 620px;
  margin: 12px auto 0;
  color: rgba(237, 228, 209, 0.76);
  font-size: 14px;
  line-height: 1.75;
}

.overlay-choice-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 10px;
  margin-top: 18px;
}

.overlay-choice-grid.constellation {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.overlay-choice-grid button,
.overlay-date-control,
.overlay-shake-button {
  border: 1px solid rgba(236, 196, 119, 0.42);
  border-radius: 15px;
  color: #f7e2b2;
  background:
    radial-gradient(circle at 50% 0%, rgba(255, 225, 158, 0.12), transparent 55%),
    rgba(8, 23, 35, 0.8);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.overlay-choice-grid button {
  min-height: 48px;
  font-size: 14px;
  font-weight: 950;
  cursor: pointer;
  transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
}

.overlay-choice-grid button:hover {
  border-color: rgba(247, 205, 120, 0.9);
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.22), 0 0 18px rgba(237, 185, 83, 0.2);
}

.overlay-date-card {
  display: grid;
  justify-items: center;
  gap: 16px;
}

.overlay-date-control {
  display: grid;
  grid-template-columns: auto minmax(180px, 1fr);
  align-items: center;
  gap: 12px;
  min-height: 54px;
  padding: 0 16px;
}

.overlay-date-control span {
  color: rgba(241, 218, 174, 0.72);
  font-size: 13px;
  font-weight: 900;
}

.overlay-date-control input {
  min-height: 38px;
  border: 0;
  color: #f7e2b2;
  background: transparent;
  font-size: 15px;
  font-weight: 900;
  outline: none;
}

.overlay-shake-button {
  display: inline-flex;
  min-width: 256px;
  min-height: 58px;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border-radius: 999px;
  color: #061827;
  background: linear-gradient(180deg, #fff0c5, #d89a39);
  box-shadow:
    0 16px 36px rgba(228, 162, 56, 0.24),
    inset 0 1px 0 rgba(255, 255, 255, 0.68);
  font-size: 17px;
  font-weight: 950;
  cursor: pointer;
}

.button-sigil {
  display: inline-grid;
  width: 28px;
  height: 28px;
  place-items: center;
  border-radius: 999px;
  background: rgba(7, 24, 36, 0.18);
}

.pre-shake-summary,
.result-boost-summary {
  margin: 0;
  color: #e7c078;
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.04em;
}

.result-boost-summary {
  margin-top: 8px;
  color: rgba(241, 216, 165, 0.7);
}

.result-balls {
  justify-content: center;
  gap: 12px;
  margin-top: 20px;
}

.result-balls :deep(.ball-shine) {
  width: 54px;
  height: 54px;
  font-size: 18px;
  box-shadow: 0 14px 24px rgba(0, 0, 0, 0.28);
}

.result-note {
  color: rgba(241, 218, 174, 0.64);
}

.pre-offering-dock {
  position: relative;
  z-index: 3;
  width: min(900px, calc(100% - 72px));
  margin: 16px auto 0;
  border: 1px solid rgba(205, 145, 55, 0.46);
  border-radius: 26px;
  padding: 20px 26px 22px;
  background:
    radial-gradient(circle at 16% 0%, rgba(244, 190, 88, 0.18), transparent 32%),
    radial-gradient(circle at 84% 0%, rgba(124, 205, 174, 0.1), transparent 28%),
    linear-gradient(180deg, rgba(12, 27, 39, 0.9), rgba(5, 16, 26, 0.92));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.pre-offering-dock::before {
  display: none;
}

.pre-offering-dock .dock-header {
  justify-content: space-between;
  padding: 0 0 15px;
  text-align: left;
}

.pre-offering-dock .dock-header span {
  color: #f0cd86;
  font-size: 17px;
  letter-spacing: 0.12em;
}

.pre-offering-dock .dock-header strong {
  color: rgba(234, 223, 204, 0.66);
}

.pre-offering-dock .dock-ad-button {
  position: static;
  min-height: 38px;
  padding: 0 18px;
  border: 1px solid rgba(238, 201, 128, 0.42);
  color: #f3d693;
  background: linear-gradient(180deg, #163247, #0a1e2e);
}

.pre-offering-dock .dock-offerings {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.pre-offering-dock .dock-offerings button {
  position: relative;
  display: flex;
  min-height: 122px;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  border-color: rgba(216, 162, 66, 0.24);
  border-radius: 16px;
  padding: 24px 8px 12px;
  color: #f7e4b6;
  background:
    radial-gradient(circle at 50% 32%, rgba(240, 200, 119, 0.25), transparent 36%),
    linear-gradient(180deg, rgba(24, 43, 55, 0.8), rgba(7, 19, 30, 0.72)),
    rgba(4, 14, 23, 0.38);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.07), 0 14px 28px rgba(0, 0, 0, 0.18);
  text-align: center;
}

.pre-offering-dock .offering-mark {
  display: inline-grid;
  width: 52px;
  height: 52px;
  place-items: center;
  border-radius: 999px;
  color: #071724;
  background: radial-gradient(circle at 34% 28%, #fff2bd, #d89a39 62%, #8a5515);
  font-size: 17px;
  font-weight: 950;
  box-shadow: 0 0 28px rgba(229, 169, 64, 0.26), inset 0 1px 0 rgba(255, 255, 255, 0.4);
}

.pre-offering-dock small {
  color: rgba(234, 223, 204, 0.58);
}

.cinematic-panel.is-pre-shake .pre-offering-dock {
  margin-top: 12px;
  padding: 14px 22px 16px;
}

.cinematic-panel.is-pre-shake .pre-offering-dock .dock-header {
  padding-bottom: 10px;
}

.cinematic-panel.is-pre-shake .pre-offering-dock .dock-header strong {
  display: none;
}

.cinematic-panel.is-pre-shake .pre-offering-dock .dock-offerings button {
  min-height: 88px;
  padding-top: 14px;
}

.cinematic-panel.is-pre-shake .overlay-point-bar {
  min-height: 46px;
  margin-top: 8px;
}

.cinematic-panel.is-pre-shake .pre-offering-dock .offering-mark {
  width: 46px;
  height: 46px;
}

.overlay-point-bar {
  position: relative;
  z-index: 3;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  width: min(900px, calc(100% - 72px));
  min-height: 58px;
  margin: 14px auto 0;
  border: 1px solid rgba(216, 162, 66, 0.44);
  border-radius: 18px;
  background:
    linear-gradient(180deg, rgba(16, 42, 61, 0.96), rgba(7, 24, 36, 0.98)),
    radial-gradient(circle at 50% 0%, rgba(231, 192, 120, 0.12), transparent 60%);
  color: #e7c078;
  box-shadow: 0 18px 42px rgba(0, 0, 0, 0.38), inset 0 1px 0 rgba(255, 255, 255, 0.08);
  text-align: center;
}

.overlay-point-bar strong {
  min-width: 96px;
  color: #fff0bf;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 30px;
  line-height: 1;
}

.has-offering-boost .cinematic-art img {
  filter: saturate(1.18) contrast(1.08) brightness(1.05);
}

.has-offering-boost .cinematic-panel {
  box-shadow:
    0 34px 120px rgba(0, 0, 0, 0.58),
    0 0 52px rgba(232, 169, 59, 0.22),
    inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

@media (max-width: 720px) {
  .home-entry-strip {
    grid-template-columns: 1fr;
  }

  .home-entry-strip span {
    min-height: 38px;
  }

  .fortune-effect-overlay {
    padding: 12px 8px 22px;
  }

  .cinematic-panel {
    width: calc(100vw - 16px);
    border-radius: 21px;
  }

  .cinematic-panel::after {
    left: -12px;
    right: -12px;
    bottom: 54px;
    height: 56px;
    border-radius: 0 0 26px 26px;
  }

  .cinematic-art {
    height: 220px;
    min-height: 0;
  }

  .cinematic-art img {
    object-position: center top;
  }

  .overlay-scroll {
    width: calc(100% - 18px);
    margin-top: -42px;
    padding: 18px 14px 16px;
  }

  .overlay-scroll h2 {
    font-size: 34px;
    letter-spacing: 0.05em;
  }

  .fortune-text {
    font-size: 12px;
    line-height: 1.55;
  }

  .cinematic-panel.is-result .fortune-text {
    display: -webkit-box;
    max-height: 42px;
    overflow: hidden;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
  }

  .overlay-choice-grid,
  .overlay-choice-grid.constellation {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;
  }

  .overlay-date-control {
    width: 100%;
    grid-template-columns: 1fr;
    justify-items: center;
    padding: 10px 14px;
  }

  .overlay-shake-button {
    width: 100%;
    min-width: 0;
  }

  .result-balls {
    max-width: 320px;
    gap: 8px;
    flex-wrap: wrap;
    margin-inline: auto;
  }

  .result-balls :deep(.ball-shine) {
    width: 44px;
    height: 44px;
    font-size: 16px;
  }

  .pre-offering-dock {
    width: calc(100% - 18px);
    padding: 16px 14px 18px;
  }

  .pre-offering-dock .dock-header {
    align-items: stretch;
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }

  .pre-offering-dock .dock-ad-button {
    width: 100%;
  }

  .pre-offering-dock .dock-offerings {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .pre-offering-dock .dock-offerings button {
    min-height: 92px;
  }

  .cinematic-panel.is-pre-shake .cinematic-art {
    height: 202px;
  }

  .cinematic-panel.is-pre-shake .overlay-scroll {
    margin-top: -38px;
    padding: 16px 14px 14px;
  }

  .cinematic-panel.is-pre-shake .overlay-scroll h2 {
    font-size: 32px;
  }

  .cinematic-panel.is-pre-shake .pre-offering-dock {
    padding: 14px 12px 16px;
  }

  .overlay-point-bar {
    width: calc(100% - 18px);
    grid-template-columns: 1fr;
    gap: 6px;
    padding: 10px 12px;
  }
}
</style>
