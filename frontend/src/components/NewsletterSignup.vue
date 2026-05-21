<script setup>
import { ref } from "vue";
import { api } from "../api.js";

defineProps({
  inputId: { type: String, default: "newsletter-email" },
});

const email = ref("");
const status = ref("idle");
const message = ref("");

async function submit() {
  const value = email.value.trim();
  if (!value) {
    status.value = "error";
    message.value = "请输入邮箱地址。";
    return;
  }

  status.value = "loading";
  message.value = "";

  try {
    const result = await api.newsletterSubscribe(value);
    status.value = "success";
    message.value = result.status === "already_subscribed"
      ? "这个邮箱已经订阅过开奖与数据更新。"
      : "订阅成功，后续会收到弈彩的数据更新邮件。";
    email.value = "";
  } catch {
    status.value = "error";
    message.value = "暂时无法提交，请稍后再试。";
  }
}
</script>

<template>
  <form class="space-y-3" @submit.prevent="submit">
    <div class="flex flex-col gap-2 sm:flex-row">
      <label class="sr-only" :for="inputId">邮箱地址</label>
      <input
        :id="inputId"
        v-model="email"
        type="email"
        autocomplete="email"
        class="min-h-11 flex-1 rounded-md border border-[#d8cbb9] bg-[#fffaf2] px-3 text-sm text-[#233142] outline-none transition focus:border-[#b9863c]"
        placeholder="输入邮箱，接收开奖与数据更新"
        :disabled="status === 'loading'"
      />
      <button
        type="submit"
        class="min-h-11 rounded-md bg-[#233142] px-5 text-sm font-semibold text-white transition hover:bg-[#31465b] disabled:cursor-wait disabled:opacity-70"
        :disabled="status === 'loading'"
      >
        {{ status === "loading" ? "提交中" : "订阅" }}
      </button>
    </div>
    <p class="text-xs leading-5 text-[#7d867f]/75">
      订阅即同意接收弈彩邮件，可随时退订。详情见
      <router-link to="/privacy" class="font-medium text-[#8d6f47] underline-offset-2 hover:underline">
        隐私政策
      </router-link>
      。
    </p>
    <p
      v-if="message"
      class="text-xs"
      :class="status === 'success' ? 'text-[#5f846d]' : 'text-[#b96d63]'"
      aria-live="polite"
    >
      {{ message }}
    </p>
  </form>
</template>
