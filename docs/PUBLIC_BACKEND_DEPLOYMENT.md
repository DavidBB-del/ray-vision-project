# Public Backend Deployment

The Netlify site is only the frontend. Real `.npy` RED-CNN reconstruction needs this FastAPI backend deployed as a public HTTPS service.

## What is ready

Backend deployment files:

```text
backend/Dockerfile
backend/.dockerignore
render.yaml
```

The RED-CNN weight is included:

```text
backend/weights/REDCNN_100000iter.ckpt
```

## Recommended first deployment: Render

1. Push `E:\Games\ray-vision` to a GitHub repository.

2. Open Render and create a new Blueprint from that repository.

3. Render will read:

```text
render.yaml
```

4. Wait for the Docker build to finish.

5. Open the backend health URL:

```text
https://YOUR-RENDER-SERVICE.onrender.com/api/health
```

Expected response:

```json
{"status":"ok","service":"Ray-Vision API"}
```

6. Copy the backend base URL, for example:

```text
https://ray-vision-api.onrender.com
```

7. Paste it into the Netlify page field:

```text
RED-CNN 后端地址
```

Do not paste the Netlify frontend address into this field.

## Test RED-CNN API

Once deployed, open:

```text
https://YOUR-RENDER-SERVICE.onrender.com/docs
```

Use:

```text
POST /api/reconstruct/low-dose-ct
```

Upload a `.npy` file. The server will:

```text
np.load -> RED-CNN -> denormalize HU -> window [-160, 240] -> PNG
```

## Important notes

- Free CPU hosting can be slow for PyTorch. The first request may also be slow because the model loads into memory.
- If the service sleeps, the next request can take longer.
- For stable medical inference, use a paid CPU/GPU server.
- Netlify hosts the frontend only. PyTorch must run on the backend.
