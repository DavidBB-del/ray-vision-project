<script setup lang="ts">
import { computed, ref } from "vue";
import { ChevronsLeftRight } from "lucide-vue-next";

defineProps<{
  beforeSrc: string;
  afterSrc: string;
  beforeLabel: string;
  afterLabel: string;
}>();

const frameRef = ref<HTMLElement | null>(null);
const position = ref(50);
const dragging = ref(false);

const clipStyle = computed(() => ({
  clipPath: `inset(0 ${100 - position.value}% 0 0)`,
}));

function setPositionFromPointer(clientX: number) {
  const frame = frameRef.value;
  if (!frame) return;
  const rect = frame.getBoundingClientRect();
  const next = ((clientX - rect.left) / rect.width) * 100;
  position.value = Math.max(0, Math.min(100, Math.round(next)));
}

function onPointerDown(event: PointerEvent) {
  dragging.value = true;
  (event.currentTarget as HTMLElement).setPointerCapture(event.pointerId);
  setPositionFromPointer(event.clientX);
}

function onPointerMove(event: PointerEvent) {
  if (!dragging.value) return;
  setPositionFromPointer(event.clientX);
}

function onPointerUp(event: PointerEvent) {
  dragging.value = false;
  (event.currentTarget as HTMLElement).releasePointerCapture(event.pointerId);
}
</script>

<template>
  <div class="comparison-wrap">
    <div
      ref="frameRef"
      class="comparison-frame"
      @pointerdown="onPointerDown"
      @pointermove="onPointerMove"
      @pointerup="onPointerUp"
      @pointercancel="onPointerUp"
    >
      <img class="comparison-image" :src="beforeSrc" :alt="beforeLabel" draggable="false" />
      <div class="comparison-after" :style="clipStyle">
        <img class="comparison-image" :src="afterSrc" :alt="afterLabel" draggable="false" />
      </div>

      <div class="comparison-label left-4 top-4">{{ beforeLabel }}</div>
      <div class="comparison-label right-4 top-4">{{ afterLabel }}</div>

      <div class="comparison-divider" :style="{ left: `${position}%` }">
        <span class="comparison-handle">
          <ChevronsLeftRight :size="22" stroke-width="2.4" />
        </span>
      </div>
    </div>

    <input
      v-model.number="position"
      class="sr-only"
      type="range"
      min="0"
      max="100"
      aria-label="Before after comparison position"
    />
  </div>
</template>
