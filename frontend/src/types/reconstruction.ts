export type TaskKey =
  | "low-dose-ct"
  | "cbct"
  | "mr-to-ct"
  | "super-resolution";

export type ProcessingStatus = "idle" | "ready" | "processing" | "done" | "error";

export interface ReconstructionTaskMeta {
  key: TaskKey;
  title: string;
  subtitle: string;
  english: string;
  metric: string;
  accent: "blue" | "cyan" | "teal" | "indigo";
}

export interface ReconstructionParams {
  iterations: number;
  denoiseStrength: number;
  upscaleFactor: number;
}

export const TASKS: ReconstructionTaskMeta[] = [
  {
    key: "low-dose-ct",
    title: "CT 图像重建",
    subtitle: "低剂量 CT 至常规剂量 CT",
    english: "Low-dose CT to Normal CT",
    metric: "Noise-aware",
    accent: "blue",
  },
  {
    key: "cbct",
    title: "CBCT 图像重建",
    subtitle: "锥形束 CT 伪影校正",
    english: "Cone-Beam CT Reconstruction",
    metric: "Artifact Control",
    accent: "cyan",
  },
  {
    key: "mr-to-ct",
    title: "MR 合成 CT",
    subtitle: "MR 到 CT 的跨模态合成",
    english: "MR to CT Synthesis",
    metric: "Cross-modal",
    accent: "teal",
  },
  {
    key: "super-resolution",
    title: "医学图像超分",
    subtitle: "低分辨率影像细节增强",
    english: "Super-Resolution",
    metric: "2x / 4x",
    accent: "indigo",
  },
];
