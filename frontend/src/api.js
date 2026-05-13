import { ref } from "vue";

export const lotteryType = ref("marksix");

// Cached data
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

async function getDraws() {
  if (!_draws) _draws = await loadJson("/data/draws.json");
  return _draws;
}

async function getFrequency() {
  if (!_frequency) _frequency = await loadJson("/data/frequency.json");
  return _frequency;
}

async function getPairs() {
  if (!_pairs) _pairs = await loadJson("/data/pairs.json");
  return _pairs;
}

async function getPatterns() {
  if (!_patterns) _patterns = await loadJson("/data/patterns.json");
  return _patterns;
}

async function getTrends() {
  if (!_trends) _trends = await loadJson("/data/trends.json");
  return _trends;
}

// Number generation strategies
function genHot(freqs, count) {
  const valid = freqs.filter((f) => f.number <= 49);
  return valid.slice(0, count * 2).map((f) => f.number).filter((v, i, a) => a.indexOf(v) === i).slice(0, count);
}

function genCold(freqs, count) {
  const valid = freqs.filter((f) => f.number <= 49);
  return valid.slice(-count * 2).reverse().map((f) => f.number).filter((v, i, a) => a.indexOf(v) === i).slice(0, count);
}

function genBalanced(freqs, count) {
  const valid = freqs.filter((f) => f.number <= 49);
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
  const valid = freqs.filter((f) => f.number <= 49).map((f) => ({ num: f.number, weight: Math.max(f.hotness_score, 1) }));
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
  const valid = freqs.filter((f) => f.number <= 49);
  return valid.sort((a, b) => b.consecutive_missed - a.consecutive_missed).slice(0, count).map((f) => f.number);
}

function genPairChain(freqs, pairs, count) {
  const valid = freqs.filter((f) => f.number <= 49).map((f) => f.number);
  if (valid.length === 0) return [1, 2, 3, 4, 5, 6].slice(0, count);
  const pairIndex = {};
  for (const p of pairs) {
    pairIndex.setdefault(p.num_a, []).push({ num: p.num_b, co: p.co_occurrences });
    pairIndex.setdefault(p.num_b, []).push({ num: p.num_a, co: p.co_occurrences });
  }
  let current = valid[0];
  const result = [current];
  while (result.length < count) {
    const candidates = pairIndex[current] || [];
    candidates.sort((a, b) => b.co - a.co);
    let next = null;
    for (const c of candidates) {
      if (!result.includes(c.num) && c.num <= 49) {
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
  const valid = freqs.filter((f) => f.number <= 49);
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
    const draws = await getDraws();
    return {
      status: "ok",
      total_draws: draws.length,
      last_scrape: draws[0]?.draw_date || null,
    };
  },

  async draws(params = {}) {
    const all = await getDraws();
    const page = params.page || 1;
    const perPage = params.per_page || 50;
    const start = (page - 1) * perPage;
    return {
      draws: all.slice(start, start + perPage),
      total: all.length,
    };
  },

  async latestDraw() {
    const draws = await getDraws();
    return draws[0] || null;
  },

  async frequency() {
    return getFrequency();
  },

  async hotCold(cutoff = 10) {
    const freq = await getFrequency();
    return {
      hot: freq.slice(0, cutoff),
      cold: freq.slice(-cutoff).reverse(),
    };
  },

  async overdue() {
    const freq = await getFrequency();
    return [...freq].sort((a, b) => b.consecutive_missed - a.consecutive_missed);
  },

  async trend(number) {
    const trends = await getTrends();
    return { data: trends[String(number)] || [] };
  },

  async summary() {
    const draws = await getDraws();
    const freq = await getFrequency();
    const pairs = await getPairs();
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
    return getPatterns();
  },

  async pairs() {
    const pairs = await getPairs();
    return { pairs };
  },

  async pairDetails(number) {
    const pairs = await getPairs();
    return {
      pairs: pairs.filter((p) => p.num_a === number || p.num_b === number),
    };
  },

  async generate(strategy = "hot", count = 1) {
    const freq = await getFrequency();
    const pairs = await getPairs();
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
};
