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
];

const faqFiles = ["guide.html", "odds.html", "jackpot.html", "responsible.html"];

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

const notFoundPath = join(distDir, "404.html");
if (!existsSync(notFoundPath)) {
  throw new Error("Missing custom 404.html");
}

const notFoundHtml = readFileSync(notFoundPath, "utf8");
if (!notFoundHtml.includes('name="robots"') || !notFoundHtml.includes("noindex")) {
  throw new Error("404.html must include robots noindex meta");
}

console.log("SEO Week2 checks passed");
