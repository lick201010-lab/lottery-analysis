import { ref } from "vue";

// Use env variable for production, fallback to local proxy for development
const API_HOST = import.meta.env.VITE_API_HOST || "";
const BASE = `${API_HOST}/api/v1`;

export const lotteryType = ref("marksix");

async function request(url, opts = {}) {
  const res = await fetch(`${BASE}${url}`, {
    headers: { "Content-Type": "application/json", ...opts.headers },
    ...opts,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || res.statusText);
  }
  return res.json();
}

function ltParam() {
  return `lottery_type=${encodeURIComponent(lotteryType.value)}`;
}

export const api = {
  health: () => request("/health"),

  draws: (params = {}) => {
    const qs = new URLSearchParams({ ...params, lottery_type: lotteryType.value }).toString();
    return request(`/draws?${qs}`);
  },

  latestDraw: () => request(`/draws/latest?${ltParam()}`),

  scrapeTrigger: (source = "hkjc") =>
    request("/scrape/trigger", {
      method: "POST",
      body: JSON.stringify({ source, lottery_type: lotteryType.value }),
    }),

  scrapeStatus: (jobId) => request(`/scrape/status/${jobId}`),

  scrapeLogs: () => request("/scrape/logs"),

  frequency: () => request(`/analysis/frequency?${ltParam()}`),

  hotCold: (cutoff = 10) => request(`/analysis/hot-cold?cutoff=${cutoff}&${ltParam()}`),

  overdue: () => request(`/analysis/overdue?${ltParam()}`),

  trend: (number, window = 50) =>
    request(`/analysis/trend/${number}?window=${window}&${ltParam()}`),

  summary: () => request(`/analysis/summary?${ltParam()}`),

  patterns: () => request(`/analysis/patterns/distribution?${ltParam()}`),

  pairs: () => request(`/analysis/pairs/top?${ltParam()}`),

  pairDetails: (number) => request(`/analysis/pairs/top/${number}?${ltParam()}`),

  generate: (strategy = "hot", count = 1) =>
    request(`/analysis/generate?strategy=${strategy}&count=${count}&${ltParam()}`),
};
