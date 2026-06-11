<script setup lang="ts">
import { computed, getCurrentInstance, nextTick, onMounted, ref, watch } from "vue";

const props = defineProps<{
  beforeSrc: string;
  afterSrc: string;
}>();

const instance = getCurrentInstance();
const frameWidth = ref(0);
const handleX = ref(0);
const position = ref(50);
const handleSize = 48;

const afterLayerStyle = computed(() => `width: ${position.value}%;`);
const fixedImageStyle = computed(() => {
  return frameWidth.value > 0 ? `width: ${frameWidth.value}px;` : "width: 100%;";
});
const dividerStyle = computed(() => `left: ${position.value}%;`);

function syncHandleFromPosition() {
  if (!frameWidth.value) return;
  const movableWidth = Math.max(1, frameWidth.value - handleSize);
  handleX.value = Math.max(0, (movableWidth * position.value) / 100);
}

function measureFrame() {
  nextTick(() => {
    uni
      .createSelectorQuery()
      .in(instance?.proxy)
      .select(".comparison-frame")
      .boundingClientRect((rect) => {
        const box = Array.isArray(rect) ? rect[0] : rect;
        if (!box?.width) return;
        frameWidth.value = box.width;
        syncHandleFromPosition();
      })
      .exec();
  });
}

function onHandleMove(event: { detail: { x: number; source?: string } }) {
  if (!frameWidth.value) return;
  const movableWidth = Math.max(1, frameWidth.value - handleSize);
  const next = (event.detail.x / movableWidth) * 100;
  position.value = Math.max(0, Math.min(100, Math.round(next)));
}

onMounted(measureFrame);
watch(() => [props.beforeSrc, props.afterSrc], measureFrame);
</script>

<template>
  <movable-area class="comparison-frame">
    <image class="comparison-image" :src="beforeSrc" mode="aspectFit" />
    <view class="after-layer" :style="afterLayerStyle">
      <image class="comparison-image after-image" :src="afterSrc" mode="aspectFit" :style="fixedImageStyle" />
    </view>

    <text class="label label-before">Input</text>
    <text class="label label-after">Reconstructed</text>
    <view class="divider" :style="dividerStyle" />

    <movable-view
      class="handle"
      direction="horizontal"
      :x="handleX"
      :damping="70"
      @change="onHandleMove"
    >
      <view class="handle-dot">
        <text>↔</text>
      </view>
    </movable-view>
  </movable-area>
</template>

<style scoped>
.comparison-frame {
  position: relative;
  width: 100%;
  height: 440rpx;
  overflow: hidden;
  border: 1rpx solid #dbe4ef;
  border-radius: 18rpx;
  background: #020617;
  box-shadow: 0 18rpx 45rpx rgba(15, 23, 42, 0.1);
}

.comparison-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.after-layer {
  position: absolute;
  inset: 0 auto 0 0;
  overflow: hidden;
  height: 100%;
}

.after-image {
  left: 0;
}

.label {
  position: absolute;
  top: 22rpx;
  z-index: 4;
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
  background: rgba(15, 23, 42, 0.72);
  color: #ffffff;
  font-size: 22rpx;
  font-weight: 800;
}

.label-before {
  left: 22rpx;
}

.label-after {
  right: 22rpx;
}

.divider {
  position: absolute;
  top: 0;
  z-index: 3;
  width: 2rpx;
  height: 100%;
  background: #ffffff;
  box-shadow: 0 0 0 1rpx rgba(15, 23, 42, 0.2);
}

.handle {
  z-index: 5;
  width: 48px;
  height: 440rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.handle-dot {
  display: flex;
  width: 88rpx;
  height: 88rpx;
  align-items: center;
  justify-content: center;
  border: 2rpx solid rgba(255, 255, 255, 0.9);
  border-radius: 999rpx;
  background: #ffffff;
  color: #2563eb;
  font-size: 30rpx;
  font-weight: 900;
  box-shadow: 0 12rpx 30rpx rgba(15, 23, 42, 0.18);
}
</style>
