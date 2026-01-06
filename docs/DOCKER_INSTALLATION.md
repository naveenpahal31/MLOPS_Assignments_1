# Docker Installation Guide

This guide provides step-by-step instructions for installing Docker on different operating systems.

## Quick Check

First, check if Docker is already installed:

```bash
docker --version
```

If you see a version number, Docker is installed. Verify it's running:

```bash
docker info
```

If you see an error, follow the installation instructions below for your operating system.

## macOS

### Option 1: Docker Desktop (Recommended)

1. Download Docker Desktop from [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Open the downloaded `.dmg` file
3. Drag Docker to Applications folder
4. Open Docker from Applications
5. Follow the setup wizard
6. Docker Desktop will start automatically

### Option 2: Homebrew

```bash
brew install --cask docker
```

Then open Docker Desktop from Applications.

### Verify Installation

```bash
docker --version
docker info
```

## Linux (Ubuntu/Debian)

### Install Docker

```bash
# Update package index
sudo apt-get update

# Install required packages
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up the repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### Alternative: Install from Ubuntu Repository

```bash
sudo apt-get update
sudo apt-get install -y docker.io
```

### Start Docker Service

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### Add User to Docker Group (Optional)

To run Docker commands without `sudo`:

```bash
sudo usermod -aG docker $USER
```

**Important**: Log out and log back in (or restart) for this change to take effect.

### Verify Installation

```bash
docker --version
sudo docker info
# Or after adding to docker group:
docker info
```

## Linux (CentOS/RHEL/Fedora)

### Install Docker

For CentOS/RHEL 7:
```bash
sudo yum install -y docker
```

For CentOS/RHEL 8+ or Fedora:
```bash
sudo dnf install -y docker
```

### Start Docker Service

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### Add User to Docker Group (Optional)

```bash
sudo usermod -aG docker $USER
```

Log out and log back in for this change to take effect.

### Verify Installation

```bash
docker --version
sudo docker info
```

## Windows

### Install Docker Desktop

1. Download Docker Desktop from [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Run the installer (`Docker Desktop Installer.exe`)
3. Follow the installation wizard
4. Restart your computer if prompted
5. Open Docker Desktop from the Start menu
6. Wait for Docker to start (whale icon in system tray)

### System Requirements

- Windows 10 64-bit: Pro, Enterprise, or Education (Build 15063 or later)
- Windows 11 64-bit: Home or Pro version 21H2 or higher
- WSL 2 feature enabled
- Virtualization enabled in BIOS

### Verify Installation

Open PowerShell or Command Prompt:

```bash
docker --version
docker info
```

## Troubleshooting

### Docker daemon not running

**macOS/Windows**: Make sure Docker Desktop is running (check the system tray/status bar)

**Linux**: Start the Docker service:
```bash
sudo systemctl start docker
sudo systemctl status docker
```

### Permission denied errors (Linux)

If you see "permission denied" errors:

1. Add your user to the docker group:
   ```bash
   sudo usermod -aG docker $USER
   ```

2. Log out and log back in

3. Verify:
   ```bash
   groups
   ```
   You should see `docker` in the list

### Cannot connect to Docker daemon

**Linux**: Make sure Docker service is running:
```bash
sudo systemctl status docker
sudo systemctl start docker
```

**macOS/Windows**: Make sure Docker Desktop is running

### Test Docker Installation

Run a simple test to verify Docker is working:

```bash
docker run hello-world
```

You should see a message indicating Docker is working correctly.

## Next Steps

After installing Docker:

1. Verify installation: `docker --version`
2. Test Docker: `docker run hello-world`
3. Build the project image: `docker build -t heart-disease-api:latest .`
4. Run the container: `docker run -d -p 8000:8000 heart-disease-api:latest`

## Additional Resources

- [Docker Official Documentation](https://docs.docker.com/)
- [Docker Desktop Documentation](https://docs.docker.com/desktop/)
- [Docker Hub](https://hub.docker.com/)

