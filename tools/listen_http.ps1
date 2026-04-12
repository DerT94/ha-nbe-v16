# ============================================================
# NBE V16 – TCP Diagnose-Listener (Windows PowerShell)
# Lauscht auf rohe TCP-Verbindungen vom EP20-Modul.
# Gibt alle empfangenen Daten als Text UND als Hex aus.
#
# Verwendung:
#   .\listen_http.ps1
#   .\listen_http.ps1 -Port 8888
#
# Im EP20 einstellen:
#   Protokoll : Http (POST oder GET)
#   Ziel-IP   : <IP dieses Windows-PCs>
#   Ziel-Port : 8888
# ============================================================

param(
    [int]$Port = 8888
)

$endpoint = [System.Net.IPEndPoint]::new([System.Net.IPAddress]::Any, $Port)
$listener = [System.Net.Sockets.TcpListener]::new($endpoint)

try {
    $listener.Start()
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  NBE V16 – TCP Listener gestartet" -ForegroundColor Cyan
    Write-Host "  Lausche auf Port $Port ..." -ForegroundColor Cyan
    Write-Host "  Stoppen mit: Ctrl+C" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    while ($true) {
        # Fix für das STRG+C Problem: .Pending() schaut nur kurz nach, ob jemand da ist.
        # Wenn nicht, schläft das Skript 100ms. So kann STRG+C jederzeit greifen.
        if ($listener.Pending()) {
            $client    = $listener.AcceptTcpClient()
            $stream    = $client.GetStream()
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            $remoteEP  = $client.Client.RemoteEndPoint

            Write-Host "----------------------------------------" -ForegroundColor DarkGray
            Write-Host "[$timestamp] Neue Verbindung" -ForegroundColor Green
            Write-Host "  Von: $remoteEP" -ForegroundColor White
            Write-Host ""

            $reader = [System.IO.StreamReader]::new($stream)
            Write-Host "  Empfangene Daten:" -ForegroundColor Yellow
            
            $contentLength = 0
            
            # HTTP Header lesen (bricht bei einer leeren Zeile ab, um Aufhängen zu vermeiden)
            while ($true) {
                $line = $reader.ReadLine()
                if ($line -eq $null -or $line -eq "") { break }
                
                Write-Host "    $line" -ForegroundColor Yellow
                
                # Wir merken uns die Länge des Bodys, falls einer mitgeschickt wird
                if ($line -match "^Content-Length:\s*(\d+)") {
                    $contentLength = [int]$matches[1]
                }
            }

            # HTTP Body lesen (z.B. bei POST-Requests), falls Content-Length > 0 ist
            if ($contentLength -gt 0) {
                Write-Host "    " # Leerzeile zur optischen Trennung
                $buffer = New-Object char[] $contentLength
                $reader.ReadBlock($buffer, 0, $contentLength) | Out-Null
                $body = -join $buffer
                Write-Host "    $body" -ForegroundColor DarkYellow
            }

            # Antwort an EP20 senden, damit es nicht in einen Timeout läuft
            $response = "HTTP/1.1 200 OK`r`nContent-Length: 2`r`nConnection: close`r`n`r`nOK"
            $writer = [System.IO.StreamWriter]::new($stream)
            $writer.Write($response)
            $writer.Flush()

            $client.Close()
            Write-Host ""
            Write-Host "  Verbindung sauber geschlossen." -ForegroundColor Green
            Write-Host "  Warte auf naechste Verbindung..." -ForegroundColor DarkGray
            Write-Host ""
        } else {
            # Kurze Pause für die CPU und für STRG+C
            Start-Sleep -Milliseconds 100
        }
    }
}
catch {
    Write-Host "Fehler: $_" -ForegroundColor Red
}
finally {
    $listener.Stop()
    Write-Host "Listener gestoppt." -ForegroundColor Yellow
}