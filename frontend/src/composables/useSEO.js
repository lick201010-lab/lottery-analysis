import { useHead } from "@unhead/vue";
import { useRoute } from "vue-router";
import { computed } from "vue";

const SITE_URL = "https://yicai.ckl.hk";
const SITE_NAME = "弈彩 YiCai";
const DEFAULT_OG_IMAGE = `${SITE_URL}/og-image.png`;
const BREADCRUMB_LABELS = {
  "/data": "开奖记录",
  "/frequency": "号码统计",
  "/patterns": "走势分析",
  "/pairs": "组合分析",
  "/generate": "模拟选号",
  "/jackpot": "奖金计算",
  "/guide": "玩法指南",
  "/odds": "中奖概率",
  "/strategy": "数据方法",
  "/patterns-article": "走势专题",
  "/responsible": "理性娱乐",
  "/marksix/results": "六合彩开奖结果查询",
  "/marksix/frequency": "六合彩号码频率",
  "/marksix/rules": "六合彩玩法规则",
  "/marksix/odds": "六合彩中奖概率",
  "/ssq/results": "双色球开奖结果查询",
  "/ssq/frequency": "双色球号码频率",
  "/ssq/rules": "双色球玩法规则",
  "/ssq/odds": "双色球中奖概率",
  "/qxc/results": "7星彩开奖结果查询",
  "/qxc/frequency": "7星彩号码频率",
  "/qxc/rules": "7星彩玩法规则",
  "/qxc/odds": "7星彩中奖概率",
  "/qxc/history": "7星彩历史开奖记录",
  "/privacy": "隐私政策",
  "/about": "关于我们",
  "/404": "页面未找到",
};

/**
 * Inject SEO meta (title / description / og / twitter / canonical) for a page.
 *
 * @param {Object} opts
 * @param {string} opts.title       Page-specific title (will be appended " - 弈彩 YiCai" if missing brand)
 * @param {string} opts.description Meta description (≤155 chars recommended)
 * @param {string} [opts.path]      Override route path for canonical (defaults to current route)
 * @param {string} [opts.image]     OG image URL (defaults to /og-image.png)
 * @param {Array}  [opts.jsonLd]    Extra JSON-LD blocks to inject as <script type="application/ld+json">
 */
export function useSEO(opts) {
  const route = useRoute();
  const path = computed(() => opts.path || route.path);
  const url = computed(() => `${SITE_URL}${path.value === "/" ? "" : path.value}`);

  const fullTitle = computed(() => {
    const t = opts.title || SITE_NAME;
    return t.includes(SITE_NAME) || t.includes("弈彩") ? t : `${t} - ${SITE_NAME}`;
  });

  const description = computed(() => opts.description || "弈彩 — 彩票开奖数据、号码统计与走势分析平台。");
  const image = opts.image || DEFAULT_OG_IMAGE;

  const meta = [
    { name: "description", content: description },
    // Open Graph
    { property: "og:title", content: fullTitle },
    { property: "og:description", content: description },
    { property: "og:url", content: url },
    { property: "og:type", content: "website" },
    { property: "og:image", content: image },
    // Twitter
    { name: "twitter:title", content: fullTitle },
    { name: "twitter:description", content: description },
    { name: "twitter:image", content: image },
  ];

  const link = [{ rel: "canonical", href: url }];

  const jsonLdBlocks = [...(opts.jsonLd || [])];
  if (path.value !== "/" && BREADCRUMB_LABELS[path.value]) {
    jsonLdBlocks.unshift(breadcrumb([
      { name: "首页", path: "/" },
      { name: BREADCRUMB_LABELS[path.value], path: path.value },
    ]));
  }

  const script = jsonLdBlocks.map((block) => ({
    type: "application/ld+json",
    innerHTML: JSON.stringify(block),
  }));

  useHead({ title: fullTitle, meta, link, script });
}

/**
 * Build a BreadcrumbList JSON-LD block. Pass an array of { name, path } pairs.
 */
export function breadcrumb(items) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((it, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: it.name,
      item: `${SITE_URL}${it.path === "/" ? "" : it.path}`,
    })),
  };
}

/**
 * Build a FAQPage JSON-LD block. Pass an array of { q, a } pairs.
 */
export function faqPage(items) {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: items.map((it) => ({
      "@type": "Question",
      name: it.q,
      acceptedAnswer: { "@type": "Answer", text: it.a },
    })),
  };
}

/**
 * Build a Dataset JSON-LD block. Only emit truthful, generic metadata —
 * never fabricate record counts or specific draw numbers.
 *
 * @param {Object} d
 * @param {string} d.name              Dataset name
 * @param {string} d.description       Truthful description
 * @param {string} d.path             Route path (canonical host is prefixed)
 * @param {string} [d.temporalCoverage] e.g. "2003-01-01/.." (open-ended ok)
 * @param {string[]} [d.variableMeasured] e.g. ["期号", "开奖日期", "前区号码", "后区号码"]
 */
export function dataset(d) {
  return {
    "@context": "https://schema.org",
    "@type": "Dataset",
    name: d.name,
    description: d.description,
    url: `${SITE_URL}${d.path}`,
    inLanguage: "zh-CN",
    isAccessibleForFree: true,
    creator: { "@type": "Organization", name: SITE_NAME, url: SITE_URL },
    ...(d.temporalCoverage ? { temporalCoverage: d.temporalCoverage } : {}),
    ...(d.variableMeasured ? { variableMeasured: d.variableMeasured } : {}),
  };
}
