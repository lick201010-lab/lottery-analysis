<script setup>
import LogoIcon from "./LogoIcon.vue";

const linkGroups = [
  {
    title: "快速入口",
    links: [
      { label: "数据概览", path: "/" },
      { label: "号码统计", path: "/frequency" },
      { label: "走势分析", path: "/patterns" },
      { label: "组合分析", path: "/pairs" },
      { label: "模拟选号", path: "/generate" },
      { label: "历史记录", path: "/data" },
    ],
  },
  {
    title: "数据说明",
    links: [
      { label: "常见问题", path: "/guide" },
      { label: "规则说明", path: "/odds" },
      { label: "奖金规则", path: "/jackpot" },
      { label: "投注策略", path: "/strategy" },
    ],
  },
  {
    title: "法律合规",
    links: [
      { label: "关于我们", path: "/about" },
      { label: "隐私政策", path: "/privacy" },
      { label: "理性投注", path: "/responsible" },
    ],
  },
];
</script>

<template>
  <footer class="mt-auto border-t border-[#e2e8f0] bg-[#f8fafc]">
    <div class="mx-auto max-w-[1440px] px-6 sm:px-8 py-12">
      <div class="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-5">
        <div class="lg:col-span-2">
          <div class="mb-4 flex items-center gap-2.5">
            <LogoIcon :size="36" />
            <span class="text-xl font-bold tracking-tight text-[#233142]">弈彩</span>
          </div>
          <p class="max-w-sm text-sm leading-relaxed text-[#7d867f]">
            专注开奖数据整理、历史统计与趋势复盘，帮助你更清楚地理解号码分布。
          </p>
          <p class="mt-4 text-xs text-[#7d867f]/70">YiCai &copy; 2026</p>
        </div>

        <div v-for="group in linkGroups" :key="group.title">
          <h4 class="mb-4 text-sm font-bold text-[#233142]">{{ group.title }}</h4>
          <ul class="space-y-2.5">
            <li v-for="link in group.links" :key="link.label">
              <router-link
                v-if="link.path !== '#'"
                :to="link.path"
                class="text-sm text-[#7d867f] transition-colors hover:text-[#6f5737]"
              >
                {{ link.label }}
              </router-link>
              <span v-else class="cursor-default text-sm text-[#7d867f]/50">{{ link.label }}</span>
            </li>
          </ul>
        </div>
      </div>

      <div class="mt-10 border-t border-[#ddd4c7] pt-6">
        <div class="space-y-3 text-center">
          <p class="text-xs leading-6 text-[#7d867f]/75">
            免责声明：本平台仅提供开奖数据的统计分析服务，所有内容仅供娱乐参考，不构成任何投注建议或诱导。
            彩票中奖号码为随机产生，历史数据不能预测未来结果。请理性娱乐，切勿沉迷。
          </p>
          <p class="text-xs text-[#7d867f]/55">
            访问本网站即表示您已年满18周岁，并同意我们的服务条款与隐私政策。
          </p>
        </div>
      </div>
    </div>
  </footer>
</template>
