<script setup lang="ts">
import { Download, FileText, ScanSearch } from "lucide-vue-next";
import ImageComparisonSlider from "./ImageComparisonSlider.vue";
import type { ProcessingStatus, ReconstructionTaskMeta } from "../types/reconstruction";

defineProps<{
  task: ReconstructionTaskMeta;
  beforeSrc: string | null;
  afterSrc: string | null;
  status: ProcessingStatus;
}>();

const emit = defineEmits<{
  download: [];
}>();
</script>

<template>
  <section class="glass-panel p-5">
    <div class="panel-heading">
      <div>
        <p class="section-kicker">Result Viewer</p>
        <h2 class="panel-title">结果对比</h2>
      </div>
      <div class="flex items-center gap-2">
        <button
          type="button"
          class="icon-action"
          :disabled="!afterSrc"
          title="导出高质图像"
          @click="emit('download')"
        >
          <Download :size="18" />
        </button>
        <button type="button" class="icon-action" disabled title="生成报告">
          <FileText :size="18" />
        </button>
      </div>
    </div>

    <ImageComparisonSlider
      v-if="beforeSrc && afterSrc"
      class="mt-5"
      :before-src="beforeSrc"
      :after-src="afterSrc"
      before-label="Input"
      after-label="Reconstructed"
    />

    <div v-else class="result-placeholder mt-5">
      <ScanSearch :size="42" stroke-width="1.5" />
      <span class="mt-4 text-base font-semibold text-clinical-ink">{{ task.title }}</span>
      <span class="mt-2 text-sm text-clinical-muted">
        {{ status === "processing" ? "推理中" : "等待重建结果" }}
      </span>
    </div>
  </section>
</template>
