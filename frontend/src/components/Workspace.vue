<script setup lang="ts">
import { computed, ref } from "vue";
import { Play, UploadCloud } from "lucide-vue-next";
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
  "file-selected": [file: File];
  "update:params": [params: ReconstructionParams];
  submit: [];
}>();

const inputRef = ref<HTMLInputElement | null>(null);
const isDragging = ref(false);

const canRun = computed(() => Boolean(props.fileName) && props.status !== "processing");

function pickFile() {
  inputRef.value?.click();
}

function emitFile(file?: File) {
  if (!file) return;
  emit("file-selected", file);
}

function onInputChange(event: Event) {
  const input = event.target as HTMLInputElement;
  emitFile(input.files?.[0]);
  input.value = "";
}

function onDrop(event: DragEvent) {
  isDragging.value = false;
  emitFile(event.dataTransfer?.files?.[0]);
}

function updateParam<K extends keyof ReconstructionParams>(
  key: K,
  value: ReconstructionParams[K],
) {
  emit("update:params", {
    ...props.params,
    [key]: value,
  });
}

const statusText = computed(() => {
  if (props.status === "processing") return "正在进行前向推理";
  if (props.status === "done") return "重建完成";
  if (props.status === "error") return "任务异常";
  if (props.status === "ready") return "输入就绪";
  return "等待输入";
});
</script>

<template>
  <section class="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
    <div class="glass-panel p-5">
      <div class="panel-heading">
        <div>
          <p class="section-kicker">Workspace</p>
          <h2 class="panel-title">{{ task.title }}</h2>
        </div>
        <span class="module-chip">{{ task.english }}</span>
      </div>

      <button
        type="button"
        class="upload-zone mt-5"
        :class="{ 'upload-zone-active': isDragging }"
        @click="pickFile"
        @dragenter.prevent="isDragging = true"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="onDrop"
      >
        <UploadCloud :size="36" stroke-width="1.7" />
        <span class="mt-4 text-base font-semibold text-clinical-ink">
          {{ fileName || "上传医学影像" }}
        </span>
        <span class="mt-2 text-sm text-clinical-muted">PNG / JPEG · DICOM Ready</span>
      </button>

      <input
        ref="inputRef"
        class="hidden"
        type="file"
        accept="image/png,image/jpeg"
        @change="onInputChange"
      />

      <div class="mt-5 rounded-lg border border-slate-200 bg-white/75 p-4">
        <div class="flex items-center justify-between text-sm">
          <span class="font-medium text-clinical-ink">{{ statusText }}</span>
          <span class="font-semibold text-clinical-blue">{{ progress }}%</span>
        </div>
        <div class="mt-3 h-2 overflow-hidden rounded-full bg-slate-100">
          <div class="progress-bar" :style="{ width: `${progress}%` }"></div>
        </div>
        <p v-if="status === 'error'" class="mt-3 text-sm text-rose-600">
          {{ errorMessage }}
        </p>
      </div>
    </div>

    <div class="glass-panel p-5">
      <div class="panel-heading">
        <div>
          <p class="section-kicker">Parameters</p>
          <h2 class="panel-title">算法参数</h2>
        </div>
      </div>

      <div class="mt-6 space-y-6">
        <label class="control-row">
          <span>
            <span class="control-label">Iterations</span>
            <span class="control-value">{{ params.iterations }}</span>
          </span>
          <input
            class="range-input"
            type="range"
            min="1"
            max="64"
            :value="params.iterations"
            @input="updateParam('iterations', Number(($event.target as HTMLInputElement).value))"
          />
        </label>

        <label class="control-row">
          <span>
            <span class="control-label">Denoise</span>
            <span class="control-value">{{ params.denoiseStrength.toFixed(2) }}</span>
          </span>
          <input
            class="range-input"
            type="range"
            min="0"
            max="1"
            step="0.05"
            :value="params.denoiseStrength"
            @input="updateParam('denoiseStrength', Number(($event.target as HTMLInputElement).value))"
          />
        </label>

        <label class="control-row">
          <span>
            <span class="control-label">Upscale</span>
            <span class="control-value">{{ params.upscaleFactor }}x</span>
          </span>
          <select
            class="select-input"
            :value="params.upscaleFactor"
            @change="updateParam('upscaleFactor', Number(($event.target as HTMLSelectElement).value))"
          >
            <option :value="1">1x</option>
            <option :value="2">2x</option>
            <option :value="4">4x</option>
          </select>
        </label>
      </div>

      <button
        type="button"
        class="primary-action mt-7"
        :disabled="!canRun"
        @click="emit('submit')"
      >
        <Play :size="18" fill="currentColor" stroke-width="2" />
        启动重建
      </button>
    </div>
  </section>
</template>
