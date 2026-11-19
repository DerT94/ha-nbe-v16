# Historical experiments

These PowerShell scripts are retained as development history. They are outside
the local, read-only Home Assistant integration and are not part of its test or
acceptance procedure. Their networking behavior has not been made passive.

| Script | Historical behavior | Evidence limitations |
| --- | --- | --- |
| `listen_tcp_telnet.ps1` | Connects to its hard-coded EP20 address and sends Telnet negotiation replies. | Prints raw bytes as text, including device identifiers; not a byte-faithful capture. |
| `listen_http.ps1` | Opens a listener on all interfaces and sends HTTP responses; its instructions assume changing the EP20 HTTP target. | Displays decoded headers/body rather than storing the original TCP stream. |
| `collect_stokercloud_data.ps1` | Contacts Stokercloud and the configured TCP endpoint; sends Telnet negotiation replies. | Splits each TCP chunk into lines without retaining the partial last line. Reconstructed frames can therefore depend on TCP fragmentation. |

## Collector behavior and evidence limits

The collector reconnects after TCP timeout, EOF or connection/read failure until
the requested snapshot count is reached or it is stopped. Defaults are 180 seconds
without TCP bytes, 15 seconds to connect and 10 seconds between attempts. These
limits do not bound cloud calls or frame assembly while bytes continue arriving.
On reconnect, incomplete lines are discarded while snapshots, numbering and the
minimum snapshot interval remain. The client is disposed on exit. A new process
does not automatically resume an earlier session's snapshots.

Reconstructed frames are not protocol fixtures or proof of UART line boundaries.
Reliable byte capture would require partial-line and split-Telnet buffering,
fragmentation tests and a documented capture/sanitization procedure. Existing
named-value correlations can inform [mapping evidence](../docs/mapping-evidence.md)
within these limits; they do not resolve every physical meaning or unit.

## Credentials and captured data

The collector accepts the password as a plain string parameter, places it in the
login URL, and places session tokens in subsequent request URLs. The login
response's `credentials` field is printed. Server login messages and raw
exception messages are also printed; PowerShell error records may include the
request URL. Command history, transcripts, copied errors and console output can
therefore contain sensitive data. No redaction guarantee is provided by these
historical scripts.

The collector also saves `raw_frame`, query values and cloud responses. Treat
these outputs as potentially identifying or sensitive. They are not sanitized
fixtures and should not be committed or uploaded as-is. Review the full error
record and output files before sharing them; removing only the password from a
single displayed line is insufficient.

## Current development workflow

Offline harnesses use the integration's actual code with synthetic or sanitized
data. Scripts, reports and the test runbook stay in the gitignored
`docs/local-abnahme/` directory. Historical passive-test authorization does not
cover running these tools. EP20 reconfiguration, cloud access, deployment and HA
restarts require the corresponding explicit instruction. The [stream reference](../docs/ep20-stream.md)
describes the integration's passive data path.
