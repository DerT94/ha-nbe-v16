# Configuration

Initial installation is described in the [README](../README.md). Settings belong to one config entry and affect only that entry.

## Endpoint and reconfiguration

Use the existing EP20 address and UART TCP server port, normally 23. The setup probe opens a short-lived connection and proves reachability only; the persistent reader must subsequently receive valid measurements.

For an address change of the same EP20, use **Reconfigure**. This updates the endpoint and reloads the same entry, preserving its entry ID and sensor unique IDs. An endpoint already assigned to another entry is rejected. The stream's `mac` parameter does not authenticate a physical replacement device.

Plan one direct reader per EP20. Parallel-client observations on the tested installation showed accepted TCP connections without simultaneous stream delivery to every reader. Use forwarding for additional consumers; the EP20's internal session-selection rule is unknown.

## Developer mode

Enable **Developer mode** during initial setup or through **Reconfigure**. Normal mode creates only primary sensors. Developer mode creates all named sensors and discovers additional numeric Z-keys as frames arrive, including keys first seen later. Unknown fields use their exact key, such as `z96`, and expose unscaled, unitless integers without a statistics class. Known fields keep their existing conversions and names.

Each entry discovers its own fields. Sensors are enabled by default in developer mode; integration-disabled entries are enabled and explicit user disabling is respected. Switching the mode reloads the entry. Turning it off removes additional Z-value entities from the registry. See [compatibility](compatibility.md#entity-registry-and-developer-mode) before changing mode if you renamed or customized those entities.

## Raw TCP forwarding

Forwarding is disabled by default. On the HA instance connected to the EP20, open the entry's **Configure** action:

1. Enable **Raw TCP forwarding**.
2. Select an explicit private or loopback bind IP that exists on the HA host/container.
3. Choose an unused port from 1024–65535; the default is 2323.
4. Enter 1–16 allowed recipient IPs, separated by commas.

Wildcard binds, public IPs and hostnames are rejected. Options reload this entry. The form rejects an address or port it cannot bind. If a saved listener fails during setup/reload, HA logs an error and continues local EP20 reading and sensor updates. Multiple entries need distinct listener endpoints.

On the receiving HA instance, add the integration using the sender's reachable address and listener port. For example, the sender can bind `192.168.1.10:2323` and allow recipient `192.168.1.20`; that recipient configures `192.168.1.10`, port `2323`, as its endpoint. These are illustrative addresses. Only the sender connects directly to the EP20.

The listener accepts clients only while its upstream stream is connected. A successful receiving setup probe does not guarantee subsequent measurement delivery. New clients wait for the next frame boundary; there is no initial measurement snapshot or replay. Detailed limits and failure behavior are in the [stream reference](ep20-stream.md#raw-tcp-forwarding).

### Network and data exposure

This is an **unencrypted raw TCP socket without login or TLS**. It exposes the original stream, including identifiers, ignored endpoints and potentially configuration data. An exact IP allowlist restricts access but provides no cryptographic authentication.

Use a trusted isolated network, restrict the port to recipients through a host/network firewall and keep it off the Internet. With containers, verify the source IP visible to the listener: NAT can make one allowed address represent multiple devices. Client input closes that client; it is never sent to the EP20.

## Availability and diagnostics

Sensors start unavailable and require valid measurements. Disconnects or expired measurements make them unavailable again; manual refresh neither fetches values nor renews their age. See [connection limits](ep20-stream.md#connection-and-measurement-lifecycle).

Entry diagnostics contain availability, constant limits, counts and known present Z-keys. Forwarding includes `enabled` and a status of `disabled`, `listening` or `not_listening`. An enabled listener that failed to bind reports `not_listening` even while local measurements continue. Endpoint details, MAC, raw values and exception messages are omitted. Unrecognized frame contents are omitted from debug logs; review other logs before sharing them.
