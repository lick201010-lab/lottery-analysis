import { copyFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { join } from "node:path";

const rootDir = fileURLToPath(new URL("../", import.meta.url));
const generatedDir = join(rootDir, ".generated");
const distDir = join(rootDir, process.env.VITE_OUT_DIR || "dist");

for (const file of ["sitemap.xml", "sitemap-baidu.xml"]) {
  const source = join(generatedDir, file);
  if (!existsSync(source)) {
    throw new Error(`Missing generated SEO asset: ${source}`);
  }
  copyFileSync(source, join(distDir, file));
}

console.log("[seo] copied fresh sitemaps into dist");
