import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  ssgOptions: {
    // The production VM has 1 GB RAM; the default concurrency of 20 can OOM
    // while each route owns a JSDOM instance.
    concurrency: 2,
  },
  build: {
    outDir: process.env.VITE_OUT_DIR || "dist",
  },
});
