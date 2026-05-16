import { ref } from "vue";

export const lotteryType = ref("marksix");

const STORAGE_KEY = "lottery_user_draws";

const BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.PROD
    ? "https://api.ckl.hk"
    : "http://localhost:8000");

async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json();
}

function getUserDraws() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

function saveUserDraws(draws) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(draws));
}

export const api = {
  async health() {
    return request(`/api/v1/health?lottery_type=${lotteryType.value}`);
  },

  async draws(params = {}) {
    const page = params.page || 1;
    const perPage = params.per_page || 50;
    return request(
      `/api/v1/draws?page=${page}&per_page=${perPage}&lottery_type=${lotteryType.value}`
    );
  },

  async latestDraw() {
    return request(`/api/v1/draws/latest?lottery_type=${lotteryType.value}`);
  },

  async frequency() {
    return request(`/api/v1/analysis/frequency?lottery_type=${lotteryType.value}&type=both`);
  },

  async hotCold(cutoff = 10) {
    return request(
      `/api/v1/analysis/hot-cold?lottery_type=${lotteryType.value}&cutoff=${cutoff}`
    );
  },

  async overdue() {
    return request(`/api/v1/analysis/overdue?lottery_type=${lotteryType.value}`);
  },

  async trend(number, window = 50) {
    return request(
      `/api/v1/analysis/trend/${number}?lottery_type=${lotteryType.value}&window=${window}`
    );
  },

  async summary() {
    return request(`/api/v1/analysis/summary?lottery_type=${lotteryType.value}`);
  },

  async patterns() {
    return request(`/api/v1/analysis/patterns/distribution?lottery_type=${lotteryType.value}`);
  },

  async pairs() {
    return request(`/api/v1/analysis/pairs/top?lottery_type=${lotteryType.value}&limit=200`);
  },

  async pairDetails(number) {
    return request(
      `/api/v1/analysis/pairs/top/${number}?lottery_type=${lotteryType.value}&limit=200`
    );
  },

  async generate(strategy = "hot", count = 1) {
    return request(
      `/api/v1/analysis/generate?lottery_type=${lotteryType.value}&strategy=${strategy}&count=${count}`
    );
  },

  // User-draws backed by localStorage (backend has no user-draws endpoint)
  addDraw(draw) {
    const userDraws = getUserDraws();
    if (userDraws.some((d) => d.draw_number === draw.draw_number)) {
      return false;
    }
    userDraws.unshift(draw);
    saveUserDraws(userDraws);
    return true;
  },

  getUserDrawCount() {
    return getUserDraws().length;
  },

  clearUserDraws() {
    localStorage.removeItem(STORAGE_KEY);
  },

  // Refresh data by triggering a scrape
  async refreshData() {
    return request(`/api/v1/scrape/trigger`, {
      method: "POST",
      body: JSON.stringify({ source: "github", lottery_type: lotteryType.value }),
    });
  },

  async scrapeTrigger() {
    return request(`/api/v1/scrape/trigger`, {
      method: "POST",
      body: JSON.stringify({ source: "github", lottery_type: lotteryType.value }),
    });
  },

  async scrapeStatus(jobId) {
    return request(`/api/v1/scrape/status/${jobId}`);
  },

  async scrapeLogs() {
    return request(`/api/v1/scrape/logs?lottery_type=${lotteryType.value}&limit=20`);
  },

  async jackpotLatest() {
    return request(`/api/v1/jackpot/latest?lottery_type=${lotteryType.value}`);
  },

  async jackpotHistory(limit = 30) {
    return request(`/api/v1/jackpot/history?lottery_type=${lotteryType.value}&limit=${limit}`);
  },

  async jackpotScrape() {
    return request(`/api/v1/jackpot/scrape`, { method: "POST" });
  },
};
