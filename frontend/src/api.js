import { ref } from "vue";

export const lotteryType = ref("marksix");

const STORAGE_KEY = "lottery_user_draws";

const LOTTERY_CONFIG = {
  marksix: {
    maxRegular: 49,
    maxSpecial: 49,
    dataPath: "/data/draws.json",
  },
  ssq: {
    maxRegular: 33,
    maxSpecial: 16,
    dataPath: "/data/ssq_draws.json",
  },
};

function getConfig() {
  return LOTTERY_CONFIG[lotteryType.value] || LOTTERY_CONFIG.marksix;
}

function getMaxRegular() {
  return getConfig().maxRegular;
}

// Cache per lottery type
let _currentType = null;
let _baseDraws = null;
let _draws = null;
let _frequency = null;
let _pairs = null;
let _patterns = null;
let _trends = null;

async function loadJson(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Failed to load ${path}`);
  return res.json();
}

function clearCache() {
  _draws = null;
  _frequency = null;
  _pairs = null;
  _patterns = null;
  _trends = null;
  _baseDraws = null;
  _currentType = null;
}

async function getBaseDraws() {
  if (_currentType !== lotteryType.value) {
    clearCache();
    _currentType = lotteryType.value;
  }
  if (!_baseDraws) {
    _baseDraws = await loadJson(getConfig().dataPath);
  }
  return _baseDraws;
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

async function getAllDraws() {
  if (_draws) return _draws;
  const base = await getBaseDraws();
  const user = getUserDraws();
  _draws = [...user, ...base];
  return _draws;
}

async function getFrequencyData() {
  if (_frequency) return _frequency;
  const draws = await getAllDraws();
  _frequency = computeFrequency(draws);
  return _frequency;
}

async function getPairsData() {
  if (_pairs) return _pairs;
  const draws = await getAllDraws();
  _pairs = computePairs(draws);
  return _pairs;
}

async function getPatternsData() {
  if (_patterns) return _patterns;
  const draws = await getAllDraws();
  _patterns = computePatterns(draws);
  return _patterns;
}

async function getTrendsData() {
  if (_trends) return _trends;
  const draws = await getAllDraws();
  _trends = computeTrends(draws);
  return _trends;
}

// Computation functions
function computeFrequency(draws) {
  const maxRegular = getMaxRegular();
  const freq = {};
  for (let n = 1; n <= maxRegular; n++) {
    freq[n] = { total: 0, special: 0, last_date: null, last_draw: null, last_seq: -1 };
  }
  for (let idx = 0; idx < draws.length; idx++) {
    const d = draws[draws.length - 1 - idx];
    const regulars = [d.num1, d.num2, d.num3, d.num4, d.num5, d.num6];
    for (const n of regulars) {
      if (freq[n]) {
        freq[n].total += 1;
        freq[n].last_date = d.draw_date;
        freq[n].last_draw = d.draw_number;
        freq[n].last_seq = idx;
      }
    }
    if (freq[d.special_num]) {
      freq[d.special_num].special += 1;
      if (freq[d.special_num].last_seq < idx) {
        freq[d.special_num].last_date = d.draw_date;
        freq[d.special_num].last_draw = d.draw_number;
        freq[d.special_num].last_seq = idx;
      }
    }
  }
  const total_draws = draws.length;
  const result = [];
  for (let n = 1; n <= maxRegular; n++) {
    const f = freq[n];
    const missed = f.last_seq >= 0 ? total_draws - f.last_seq - 1 : total_draws;
    const score = f.total * 100 + f.special * 50;
    result.push({
      number: n,
      total_appearances: f.total,
      special_appearances: f.special,
      last_appearance_date: f.last_date,
      last_appearance_draw: f.last_draw,
      consecutive_missed: missed,
      hotness_score: score,
    });
  }
  return result.sort((a, b) => b.hotness_score - a.hotness_score);
}

function computePairs(draws) {
  const pairCounts = new Map();
  for (const d of draws) {
    const regulars = [d.num1, d.num2, d.num3, d.num4, d.num5, d.num6];
    for (let i = 0; i < 6; i++) {
      for (let j = i + 1; j < 6; j++) {
        const a = regulars[i], b = regulars[j];
        const key = a < b ? `${a}-${b}` : `${b}-${a}`;
        pairCounts.set(key, (pairCounts.get(key) || 0) + 1);
      }
    }
  }
  const result = [];
  for (const [key, count] of pairCounts.entries()) {
    const [a, b] = key.split("-").map(Number);
    result.push({ num_a: a, num_b: b, co_occurrences: count });
  }
  return result.sort((a, b) => b.co_occurrences - a.co_occurrences);
}

function computePatterns(draws) {
  const maxRegular = getMaxRegular();
  const oddEvenCounts = {};
  const bigSmallCounts = {};
  const consecutiveCounts = {};
  const rangeSize = 10;
  const rangeLabels = [];
  for (let i = 1; i <= maxRegular; i += rangeSize) {
    rangeLabels.push(`${i}-${Math.min(i + rangeSize - 1, maxRegular)}`);
  }
  const rangeCountsDict = {};
  for (const lbl of rangeLabels) rangeCountsDict[lbl] = 0;
  const sumValues = [];

  for (const d of draws) {
    const regulars = [d.num1, d.num2, d.num3, d.num4, d.num5, d.num6];
    const oeKey = `${d.odd_count}:${d.even_count}`;
    oddEvenCounts[oeKey] = (oddEvenCounts[oeKey] || 0) + 1;
    const bsKey = `${d.small_count}:${d.big_count}`;
    bigSmallCounts[bsKey] = (bigSmallCounts[bsKey] || 0) + 1;
    const sortedNs = [...regulars].sort((a, b) => a - b);
    let cons = 0;
    for (let i = 0; i < 5; i++) {
      if (sortedNs[i + 1] - sortedNs[i] === 1) cons++;
    }
    consecutiveCounts[String(cons)] = (consecutiveCounts[String(cons)] || 0) + 1;
    for (const n of regulars) {
      const idx = Math.min(Math.floor((n - 1) / rangeSize), rangeLabels.length - 1);
      rangeCountsDict[rangeLabels[idx]]++;
    }
    sumValues.push(d.sum_total);
  }

  let sumHistogram = [];
  if (sumValues.length > 0) {
    const sMin = Math.min(...sumValues);
    const sMax = Math.max(...sumValues);
    const binWidth = Math.max(1, Math.floor((sMax - sMin) / 20));
    const bins = {};
    for (const s of sumValues) {
      const b = Math.floor(s / binWidth) * binWidth;
      bins[b] = (bins[b] || 0) + 1;
    }
    sumHistogram = Object.entries(bins).map(([k, v]) => ({ bin: Number(k), count: v })).sort((a, b) => a.bin - b.bin);
  }

  const oddTotal = draws.reduce((s, d) => s + d.odd_count, 0);
  const evenTotal = draws.reduce((s, d) => s + d.even_count, 0);
  const smallTotal = draws.reduce((s, d) => s + d.small_count, 0);
  const bigTotal = draws.reduce((s, d) => s + d.big_count, 0);
  const total = draws.length;

  return {
    total_draws: total,
    odd_even: { labels: ["奇数", "偶数"], values: [oddTotal, evenTotal] },
    big_small: { labels: ["大数", "小数"], values: [bigTotal, smallTotal] },
    consecutive: { labels: Object.keys(consecutiveCounts), values: Object.values(consecutiveCounts) },
    range_distribution: { labels: rangeLabels, values: rangeLabels.map((l) => rangeCountsDict[l]) },
    sum_histogram: sumHistogram,
    summary: {
      odd_pct: (oddTotal + evenTotal) > 0 ? Math.round((oddTotal / (oddTotal + evenTotal)) * 100 * 10) / 10 : 0,
      even_pct: (oddTotal + evenTotal) > 0 ? Math.round((evenTotal / (oddTotal + evenTotal)) * 100 * 10) / 10 : 0,
      small_pct: (smallTotal + bigTotal) > 0 ? Math.round((smallTotal / (smallTotal + bigTotal)) * 100 * 10) / 10 : 0,
      big_pct: (smallTotal + bigTotal) > 0 ? Math.round((bigTotal / (smallTotal + bigTotal)) * 100 * 10) / 10 : 0,
      avg_sum: total > 0 ? Math.round((sumValues.reduce((a, b) => a + b, 0) / total) * 10) / 10 : 0,
      sum_range: sumValues.length > 0 ? `${Math.min(...sumValues)}-${Math.max(...sumValues)}` : "N/A",
    },
  };
}

function computeTrends(draws) {
  const maxRegular = getMaxRegular();
  const regularsPerDraw = draws.map((d) => [d.num1, d.num2, d.num3, d.num4, d.num5, d.num6]);
  const window = 50;
  const trends = {};
  for (let n = 1; n <= maxRegular; n++) {
    const data = [];
    for (let i = 0; i < regularsPerDraw.length; i++) {
      if (i < window - 1) continue;
      let count = 0;
      for (let j = i - window + 1; j <= i; j++) {
        if (regularsPerDraw[j].includes(n)) count++;
      }
      data.push({ draw_number: draws[draws.length - 1 - i].draw_number, count });
    }
    trends[String(n)] = data;
  }
  return trends;
}

// Number generation strategies
function genHot(freqs, count) {
  const maxRegular = getMaxRegular();
  const valid = freqs.filter((f) => f.number <= maxRegular);
  return valid.slice(0, count * 2).map((f) => f.number).filter((v, i, a) => a.indexOf(v) === i).slice(0, count);
}

function genCold(freqs, count) {
  const maxRegular = getMaxRegular();
  const valid = freqs.filter((f) => f.number <= maxRegular);
  return valid.slice(-count * 2).reverse().map((f) => f.number).filter((v, i, a) => a.indexOf(v) === i).slice(0, count);
}

function genBalanced(freqs, count) {
  const maxRegular = getMaxRegular();
  const valid = freqs.filter((f) => f.number <= maxRegular);
  const hotPool = valid.slice(0, Math.floor(valid.length / 3));
  const midPool = valid.slice(Math.floor(valid.length / 3), Math.floor(2 * valid.length / 3));
  const coldPool = valid.slice(Math.floor(2 * valid.length / 3));
  const result = [];
  const pools = [
    [hotPool, Math.ceil(count / 3)],
    [midPool, Math.floor(count / 3)],
    [coldPool, count - Math.ceil(count / 3) - Math.floor(count / 3)],
  ];
  for (const [pool, n] of pools) {
    if (pool.length > 0) {
      const shuffled = pool.map((f) => f.number).sort(() => Math.random() - 0.5);
      result.push(...shuffled.slice(0, Math.min(n, shuffled.length)));
    }
  }
  return result.slice(0, count);
}

function genWeightedRandom(freqs, count) {
  const maxRegular = getMaxRegular();
  const valid = freqs.filter((f) => f.number <= maxRegular).map((f) => ({ num: f.number, weight: Math.max(f.hotness_score, 1) }));
  const result = [];
  let pool = [...valid];
  for (let i = 0; i < count; i++) {
    if (pool.length === 0) break;
    const totalWeight = pool.reduce((s, p) => s + p.weight, 0);
    let r = Math.random() * totalWeight;
    for (let j = 0; j < pool.length; j++) {
      r -= pool[j].weight;
      if (r <= 0) {
        result.push(pool[j].num);
        pool.splice(j, 1);
        break;
      }
    }
  }
  return result;
}

function genOverdue(freqs, count) {
  const maxRegular = getMaxRegular();
  const valid = freqs.filter((f) => f.number <= maxRegular);
  return valid.sort((a, b) => b.consecutive_missed - a.consecutive_missed).slice(0, count).map((f) => f.number);
}

function genPairChain(freqs, pairs, count) {
  const maxRegular = getMaxRegular();
  const valid = freqs.filter((f) => f.number <= maxRegular).map((f) => f.number);
  if (valid.length === 0) return [1, 2, 3, 4, 5, 6].slice(0, count);
  const pairIndex = {};
  for (const p of pairs) {
    if (!pairIndex[p.num_a]) pairIndex[p.num_a] = [];
    if (!pairIndex[p.num_b]) pairIndex[p.num_b] = [];
    pairIndex[p.num_a].push({ num: p.num_b, co: p.co_occurrences });
    pairIndex[p.num_b].push({ num: p.num_a, co: p.co_occurrences });
  }
  let current = valid[0];
  const result = [current];
  while (result.length < count) {
    const candidates = pairIndex[current] || [];
    candidates.sort((a, b) => b.co - a.co);
    let next = null;
    for (const c of candidates) {
      if (!result.includes(c.num) && c.num <= maxRegular) {
        next = c.num;
        break;
      }
    }
    if (next === null) {
      for (const n of valid) {
        if (!result.includes(n)) {
          next = n;
          break;
        }
      }
    }
    if (next === null) break;
    result.push(next);
    current = next;
  }
  return result;
}

function genSpecial(freqs) {
  const maxRegular = getMaxRegular();
  const valid = freqs.filter((f) => f.number <= maxRegular);
  if (valid.length === 0) return 1;
  const totalWeight = valid.reduce((s, f) => s + Math.max(f.hotness_score, 1), 0);
  let r = Math.random() * totalWeight;
  for (const f of valid) {
    r -= Math.max(f.hotness_score, 1);
    if (r <= 0) return f.number;
  }
  return valid[0].number;
}

export const api = {
  async health() {
    const draws = await getAllDraws();
    return {
      status: "ok",
      total_draws: draws.length,
      last_scrape: draws[0]?.draw_date || null,
    };
  },

  async draws(params = {}) {
    const all = await getAllDraws();
    const page = params.page || 1;
    const perPage = params.per_page || 50;
    const start = (page - 1) * perPage;
    return {
      draws: all.slice(start, start + perPage),
      total: all.length,
    };
  },

  async latestDraw() {
    const draws = await getAllDraws();
    return draws[0] || null;
  },

  async frequency() {
    return getFrequencyData();
  },

  async hotCold(cutoff = 10) {
    const freq = await getFrequencyData();
    return {
      hot: freq.slice(0, cutoff),
      cold: freq.slice(-cutoff).reverse(),
    };
  },

  async overdue() {
    const freq = await getFrequencyData();
    return [...freq].sort((a, b) => b.consecutive_missed - a.consecutive_missed);
  },

  async trend(number) {
    const trends = await getTrendsData();
    return { data: trends[String(number)] || [] };
  },

  async summary() {
    const draws = await getAllDraws();
    const freq = await getFrequencyData();
    const pairs = await getPairsData();
    const hot = freq.slice(0, 3);
    const cold = freq.slice(-3).reverse();
    const overdueSorted = [...freq].sort((a, b) => b.consecutive_missed - a.consecutive_missed);
    const mostOverdue = overdueSorted[0];
    const topPairs = pairs.slice(0, 3);
    return {
      total_draws: draws.length,
      latest_date: draws[0]?.draw_date || null,
      top_hot: hot.map((f) => ({ number: f.number, total_appearances: f.total_appearances, consecutive_missed: f.consecutive_missed, hotness_score: f.hotness_score })),
      top_cold: cold.map((f) => ({ number: f.number, total_appearances: f.total_appearances, consecutive_missed: f.consecutive_missed, hotness_score: f.hotness_score })),
      most_overdue: mostOverdue ? { number: mostOverdue.number, total_appearances: mostOverdue.total_appearances, consecutive_missed: mostOverdue.consecutive_missed, hotness_score: mostOverdue.hotness_score } : null,
      top_pairs: topPairs.map((p) => ({ num_a: p.num_a, num_b: p.num_b, co_occurrences: p.co_occurrences })),
    };
  },

  async patterns() {
    return getPatternsData();
  },

  async pairs() {
    const pairs = await getPairsData();
    return { pairs };
  },

  async pairDetails(number) {
    const pairs = await getPairsData();
    return {
      pairs: pairs.filter((p) => p.num_a === number || p.num_b === number),
    };
  },

  async generate(strategy = "hot", count = 1) {
    const freq = await getFrequencyData();
    const pairs = await getPairsData();
    const sets = [];
    for (let i = 0; i < count; i++) {
      let regular;
      if (strategy === "hot") regular = genHot(freq, 6);
      else if (strategy === "cold") regular = genCold(freq, 6);
      else if (strategy === "balanced") regular = genBalanced(freq, 6);
      else if (strategy === "weighted_random") regular = genWeightedRandom(freq, 6);
      else if (strategy === "overdue") regular = genOverdue(freq, 6);
      else if (strategy === "pair_chain") regular = genPairChain(freq, pairs, 6);
      else regular = genHot(freq, 6);
      sets.push({
        regular: regular.sort((a, b) => a - b),
        special: genSpecial(freq),
        strategy,
      });
    }
    return { sets, strategy };
  },

  // Add a new draw manually
  addDraw(draw) {
    const userDraws = getUserDraws();
    if (userDraws.some((d) => d.draw_number === draw.draw_number)) {
      return false;
    }
    userDraws.unshift(draw);
    saveUserDraws(userDraws);
    clearCache();
    return true;
  },

  // Get count of user-added draws
  getUserDrawCount() {
    return getUserDraws().length;
  },

  // Clear user-added draws
  clearUserDraws() {
    localStorage.removeItem(STORAGE_KEY);
    clearCache();
  },

  // Refresh data (clear cache and reload)
  async refreshData() {
    clearCache();
    return getAllDraws();
  },

  // Placeholder: frontend is static, scraping runs via scheduled task
  async scrapeTrigger() {
    return { job_id: "local", status: "scheduled_task" };
  },

  async scrapeStatus() {
    return { status: "completed", draws_fetched: 0, draws_new: 0 };
  },

  async scrapeLogs() {
    return [];
  },
};
