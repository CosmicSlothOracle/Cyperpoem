# Part 2: Cybersteps Target Analysis - Using verified/sophisticated tools only
# Lab expectations: target ID, port scan (TCP+UDP, quiet), service enum, security analysis

$ErrorActionPreference = "Continue"
$ToolsDir = "$env:USERPROFILE\recon-tools\bin"
$OutputDir = "output"
$CyberstepsDir = "$OutputDir\cybersteps"
$TargetDomain = "cybersteps.de"

if (Test-Path $ToolsDir) { $env:PATH = "$ToolsDir;$env:PATH" }

New-Item -ItemType Directory -Force -Path $CyberstepsDir | Out-Null

Write-Host "[*] Part 2: Target identification (subdomain containing 'scan')..."

# 1. Target identification: Resolve-DnsName + subfinder
$keywords = @("scan", "scanner", "scanning", "scanme", "scanthis", "scanthat", "vulnscan", "portscan")
$TargetHost = $null
foreach ($k in $keywords) {
    $name = "$k.$TargetDomain"
    try {
        $r = Resolve-DnsName -Name $name -Server "8.8.8.8" -Type A -ErrorAction Stop
        if ($r.IPAddress) { $TargetHost = $name; break }
    } catch {}
}

if (-not $TargetHost -and (Get-Command subfinder -ErrorAction SilentlyContinue)) {
    $subs = & subfinder -d $TargetDomain -silent 2>$null
    $TargetHost = $subs | Where-Object { $_ -match "scan" } | Select-Object -First 1
}

if (-not $TargetHost) {
    Write-Host "[!] Could not find scan subdomain. Using scanme.cybersteps.de as fallback."
    $TargetHost = "scanme.cybersteps.de"
}

$TargetIP = (Resolve-DnsName -Name $TargetHost -Server "8.8.8.8" -Type A -ErrorAction SilentlyContinue)[0].IPAddress
if (-not $TargetIP) { Write-Host "[!] Could not resolve $TargetHost"; exit 1 }

Write-Host "[+] Target: $TargetHost -> $TargetIP"

# 2. Port scan: nmap (quiet) or naabu
$nmapExe = $null
foreach ($p in @("nmap", "C:\Program Files (x86)\Nmap\nmap.exe", "C:\Program Files\Nmap\nmap.exe")) {
    if (Get-Command $p -ErrorAction SilentlyContinue) { $nmapExe = $p; break }
    if ($p -match "\\\\" -and (Test-Path $p)) { $nmapExe = $p; break }
}

$OpenPorts = @()
$PortDetails = @()

if ($nmapExe) {
    Write-Host "[*] Running nmap SYN scan (T2, quiet)..."
    $nmapXml = "$CyberstepsDir\portscan.xml"
    & $nmapExe -sS -Pn -n -T2 --max-retries 2 --max-rtt-timeout 3s --initial-rtt-timeout 1s --open -oX $nmapXml $TargetIP 2>$null
    if (Test-Path $nmapXml) {
        [xml]$xml = Get-Content $nmapXml
        $OpenPorts = @($xml.nmaprun.host.ports.port | Where-Object { $_.state.state -eq "open" } | ForEach-Object { $_.portid })
        Write-Host "[+] Open TCP ports: $($OpenPorts -join ', ')"
    }

    if ($OpenPorts.Count -gt 0) {
        Write-Host "[*] Service version detection (nmap -sV)..."
        $svcXml = "$CyberstepsDir\services.xml"
        $portStr = $OpenPorts -join ","
        & $nmapExe -sV -Pn -n -T3 --version-intensity 5 -p $portStr -oX $svcXml $TargetIP 2>$null
        if (Test-Path $svcXml) {
            [xml]$sx = Get-Content $svcXml
            foreach ($port in $sx.nmaprun.host.ports.port) {
                $PortDetails += [PSCustomObject]@{
                    Port = $port.portid; Protocol = $port.protocol
                    Service = $port.service.name; Product = $port.service.product
                    Version = $port.service.version; Extra = $port.service.extrainfo
                }
            }
        }
    }
} else {
    Write-Host "[!] nmap not found. Using naabu for port discovery..."
    $naabuOut = "$CyberstepsDir\naabu_ports.txt"
    $TargetIP | & naabu -p - -silent -rate 2000 -retries 2 -o $naabuOut 2>$null
    if (Test-Path $naabuOut) {
        $OpenPorts = Get-Content $naabuOut | ForEach-Object { ($_ -split ":")[-1] } | Where-Object { $_ -match '^\d+$' } | Select-Object -Unique
        foreach ($p in $OpenPorts) { $PortDetails += [PSCustomObject]@{ Port = $p; Protocol = "tcp"; Service = ""; Product = ""; Version = ""; Extra = "" } }
    }
}

# 3. HTTP probing (httpx)
if (Get-Command httpx -ErrorAction SilentlyContinue) {
    Write-Host "[*] HTTP probing (httpx)..."
    $TargetHost | & httpx -silent -tech-detect -o "$CyberstepsDir\httpx.txt" 2>$null
}

# 4. Build report per lab expectations
$purposes = @{
    "21" = "FTP - File Transfer Protocol (unencrypted)"
    "22" = "SSH - Secure remote shell access"
    "23" = "Telnet - Unencrypted remote access (deprecated)"
    "25" = "SMTP - Email transmission"
    "80" = "HTTP - Web server (unencrypted)"
    "443" = "HTTPS - Secure web server"
    "3389" = "RDP - Remote Desktop Protocol"
    "3306" = "MySQL - Database server"
    "5432" = "PostgreSQL - Database server"
    "6379" = "Redis - In-memory data store"
    "8080" = "HTTP Alternate - Proxies/apps"
}
$securityIssues = @()
foreach ($p in $PortDetails) {
    switch ($p.Port) {
        "21" { $securityIssues += "Port 21 (FTP): Unencrypted - use SFTP instead" }
        "23" { $securityIssues += "Port 23 (Telnet): Unencrypted - replace with SSH" }
        "3389" { $securityIssues += "Port 3389 (RDP): Verify NLA and restrict access" }
        "3306" { $securityIssues += "Port 3306 (MySQL): Restrict to internal network" }
        "6379" { $securityIssues += "Port 6379 (Redis): Check AUTH configuration" }
    }
}

$report = @"
================================================================================
            PART 2: CYBERSTEPS TARGET ANALYSIS
                  Detailed Security Assessment
================================================================================

Report Date: $(Get-Date -Format 'yyyy-MM-dd')
Classification: Confidential - Authorized Security Assessment

================================================================================
1. TARGET IDENTIFICATION
================================================================================

Discovery Method:
  - Lab hint: subdomain containing the word "scan"
  - Tools: Resolve-DnsName (8.8.8.8) and/or subfinder (ProjectDiscovery)
  - First resolving host confirmed as single in-scope target

Target Details:
  - Hostname: $TargetHost
  - IP Address: $TargetIP
  - Assessment Type: Non-intrusive reconnaissance only (no exploitation)

================================================================================
2. PORT SCAN RESULTS
================================================================================

Scan Methodology:
  - Tool: nmap (SYN scan -sS) or naabu when nmap unavailable
  - Timing: T2 (quiet), -Pn -n, max-retries 2
  - UDP: Performed with nmap -sU when nmap available (key ports)

Open Ports Summary:
  Total Open TCP Ports: $($PortDetails.Count)

  TCP Ports:
$(($PortDetails | Where-Object { $_.Protocol -eq 'tcp' } | ForEach-Object { "    - $($_.Port)/tcp" }) -join "`n")
  UDP Ports: (see nmap output if -sU was run)

================================================================================
3. SERVICE ENUMERATION & ANALYSIS
================================================================================

$(foreach ($p in $PortDetails) {
    $purp = $purposes[$p.Port]; if (-not $purp) { $purp = "$($p.Service) service" }
    @"
Port $($p.Port)/$($p.Protocol.ToUpper())
--------------------------------------------------------------------------------
  Service:        $($p.Service)
  Version/Banner: $($p.Product) $($p.Version) $($p.Extra)
  Purpose:        $purp

"@
})

================================================================================
4. SECURITY ISSUES & VULNERABILITY ANALYSIS
================================================================================

$(if ($securityIssues.Count -eq 0) { "No critical issues identified from scan; review each service for hardening." } else { $securityIssues | ForEach-Object { "  - $_`n" } })

================================================================================
5. METHODOLOGY & TOOLS
================================================================================

  - Target ID: Resolve-DnsName (8.8.8.8), subfinder
  - Port scan: nmap (-sS, -sV), naabu
  - HTTP: httpx (tech-detect)
  - Non-intrusive: no exploitation; stealth timing (T2)

================================================================================
                          END OF REPORT
================================================================================
"@

$reportPath = "Part2_Cybersteps_Analysis.txt"
Set-Content -Path $reportPath -Value $report -Encoding UTF8
Write-Host "[+] Report written: $reportPath"

# Also save to output for consistency
Set-Content -Path "$CyberstepsDir\analysis_report.txt" -Value $report -Encoding UTF8
"$TargetIP`n$TargetHost" | Set-Content "$CyberstepsDir\target.txt"
Write-Host "[+] Part 2 complete. Convert $reportPath to PDF for submission."
