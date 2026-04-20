# ============================================================
# Connects to TCP/telnet server 10.30.0.14:23, reads and prints incoming UTF-8
# data, and silently rejects all Telnet option negotiation (IAC sequences).
# ============================================================
$tcp = [System.Net.Sockets.TcpClient]::new("10.30.0.14", 23)
$stream = $tcp.GetStream()
$buffer = New-Object byte[] 4096

Write-Host "Verbunden. Warte auf Daten..." -ForegroundColor Green

while ($true) {
    $bytesRead = $stream.Read($buffer, 0, $buffer.Length)
    if ($bytesRead -eq 0) { break }
    
    # Telnet IAC-Sequenzen (0xFF) abfangen und beantworten
    $i = 0
    while ($i -lt $bytesRead) {
        if ($buffer[$i] -eq 0xFF -and ($i + 2) -lt $bytesRead) {
            # IAC DO/WILL -> mit WONT/DONT antworten
            $cmd = $buffer[$i + 1]
            $opt = $buffer[$i + 2]
            $response = if ($cmd -eq 0xFD) { 0xFC } else { 0xFE }
            $stream.Write([byte[]]@(0xFF, $response, $opt), 0, 3)
            $i += 3
        } else {
            $text = [System.Text.Encoding]::UTF8.GetString($buffer, $i, 1)
            Write-Host $text -NoNewline
            $i++
        }
    }
}