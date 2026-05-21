<script setup>
import { useSEO } from "../composables/useSEO.js";

useSEO({
  title: "理性娱乐指南",
  description: "彩票是娱乐不是投资。识别问题性赌博的信号，了解负责任的娱乐原则与求助渠道。",
});
</script>

<template>
  <div class="ref-card p-8">
    <h1 class="text-2xl font-semibold text-[#1c3342] mb-4">理性投注</h1>
    <div class="prose prose-sm text-[#5f6868] space-y-4">
      <div class="bg-[#fef9f0] border border-[#e8dcc8] rounded-lg p-4 mb-6">
        <p class="font-medium text-[#c5443f]">⚠️ 重要提示</p>
        <p class="mt-2">彩票是一种娱乐方式，而非赚钱手段。请务必理性投注，切勿沉迷。</p>
      </div>
      
      <h2 class="text-lg font-medium">健康投注原则</h2>
      <ul class="list-disc pl-6 space-y-2">
        <li><strong>设定预算：</strong>只为娱乐目的而投注，绝不动用必要的生活费用。</li>
        <li><strong>控制时间：</strong>不要让彩票影响您的正常工作和生活。</li>
        <li><strong>接受输赢：</strong>把投注视为娱乐消费，中奖是惊喜，不中亦属正常。</li>
        <li><strong>拒绝借贷：</strong>绝不借钱投注，不影响正常家庭财务。</li>
        <li><strong>及时求助：</strong>如发现自己有投注问题，请及时寻求专业帮助。</li>
      </ul>
      
      <h2 class="text-lg font-medium mt-6">常见问题</h2>
      <p><strong>Q: 彩票真的可以预测吗？</strong><br/>A: 彩票开奖是完全随机的独立事件，历史数据无法预测未来结果。</p>
      <p><strong>Q: 有什么方法可以提高中奖率？</strong><br/>A: 理论上各号码的中奖概率相同，不存在提高中奖率的方法。</p>
      
      <div class="mt-6 p-4 bg-[#f5f5f5] rounded text-xs text-[#7d867f]">
        <p>如需帮助，请联系当地心理健康服务热线或相关戒赌机构。</p>
      </div>
    </div>
  </div>
</template>