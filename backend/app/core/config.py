from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "Ray-Vision API"
    api_prefix: str = "/api"
    cors_origins: tuple[str, ...] = (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8088",
        "http://127.0.0.1:8088",
        "null",
    )
    cors_origin_regex: str = (
        r"http://(localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|"
        r"172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+|"
        r"192\.168\.\d+\.\d+)(:\d+)?"
        r"|https://.*\.netlify\.app"
    )


settings = Settings()
