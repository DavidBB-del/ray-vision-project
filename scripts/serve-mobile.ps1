$ErrorActionPreference = "Stop"

$Root = "E:\Games\ray-vision\mobile-web"
$Python = "C:\Users\13094\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

Set-Location $Root
& $Python -m http.server 8088 --bind 0.0.0.0 --directory $Root *> $null
