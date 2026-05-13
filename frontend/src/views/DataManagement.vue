<script setup>
import { ref, onMounted, watch, computed } from "vue";
import { api, lotteryType } from "../api.js";
import DrawTable from "../components/DrawTable.vue";

const draws = ref([]);
const total = ref(0);
const page = ref(1);
const loading = ref(false);
const scrapeStatus = ref("");
const scrapeJobId = ref(null);
const scrapeLogs = ref([]);

const perPage = 50;

async function loadDraws() {
  loading.value = true;
  try {
    const data = await api.draws({ page: page.value, per_page: perPage });
    draws.value = data.draws;
    total.value = data.total;
  } finally {
    loading.value = false;
  }
}

async function triggerScrape() {
  scrapeStatus.value = "正在爬取数据...";
  try {
    const res = await api.scrapeTrigger("hkjc");
    scrapeJobId.value = res.job_id;
    pollScrapeStatus(res.job_id);
  } catch (e) {
    scrapeStatus.value = "爬取失败: " + e.message;
  }
}

async function pollScrapeStatus(jobId) {
  const res = await api.scrapeStatus(jobId);
  scrapeStatus.value = `状态: ${res.status} | 获取: ${res.draws_fetched} | 新增: ${res.draws_new}`;
  if (res.status === "running") {
    setTimeout(() => pollScrapeStatus(jobId), 2000);
  } else {
    await loadDraws();
    await loadLogs();
    scrapeJobId.value = null;
  }
}

async function loadLogs() {
  try {
    scrapeLogs.value = await api.scrapeLogs();
  } catch (e) {
    // ignore
  }
}

function changePage(p) {
  page.value = p;
  loadDraws();
}

const totalPages = computed(() => Math.ceil(total.value / perPage));

onMounted(() => {
  loadDraws();
  loadLogs();
});

watch(lotteryType, () => {
  page.value = 1;
  loadDraws();
});
</script>

<template>
  <div class="space-y-8 animate-fade-in-up">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 tracking-tight">数据管理</h1>
        <p class="text-base text-gray-400 mt-1">查看历史开奖记录与数据更新</p>
      </div>
      <div class="flex items-center gap-4">
        <span class="text-base text-gray-500 font-medium">共 {{ total.toLocaleString() }} 条记录</span>
        <button
          @click="triggerScrape"
          :disabled="!!scrapeJobId"
          class="btn-premium inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-red-600 to-red-700 text-white text-base font-bold rounded-xl hover:shadow-lg hover:shadow-red-500/25 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg v-if="!scrapeJobId" class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>
          <svg v-else class="w-5 h-5 animate-spin" fill="currentColor" viewBox="0 0 24 24"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/></svg>
          {{ scrapeJobId ? "爬取中..." : "更新数据" }}
        </button>
      </div>
    </div>

    <div v-if="scrapeStatus" class="flex items-center gap-3 text-base text-blue-700 bg-blue-50/80 border border-blue-100 px-5 py-3 rounded-xl backdrop-blur-sm">
      <svg class="w-5 h-5 text-blue-500 animate-spin" fill="currentColor" viewBox="0 0 24 24" v-if="scrapeJobId"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/></svg>
      <svg v-else class="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
      {{ scrapeStatus }}
    </div>

    <DrawTable :draws="draws" :loading="loading" />

    <div v-if="total > perPage" class="flex items-center justify-center gap-3">
      <button
        @click="changePage(page - 1)"
        :disabled="page <= 1"
        class="inline-flex items-center gap-1 px-5 py-2.5 text-base font-medium border border-gray-200 rounded-xl disabled:opacity-30 hover:bg-white hover:shadow-sm transition-all bg-white"
      >
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/></svg>
        上一页
      </button>
      <span class="text-base text-gray-500 font-medium px-4">
        第 {{ page }} / {{ totalPages }} 页
      </span>
      <button
        @click="changePage(page + 1)"
        :disabled="page >= totalPages"
        class="inline-flex items-center gap-1 px-5 py-2.5 text-base font-medium border border-gray-200 rounded-xl disabled:opacity-30 hover:bg-white hover:shadow-sm transition-all bg-white"
      >
        下一页
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/></svg>
      </button>
    </div>

    <!-- Scrape Logs -->
    <div class="bg-white rounded-2xl border border-gray-200/80 p-6 shadow-sm card-lift">
      <div class="flex items-center gap-3 mb-5">
        <div class="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center">
          <svg class="w-5 h-5 text-gray-500" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
        </div>
        <h3 class="text-base font-bold text-gray-900">爬取日志</h3>
      </div>
      <div v-if="scrapeLogs.length === 0" class="text-base text-gray-400 py-4">暂无日志</div>
      <div v-else class="overflow-x-auto">
        <table class="w-full table-premium text-[15px]">
          <thead>
            <tr class="text-left text-gray-400 border-b border-gray-200">
              <th class="py-3 pr-4">时间</th>
              <th class="py-3 pr-4">来源</th>
              <th class="py-3 pr-4">状态</th>
              <th class="py-3 pr-4 text-right">获取</th>
              <th class="py-3 pr-4 text-right">新增</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in scrapeLogs" :key="log.id" class="text-gray-600 border-b border-gray-100">
              <td class="py-3 pr-4 font-medium">{{ log.started_at?.slice(0, 19) }}</td>
              <td class="py-3 pr-4">{{ log.source }}</td>
              <td class="py-3 pr-4">
                <span
                  class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold"
                  :class="log.status === 'success' ? 'bg-green-100 text-green-700' : log.status === 'failed' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'"
                >
                  <span class="w-1.5 h-1.5 rounded-full" :class="log.status === 'success' ? 'bg-green-500' : log.status === 'failed' ? 'bg-red-500' : 'bg-blue-500'"></span>
                  {{ log.status }}
                </span>
              </td>
              <td class="py-3 pr-4 text-right font-semibold">{{ log.draws_fetched }}</td>
              <td class="py-3 pr-4 text-right font-semibold">{{ log.draws_new }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
