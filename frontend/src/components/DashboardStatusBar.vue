<script setup>
import { useI18n } from "../i18n.js";

const { t } = useI18n();

defineProps({
  statusSourceText: { type: String, required: true },
  displayDate: { type: String, required: true },
  displayDrawTime: { type: String, required: true },
});
</script>

<template>
  <div class="dashboard-statusbar">
    <span>盾</span>
    <span>{{ t("仅供娱乐参考，不构成任何投注建议。") }}</span>
    <span class="mx-auto">{{ statusSourceText }}</span>
    <span>{{ t("最近开奖： {date} {time}", { date: displayDate, time: displayDrawTime }) }}</span>
    <span>⟳</span>
  </div>
</template>
