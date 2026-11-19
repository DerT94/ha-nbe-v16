# Historical experiments

These PowerShell scripts are retained as development history. They are outside
the local, read-only Home Assistant integration and are not part of its test or
acceptance procedure. Their networking behavior has not been made passive.

| Script | Historical behavior | Evidence limitations |
| --- | --- | --- |
| `listen_tcp_telnet.ps1` | Connects to its hard-coded EP20 address and sends Telnet negotiation replies. | Prints raw bytes as text, including device identifiers; not a byte-faithful capture. |
| `listen_http.ps1` | Opens a listener on all interfaces and sends HTTP responses; its instructions assume changing the EP20 HTTP target. | Displays decoded headers/body rather than storing the original TCP stream. |
| `collect_stokercloud_data.ps1` | Contacts Stokercloud and the configured TCP endpoint; sends Telnet negotiation replies. | Splits each TCP chunk into lines without retaining the partial last line. Reconstructed frames can therefore depend on TCP fragmentation. |

The collector now reconnects after a TCP read timeout, EOF, or a connection/read
failure. `-ReadTimeoutSec` defaults to 180 seconds without received TCP bytes,
`-ConnectTimeoutSec` to 15 seconds, and `-ReconnectDelaySec` to 10 seconds.
Retries continue until the requested snapshot count is reached or the script is
stopped. Incomplete frame lines are discarded on reconnect; saved snapshots,
snapshot numbering, and the minimum snapshot interval are retained. The current
client is disposed when collection exits. These limits apply to TCP transport,
not to cloud calls or the time to assemble a complete frame while bytes continue
arriving. An already running copy must be restarted to use this change; it does
not automatically resume snapshots from an earlier process/session.

The collector's reconstructed frames must not be used as protocol fixtures or as
proof of UART line boundaries. Before any future use as an evidence source, it
would need complete buffering of partial lines and split Telnet sequences, tests
of TCP fragmentation, and a documented capture/sanitization procedure. Existing
snapshot correlations alone do not resolve the open sensor-mapping questions.

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

Use the integration's actual `api.py` through an offline harness with synthetic
or sanitized data. Local acceptance scripts and results live in the gitignored
`docs/local-abnahme/` directory. Passive live checks follow its test runbook and
the authorization recorded there. Running any of these historical tools is not
covered by that passive-test authorization. EP20 reconfiguration, cloud access,
deployment and Home Assistant restarts require separate authorization.
