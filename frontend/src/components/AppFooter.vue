<script setup>
import LogoIcon from "./LogoIcon.vue";
import NewsletterSignup from "./NewsletterSignup.vue";

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
      { label: "数据方法", path: "/strategy" },
    ],
  },
  {
    title: "专题入口",
    links: [
      { label: "六合彩开奖", path: "/marksix/results" },
      { label: "六合彩频率", path: "/marksix/frequency" },
      { label: "双色球开奖", path: "/ssq/results" },
      { label: "双色球规则", path: "/ssq/rules" },
    ],
  },
  {
    title: "法律合规",
    links: [
      { label: "关于我们", path: "/about" },
      { label: "隐私政策", path: "/privacy" },
      { label: "理性娱乐", path: "/responsible" },
    ],
  },
];
</script>

<template>
  <footer class="mt-auto border-t border-[#ddd4c7] bg-[#fffdf8]/95">
    <div class="mx-auto max-w-[1440px] px-6 sm:px-8 py-12">
      <div class="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-8">
        <div class="lg:col-span-2">
          <div class="mb-4 flex items-center gap-3">
            <LogoIcon :size="38" />
            <div class="leading-none">
              <div class="flex items-end gap-2">
                <span class="text-[22px] font-semibold tracking-[0.08em] text-[#233142]">弈彩</span>
                <span class="text-[18px] font-semibold tracking-wide text-[#b9863c]">YiCai</span>
              </div>
              <div class="mt-1.5 text-[10px] tracking-[0.32em] text-[#7d867f]">数据分析平台</div>
            </div>
          </div>
          <p class="max-w-sm text-sm leading-relaxed text-[#7d867f]">
            专注开奖数据整理、历史统计与趋势复盘，帮助你更清楚地理解号码分布。
          </p>
          <p class="mt-4 text-xs text-[#7d867f]/70">YiCai &copy; 2026</p>
          <div class="mt-5 rounded-md border border-[#ddd4c7] bg-[#fffaf2] p-4">
            <p class="text-sm font-semibold text-[#233142]">支持弈彩持续维护</p>
            <p class="mt-1 text-xs leading-5 text-[#7d867f]">
              用于数据整理、服务器成本与产品改进，不提供任何结果判断服务。
            </p>
            <div class="mt-3 flex flex-wrap gap-3 text-xs font-semibold">
              <a
                href="https://www.buymeacoffee.com/yicai"
                target="_blank"
                rel="noopener"
                class="text-[#8d6f47] underline-offset-2 hover:underline"
              >Buy Me a Coffee</a>
            </div>
          </div>
        </div>

        <div class="lg:col-span-2">
          <h4 class="mb-4 text-sm font-bold text-[#233142]">邮件订阅</h4>
          <p class="mb-4 max-w-sm text-sm leading-relaxed text-[#7d867f]">
            接收开奖数据更新、月度统计摘要与产品通知，仅供数据分析与娱乐参考。
          </p>
          <NewsletterSignup input-id="newsletter-email-footer" />
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
            彩票中奖号码为随机产生，历史数据不能保证未来结果。请理性娱乐，切勿沉迷。
          </p>
          <p class="text-xs text-[#7d867f]/55">
            访问本网站即表示您已年满18周岁，并同意我们的服务条款与隐私政策。
          </p>
          <p class="text-xs text-[#7d867f]/70">
            联系我们：
            <a
              href="mailto:lick201010@gmail.com"
              class="font-medium text-[#8d6f47] hover:text-[#6f5737] underline-offset-2 hover:underline"
            >lick201010@gmail.com</a>
          </p>
        </div>
      </div>
    </div>
  </footer>
</template>
