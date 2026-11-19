# EP20 UART stream

The integration opens a persistent local TCP connection to the EP20 UART stream, normally on port 23. Request lines and headers are text carried inside that stream; they are parsed locally. The integration sends no HTTP request, application data, Telnet reply or boiler command.

## Frames and accepted payloads

`???` delimits frames, even across TCP reads or several times on one line. Noise, negotiation bytes or prompts may precede a GET request. A synthetic example is:

```text
GET /v16dev/opr.php?mac=example&z02=502&z01=0 HTTP/1.1
Host: example.invalid
???
```

The parser searches frame lines for a complete GET request with a complete HTTP version. Only `/v16dev/opr.php` is processed; setup, events, unrelated endpoints and header-only fragments are ignored.

Query parsing uses `urllib.parse.parse_qs`. Measurement keys must match `z[0-9]+` and raw values must be signed or unsigned ASCII integers. At least one valid pair is required. Invalid fields are omitted; MAC-only and malformed payloads do not refresh measurements. For duplicate query parameters the first value is used, including an empty first value.

Exact keys are retained: `z02` and `z000` are different fields. Optional nonempty `mac` is passed internally only alongside valid measurements; it is not verified hardware identity. Valid partial payloads replace the previous payload; missing keys are not filled from older frames. Entity conversions are defined by the [sensor reference](sensors.md).

## Buffering and completion

| Condition | Handling |
| --- | --- |
| Frame marker | Completes the frame immediately; newline is not required. |
| Clean EOF | May complete a syntactically complete request without a final marker. |
| Reset, timeout, stop or cancellation | Discards unfinished data. |
| Frame larger than 32 KiB | Discards that frame and resynchronizes at the next marker. |

The limit counts wire bytes between markers, including headers, CR/LF and noise. It is a local protection limit, not an EP20 protocol maximum. Reading uses blocks of at most 4 KiB; the retained frame buffer is bounded by the frame limit plus two potential marker bytes, with a temporary read block in addition. Asyncio/OS transport buffers are separate.

## Connection and measurement lifecycle

| Limit | Current value | Meaning |
| --- | --- | --- |
| Persistent connect timeout | 15 s | Time allowed to establish a reader connection. |
| Read timeout | 60 s | Time without received TCP bytes. |
| Reconnect delay | 10 s | Delay after EOF or connection/read failure. |
| Measurement maximum age | 180 s | Time without valid measurements, independently of other traffic. |

The measurement-age limit was chosen provisionally from a short passive observation with about 62 seconds between updates; it is not a documented device interval. The config-flow probe separately limits connection to 5 seconds and closing to 2 seconds.

Setup starts without successful data. Valid measurements restore availability and restart the age timer. Disconnects and expired measurements make data unavailable. Manual refresh is a successful no-op: it does not fetch data, clear errors or renew the timer. Each entry has independent connection/coordinator state.

Planned stop/unload marks data unavailable quietly. Unexpected outages use one warning per outage, subsequent retries at DEBUG and TCP recovery at INFO; TCP recovery alone does not establish measurement delivery. Unrecognized frame logs contain counts rather than raw content. Unload and HA shutdown close streams and background tasks.

## Raw TCP forwarding

For configuration and network exposure, see [configuration](configuration.md#raw-tcp-forwarding). The listener forwards original bytes before parsing, including non-operational content. It does not preserve read/packet boundaries or retain bytes for replay or diagnostics.

New recipients discard the incomplete initial fragment and receive bytes starting with the next `???` marker. There is no historical or initial measurement snapshot. A listener accepts clients only while its upstream connection is connected; this does not guarantee that the next bytes contain measurements.

At most four clients share a listener. Each has a 64 KiB application queue plus one sending chunk of at most 4 KiB. A full queue or five-second send timeout disconnects that client without waiting in the upstream reader. Asyncio/OS buffers use their own defaults; these limits do not guarantee survival of arbitrarily large bursts.

Client input closes that recipient and is never forwarded upstream. Upstream EOF, error or timeout disconnects recipients and discards pending data; reconnect begins a new stream. Unload and HA shutdown close listener, clients and tasks. A saved listener bind failure leaves local EP20 reading operational and appears in diagnostics as `not_listening`.

## Reference material

The formatted [TCP example](ExampleEP20Data_tcp.txt) and HTTP examples are historical illustrations, not byte-faithful parser fixtures. Sanitized live fixtures and their provenance stay in local acceptance storage. Hardware terminology and commands are preserved in the [archived CLI notes](archive/ep20-cli.md).
