# Linux Recon Commands (Part 2, Compact)

Use this exact flow to reproduce the evidence style from your analysis on Linux.
Replace `TARGET_IP`/`TARGET_DOMAIN` as needed.

`TARGET_IP=165.232.131.154`
`TARGET_DOMAIN=scanme.cybersteps.de`

## 1) DNS validation
```bash
dig @8.8.8.8 "$TARGET_DOMAIN" A +noall +answer
```
Flags: `@8.8.8.8` use Google resolver, `A` query IPv4, `+noall +answer` minimal output.

## 2) Passive subdomain enum
```bash
subfinder -d cybersteps.de -silent
```
Flags: `-d` domain, `-silent` only results (clean for pipelines/logging).

## 3) Full TCP port discovery
```bash
echo "$TARGET_IP" | naabu -p - -silent -rate 2000 -retries 2
```
Flags: `-p -` all 65535 ports, `-silent` compact output, `-rate` packets/sec cap, `-retries` retry budget.

## 4) Service fingerprinting on confirmed TCP ports
```bash
nmap -sV -Pn -n -T3 --version-intensity 7 -p 21,22,80,1080,3389 "$TARGET_IP"
```
Flags: `-sV` service/version detect, `-Pn` skip host discovery, `-n` no DNS reverse lookup, `-T3` moderate timing, `--version-intensity 7` deeper probes, `-p` fixed port set.

## 5) SOCKS/proxy-focused NSE check (1080)
```bash
nmap -Pn -n -p 1080 --script=socks-auth-info,socks-open-proxy,banner --script-timeout 15s "$TARGET_IP"
```
Flags: `--script` run NSE scripts, `--script-timeout 15s` cap script runtime.

## 6) Focused UDP validation
```bash
nmap -sU -Pn -n -T3 --max-retries 1 --reason -p 53,67,68,69,123,137,138,161,162,500,514,520 "$TARGET_IP"
```
Flags: `-sU` UDP scan, `--max-retries 1` reduce ambiguous re-probing, `--reason` include state reason (e.g. `port-unreach`, `no-response`).

## 7) UDP top-ports corroboration
```bash
nmap -sU -Pn -n --top-ports 200 "$TARGET_IP"
```
Flags: `--top-ports 200` scan most common UDP ports only.

## 8) HTTP metadata/tech fingerprint
```bash
echo "$TARGET_DOMAIN" | httpx -silent -status-code -title -tech-detect
```
Flags: `-silent` clean output, `-status-code` HTTP code, `-title` page title, `-tech-detect` stack hints.

## 9) Raw banner probe (custom)
```bash
python3 output/cybersteps/banner_probe.py
```
Purpose: direct banner capture without scanner interpretation layer.

## 10) Protocol handshake probe (custom)
```bash
python3 output/cybersteps/protocol_probe.py
```
Purpose: protocol-native checks (e.g., SOCKS greeting, RDP handshake) for identity confirmation.

## 11) TTL on port-state reason (quick check)
```bash
nmap -Pn -n --reason -p 3389 "$TARGET_IP"
```
Flags: `--reason` prints why port is marked open/closed and may include reply TTL.

## Evidence-friendly output variants (same commands + files)
```bash
nmap -sV -Pn -n -T3 --version-intensity 7 -p 21,22,80,1080,3389 "$TARGET_IP" -oX output/cybersteps/nmap_tcp_full.xml
nmap -sU -Pn -n -T3 --max-retries 1 --reason -p 53,67,68,69,123,137,138,161,162,500,514,520 "$TARGET_IP" -oX output/cybersteps/nmap_udp_focused_reason.xml
echo "$TARGET_IP" | naabu -p - -silent -rate 2000 -retries 2 | tee output/cybersteps/evidence_naabu_full_tcp.txt
echo "$TARGET_DOMAIN" | httpx -silent -status-code -title -tech-detect | tee output/cybersteps/evidence_httpx.txt
```
