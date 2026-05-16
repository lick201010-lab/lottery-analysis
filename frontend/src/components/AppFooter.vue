<script setup>
import LogoIcon from "./LogoIcon.vue";

const linkGroups = [
  {
    title: "快速链接",
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
    title: "帮助中心",
    links: [
      { label: "常见问题", path: "#" },
      { label: "玩法说明", path: "#" },
      { label: "奖金规则", path: "#" },
      { label: "自我排除", path: "#" },
    ],
  },
  {
    title: "法律合规",
    links: [
      { label: "免责声明", path: "#" },
      { label: "隐私政策", path: "#" },
      { label: "服务条款", path: "#" },
      { label: "联系我们", path: "#" },
    ],
  },
];
</script>

<template>
  <footer class="border-t border-white/20 bg-white/80 backdrop-blur-xl mt-auto">
    <div class="max-w-[1280px] mx-auto px-6 py-12">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
        <div class="lg:col-span-2">
          <div class="flex items-center gap-2.5 mb-4">
            <LogoIcon :size="36" />
            <span class="text-xl font-bold tracking-tight text-[#0a0e27]">弈彩</span>
          </div>
          <p class="text-sm text-[#64748d] leading-relaxed max-w-sm">
            专业的开奖数据统计分析平台，提供六合彩与双色球的深度统计、走势分析与模拟选号功能。
          </p>
          <p class="text-xs text-[#64748d]/70 mt-4">YiCai &copy; 2026</p>
        </div>
        <div v-for="group in linkGroups" :key="group.title">
          <h4 class="text-sm font-bold text-[#0a0e27] mb-4">{{ group.title }}</h4>
          <ul class="space-y-2.5">
            <li v-for="link in group.links" :key="link.label">
              <router-link
                v-if="link.path !== '#'"
                :to="link.path"
                class="text-sm text-[#64748d] hover:text-[#533afd] transition-colors"
              >{{ link.label }}</router-link>
              <span v-else class="text-sm text-[#64748d]/50 cursor-default">{{ link.label }}</span>
            </li>
          </ul>
        </div>
      </div>
      <div class="mt-10 pt-6 border-t border-[#e3e8ee]">
        <div class="text-center space-y-3">
          <p class="text-xs text-[#64748d]/70">
            免责声明：本平台仅提供开奖数据的统计分析服务，所有内容仅供娱乐参考，不构成任何投注建议或诱导。
            彩票中奖号码为随机产生，历史数据不能预测未来结果。请理性娱乐，切勿沉迷。
          </p>
          <p class="text-xs text-[#64748d]/50">
            访问本网站即表示您已年满18周岁，并同意我们的服务条款与隐私政策。
          </p>
        </div>
      </div>
    </div>
  </footer>
</template>
