#!/usr/bin/env powershell
# Professional Reconnaissance Tools Installation Script
# Downloads and installs the best open-source reconnaissance tools

param(
    [string]$InstallPath = "$env:USERPROFILE\recon-tools",
    [switch]$AddToPath = $true
)

$ErrorActionPreference = "Stop"

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  Installing Professional Reconnaissance Tools" -ForegroundColor Cyan
Write-Host "  Standing on the shoulders of giants" -ForegroundColor DarkGray
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

# Create installation directory
New-Item -ItemType Directory -Force -Path $InstallPath | Out-Null
$binPath = Join-Path $InstallPath "bin"
New-Item -ItemType Directory -Force -Path $binPath | Out-Null

Write-Host "[*] Installation directory: $InstallPath" -ForegroundColor Yellow
Write-Host ""

# Function to download and extract
function Install-FromGitHub {
    param(
        [string]$ToolName,
        [string]$Repo,
        [string]$Pattern,
        [switch]$IsZip = $false
    )

    Write-Host "[*] Installing $ToolName..." -ForegroundColor Yellow

    try {
        # Get latest release
        $release = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases/latest" -TimeoutSec 30
        $asset = $release.assets | Where-Object { $_.name -match $Pattern } | Select-Object -First 1

        if (-not $asset) {
            Write-Host "  [!] Could not find matching asset for $ToolName" -ForegroundColor Red
            return $false
        }

        $downloadUrl = $asset.browser_download_url
        $outputFile = Join-Path $binPath $asset.name

        # Download
        Write-Host "  [+] Downloading from $downloadUrl" -ForegroundColor DarkGray
        Invoke-WebRequest -Uri $downloadUrl -OutFile $outputFile -TimeoutSec 120

        # Extract if zip
        if ($IsZip -or $asset.name.EndsWith('.zip')) {
            Expand-Archive -Path $outputFile -DestinationPath $binPath -Force
            Remove-Item $outputFile -Force
        }

        Write-Host "  [+] $ToolName installed successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "  [!] Failed to install ${ToolName}: $_" -ForegroundColor Red
        return $false
    }
}

# Tools to install
$tools = @(
    # ProjectDiscovery Tools
    @{ Name = "subfinder"; Repo = "projectdiscovery/subfinder"; Pattern = "windows_amd64\.zip$"; Zip = $true },
    @{ Name = "dnsx"; Repo = "projectdiscovery/dnsx"; Pattern = "windows_amd64\.zip$"; Zip = $true },
    @{ Name = "naabu"; Repo = "projectdiscovery/naabu"; Pattern = "windows_amd64\.zip$"; Zip = $true },
    @{ Name = "httpx"; Repo = "projectdiscovery/httpx"; Pattern = "windows_amd64\.zip$"; Zip = $true },
    @{ Name = "nuclei"; Repo = "projectdiscovery/nuclei"; Pattern = "windows_amd64\.zip$"; Zip = $true },

    # Other reconnaissance tools
    @{ Name = "findomain"; Repo = "Findomain/Findomain"; Pattern = "windows-amd64\.exe\.zip$"; Zip = $true },
    @{ Name = "assetfinder"; Repo = "tomnomnom/assetfinder"; Pattern = "windows-amd64-[0-9\.]+\.zip$"; Zip = $true },
    @{ Name = "shuffledns"; Repo = "projectdiscovery/shuffledns"; Pattern = "windows_amd64\.zip$"; Zip = $true }
)

$installed = @()
$failed = @()

foreach ($tool in $tools) {
    $result = Install-FromGitHub -ToolName $tool.Name -Repo $tool.Repo -Pattern $tool.Pattern -IsZip:$tool.Zip
    if ($result) {
        $installed += $tool.Name
    } else {
        $failed += $tool.Name
    }
}

# Special handling for amass (requires Go or different approach)
Write-Host ""
Write-Host "[*] Installing amass (OWASP)..." -ForegroundColor Yellow
Write-Host "  [!] amass requires manual installation or Go build" -ForegroundColor DarkYellow
Write-Host "  [+] Instructions:" -ForegroundColor Cyan
Write-Host "      1. Install Go from https://golang.org/dl/" -ForegroundColor White
Write-Host "      2. Run: go install -v github.com/owasp-amass/amass/v4/...@master" -ForegroundColor White
Write-Host "      3. Or download from: https://github.com/owasp-amass/amass/releases" -ForegroundColor White

# Check for nmap
Write-Host ""
Write-Host "[*] Checking for nmap..." -ForegroundColor Yellow
$nmap = Get-Command nmap -ErrorAction SilentlyContinue
if ($nmap) {
    Write-Host "  [+] nmap found: $($nmap.Source)" -ForegroundColor Green
} else {
    Write-Host "  [!] nmap not found" -ForegroundColor Red
    Write-Host "  [+] Download from: https://nmap.org/download.html" -ForegroundColor Cyan
    Write-Host "  [+] Or install via chocolatey: choco install nmap" -ForegroundColor Cyan
}

# Add to PATH
if ($AddToPath) {
    Write-Host ""
    Write-Host "[*] Adding to PATH..." -ForegroundColor Yellow

    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($currentPath -notlike "*$binPath*") {
        [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$binPath", "User")
        Write-Host "  [+] Added to user PATH" -ForegroundColor Green
        Write-Host "  [!] Restart your terminal to use the tools" -ForegroundColor DarkYellow
    } else {
        Write-Host "  [+] Already in PATH" -ForegroundColor Green
    }
}

# Create wrapper script
$wrapperPath = Join-Path $InstallPath "recon-env.ps1"
@"
# Reconnaissance Environment Setup
`$env:PATH = "$binPath;`$env:PATH"
Write-Host "Reconnaissance tools loaded from $binPath" -ForegroundColor Green
Write-Host "Available tools:" -ForegroundColor Cyan

Get-ChildItem "$binPath" -Filter "*.exe" | ForEach-Object {
    Write-Host "  - `$(`$_.Name)" -ForegroundColor White
}
"@ | Out-File -FilePath $wrapperPath -Encoding UTF8

Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "Installation Summary" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "Installed ($($installed.Count)): $($installed -join ', ')" -ForegroundColor Green
if ($failed.Count -gt 0) {
    Write-Host "Failed ($($failed.Count)): $($failed -join ', ')" -ForegroundColor Red
}
Write-Host ""
Write-Host "Location: $InstallPath" -ForegroundColor Yellow
Write-Host "Binaries: $binPath" -ForegroundColor Yellow
Write-Host "Wrapper: $wrapperPath" -ForegroundColor Yellow
Write-Host ""
Write-Host "To use the tools:" -ForegroundColor Cyan
Write-Host "  1. Restart your terminal, OR" -ForegroundColor White
Write-Host "  2. Run: & '$wrapperPath'" -ForegroundColor White
Write-Host ""

# List available tools
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "Tool Descriptions" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

$descriptions = @{
    "subfinder" = "Passive subdomain discovery from multiple sources"
    "dnsx" = "Fast DNS resolver with wildcard filtering"
    "naabu" = "Fast port scanner with SYN/CONNECT support"
    "httpx" = "Fast HTTP prober with technology detection"
    "nuclei" = "Vulnerability scanner based on templates"
    "findomain" = "Cross-platform subdomain enumerator"
    "assetfinder" = "Find domains and subdomains related to target"
    "shuffledns" = "MassDNS wrapper with wildcard filtering"
}

foreach ($tool in $installed) {
    $desc = $descriptions[$tool]
    Write-Host "$tool" -ForegroundColor Green -NoNewline
    Write-Host ": $desc" -ForegroundColor White
}

Write-Host ""
Write-Host "[+] Installation complete!" -ForegroundColor Green
