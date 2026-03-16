#!/usr/bin/env python3
import asyncio
import json


TARGET = "165.232.131.154"


async def probe_socks5():
    out = {"port": 1080, "protocol_check": "socks5", "matched": False, "raw_response_hex": ""}
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(TARGET, 1080), timeout=4)
        # SOCKS5 greeting: version 5, one method, no-auth
        writer.write(b"\x05\x01\x00")
        await writer.drain()
        data = await asyncio.wait_for(reader.read(8), timeout=3)
        writer.close()
        await writer.wait_closed()
        if data:
            out["raw_response_hex"] = data.hex()
            # Expected response starts with 0x05
            out["matched"] = data[0] == 0x05
    except Exception:
        pass
    return out


async def probe_rdp():
    out = {"port": 3389, "protocol_check": "rdp", "matched": False, "raw_response_hex": ""}
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(TARGET, 3389), timeout=4)
        # Minimal RDP negotiation request (TPKT + X.224 + RDP Negotiation Request)
        req = bytes.fromhex("030000130ee0000000000001000800000000")
        writer.write(req)
        await writer.drain()
        data = await asyncio.wait_for(reader.read(32), timeout=3)
        writer.close()
        await writer.wait_closed()
        if data:
            out["raw_response_hex"] = data.hex()
            # RDP typically responds with TPKT header starting 03 00
            out["matched"] = len(data) >= 2 and data[0] == 0x03 and data[1] == 0x00
    except Exception:
        pass
    return out


async def main():
    results = await asyncio.gather(probe_socks5(), probe_rdp())
    with open("output/cybersteps/evidence_protocol_probe.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    asyncio.run(main())
