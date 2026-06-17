const LOTTERY_CONFIG = {
  marksix: { min: 1, max: 49, strategy: "\u5206\u5c42\u6f0f\u6597" },
  ssq: { min: 1, max: 33, strategy: "\u52a0\u6743\u968f\u673a" },
  qxc: { min: 0, max: 14, strategy: "\u4f4d\u7f6e\u6f0f\u6597" },
};

const MESSAGES = [
  "\u8d22\u795e\u6446\u4e86\u4e00\u4e0b\uff1a\u4eca\u5929\u624b\u6c14\u504f\u65fa",
  "\u8d22\u795e\u70b9\u5934\uff1a\u5148\u8bd5\u4e00\u7ec4\u624b\u6c14",
  "\u8d22\u795e\u5230\u4f4d\uff1a\u6570\u5b57\u5df2\u7ecf\u6eda\u51fa\u6765",
  "\u8d22\u795e\u8f7b\u6447\uff1a\u5e26\u70b9\u8fd0\u6c14\u518d\u51fa\u53d1",
];

function hashSeed(input) {
  let hash = 2166136261;
  for (let index = 0; index < input.length; index += 1) {
    hash ^= input.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

function seededRandom(seed) {
  let state = seed || 1;
  return () => {
    state = Math.imul(state ^ (state >>> 15), 1 | state);
    state ^= state + Math.imul(state ^ (state >>> 7), 61 | state);
    return ((state ^ (state >>> 14)) >>> 0) / 4294967296;
  };
}

function formatNumber(value, lotteryType) {
  if (lotteryType === "qxc") return String(value);
  return String(value).padStart(2, "0");
}

export function createFortuneResult({
  lotteryType = "marksix",
  nonce = 0,
  dateSeed = new Date().toISOString().slice(0, 10),
} = {}) {
  const config = LOTTERY_CONFIG[lotteryType] || LOTTERY_CONFIG.marksix;
  const random = seededRandom(hashSeed(`${lotteryType}:${dateSeed}:${nonce}`));
  const count = Math.min(3, config.max - config.min + 1);
  const picked = new Set();

  while (picked.size < count) {
    const value = config.min + Math.floor(random() * (config.max - config.min + 1));
    picked.add(value);
  }

  const numbers = [...picked]
    .sort((a, b) => a - b)
    .map((value) => ({
      value,
      display: formatNumber(value, lotteryType),
    }));

  return {
    message: MESSAGES[Math.floor(random() * MESSAGES.length)],
    numbers,
    strategy: config.strategy,
  };
}
