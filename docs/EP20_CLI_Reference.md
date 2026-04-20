# EP20 CLI Reference – Hi-Flying Eport Pro-EP20

**Hardware:** Hi-Flying Eport Pro-EP20 (32 MB RAM, Embedded Linux)  
**Zugang:** Telnet Port 23  
**Firmware:** V1.3x  

---

## Navigation

| Aktion | Beschreibung |
|---|---|
| `TAB` (ohne Eingabe) | Alle Befehle der aktuellen Ebene anzeigen |
| `Quit` | Eine Ebene zurück |
| `Exit` | Telnet-Session beenden (nur Root-Ebene) |
| Einzelner Buchstabe + Enter | Alle Befehle mit diesem Anfangsbuchstaben filtern |
| CLI-Timeout | 300 Sekunden Inaktivität → automatische Trennung |
| CLI-Trigger (UART) | Serielle Zeichenkette `+++` wechselt in CLI-Modus |

---

## Root `EPORT>`

Verfügbare Befehle (TAB):

```
Show        SYS         UART        SOCK        DATA
Restart     Reload      FwUpgrade   Debug       CfgVer
ScriptCrc   Exit
```

| Befehl | Typ | Funktion |
|---|---|---|
| `Show` | Info | Schnellübersicht: `Show SYS` / `Show UART` / `Show SOCK` |
| `SYS` | Verzeichnis | Systemkonfiguration |
| `UART` | Verzeichnis | Serielle Schnittstelle |
| `SOCK` | Verzeichnis | Netzwerk-Socket-Verbindungen |
| `DATA` | Verzeichnis | Live-Datenstrom (String/Hex) |
| `Restart` | Aktion | Modul-Neustart |
| `Reload` | Aktion | Werkseinstellungen laden |
| `FwUpgrade` | Aktion | Firmware-Update |
| `Debug` | Info | Debug-Level anzeigen |
| `CfgVer` | Info | Config-Versionsnummer |
| `ScriptCrc` | Info | CRC-Prüfsumme des internen Scripts |
| `Exit` | Navigation | Session beenden |

### Show-Unterbefehle

```
Show          → Vollständige Übersicht (System State + NETWORK + UART + SOCK)
Show SYS      → Systemkonfiguration (User, DHCP, Telnet, Web, IPv6...)
Show UART     → UART-Status (Baudrate, Bytes, Frames, Fehler)
Show SOCK     → Socket-Status (Name, Server, State, TX/RX)
```

---

## SYS `EPORT/SYS>`

Verfügbare Befehle (TAB):

```
Version     Auth        Network     Telnet      Web
NTP         MAC         JCMD        NAT         Ping
ProductID   CustomerID  UserID      CfgProtect  FactoryCfg
Script      XmlLoad     Language    Quit
```

| Befehl | Funktion |
|---|---|
| `Version` | Firmware-Version anzeigen |
| `Auth` | Unterverzeichnis: User/Passwort |
| `Network` | Unterverzeichnis: Netzwerk-Konfiguration |
| `Telnet` | Telnet-Status, Port, CLI-Echo anzeigen |
| `Web` | Web-Interface-Status und Port anzeigen |
| `NTP` | Zeitserver-Konfiguration |
| `MAC` | MAC-Adresse anzeigen |
| `JCMD` | JSON-Command-Interface Status |
| `NAT` | Cloud-NAT-Traversal Konfiguration |
| `Ping` | Netzwerk-Diagnose – Syntax: `Ping <IP-Adresse>` |
| `ProductID` | Produkt-Bezeichnung anzeigen |
| `CustomerID` | Kunden-ID anzeigen |
| `UserID` | User-ID anzeigen |
| `CfgProtect` | Config-Schreibschutz aktivieren/deaktivieren |
| `FactoryCfg` | Werksreset durchführen |
| `Script` | Script-Engine Status anzeigen |
| `XmlLoad` | XML-Konfiguration laden |
| `Language` | Interne Firmware-Sprache anzeigen |

### SYS/Auth `EPORT/SYS/Auth>`

Verfügbare Befehle (TAB):

```
User    Password    Quit
```

| Befehl | Funktion | Syntax |
|---|---|---|
| `User` | Aktuellen Benutzernamen anzeigen/setzen | `User <name>` |
| `Password` | Aktuelles Passwort anzeigen/setzen | `Password <passwort>` |

### SYS/Network `EPORT/SYS/Network>`

Verfügbare Befehle (TAB):

```
Show    DHCP    DNS    HostName    Quit
```

| Befehl | Funktion | Syntax |
|---|---|---|
| `Show` | Vollständige Netzwerkinfo (MAC, IP, Maske, Gateway) | — |
| `DHCP` | DHCP-Status anzeigen/setzen | `DHCP Enable` / `DHCP Disable` |
| `DNS` | DNS-Server anzeigen/setzen | `DNS <IP>` |
| `HostName` | Hostname anzeigen/setzen | `HostName <name>` |

> Hinweis: Es gibt keinen `Lan`-Befehl. Statische IP-Zuweisung nur über
> Web-Interface (Port 80) oder DHCP-Reservation per MAC im Router möglich.

---

## UART `EPORT/UART>`

Verfügbare Befehle (TAB):

```
Show        Baudrate    Databits    Stopbits    Parity
Buf         FlowCtrl    SWFlowCtrl  Cli-Getin   Cli-WaitTime
Proto       Frame       Edit        Clean       Quit
```

| Befehl | Funktion | Syntax |
|---|---|---|
| `Show` | Vollständige UART-Konfiguration anzeigen | — |
| `Baudrate` | Baudrate anzeigen/setzen | `Baudrate <wert>` |
| `Databits` | Datenbits anzeigen/setzen (5/6/7/8) | `Databits <wert>` |
| `Stopbits` | Stoppbits anzeigen/setzen (1/2) | `Stopbits <wert>` |
| `Parity` | Parität anzeigen/setzen (NONE/ODD/EVEN) | `Parity <wert>` |
| `Buf` | Unterverzeichnis: Puffer-Einstellungen | — |
| `FlowCtrl` | Hardware-Flusskontrolle (RTS/CTS) | `FlowCtrl Enable/Disable` |
| `SWFlowCtrl` | Software-Flusskontrolle (XON/XOFF) | `SWFlowCtrl Enable/Disable` |
| `Cli-Getin` | CLI-Aktivierungs-Sequenz über UART anzeigen/setzen | — |
| `Cli-WaitTime` | CLI-Inaktivitäts-Timeout in Sekunden | `Cli-WaitTime <sekunden>` |
| `Proto` | Protokoll anzeigen/setzen (NONE/Modbus/...) | — |
| `Frame` | Unterverzeichnis: Frame-Einstellungen | — |
| `Edit` | UART direkt konfigurieren | `Edit <baud> <databits> <stopbits> <parity>` |
| `Clean` | Statistik-Zähler zurücksetzen | — |

### UART/Buf `EPORT/UART/Buf>`

Verfügbare Befehle (TAB):

```
BufSize    GapTime    Quit
```

| Befehl | Funktion | Syntax |
|---|---|---|
| `BufSize` | Puffergröße in Bytes anzeigen/setzen | `BufSize <bytes>` |
| `GapTime` | Pause zwischen Frames in ms anzeigen/setzen | `GapTime <ms>` |

### UART/Frame `EPORT/UART/Frame>`

Verfügbare Befehle (TAB):

```
FrameLen    FrameTime    Tag    Quit
```

| Befehl | Funktion | Syntax |
|---|---|---|
| `FrameLen` | Max. Frame-Länge in Bytes | `FrameLen <bytes>` |
| `FrameTime` | Frame-Timeout in ms | `FrameTime <ms>` |
| `Tag` | Frame-Tagging aktivieren/deaktivieren | `Tag Enable/Disable` |

---

## SOCK `EPORT/SOCK>`

Verfügbare Befehle (TAB):

```
Show    New    <socket-name>    Quit
```

| Befehl | Funktion |
|---|---|
| `Show` | Alle konfigurierten Sockets anzeigen |
| `New` | Neuen Socket anlegen (interaktiv) |
| `<socket-name>` | Unterverzeichnis des jeweiligen Sockets |

### SOCK/`<socket-name>` `EPORT/SOCK/<name>>`

Verfügbare Befehle (TAB):

```
Show        Name        Proto       Server      ServerPort
LocalPort   BufSize     KeepAlive   Timeout     Security
HeartBeat   ConnectMode MaxAccept   Rout        Save
Clean       Del         Quit
```

| Befehl | Funktion | Syntax |
|---|---|---|
| `Show` | Config + Status des Sockets anzeigen | — |
| `Name` | Socket-Name anzeigen/setzen | `Name <name>` |
| `Proto` | Protokoll (TCP-CLIENT / TCP-SERVER / UDP) | `Proto <typ>` |
| `Server` | Ziel-Serveradresse | `Server <hostname/IP>` |
| `ServerPort` | Ziel-Port | `ServerPort <port>` |
| `LocalPort` | Lokaler Port | `LocalPort <port>` |
| `BufSize` | Puffergröße | `BufSize <bytes>` |
| `KeepAlive` | TCP-KeepAlive Intervall | `KeepAlive <sekunden>` |
| `Timeout` | Verbindungs-Timeout | `Timeout <sekunden>` |
| `Security` | TLS/Verschlüsselung | `Security Enable/Disable` |
| `HeartBeat` | Heartbeat-Paket | `HeartBeat Enable/Disable` |
| `ConnectMode` | Verbindungsmodus (Burst/Always/...) | `ConnectMode <modus>` |
| `MaxAccept` | Max. gleichzeitige Verbindungen (Server-Modus) | `MaxAccept <n>` |
| `Rout` | Daten-Routing-Ziel (uart / ...) | `Rout <ziel>` |
| `Save` | Konfiguration speichern | — |
| `Clean` | Zähler zurücksetzen | — |
| `Del` | Socket löschen | — |

---

## DATA `EPORT/DATA-Str>` / `EPORT/DATA-Hex>`

Zwei Modi, zwischen denen man wechseln kann:

```
DATA-Str:  Hex     Quit
DATA-Hex:  Str     Quit
```

| Befehl | Funktion |
|---|---|
| `Hex` | Wechsel in Hex-Darstellung (DATA-Hex) |
| `Str` | Wechsel in String-Darstellung (DATA-Str) |
| `Quit` | Zurück zum Root |

Das DATA-Verzeichnis zeigt den Live-Datenstrom der UART-Socket-Bridge in Echtzeit.
Jede UART-Nachricht des angeschlossenen Geräts erscheint hier direkt lesbar.

---
