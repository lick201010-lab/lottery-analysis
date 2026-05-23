<script setup>
import { onMounted, onUnmounted, ref } from "vue";
import NavBar from "./components/NavBar.vue";
import AppFooter from "./components/AppFooter.vue";
import CookieConsent from "./components/CookieConsent.vue";

const canvasRef = ref(null);
let ctx = null;
let animId = null;
const particles = [];

class Particle {
  constructor(x, y, cursor) {
    this.x = x;
    this.y = y;
    this.vx = (Math.random() - 0.5) * (cursor ? 2.4 : 0.7);
    this.vy = -(0.6 + Math.random() * (cursor ? 2.2 : 1.0));
    this.life = 1;
    this.decay = cursor ? 0.013 + Math.random() * 0.009 : 0.006 + Math.random() * 0.004;
    this.size = cursor ? 3 + Math.random() * 5 : 1.5 + Math.random() * 3;
    const r = 195 + Math.random() * 55 | 0;
    const g = 155 + Math.random() * 45 | 0;
    const b = 45 + Math.random() * 35 | 0;
    this.colorBase = `${r},${g},${b}`;
  }
  update() {
    this.x += this.vx;
    this.y += this.vy;
    this.vy -= 0.022;
    this.vx *= 0.98;
    this.life -= this.decay;
  }
  draw(c) {
    if (this.life <= 0) return;
    c.beginPath();
    c.arc(this.x, this.y, Math.max(0, this.size * this.life), 0, Math.PI * 2);
    c.fillStyle = `rgba(${this.colorBase},${this.life.toFixed(2)})`;
    c.fill();
  }
}

function resizeCanvas() {
  if (!canvasRef.value) return;
  canvasRef.value.width  = window.innerWidth;
  canvasRef.value.height = window.innerHeight;
}

function animate() {
  if (!ctx || !canvasRef.value) return;
  ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);

  // Ambient particles
  if (Math.random() < 0.12 && particles.length < 55) {
    particles.push(new Particle(
      Math.random() * window.innerWidth,
      window.innerHeight * (0.3 + Math.random() * 0.7),
      false
    ));
  }

  for (let i = particles.length - 1; i >= 0; i--) {
    particles[i].update();
    particles[i].draw(ctx);
    if (particles[i].life <= 0) particles.splice(i, 1);
  }

  animId = requestAnimationFrame(animate);
}

function onMouseMove(e) {
  if (particles.length < 120 && Math.random() < 0.4) {
    particles.push(new Particle(e.clientX, e.clientY, true));
  }
}

onMounted(() => {
  if (!canvasRef.value) return;
  ctx = canvasRef.value.getContext("2d");
  resizeCanvas();
  window.addEventListener("resize", resizeCanvas);
  window.addEventListener("mousemove", onMouseMove);
  animate();
});

onUnmounted(() => {
  window.removeEventListener("resize", resizeCanvas);
  window.removeEventListener("mousemove", onMouseMove);
  if (animId) cancelAnimationFrame(animId);
});
</script>

<template>
  <div class="min-h-screen flex flex-col diamond-bg">
    <!-- Particle canvas -->
    <canvas ref="canvasRef" class="v62-particle-canvas" aria-hidden="true"></canvas>
    <!-- Seal watermark -->
    <div class="v62-seal-watermark" aria-hidden="true">彩</div>

    <NavBar />

    <main class="v62-main-content flex-1 w-full max-w-[1840px] mx-auto px-6 sm:px-10 pb-8" style="position:relative;z-index:2;">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <AppFooter />
    <CookieConsent />
  </div>
</template>

<style>
.page-enter-active,
.page-leave-active {
  transition: opacity 0.35s cubic-bezier(0.4, 0, 0.2, 1),
              transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}
.page-enter-from {
  opacity: 0;
  transform: translateY(16px) scale(0.985);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.99);
}
</style>
