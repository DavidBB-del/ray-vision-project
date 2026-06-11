<script setup lang="ts">
import { Activity, Atom, ScanLine, Sparkles } from "lucide-vue-next";
import type { Component } from "vue";
import type { ReconstructionTaskMeta, TaskKey } from "../types/reconstruction";

defineProps<{
  tasks: ReconstructionTaskMeta[];
  selectedTask: TaskKey;
}>();

const emit = defineEmits<{
  select: [task: TaskKey];
}>();

const iconMap: Record<TaskKey, Component> = {
  "low-dose-ct": Activity,
  cbct: ScanLine,
  "mr-to-ct": Atom,
  "super-resolution": Sparkles,
};
</script>

<template>
  <section class="space-y-5">
    <div class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p class="section-kicker">Dashboard</p>
        <h1 class="text-2xl font-semibold text-clinical-ink sm:text-3xl">
          锐影智建 Ray-Vision
        </h1>
      </div>
      <div class="status-pill">
        <span class="status-dot"></span>
        AI Reconstruction Console
      </div>
    </div>

    <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <button
        v-for="task in tasks"
        :key="task.key"
        type="button"
        class="task-card"
        :class="[
          selectedTask === task.key ? 'task-card-active' : '',
          `task-accent-${task.accent}`,
        ]"
        @click="emit('select', task.key)"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="task-icon">
            <component :is="iconMap[task.key]" :size="22" stroke-width="2" />
          </div>
          <span class="task-metric">{{ task.metric }}</span>
        </div>
        <div class="mt-5 text-left">
          <h2 class="text-lg font-semibold text-clinical-ink">{{ task.title }}</h2>
          <p class="mt-1 text-sm text-clinical-muted">{{ task.subtitle }}</p>
          <p class="mt-4 text-xs font-medium uppercase tracking-[0.16em] text-slate-400">
            {{ task.english }}
          </p>
        </div>
      </button>
    </div>
  </section>
</template>
