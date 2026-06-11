$ErrorActionPreference = "Stop"

$Root = "E:\Games\ray-vision\mobile-web"
$IndexPath = Join-Path $Root "index.html"
$Port = 8088

$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Any, $Port)
$listener.Server.SetSocketOption(
  [System.Net.Sockets.SocketOptionLevel]::Socket,
  [System.Net.Sockets.SocketOptionName]::ReuseAddress,
  $true
)
$listener.Start()

while ($true) {
  $client = $listener.AcceptTcpClient()
  try {
    $stream = $client.GetStream()
    $reader = [System.IO.StreamReader]::new($stream, [System.Text.Encoding]::ASCII, $false, 1024, $true)
    $null = $reader.ReadLine()

    do {
      $line = $reader.ReadLine()
    } while ($line -ne $null -and $line.Length -gt 0)

    $body = [System.IO.File]::ReadAllBytes($IndexPath)
    $headerText = "HTTP/1.1 200 OK`r`nContent-Type: text/html; charset=utf-8`r`nCache-Control: no-store`r`nContent-Length: $($body.Length)`r`nConnection: close`r`n`r`n"
    $header = [System.Text.Encoding]::ASCII.GetBytes($headerText)
    $stream.Write($header, 0, $header.Length)
    $stream.Write($body, 0, $body.Length)
    $stream.Flush()
  } finally {
    $client.Close()
  }
}
