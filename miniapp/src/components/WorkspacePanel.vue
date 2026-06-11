<script setup lang="ts">
import { computed } from "vue";
import type {
  ProcessingStatus,
  ReconstructionParams,
  ReconstructionTaskMeta,
} from "../types/reconstruction";

const props = defineProps<{
  task: ReconstructionTaskMeta;
  fileName: string;
  params: ReconstructionParams;
  status: ProcessingStatus;
  progress: number;
  errorMessage: string;
}>();

const emit = defineEmits<{
  choose: [];
  "update:params": [params: ReconstructionParams];
  submit: [];
}>();

const upscaleOptions = [1, 2, 4];
const upscaleLabels = ["1x", "2x", "4x"];

const canRun = computed(() => Boolean(props.fileName) && props.status !== "processing");
const upscaleIndex = computed(() => {
  const index = upscaleOptions.indexOf(props.params.upscaleFactor);
  return index >= 0 ? index : 1;
});

const statusText = computed(() => {
  if (props.status === "processing") return "正在进行前向推理";
  if (props.status === "done") return "重建完成";
  if (props.status === "error") return "任务异常";
  if (props.status === "ready") return "输入就绪";
  return "等待输入";
});

function updateParams(next: Partial<ReconstructionParams>) {
  emit("update:params", {
    ...props.params,
    ...next,
  });
}

function onUpscaleChange(event: { detail: { value: number | string } }) {
  updateParams({
    upscaleFactor: upscaleOptions[Number(event.detail.value)] ?? 2,
  });
}
</script>

<template>
  <view class="workspace-stack">
    <view class="workspace-card">
      <view class="panel-head">
        <view>
          <text class="kicker">Workspace</text>
          <text class="panel-title">{{ task.title }}</text>
        </view>
        <text class="module-chip">{{ task.short }}</text>
      </view>

      <view class="upload-zone" @tap="emit('choose')">
        <view class="upload-icon">
          <text>+</text>
        </view>
        <text class="upload-title">{{ fileName || "选择或拍摄医学影像" }}</text>
        <text class="upload-subtitle">PNG / JPEG · DICOM 接口预留</text>
      </view>

      <view class="status-box">
        <view class="status-row">
          <text class="status-text">{{ statusText }}</text>
          <text class="progress-text">{{ progress }}%</text>
        </view>
        <view class="progress-track">
          <view class="progress-fill" :style="{ width: `${progress}%` }" />
        </view>
        <text v-if="status === 'error'" class="error-text">{{ errorMessage }}</text>
      </view>
    </view>

    <view class="workspace-card">
      <view class="panel-head">
        <view>
          <text class="kicker">Parameters</text>
          <text class="panel-title">算法参数</text>
        </view>
      </view>

      <view class="control-box">
        <view class="control-label-row">
          <text class="control-label">Iterations</text>
          <text class="control-value">{{ params.iterations }}</text>
        </view>
        <slider
          :value="params.iterations"
          min="1"
          max="64"
          step="1"
          block-size="20"
          activeColor="#2563eb"
          backgroundColor="#dbe4ef"
          @changing="updateParams({ iterations: $event.detail.value })"
          @change="updateParams({ iterations: $event.detail.value })"
        />
      </view>

      <view class="control-box">
        <view class="control-label-row">
          <text class="control-label">Denoise</text>
          <text class="control-value">{{ params.denoiseStrength.toFixed(2) }}</text>
        </view>
        <slider
          :value="Math.round(params.denoiseStrength * 100)"
          min="0"
          max="100"
          step="5"
          block-size="20"
          activeColor="#14b8a6"
          backgroundColor="#dbe4ef"
          @changing="updateParams({ denoiseStrength: $event.detail.value / 100 })"
          @change="updateParams({ denoiseStrength: $event.detail.value / 100 })"
        />
      </view>

      <view class="control-box">
        <view class="control-label-row">
          <text class="control-label">Upscale</text>
          <text class="control-value">{{ params.upscaleFactor }}x</text>
        </view>
        <picker
          mode="selector"
          :range="upscaleLabels"
          :value="upscaleIndex"
          @change="onUpscaleChange"
        >
          <view class="picker-surface">
            <text>{{ params.upscaleFactor }}x</text>
            <text class="picker-arrow">⌄</text>
          </view>
        </picker>
      </view>

      <button class="primary-action" :disabled="!canRun" @tap="emit('submit')">
        启动重建
      </button>
    </view>
  </view>
</template>

<style scoped>
.workspace-card {
  margin: 24rpx 32rpx 0;
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

.module-chip {
  min-width: 66rpx;
  padding: 10rpx 14rpx;
  border: 1rpx solid #dbe4ef;
  border-radius: 999rpx;
  background: #ffffff;
  color: #2563eb;
  font-size: 22rpx;
  font-weight: 800;
  text-align: center;
}

.upload-zone {
  display: flex;
  min-height: 310rpx;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  margin-top: 26rpx;
  border: 2rpx dashed #cbd5e1;
  border-radius: 18rpx;
  background: rgba(248, 250, 252, 0.78);
}

.upload-icon {
  display: grid;
  width: 82rpx;
  height: 82rpx;
  place-items: center;
  border-radius: 22rpx;
  background: #e0f2fe;
  color: #0ea5e9;
  font-size: 54rpx;
  font-weight: 300;
}

.upload-title {
  display: block;
  max-width: 560rpx;
  margin-top: 24rpx;
  overflow: hidden;
  color: #0f172a;
  font-size: 29rpx;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.upload-subtitle {
  display: block;
  margin-top: 12rpx;
  color: #64748b;
  font-size: 24rpx;
}

.status-box {
  margin-top: 24rpx;
  padding: 22rpx;
  border: 1rpx solid #e2e8f0;
  border-radius: 16rpx;
  background: rgba(255, 255, 255, 0.76);
}

.status-row,
.control-label-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.status-text,
.control-label {
  color: #0f172a;
  font-size: 26rpx;
  font-weight: 700;
}

.progress-text,
.control-value {
  color: #2563eb;
  font-size: 24rpx;
  font-weight: 800;
}

.progress-track {
  height: 12rpx;
  margin-top: 18rpx;
  overflow: hidden;
  border-radius: 999rpx;
  background: #e2e8f0;
}

.progress-fill {
  height: 100%;
  border-radius: 999rpx;
  background: linear-gradient(90deg, #14b8a6, #0ea5e9, #2563eb);
  transition: width 0.25s ease;
}

.error-text {
  display: block;
  margin-top: 16rpx;
  color: #e11d48;
  font-size: 24rpx;
  line-height: 1.4;
}

.control-box {
  margin-top: 22rpx;
  padding: 22rpx;
  border: 1rpx solid #e2e8f0;
  border-radius: 16rpx;
  background: rgba(255, 255, 255, 0.78);
}

.picker-surface {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 76rpx;
  margin-top: 18rpx;
  padding: 0 22rpx;
  border: 1rpx solid #dbe4ef;
  border-radius: 14rpx;
  background: #ffffff;
  color: #0f172a;
  font-size: 26rpx;
  font-weight: 700;
}

.picker-arrow {
  color: #64748b;
  font-size: 34rpx;
}

.primary-action {
  display: flex;
  width: 100%;
  height: 86rpx;
  align-items: center;
  justify-content: center;
  margin-top: 28rpx;
  border-radius: 16rpx;
  background: #2563eb;
  color: #ffffff;
  font-size: 28rpx;
  font-weight: 800;
  line-height: 86rpx;
  box-shadow: 0 16rpx 34rpx rgba(37, 99, 235, 0.18);
}

.primary-action[disabled] {
  background: #cbd5e1;
  color: #ffffff;
  box-shadow: none;
}
</style>
