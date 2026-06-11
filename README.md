# 锐影智建 (Ray-Vision)

面向医学影像研究人员和医生的医学图像智能重建应用。当前项目包含：

- `miniapp/`：UniApp + Vue 3 微信小程序前端
- `frontend/`：Vue 3 + TypeScript + Tailwind CSS Web 前端
- `backend/`：FastAPI Python 后端，便于后续集成 PyTorch `.pth` 模型

## 项目结构

```text
ray-vision/
  backend/
    app/
      api/routes/reconstruction.py      # 重建 API 路由
      core/config.py                     # 基础配置
      services/reconstruction_service.py # PyTorch 模型加载与 forward 接入点
      services/mock_image_ops.py         # 当前阶段 Mock 图像处理
      main.py                            # FastAPI 入口
    requirements.txt

  miniapp/
    src/
      components/
        DashboardGrid.vue
        WorkspacePanel.vue
        ComparisonSlider.vue
        ResultViewer.vue
      pages/index/index.vue              # 微信小程序首页
      services/api.ts                    # 小程序上传与推理接口
      config/api.ts                      # 后端地址配置
      manifest.json
      pages.json
    package.json

  frontend/
    src/
      components/
        Dashboard.vue
        Workspace.vue
        ResultViewer.vue
        ImageComparisonSlider.vue
      services/api.ts
      types/reconstruction.ts
      App.vue
      main.ts
      style.css
    package.json
```

## 启动后端

```powershell
cd E:\Games\ray-vision\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 文档：

```text
http://localhost:8000/docs
```

当前 Mock API：

- `GET /api/health`
- `GET /api/reconstruct/tasks`
- `POST /api/reconstruct/low-dose-ct`
- `POST /api/reconstruct/cbct`
- `POST /api/reconstruct/mr-to-ct`
- `POST /api/reconstruct/super-resolution`

## 打开微信小程序

1. 先启动 FastAPI 后端，保持 `http://127.0.0.1:8000` 可访问。

2. 编译小程序：

```powershell
cd E:\Games\ray-vision\miniapp
npm install
npm run dev:mp-weixin
```

3. 打开微信开发者工具，导入目录：

```text
E:\Games\ray-vision\miniapp\dist\dev\mp-weixin
```

没有微信小程序 AppID 时，可以在微信开发者工具里使用测试号或游客模式。

## 小程序联调后端地址

小程序端后端地址在：

```text
miniapp/src/config/api.ts
```

默认值：

```ts
export const API_BASE_URL = "http://127.0.0.1:8000";
```

注意：

- 微信开发者工具模拟器通常可以访问 `127.0.0.1`。
- 真机预览时，`127.0.0.1` 指向手机自己，需要改成电脑局域网 IP，例如 `http://192.168.1.8:8000`。
- 开发阶段可在微信开发者工具中勾选“不校验合法域名、web-view 域名、TLS 版本以及 HTTPS 证书”。
- 后端接口已支持小程序所需的 `response_format=base64` 返回格式。

## 打开 Web 版

```powershell
cd E:\Games\ray-vision\frontend
npm install
npm run dev
```

浏览器访问：

```text
http://localhost:5173
```

## 接入你的 `.pth` 模型

后续主要修改：

- `backend/app/services/reconstruction_service.py`
- `load_model_for_task()`：加载并缓存对应任务的 `.pth` 权重
- `run_model_forward()`：写入预处理、`torch.no_grad()` 前向推理、后处理逻辑

当前 API 入参已经预留：

- `file`：上传图像
- `iterations`：迭代次数
- `denoise_strength`：去噪强度
- `upscale_factor`：超分倍率
- `response_format`：返回格式，Web 默认图片流，小程序使用 `base64`

替换 Mock 逻辑后，小程序和 Web 前端都可以继续沿用同一套 API。
