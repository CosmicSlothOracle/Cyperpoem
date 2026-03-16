#!/usr/bin/env python3
import asyncio
import json


TARGET = "165.232.131.154"
PORTS = [21, 22, 80, 1080, 3389]


async def probe(port: int):
    result = {"port": port, "open": False, "banner": ""}
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(TARGET, port), timeout=4)
        result["open"] = True
        probes = [b"", b"HEAD / HTTP/1.0\r\nHost: scanme.cybersteps.de\r\n\r\n", b"\r\n"]
        data = b""
        for p in probes:
            if p:
                writer.write(p)
                await writer.drain()
            try:
                chunk = await asyncio.wait_for(reader.read(1024), timeout=3)
            except Exception:
                chunk = b""
            if chunk:
                data = chunk
                break
        writer.close()
        await writer.wait_closed()
        if data:
            result["banner"] = data.decode("utf-8", errors="replace").strip()
    except Exception:
        pass
    return result


async def main():
    results = await asyncio.gather(*[probe(p) for p in PORTS])
    with open("output/cybersteps/evidence_banner_probe.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    asyncio.run(main())
