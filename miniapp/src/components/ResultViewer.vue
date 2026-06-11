<script setup lang="ts">
import ComparisonSlider from "./ComparisonSlider.vue";
import type { ProcessingStatus, ReconstructionTaskMeta } from "../types/reconstruction";

defineProps<{
  task: ReconstructionTaskMeta;
  beforeSrc: string;
  afterSrc: string;
  status: ProcessingStatus;
}>();

const emit = defineEmits<{
  download: [];
}>();
</script>

<template>
  <view class="result-card">
    <view class="panel-head">
      <view>
        <text class="kicker">Result Viewer</text>
        <text class="panel-title">结果对比</text>
      </view>
      <button class="icon-button" :disabled="!afterSrc" @tap="emit('download')">
        保存
      </button>
    </view>

    <ComparisonSlider
      v-if="beforeSrc && afterSrc"
      class="comparison"
      :before-src="beforeSrc"
      :after-src="afterSrc"
    />

    <view v-else class="result-placeholder">
      <view class="scan-mark">
        <text>{{ task.short }}</text>
      </view>
      <text class="placeholder-title">{{ task.title }}</text>
      <text class="placeholder-copy">
        {{ status === "processing" ? "推理中，请稍候" : "等待重建结果" }}
      </text>
    </view>
  </view>
</template>

<style scoped>
.result-card {
  margin: 24rpx 32rpx 44rpx;
  padding: 28rpx;
  border: 1rpx solid rgba(255, 255, 255, 0.88);
  border-radius: 18rpx;
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 18rpx 45rpx rgba(15, 23, 42, 0.08);
}

.panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20rpx;
}

.kicker {
  display: block;
  color: #0ea5e9;
  font-size: 22rpx;
  font-weight: 700;
  letter-spacing: 0;
}

.panel-title {
  display: block;
  margin-top: 6rpx;
  color: #0f172a;
  font-size: 34rpx;
  font-weight: 700;
}

.icon-button {
  min-width: 92rpx;
  height: 62rpx;
  padding: 0 20rpx;
  border: 1rpx solid #dbe4ef;
  border-radius: 14rpx;
  background: #ffffff;
  color: #2563eb;
  font-size: 24rpx;
  font-weight: 800;
  line-height: 62rpx;
}

.icon-button[disabled] {
  color: #94a3b8;
}

.comparison,
.result-placeholder {
  margin-top: 26rpx;
}

.result-placeholder {
  display: flex;
  height: 440rpx;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  border: 2rpx dashed #cbd5e1;
  border-radius: 18rpx;
  background: rgba(248, 250, 252, 0.78);
}

.scan-mark {
  display: grid;
  width: 92rpx;
  height: 92rpx;
  place-items: center;
  border-radius: 26rpx;
  background: #e0f2fe;
  color: #0ea5e9;
  font-size: 30rpx;
  font-weight: 900;
}

.placeholder-title {
  display: block;
  margin-top: 26rpx;
  color: #0f172a;
  font-size: 30rpx;
  font-weight: 800;
}

.placeholder-copy {
  display: block;
  margin-top: 12rpx;
  color: #64748b;
  font-size: 24rpx;
}
</style>
