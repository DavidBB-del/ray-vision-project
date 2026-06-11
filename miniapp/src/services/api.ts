import { API_BASE_URL } from "../config/api";
import type {
  ReconstructionParams,
  ReconstructionResponse,
  TaskKey,
} from "../types/reconstruction";

function parseUploadResponse(data: string): ReconstructionResponse {
  try {
    return JSON.parse(data) as ReconstructionResponse;
  } catch (error) {
    throw new Error(`无法解析后端返回结果：${String(error)}`);
  }
}

export function requestReconstruction(
  task: TaskKey,
  filePath: string,
  params: ReconstructionParams,
): Promise<ReconstructionResponse> {
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: `${API_BASE_URL}/api/reconstruct/${task}`,
      filePath,
      name: "file",
      formData: {
        iterations: String(params.iterations),
        denoise_strength: String(params.denoiseStrength),
        upscale_factor: String(params.upscaleFactor),
        response_format: "base64",
      },
      success: (response) => {
        const statusCode = response.statusCode ?? 0;
        if (statusCode < 200 || statusCode >= 300) {
          reject(new Error(response.data || `请求失败：${statusCode}`));
          return;
        }

        try {
          resolve(parseUploadResponse(response.data));
        } catch (error) {
          reject(error);
        }
      },
      fail: (error) => {
        reject(new Error(error.errMsg || "无法连接 Ray-Vision 后端服务"));
      },
    });
  });
}
