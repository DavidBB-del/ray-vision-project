<script setup lang="ts">
import { computed, onUnmounted, reactive, ref } from "vue";
import DashboardGrid from "../../components/DashboardGrid.vue";
import ResultViewer from "../../components/ResultViewer.vue";
import WorkspacePanel from "../../components/WorkspacePanel.vue";
import { requestReconstruction } from "../../services/api";
import { persistBase64Image, saveImageToAlbum } from "../../utils/imageFile";
import { TASKS } from "../../types/reconstruction";
import type { ProcessingStatus, ReconstructionParams, TaskKey } from "../../types/reconstruction";

const selectedTaskKey = ref<TaskKey>("low-dose-ct");
const selectedTask = computed(() => {
  return TASKS.find((task) => task.key === selectedTaskKey.value) ?? TASKS[0];
});

const params = reactive<ReconstructionParams>({
  iterations: 12,
  denoiseStrength: 0.45,
  upscaleFactor: 2,
});

const inputImagePath = ref("");
const outputImagePath = ref("");
const fileName = ref("");
const status = ref<ProcessingStatus>("idle");
const progress = ref(0);
const errorMessage = ref("");
let progressTimer: ReturnType<typeof setInterval> | undefined;

function clearProgressTimer() {
  if (progressTimer) {
    clearInterval(progressTimer);
    progressTimer = undefined;
  }
}

function selectTask(task: TaskKey) {
  selectedTaskKey.value = task;
  if (status.value === "done") {
    status.value = inputImagePath.value ? "ready" : "idle";
    progress.value = inputImagePath.value ? 8 : 0;
    outputImagePath.value = "";
  }
}

function updateParams(next: ReconstructionParams) {
  params.iterations = next.iterations;
  params.denoiseStrength = next.denoiseStrength;
  params.upscaleFactor = next.upscaleFactor;
}

function chooseImage() {
  uni.chooseImage({
    count: 1,
    sizeType: ["original"],
    sourceType: ["album", "camera"],
    success: (result) => {
      const path = result.tempFilePaths[0];
      if (!path) return;

      inputImagePath.value = path;
      outputImagePath.value = "";
      fileName.value = path.split("/").pop() || "medical-image";
      status.value = "ready";
      progress.value = 8;
      errorMessage.value = "";
    },
    fail: (error) => {
      if (!error.errMsg?.includes("cancel")) {
        status.value = "error";
        errorMessage.value = error.errMsg || "选择图片失败";
      }
    },
  });
}

async function runReconstruction() {
  if (!inputImagePath.value || status.value === "processing") return;

  clearProgressTimer();
  outputImagePath.value = "";
  status.value = "processing";
  progress.value = 14;
  errorMessage.value = "";

  progressTimer = setInterval(() => {
    progress.value = Math.min(92, progress.value + Math.ceil(Math.random() * 7));
  }, 420);

  try {
    const response = await requestReconstruction(selectedTaskKey.value, inputImagePath.value, params);
    outputImagePath.value = await persistBase64Image(response.image_base64, response.filename);
    progress.value = 100;
    status.value = "done";
  } catch (error) {
    status.value = "error";
    progress.value = 0;
    errorMessage.value = error instanceof Error ? error.message : "重建请求失败";
  } finally {
    clearProgressTimer();
  }
}

async function downloadResult() {
  if (!outputImagePath.value) return;
  try {
    await saveImageToAlbum(outputImagePath.value);
    uni.showToast({
      title: "已保存到相册",
      icon: "success",
    });
  } catch (error) {
    uni.showToast({
      title: error instanceof Error ? error.message : "保存失败",
      icon: "none",
    });
  }
}

onUnmounted(clearProgressTimer);
</script>

<template>
  <view class="page">
    <view class="nav-space" />
    <view class="app-header">
      <view class="brand-mark">
        <text>R</text>
      </view>
      <view class="brand-copy">
        <text class="brand-name">锐影智建</text>
        <text class="brand-subtitle">Ray-Vision Reconstruction</text>
      </view>
      <view class="api-chip">
        <text>FastAPI</text>
      </view>
    </view>

    <DashboardGrid
      :tasks="TASKS"
      :selected-task="selectedTaskKey"
      @select="selectTask"
    />

    <WorkspacePanel
      :task="selectedTask"
      :file-name="fileName"
      :params="params"
      :status="status"
      :progress="progress"
      :error-message="errorMessage"
      @choose="chooseImage"
      @update:params="updateParams"
      @submit="runReconstruction"
    />

    <ResultViewer
      :task="selectedTask"
      :before-src="inputImagePath"
      :after-src="outputImagePath"
      :status="status"
      @download="downloadResult"
    />
  </view>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8fafc 0%, #eef7fb 46%, #f8fafc 100%);
}

.nav-space {
  height: 68rpx;
}

.app-header {
  display: flex;
  align-items: center;
  gap: 18rpx;
  padding: 10rpx 32rpx 32rpx;
}

.brand-mark {
  display: grid;
  width: 76rpx;
  height: 76rpx;
  place-items: center;
  border-radius: 18rpx;
  background: #2563eb;
  color: #ffffff;
  font-size: 32rpx;
  font-weight: 900;
  box-shadow: 0 16rpx 34rpx rgba(37, 99, 235, 0.18);
}

.brand-copy {
  flex: 1;
  min-width: 0;
}

.brand-name {
  display: block;
  color: #0f172a;
  font-size: 30rpx;
  font-weight: 800;
}

.brand-subtitle {
  display: block;
  margin-top: 4rpx;
  color: #64748b;
  font-size: 22rpx;
  font-weight: 600;
}

.api-chip {
  padding: 10rpx 16rpx;
  border: 1rpx solid #dbe4ef;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.86);
  color: #64748b;
  font-size: 22rpx;
  font-weight: 800;
}
</style>
