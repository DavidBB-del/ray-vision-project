import type { ReconstructionParams, TaskKey } from "../types/reconstruction";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function requestReconstruction(
  task: TaskKey,
  file: File,
  params: ReconstructionParams,
): Promise<Blob> {
  const payload = new FormData();
  payload.append("file", file);
  payload.append("iterations", String(params.iterations));
  payload.append("denoise_strength", String(params.denoiseStrength));
  payload.append("upscale_factor", String(params.upscaleFactor));

  const response = await fetch(`${API_BASE_URL}/api/reconstruct/${task}`, {
    method: "POST",
    body: payload,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `Request failed with status ${response.status}`);
  }

  return response.blob();
}
