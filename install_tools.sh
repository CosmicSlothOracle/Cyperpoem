#!/bin/bash
#===============================================================================
# Professional Reconnaissance Tools Installation Script
# Linux/Mac Edition
#===============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="${HOME}/recon-tools"
BIN_DIR="${INSTALL_DIR}/bin"
GO_VERSION="1.21.5"

# Banner
echo -e "${CYAN}"
echo "================================================================================"
echo "  Installing Professional Reconnaissance Tools"
echo "  Linux/Mac Edition"
echo "================================================================================"
echo -e "${NC}"

# Create directories
mkdir -p "$BIN_DIR"
mkdir -p "$INSTALL_DIR/sources"

# Detect OS and architecture
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

case $ARCH in
    x86_64) ARCH="amd64" ;;
    aarch64|arm64) ARCH="arm64" ;;
    *) echo -e "${RED}Unsupported architecture: $ARCH${NC}"; exit 1 ;;
esac

echo -e "${YELLOW}[*] Detected: $OS/$ARCH${NC}"
echo -e "${YELLOW}[*] Install directory: $INSTALL_DIR${NC}"
echo ""

# Check for required tools
check_dependency() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}[✓]${NC} $1 found"
        return 0
    else
        echo -e "${RED}[✗]${NC} $1 not found"
        return 1
    fi
}

echo -e "${YELLOW}[*] Checking dependencies...${NC}"
check_dependency curl || MISSING=1
check_dependency unzip || MISSING=1
check_dependency tar || MISSING=1

if [ -n "$MISSING" ]; then
    echo -e "${RED}[!] Missing required tools. Please install them first.${NC}"
    exit 1
fi

# Function to install from GitHub releases
install_from_github() {
    local name=$1
    local repo=$2
    local pattern=$3

    echo -e "${YELLOW}[*] Installing $name...${NC}"

    # Get latest release
    local download_url
    download_url=$(curl -s "https://api.github.com/repos/$repo/releases/latest" | \
        grep -oP '"browser_download_url": "\K[^"]*' | \
        grep -E "$pattern" | head -1)

    if [ -z "$download_url" ]; then
        echo -e "${RED}[!] Could not find download for $name${NC}"
        return 1
    fi

    echo -e "${BLUE}[*]${NC} Downloading from: $download_url"

    local temp_file="${INSTALL_DIR}/sources/${name}_download"
    curl -L -o "$temp_file" "$download_url" --progress-bar

    # Extract based on file type
    if [[ "$download_url" == *.zip ]]; then
        unzip -q "$temp_file" -d "$BIN_DIR"
    elif [[ "$download_url" == *.tar.gz ]]; then
        tar -xzf "$temp_file" -C "$BIN_DIR"
    elif [[ "$download_url" == *.gz ]]; then
        local binary_name="${name}"
        gunzip -c "$temp_file" > "${BIN_DIR}/${binary_name}"
        chmod +x "${BIN_DIR}/${binary_name}"
    else
        # Assume it's the binary directly
        cp "$temp_file" "${BIN_DIR}/${name}"
        chmod +x "${BIN_DIR}/${name}"
    fi

    rm -f "$temp_file"
    echo -e "${GREEN}[✓]${NC} $name installed"
}

# Function to install Go if needed
install_go() {
    if command -v go &> /dev/null; then
        echo -e "${GREEN}[✓]${NC} Go found: $(go version)"
        return 0
    fi

    echo -e "${YELLOW}[*] Installing Go...${NC}"

    local go_tar="go${GO_VERSION}.${OS}-${ARCH}.tar.gz"
    local go_url="https://golang.org/dl/${go_tar}"

    curl -L -o "${INSTALL_DIR}/sources/${go_tar}" "$go_url" --progress-bar
    tar -xzf "${INSTALL_DIR}/sources/${go_tar}" -C "$INSTALL_DIR"

    # Add to PATH for this session
    export PATH="${INSTALL_DIR}/go/bin:${PATH}"
    export GOPATH="${INSTALL_DIR}/go"

    # Add to shell config for future sessions
    if [ -f "${HOME}/.bashrc" ]; then
        echo 'export PATH="'${INSTALL_DIR}'/go/bin:${PATH}"' >> "${HOME}/.bashrc"
        echo 'export GOPATH="'${INSTALL_DIR}'/go"' >> "${HOME}/.bashrc"
    fi
    if [ -f "${HOME}/.zshrc" ]; then
        echo 'export PATH="'${INSTALL_DIR}'/go/bin:${PATH}"' >> "${HOME}/.zshrc"
        echo 'export GOPATH="'${INSTALL_DIR}'/go"' >> "${HOME}/.zshrc"
    fi

    echo -e "${GREEN}[✓]${NC} Go installed"
}

# Install Go
install_go

# Install tools via Go
echo ""
echo -e "${CYAN}================================================================================${NC}"
echo -e "${CYAN}  Installing Go-based tools${NC}"
echo -e "${CYAN}================================================================================${NC}"

go_install() {
    local name=$1
    local pkg=$2

    echo -e "${YELLOW}[*] Installing $name...${NC}"
    if go install -v "$pkg" 2>/dev/null; then
        echo -e "${GREEN}[✓]${NC} $name installed"
    else
        echo -e "${RED}[!]${NC} Failed to install $name"
    fi
}

# ProjectDiscovery tools
go_install "subfinder" "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
go_install "dnsx" "github.com/projectdiscovery/dnsx/cmd/dnsx@latest"
go_install "naabu" "github.com/projectdiscovery/naabu/v2/cmd/naabu@latest"
go_install "httpx" "github.com/projectdiscovery/httpx/cmd/httpx@latest"
go_install "nuclei" "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
go_install "shuffledns" "github.com/projectdiscovery/shuffledns/cmd/shuffledns@latest"

# Tom Nomnom tools
go_install "assetfinder" "github.com/tomnomnom/assetfinder@latest"

# OWASP Amass
go_install "amass" "github.com/owasp-amass/amass/v4/...@master"

# Move Go binaries to bin directory
if [ -d "${HOME}/go/bin" ]; then
    mv "${HOME}/go/bin/"* "$BIN_DIR/" 2>/dev/null || true
fi

# Install binary releases
echo ""
echo -e "${CYAN}================================================================================${NC}"
echo -e "${CYAN}  Installing binary releases${NC}"
echo -e "${CYAN}================================================================================${NC}"

# Findomain (different repo structure)
echo -e "${YELLOW}[*] Installing findomain...${NC}"
if [ "$OS" = "linux" ]; then
    if [ "$ARCH" = "amd64" ]; then
        curl -sL "https://github.com/Findomain/Findomain/releases/latest/download/findomain-linux.zip" -o "${INSTALL_DIR}/sources/findomain.zip"
        unzip -q "${INSTALL_DIR}/sources/findomain.zip" -d "$BIN_DIR"
        chmod +x "${BIN_DIR}/findomain"
        echo -e "${GREEN}[✓]${NC} findomain installed"
    fi
elif [ "$OS" = "darwin" ]; then
    curl -sL "https://github.com/Findomain/Findomain/releases/latest/download/findomain-osx.zip" -o "${INSTALL_DIR}/sources/findomain.zip"
    unzip -q "${INSTALL_DIR}/sources/findomain.zip" -d "$BIN_DIR"
    chmod +x "${BIN_DIR}/findomain"
    echo -e "${GREEN}[✓]${NC} findomain installed"
fi

# Install massdns (for shuffledns)
if ! command -v massdns &> /dev/null; then
    echo -e "${YELLOW}[*] Installing massdns...${NC}"
    cd "${INSTALL_DIR}/sources"
    git clone https://github.com/blechschmidt/massdns.git 2>/dev/null || true
    if [ -d "massdns" ]; then
        cd massdns
        make -j$(nproc) 2>/dev/null || make
        cp bin/massdns "$BIN_DIR/"
        cd "$OLDPWD"
        echo -e "${GREEN}[✓]${NC} massdns installed"
    fi
fi

# Check for nmap
echo ""
echo -e "${CYAN}================================================================================${NC}"
echo -e "${CYAN}  Checking for nmap${NC}"
echo -e "${CYAN}================================================================================${NC}"

if command -v nmap &> /dev/null; then
    echo -e "${GREEN}[✓]${NC} nmap found: $(nmap --version | head -1)"
else
    echo -e "${YELLOW}[!]${NC} nmap not found"
    echo -e "${BLUE}[*]${NC} Install with:"
    if [ "$OS" = "linux" ]; then
        echo "  sudo apt-get install nmap  (Debian/Ubuntu)"
        echo "  sudo yum install nmap      (RHEL/CentOS)"
        echo "  sudo pacman -S nmap        (Arch)"
    elif [ "$OS" = "darwin" ]; then
        echo "  brew install nmap"
    fi
fi

# Update PATH
echo ""
echo -e "${CYAN}================================================================================${NC}"
echo -e "${CYAN}  Updating PATH${NC}"
echo -e "${CYAN}================================================================================${NC}"

# Add to current session
export PATH="${BIN_DIR}:${PATH}"

# Add to shell configs
SHELL_CONFIG=""
if [ -f "${HOME}/.bashrc" ]; then
    SHELL_CONFIG="${HOME}/.bashrc"
    if ! grep -q "$BIN_DIR" "${HOME}/.bashrc"; then
        echo 'export PATH="'${BIN_DIR}':${PATH}"' >> "${HOME}/.bashrc"
        echo -e "${GREEN}[✓]${NC} Added to .bashrc"
    fi
fi
if [ -f "${HOME}/.zshrc" ]; then
    SHELL_CONFIG="${HOME}/.zshrc"
    if ! grep -q "$BIN_DIR" "${HOME}/.zshrc"; then
        echo 'export PATH="'${BIN_DIR}':${PATH}"' >> "${HOME}/.zshrc"
        echo -e "${GREEN}[✓]${NC} Added to .zshrc"
    fi
fi

# Create activation script
cat > "${INSTALL_DIR}/activate" << EOF
#!/bin/bash
export PATH="${BIN_DIR}:\${PATH}"
export GOPATH="${INSTALL_DIR}/go"
echo "Reconnaissance tools activated from ${BIN_DIR}"
echo "Available tools:"
ls -1 ${BIN_DIR}
EOF
chmod +x "${INSTALL_DIR}/activate"

# Summary
echo ""
echo -e "${CYAN}================================================================================${NC}"
echo -e "${CYAN}  Installation Summary${NC}"
echo -e "${CYAN}================================================================================${NC}"

echo ""
echo -e "${GREEN}Installed tools:${NC}"
ls -1 "$BIN_DIR" 2>/dev/null | while read tool; do
    echo -e "  ${GREEN}✓${NC} $tool"
done

echo ""
echo -e "${YELLOW}Installation directory:${NC} $INSTALL_DIR"
echo -e "${YELLOW}Binary directory:${NC} $BIN_DIR"
echo -e "${YELLOW}Activation script:${NC} ${INSTALL_DIR}/activate"

echo ""
echo -e "${CYAN}Usage:${NC}"
echo -e "  ${BLUE}1.${NC} Restart your terminal, OR"
echo -e "  ${BLUE}2.${NC} Run: source ${INSTALL_DIR}/activate"
echo -e "  ${BLUE}3.${NC} Run: subfinder -version"

echo ""
echo -e "${CYAN}Tool Descriptions:${NC}"
TOOLS_INFO=(
    "amass:Comprehensive attack surface mapping"
    "subfinder:Passive subdomain discovery"
    "dnsx:High-performance DNS resolver"
    "naabu:Fast port scanner"
    "httpx:HTTP prober with tech detection"
    "nuclei:Vulnerability scanner"
    "findomain:Fast cross-platform enumerator"
    "assetfinder:Find related domains"
    "shuffledns:MassDNS with wildcard filtering"
)

for info in "${TOOLS_INFO[@]}"; do
    IFS=':' read -r name desc <<< "$info"
    if [ -f "${BIN_DIR}/${name}" ]; then
        printf "  ${GREEN}%-15s${NC} %s\n" "$name" "$desc"
    fi
done

echo ""
echo -e "${GREEN}[+] Installation complete!${NC}"
echo -e "${YELLOW}[!]${NC} Restart your terminal or run: source ${INSTALL_DIR}/activate"
