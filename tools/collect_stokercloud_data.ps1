# HISTORICAL EXPERIMENT - not part of the read-only integration or its tests.
# Uses the cloud, sends Telnet replies and loses partial lines across TCP reads.
# Credentials/tokens can leak through URLs, console output and error records.
# Its reconstructed frames are not byte-faithful fixtures. See tools/README.md.

# ============================================================
# NBE V16 - Datensammler v4
# Aenderungen ggÃ¼ v3:
#   - $screen aufgeteilt in $screen1 + $screen2 (alle gueltigen IDs, keine Dopplungen)
#   - livedata1 + livedata2 pro Snapshot gespeichert
# Aufruf: .\01_collect_v4.ps1 -Password "deinPasswort" [-Frames 10] [-MinIntervalSec 120]
# ============================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$Password,
    [string]$User           = "",
    [string]$TcpHost        = "",
    [int]   $TcpPort        = 23,
    [string]$BaseUrl        = "https://stokercloud.dk/v16bckbeta/dataout2",
    [string]$OutDir         = $PSScriptRoot,
    [int]   $Frames         = 10,
    [int]   $MinIntervalSec = 120,
    [ValidateRange(1, 2147483)]
    [int]   $ReadTimeoutSec = 180,
    [ValidateRange(1, 2147483)]
    [int]   $ConnectTimeoutSec = 15,
    [ValidateRange(1, 3600)]
    [int]   $ReconnectDelaySec = 10
)

$ErrorActionPreference = "Stop"

$sessionId     = Get-Date -Format "yyyyMMdd_HHmmss"
$sessionDir    = "$OutDir\$sessionId"
New-Item -ItemType Directory -Path $sessionDir | Out-Null
$fileMenudata  = "$sessionDir\menudata.json"
$fileSnapshots = "$sessionDir\snapshots.json"

# Screen 1: boil 1-14, dhw 2/3/10/11/12, hopper 1-13, weather 1-5
$screen1 = "b1,1,b2,2,b3,3,b4,4,b5,5,b6,7,b7,9,b8,12,b9,13,b10,14," +
           "d1,2,d2,3,d3,10,d4,11,d5,12,d6,0,d7,0,d8,0,d9,0,d10,0," +
           "h1,1,h2,2,h3,3,h4,4,h5,5,h6,7,h7,8,h8,9,h9,10,h10,13," +
           "w1,1,w2,2,w3,3,w4,4,w5,5"

# Screen 2: boil 15-25, hopper 14/15
$screen2 = "b1,15,b2,16,b3,18,b4,19,b5,20,b6,21,b7,22,b8,23,b9,24,b10,25," +
           "d1,0,d2,0,d3,0,d4,0,d5,0,d6,0,d7,0,d8,0,d9,0,d10,0," +
           "h1,14,h2,15,h3,0,h4,0,h5,0,h6,0,h7,0,h8,0,h9,0,h10,0," +
           "w1,0,w2,0,w3,0,w4,0,w5,0"

$menus = @("boiler", "oxygen", "hopper", "cleaning", "ignition",
           "hot_water", "weather", "ext_feed")

function Invoke-Api($url) {
    Invoke-RestMethod -Uri $url -Method Get -Headers @{
        "Accept"  = "application/json"
        "Origin"  = "https://v16.stokercloud.dk"
        "Referer" = "https://v16.stokercloud.dk/"
    }
}

function Get-Token {
    param([string]$t)
    Write-Host "      Token wird erneuert..." -ForegroundColor DarkGray
    $login = Invoke-Api "$BaseUrl/login.php?user=$User&password=$Password"
    if ($login.status -ne 0) { Write-Error "Login fehlgeschlagen: $($login.message)"; exit 1 }
    Write-Host "      Token OK ($($login.credentials))" -ForegroundColor DarkGray
    return $login.token
}

function Save-Snapshots {
    param($list, $path)
    $list | ConvertTo-Json -Depth 15 | Out-File $path -Encoding UTF8
}

function New-CollectorConnection {
    param($HostName, $Port, $ConnectTimeoutSec, $ReadTimeoutSec)
    $client = [System.Net.Sockets.TcpClient]::new()
    try {
        $pending = $client.ConnectAsync($HostName, $Port)
        if (-not $pending.Wait($ConnectTimeoutSec * 1000)) {
            throw [System.TimeoutException]::new('TCP connect timeout')
        }
        $pending.GetAwaiter().GetResult()
        $networkStream = $client.GetStream()
        $networkStream.ReadTimeout = $ReadTimeoutSec * 1000
        return @{ Client = $client; Stream = $networkStream }
    } catch {
        $client.Dispose()
        throw
    }
}

function Read-CollectorBytes {
    param($State, $Buffer, $HostName, $Port,
          $ConnectTimeoutSec, $ReadTimeoutSec, $ReconnectDelaySec)
    while ($true) {
        try {
            if ($null -eq $State.Connection) {
                Write-Host '      TCP-Verbindung wird aufgebaut...' -ForegroundColor DarkGray
                $State.Connection = New-CollectorConnection -HostName $HostName -Port $Port `
                    -ConnectTimeoutSec $ConnectTimeoutSec -ReadTimeoutSec $ReadTimeoutSec
                Write-Host "      TCP verbunden (Lese-Timeout: ${ReadTimeoutSec}s)." -ForegroundColor DarkGray
            }
            $count = $State.Connection.Stream.Read($Buffer, 0, $Buffer.Length)
            if ($count -eq 0) { throw [System.IO.EndOfStreamException]::new() }
            return $count
        } catch {
            # Never carry an incomplete frame into a different TCP connection.
            if ($null -ne $State.Connection) { $State.Connection.Client.Dispose() }
            $State.Connection = $null
            $State.FrameLines.Clear()
            Write-Warning "TCP-Lesen/Verbindungsaufbau fehlgeschlagen oder EOF (Lese-Timeout: ${ReadTimeoutSec}s). Reconnect in ${ReconnectDelaySec}s; Snapshots bleiben erhalten."
            Start-Sleep -Seconds $ReconnectDelaySec
        }
    }
}

function Resolve-Name($key) {
    if ($uk.PSObject.Properties[$key]) { return $uk.$key }
    return $key  # Fallback: Originalkey
}

function ConvertTo-Sensors {
    param($livedata)
    if (-not $livedata) { return @() }
    foreach ($sec in $livedata.PSObject.Properties) {
        if ($sec.Value -isnot [array]) { continue }
        foreach ($entry in $sec.Value) {
            if ($entry.id -notmatch '^\d+$') { continue }
            [PSCustomObject]@{
                name  = if ($uk.($entry.name)) { $uk.($entry.name) } else { $entry.name }
                value = $entry.value
            }
        }
    }
}

# Schritt 1: Login
Write-Host "[1/3] Login... (Session: $sessionId)" -ForegroundColor Cyan
$token    = Get-Token
$tokenAge = [DateTime]::Now

# Schritt 1b: Sprachdatei laden
Write-Host "[1b] Lade uk.json..." -ForegroundColor Cyan
$uk = Invoke-RestMethod "https://v16.stokercloud.dk/locales/uk.json"
Write-Host "     OK $(@($uk.PSObject.Properties).Count) Einträge" -ForegroundColor Green

# Schritt 2: Menudata einmalig abrufen
Write-Host "[2/3] Menudata einmalig abrufen..." -ForegroundColor Cyan
$menudata = @{}
foreach ($menu in $menus) {
    Write-Host "      -> $menu" -NoNewline
    try {
        $menudata[$menu] = Invoke-Api "$BaseUrl/getmenudata.php?menu=$menu&token=$token"
        Write-Host " OK" -ForegroundColor Green
    } catch {
        Write-Host " FEHLER: $($_.Exception.Message)" -ForegroundColor Yellow
        $menudata[$menu] = $null
    }
}
$menudata | ConvertTo-Json -Depth 10 | Out-File $fileMenudata -Encoding UTF8
Write-Host "      Gespeichert: $fileMenudata" -ForegroundColor Green

# Schritt 3: TCP verbinden und Frames sammeln
Write-Host "[3/3] Verbinde TCP ${TcpHost}:$TcpPort ..." -ForegroundColor Cyan
$buffer = New-Object byte[] 4096

$frameLines   = [System.Collections.Generic.List[string]]::new()
$snapshots    = [System.Collections.Generic.List[object]]::new()
$frameCount   = 0
$lastSnapshot = [DateTime]::MinValue
$lastZvals    = $null
$connectionState = @{ Connection = $null; FrameLines = $frameLines }

Write-Host "      Warte auf $Frames Frames (Mindestabstand: ${MinIntervalSec}s)..." -ForegroundColor Cyan
Write-Host ""

try {
while ($frameCount -lt $Frames) {
    $bytesRead = Read-CollectorBytes -State $connectionState -Buffer $buffer `
        -HostName $TcpHost -Port $TcpPort -ConnectTimeoutSec $ConnectTimeoutSec `
        -ReadTimeoutSec $ReadTimeoutSec -ReconnectDelaySec $ReconnectDelaySec
    $stream = $connectionState.Connection.Stream

    # IAC abhandeln
    $cleanBytes = [System.Collections.Generic.List[byte]]::new()
    $i = 0
    while ($i -lt $bytesRead) {
        if ($buffer[$i] -eq 0xFF -and ($i + 2) -lt $bytesRead) {
            $cmd = $buffer[$i + 1]; $opt = $buffer[$i + 2]
            $response = if ($cmd -eq 0xFD) { 0xFC } else { 0xFE }
            $stream.Write([byte[]]@(0xFF, $response, $opt), 0, 3)
            $i += 3
        } else {
            $cleanBytes.Add($buffer[$i]); $i++
        }
    }

    $text  = [System.Text.Encoding]::UTF8.GetString($cleanBytes.ToArray())
    $lines = $text -split "`n"

    foreach ($line in $lines) {
        $line = $line.Trim()
        if ($line.Length -eq 0) { continue }
        $frameLines.Add($line)

        if ($line -eq "???") {
            $oprLine = $frameLines | Where-Object {
                $_ -match 'GET\s+/v16dev/opr\.php\?'
            } | Select-Object -First 1

            if (-not $oprLine) {
                $frameLines.Clear()
                continue
            }

            $now     = [DateTime]::Now
            $elapsed = ($now - $lastSnapshot).TotalSeconds

            if ($lastSnapshot -ne [DateTime]::MinValue -and $elapsed -lt $MinIntervalSec) {
                $remaining = [int]($MinIntervalSec - $elapsed)
                Write-Host "  Frame empfangen (wird uebersprungen, naechster in ~${remaining}s)" `
                    -ForegroundColor DarkGray
                $frameLines.Clear()
                continue
            }

            $ts = $now.ToString("yyyy-MM-ddTHH:mm:ss")
            $frameCount++
            $lastSnapshot = $now
            Write-Host "  Frame #$frameCount um $ts" -ForegroundColor Green

            $rawFrame = $frameLines -join "`n"

            # Z-Werte parsen
            $null = $oprLine -match 'GET\s+/v16dev/opr\.php\?([^\s]+)\s+HTTP'
            $qs    = $matches[1]
            $zvals = [ordered]@{}
            foreach ($pair in $qs.Split('&')) {
                $kv = $pair.Split('=', 2)
                if ($kv.Length -eq 2) { $zvals[$kv[0]] = $kv[1] }
            }
            Write-Host "    Z-Werte: $($zvals.Count)" -NoNewline

            # Z-Wert-Diff pruefen
            $zvalsChanged = $true
            if ($null -ne $lastZvals) {
                $zvalsChanged = $false
                foreach ($key in $zvals.Keys) {
                    if ($lastZvals[$key] -ne $zvals[$key]) {
                        $zvalsChanged = $true
                        break
                    }
                }
            }

            # Token alle 5 Minuten erneuern
            if (([DateTime]::Now - $tokenAge).TotalSeconds -gt 270) {
                $token    = Get-Token
                $tokenAge = [DateTime]::Now
            }

            $livedata1   = $null
            $livedata2   = $null
            $livedataRef = $null

            if ($zvalsChanged) {
                try {
                    $livedata1 = Invoke-Api "$BaseUrl/controllerdata2.php?screen=$screen1&token=$token"
                    Write-Host " | screen1: OK" -NoNewline -ForegroundColor DarkGray
                } catch {
                    Write-Host " | screen1 FEHLER: $($_.Exception.Message)" -ForegroundColor Yellow
                }
                try {
                    $livedata2 = Invoke-Api "$BaseUrl/controllerdata2.php?screen=$screen2&token=$token"
                    $liveDelay = ([DateTime]::Now - [DateTime]::Parse($ts)).TotalMilliseconds
                    Write-Host " | screen2: OK ($([int]$liveDelay)ms)" -ForegroundColor DarkGray
                } catch {
                    Write-Host " | screen2 FEHLER: $($_.Exception.Message)" -ForegroundColor Yellow
                }
                $lastZvals = $zvals
            } else {
                $livedataRef = $frameCount - 1
                Write-Host " | livedata: unveraendert (ref=#$livedataRef)" -ForegroundColor DarkGray
            }

            # getstatus abrufen (immer)
            $getstatus = $null
            try {
                $getstatus = Invoke-Api "$BaseUrl/getstatus.php?token=$token"
            } catch {}

            $snapshot = [PSCustomObject]@{
                timestamp     = $ts
                session_id    = $sessionId
                frame_nr      = $frameCount
                zvals         = $zvals
                zvals_changed = $zvalsChanged
                sensors = @(ConvertTo-Sensors $livedata1) + @(ConvertTo-Sensors $livedata2)
                livedata_ref  = $livedataRef
                getstatus     = $getstatus
                raw_frame     = $rawFrame
            }
            $snapshots.Add($snapshot)

            Save-Snapshots $snapshots $fileSnapshots
            Write-Host "    Snapshot #$frameCount gespeichert" -ForegroundColor DarkGray

            $frameLines.Clear()
        }
    }
}

} finally {
    if ($null -ne $connectionState.Connection) {
        $connectionState.Connection.Client.Dispose()
    }
}

Write-Host ""
Write-Host "Fertig! $($snapshots.Count) Snapshots gesammelt." -ForegroundColor Green
Write-Host ""
Write-Host "Gespeicherte Dateien (Session: $sessionId):" -ForegroundColor White
Write-Host "  $fileMenudata" -ForegroundColor White
Write-Host "  $fileSnapshots" -ForegroundColor White
Write-Host ""
Write-Host "Beide Dateien zur Analyse hochladen." -ForegroundColor Yellow
