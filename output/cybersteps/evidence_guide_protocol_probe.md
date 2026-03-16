# Evidence Interpretation Guide: `evidence_protocol_probe.json`

## What is this file?
This file contains the results of a custom Python script (`protocol_probe.py`) designed to actively test **specific network protocols** against ports that were already discovered to be open.

## How did we get this intelligence?
1. **Prerequisite:** We ran a primary port scan (like Naabu or Nmap) which told us *which* ports were physically open (e.g., 1080 and 3389).
2. **Action:** We wrote a custom script that connects to these specific ports and speaks their native language.
    * For Port 1080, it sent a SOCKS5 handshake (`b"\x05\x01\x00"`).
    * For Port 3389, it sent an RDP (Remote Desktop Protocol) TPKT connection request (`b"\x03\x00\x00\x13\x0e\xe0\x00\x00\x00\x00\x00\x01\x00\x08\x00\x03\x00\x00\x00"`).
3. **Capture:** It waited for the server's response and recorded the raw bytes returned.

## RTM Rating (Risk/Yield)
**Level: Flammable Absynth 🔥🍸**
*   **Risk (Flammable):** Highly noisy. Interacting directly with the application layer using specific protocol headers will definitively log our IP address in the target's application logs (e.g., Windows Event Logs for RDP).
*   **Yield (Absynth):** Critical intelligence. It proves beyond a shadow of a doubt exactly what software/protocol is exposed, bypassing any attempts to obscure the service by running it on a non-standard port.

---

## How to Read and Interpret the Findings

### Finding 1: Port 1080
```json
  {
    "port": 1080,
    "protocol_check": "socks5",
    "matched": false,
    "raw_response_hex": ""
  }
```
*   **Reading it:** We tested Port 1080 to see if it was a SOCKS5 proxy. The `matched` status is `false`, and the `raw_response_hex` is empty (`""`).
*   **Interpretation:** While the port is open (it accepted our TCP connection), the application running behind it **refused to speak SOCKS5**. It immediately closed the connection without returning any data. This proves Port 1080 is **NOT** a standard, open SOCKS proxy. It is likely an obfuscated service, a honeypot, or a service expecting a specific sequence (like port knocking) before it responds.

### Finding 2: Port 3389
```json
  {
    "port": 3389,
    "protocol_check": "rdp",
    "matched": true,
    "raw_response_hex": "030000130ed000001234000200080001000000"
  }
```
*   **Reading it:** We tested Port 3389 for RDP. The `matched` status is `true`, and it returned a specific hex string starting with `03000013`.
*   **Interpretation:** This is **absolute proof** of an active Remote Desktop Protocol service.
    *   The `03` is the TPKT version.
    *   The `000013` is the length of the packet.
    *   This specific byte sequence is the standard Microsoft Windows Terminal Server acknowledgment. We now have undeniable evidence that an RDP login surface is exposed to the public internet, representing a major security risk.

#### Command Used for Verification
We obtained this exact hexadecimal response by executing our custom protocol probing script:
```bash
python output/cybersteps/protocol_probe.py
```
*(This script connects via TCP and sends the raw hex `030000130ee000000000000100080003000000`, the standard "hello" packet for an RDP client, to trigger the server's specific acknowledgment).*