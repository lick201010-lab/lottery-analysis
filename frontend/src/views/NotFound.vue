<script setup>
import { useHead } from "@unhead/vue";
import { useSEO } from "../composables/useSEO.js";

useSEO({
  title: "页面未找到",
  description: "你访问的页面不存在。可返回弈彩首页，继续查看开奖记录、号码统计、走势分析与玩法说明。",
  path: "/404",
});

useHead({
  meta: [{ name: "robots", content: "noindex" }],
});

const links = [
  { label: "首页", path: "/" },
  { label: "开奖记录", path: "/data" },
  { label: "号码统计", path: "/frequency" },
  { label: "模拟选号", path: "/generate" },
  { label: "理性娱乐", path: "/responsible" },
];
</script>

<template>
  <div class="ref-card p-8 sm:p-10">
    <div class="max-w-2xl">
      <p class="text-sm font-medium tracking-[0.18em] text-[#8d6f47]">404</p>
      <h1 class="mt-3 text-3xl font-semibold text-[#233142]">页面未找到</h1>
      <p class="mt-4 text-base leading-7 text-[#66706b]">
        这个页面可能已经移动或不存在。你可以回到首页，继续查看开奖数据、号码统计与走势分析。
      </p>
      <div class="mt-8 flex flex-wrap gap-3">
        <router-link
          v-for="link in links"
          :key="link.path"
          :to="link.path"
          class="rounded-md border border-[#d8cbb9] bg-[#fffaf2] px-4 py-2 text-sm font-medium text-[#233142] transition hover:border-[#b9863c] hover:text-[#8d6f47]"
        >
          {{ link.label }}
        </router-link>
      </div>
    </div>
  </div>
</template>
