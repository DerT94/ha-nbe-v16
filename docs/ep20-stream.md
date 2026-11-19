# EP20 UART stream

Home Assistant opens a persistent local TCP connection to the EP20, normally on port 23. The integration passively reads the UART stream. The GET request line and Host header arrive as text in that stream. All parsing happens locally.

## Frames

The stream uses `???` to delimit frames. A single line can contain multiple markers. Telnet negotiation bytes, a login prompt or other noise can precede the GET request. A typical operational frame contains a request line, a header and the frame marker.

```text
GET /v16dev/opr.php?mac=12345&z000=502&z001=0 HTTP/1.1
Host: stokercloud.dk
???
```

The parser searches within frame lines for the GET request. For `/v16dev/opr.php`, it parses the query with `urllib.parse.parse_qs` and passes the Z-values and optional `mac` to the coordinator. The metadata in `const.py` drives the decoded sensor entities.

| Frame content | Handling |
| --- | --- |
| `/v16dev/opr.php` | Parse the operational payload. |
| `/v16dev/setup.php`, `/v16dev/events2.php` | Ignore. |
| Other endpoints or header-only fragments | Ignore. These can occur during normal stream processing. |

## Connection and buffering behavior

- **End of stream.** `api.py` processes buffered data at EOF even if the final `???` is missing. It discards buffered data on read timeout.
- **Reconnect.** Connection errors, read timeouts and clean EOF use a fixed retry delay before reconnecting.
- **Logging.** Ignored endpoints and header-only fragments can produce DEBUG messages in the current code.

See [the TCP capture](ExampleEP20Data_tcp.txt) for existing stream examples, [the Z-value reference](NBE_zValue_maping.md) for mapping evidence, and [the EP20 CLI reference](EP20_CLI_Reference.md) for hardware terminology.
