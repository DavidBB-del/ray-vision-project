<script setup lang="ts">
import { computed, onUnmounted, reactive, ref } from "vue";
import { BrainCircuit } from "lucide-vue-next";
import Dashboard from "./components/Dashboard.vue";
import ResultViewer from "./components/ResultViewer.vue";
import Workspace from "./components/Workspace.vue";
import { requestReconstruction } from "./services/api";
import { TASKS } from "./types/reconstruction";
import type { ProcessingStatus, ReconstructionParams, TaskKey } from "./types/reconstruction";

const selectedTaskKey = ref<TaskKey>("low-dose-ct");
const selectedTask = computed(() => TASKS.find((task) => task.key === selectedTaskKey.value) ?? TASKS[0]);

const params = reactive<ReconstructionParams>({
  iterations: 12,
  denoiseStrength: 0.45,
  upscaleFactor: 2,
});

const inputFile = ref<File | null>(null);
const inputPreviewUrl = ref<string | null>(null);
const outputPreviewUrl = ref<string | null>(null);
const status = ref<ProcessingStatus>("idle");
const progress = ref(0);
const errorMessage = ref("");
let progressTimer: number | undefined;

const fileName = computed(() => inputFile.value?.name ?? "");

function clearTimer() {
  if (progressTimer) {
    window.clearInterval(progressTimer);
    progressTimer = undefined;
  }
}

function revokeUrl(url: string | null) {
  if (url) URL.revokeObjectURL(url);
}

function selectTask(task: TaskKey) {
  selectedTaskKey.value = task;
  if (status.value === "done") {
    status.value = inputFile.value ? "ready" : "idle";
    progress.value = inputFile.value ? 8 : 0;
    revokeUrl(outputPreviewUrl.value);
    outputPreviewUrl.value = null;
  }
}

function handleFileSelected(file: File) {
  inputFile.value = file;
  revokeUrl(inputPreviewUrl.value);
  revokeUrl(outputPreviewUrl.value);
  inputPreviewUrl.value = URL.createObjectURL(file);
  outputPreviewUrl.value = null;
  errorMessage.value = "";
  status.value = "ready";
  progress.value = 8;
}

function updateParams(nextParams: ReconstructionParams) {
  params.iterations = nextParams.iterations;
  params.denoiseStrength = nextParams.denoiseStrength;
  params.upscaleFactor = nextParams.upscaleFactor;
}

async function runReconstruction() {
  if (!inputFile.value) return;

  clearTimer();
  status.value = "processing";
  errorMessage.value = "";
  progress.value = 14;

  progressTimer = window.setInterval(() => {
    progress.value = Math.min(92, progress.value + Math.ceil(Math.random() * 7));
  }, 420);

  try {
    const outputBlob = await requestReconstruction(selectedTaskKey.value, inputFile.value, params);
    revokeUrl(outputPreviewUrl.value);
    outputPreviewUrl.value = URL.createObjectURL(outputBlob);
    progress.value = 100;
    status.value = "done";
  } catch (error) {
    status.value = "error";
    progress.value = 0;
    errorMessage.value = error instanceof Error ? error.message : "Reconstruction failed.";
  } finally {
    clearTimer();
  }
}

function downloadResult() {
  if (!outputPreviewUrl.value) return;
  const link = document.createElement("a");
  link.href = outputPreviewUrl.value;
  link.download = `ray-vision-${selectedTaskKey.value}.png`;
  link.click();
}

onUnmounted(() => {
  clearTimer();
  revokeUrl(inputPreviewUrl.value);
  revokeUrl(outputPreviewUrl.value);
});
</script>

<template>
  <main class="app-shell">
    <header class="mx-auto flex w-full max-w-7xl items-center justify-between px-5 py-5 sm:px-8">
      <div class="flex items-center gap-3">
        <div class="brand-mark">
          <BrainCircuit :size="22" stroke-width="2.2" />
        </div>
        <div>
          <p class="text-sm font-semibold text-clinical-ink">Ray-Vision</p>
          <p class="text-xs text-clinical-muted">Medical Image Reconstruction</p>
        </div>
      </div>
      <span class="rounded-full border border-slate-200 bg-white/80 px-3 py-1 text-xs font-medium text-clinical-muted">
        FastAPI · Vue 3 · AI Backend Ready
      </span>
    </header>

    <div class="mx-auto grid w-full max-w-7xl gap-6 px-5 pb-10 sm:px-8">
      <Dashboard
        :tasks="TASKS"
        :selected-task="selectedTaskKey"
        @select="selectTask"
      />

      <Workspace
        :task="selectedTask"
        :file-name="fileName"
        :params="params"
        :status="status"
        :progress="progress"
        :error-message="errorMessage"
        @file-selected="handleFileSelected"
        @update:params="updateParams"
        @submit="runReconstruction"
      />

      <ResultViewer
        :task="selectedTask"
        :before-src="inputPreviewUrl"
        :after-src="outputPreviewUrl"
        :status="status"
        @download="downloadResult"
      />
    </div>
  </main>
</template>
