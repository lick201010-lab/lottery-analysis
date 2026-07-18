import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const distDir = fileURLToPath(new URL("../dist/", import.meta.url));

const routeFiles = [
  "data.html",
  "frequency.html",
  "patterns.html",
  "pairs.html",
  "generate.html",
  "jackpot.html",
  "guide.html",
  "odds.html",
  "strategy.html",
  "patterns-article.html",
  "responsible.html",
  "privacy.html",
  "about.html",
  "marksix/results.html",
  "marksix/frequency.html",
  "marksix/rules.html",
  "marksix/odds.html",
  "ssq/results.html",
  "ssq/frequency.html",
  "ssq/rules.html",
  "ssq/odds.html",
];

const faqFiles = ["guide.html", "odds.html", "jackpot.html", "responsible.html"];
const topicFiles = [
  "marksix/results.html",
  "marksix/frequency.html",
  "marksix/rules.html",
  "marksix/odds.html",
  "ssq/results.html",
  "ssq/frequency.html",
  "ssq/rules.html",
  "ssq/odds.html",
];
const archiveFiles = [
  "marksix/2026.html",
  "ssq/2026.html",
  "qxc/2026.html",
];

function readDist(file) {
  const path = join(distDir, file);
  if (!existsSync(path)) {
    throw new Error(`Missing dist file: ${file}`);
  }
  return readFileSync(path, "utf8");
}

const missingBreadcrumbs = routeFiles.filter((file) => !readDist(file).includes('"@type":"BreadcrumbList"'));
if (missingBreadcrumbs.length) {
  throw new Error(`Missing BreadcrumbList JSON-LD in: ${missingBreadcrumbs.join(", ")}`);
}

const missingFaq = faqFiles.filter((file) => !readDist(file).includes('"@type":"FAQPage"'));
if (missingFaq.length) {
  throw new Error(`Missing FAQPage JSON-LD in: ${missingFaq.join(", ")}`);
}

const weakTopicPages = topicFiles.filter((file) => {
  const html = readDist(file);
  return (
    !html.includes("仅供数据分析与娱乐参考") ||
    !html.includes("开奖结果具有随机性") ||
    !html.includes('"@type":"Article"')
  );
});
if (weakTopicPages.length) {
  throw new Error(`Week3 topic pages need compliance copy and Article JSON-LD: ${weakTopicPages.join(", ")}`);
}

const weakArchivePages = archiveFiles.filter((file) => {
  const html = readDist(file);
  return (
    !html.includes("开奖归档") ||
    !html.includes('"@type":"Dataset"') ||
    !html.includes('"@type":"BreadcrumbList"') ||
    !html.includes("仅供数据分析与娱乐参考") ||
    !html.includes("开奖结果具有随机性")
  );
});
if (weakArchivePages.length) {
  throw new Error(`Week4 archive pages need archive copy, Dataset JSON-LD and compliance copy: ${weakArchivePages.join(", ")}`);
}

const sitemapPath = fileURLToPath(new URL("../dist/sitemap.xml", import.meta.url));
if (!existsSync(sitemapPath)) {
  throw new Error("Missing sitemap.xml");
}

const sitemapXml = readFileSync(sitemapPath, "utf8");
const sitemapLocs = [...sitemapXml.matchAll(/<loc>(.*?)<\/loc>/g)].map((match) => match[1]);
const duplicateSitemapLocs = sitemapLocs.filter((loc, index) => sitemapLocs.indexOf(loc) !== index);
if (duplicateSitemapLocs.length) {
  throw new Error(`Duplicate sitemap loc entries: ${[...new Set(duplicateSitemapLocs)].join(", ")}`);
}

const sitemapEntries = [...sitemapXml.matchAll(/<url>([\s\S]*?)<\/url>/g)].map((match) => match[1]);
const entriesWithoutLastmod = sitemapEntries.filter((entry) => !entry.includes("<lastmod>"));
if (entriesWithoutLastmod.length) {
  throw new Error(`Every sitemap URL must include lastmod (${entriesWithoutLastmod.length} missing)`);
}

for (const requiredPath of ["/marksix/2026/", "/ssq/2026/", "/qxc/2026/"]) {
  if (!sitemapLocs.some((loc) => loc.includes(requiredPath))) {
    throw new Error(`Sitemap missing current archive URLs for ${requiredPath}`);
  }
}

const baiduSitemapPath = fileURLToPath(new URL("../dist/sitemap-baidu.xml", import.meta.url));
const baiduSitemapXml = readFileSync(baiduSitemapPath, "utf8");
if (baiduSitemapXml.includes("/marksix/")) {
  throw new Error("Baidu sitemap must not include MarkSix URLs");
}
if (!baiduSitemapXml.includes("/ssq/") || !baiduSitemapXml.includes("/qxc/")) {
  throw new Error("Baidu sitemap must include SSQ and QXC URLs");
}

const homeHtml = readDist("index.html");
if (homeHtml.includes('"@type":"SearchAction"')) {
  throw new Error("Home page declares SearchAction without a working site search");
}
for (const badText of ["Failed to fetch", "等待数据", "暂无近期开奖"]) {
  if (homeHtml.includes(badText)) {
    throw new Error(`Home prerender contains crawler-visible fallback text: ${badText}`);
  }
}

const snapshotModuleUrl = new URL("../.generated/seoData.js", import.meta.url);
const { dashboardSnapshots } = await import(snapshotModuleUrl.href);
const latestSsqDraw = dashboardSnapshots.ssq?.latestDraw?.draw_number;
if (!latestSsqDraw || !homeHtml.includes(latestSsqDraw)) {
  throw new Error("Home prerender does not contain the latest SSQ draw snapshot");
}

const notFoundPath = join(distDir, "404.html");
if (!existsSync(notFoundPath)) {
  throw new Error("Missing custom 404.html");
}

const notFoundHtml = readFileSync(notFoundPath, "utf8");
if (!notFoundHtml.includes('name="robots"') || !notFoundHtml.includes("noindex")) {
  throw new Error("404.html must include robots noindex meta");
}

console.log("SEO Week2 + Week3 + Week4 checks passed");
