<script setup lang="ts">
import type { ReconstructionTaskMeta, TaskKey } from "../types/reconstruction";

defineProps<{
  tasks: ReconstructionTaskMeta[];
  selectedTask: TaskKey;
}>();

const emit = defineEmits<{
  select: [task: TaskKey];
}>();
</script>

<template>
  <view class="dashboard">
    <view class="section-head">
      <view>
        <text class="kicker">Dashboard</text>
        <text class="title">首台控制台</text>
      </view>
      <view class="state-pill">
        <view class="state-dot" />
        <text>AI Ready</text>
      </view>
    </view>

    <view class="task-grid">
      <view
        v-for="task in tasks"
        :key="task.key"
        class="task-card"
        :class="[
          selectedTask === task.key ? 'task-card-active' : '',
          `accent-${task.accent}`,
        ]"
        @tap="emit('select', task.key)"
      >
        <view class="task-top">
          <view class="task-icon">
            <text>{{ task.short }}</text>
          </view>
          <text class="metric">{{ task.metric }}</text>
        </view>
        <text class="task-title">{{ task.title }}</text>
        <text class="task-subtitle">{{ task.subtitle }}</text>
        <text class="task-english">{{ task.english }}</text>
      </view>
    </view>
  </view>
</template>

<style scoped>
.dashboard {
  padding: 0 32rpx;
}

.section-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 24rpx;
  margin-bottom: 24rpx;
}

.kicker {
  display: block;
  color: #0ea5e9;
  font-size: 22rpx;
  font-weight: 700;
  letter-spacing: 0;
  text-transform: uppercase;
}

.title {
  display: block;
  margin-top: 8rpx;
  color: #0f172a;
  font-size: 40rpx;
  font-weight: 700;
}

.state-pill {
  display: flex;
  align-items: center;
  gap: 10rpx;
  padding: 10rpx 18rpx;
  border: 1rpx solid #dbe4ef;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.86);
  color: #64748b;
  font-size: 22rpx;
  font-weight: 700;
}

.state-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 999rpx;
  background: #14b8a6;
  box-shadow: 0 0 0 8rpx rgba(20, 184, 166, 0.12);
}

.task-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20rpx;
}

.task-card {
  min-height: 236rpx;
  padding: 24rpx;
  border: 1rpx solid #dbe4ef;
  border-radius: 18rpx;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 8rpx 28rpx rgba(15, 23, 42, 0.05);
}

.task-card-active {
  border-color: #0ea5e9;
  box-shadow: 0 18rpx 42rpx rgba(37, 99, 235, 0.12);
}

.task-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16rpx;
  margin-bottom: 28rpx;
}

.task-icon {
  display: grid;
  width: 66rpx;
  height: 66rpx;
  place-items: center;
  border-radius: 16rpx;
  background: #f1f5f9;
  color: #2563eb;
  font-size: 24rpx;
  font-weight: 800;
}

.metric {
  max-width: 130rpx;
  padding: 8rpx 12rpx;
  overflow: hidden;
  border: 1rpx solid #dbe4ef;
  border-radius: 999rpx;
  background: #ffffff;
  color: #64748b;
  font-size: 20rpx;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-title {
  display: block;
  color: #0f172a;
  font-size: 30rpx;
  font-weight: 700;
  line-height: 1.25;
}

.task-subtitle {
  display: block;
  margin-top: 8rpx;
  color: #64748b;
  font-size: 23rpx;
  line-height: 1.35;
}

.task-english {
  display: block;
  margin-top: 22rpx;
  color: #94a3b8;
  font-size: 20rpx;
  font-weight: 700;
  letter-spacing: 0;
  line-height: 1.25;
}

.accent-cyan .task-icon {
  color: #0ea5e9;
}

.accent-teal .task-icon {
  color: #14b8a6;
}

.accent-indigo .task-icon {
  color: #6366f1;
}
</style>
