import { useHead } from "@unhead/vue";
import { useRoute } from "vue-router";
import { computed } from "vue";

const SITE_URL = "https://www.ckl.hk";
const SITE_NAME = "弈彩 YiCai";
const DEFAULT_OG_IMAGE = `${SITE_URL}/og-image.png`;

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

  const description = computed(() => opts.description || "弈彩 — 六合彩与双色球开奖数据统计分析平台。");
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

  const script = (opts.jsonLd || []).map((block) => ({
    type: "application/ld+json",
    children: JSON.stringify(block),
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
