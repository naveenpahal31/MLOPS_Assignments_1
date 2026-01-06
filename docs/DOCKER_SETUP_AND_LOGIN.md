# Docker Installation and Setup Guide for Windows

## Step 1: Install Docker Desktop

1. **Download Docker Desktop**:
   - Go to: https://www.docker.com/products/docker-desktop/
   - Click "Download for Windows"
   - Or direct link: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe

2. **Install**:
   - Run the installer
   - Follow the installation wizard
   - Enable WSL 2 if prompted (recommended)
   - Restart your computer when installation completes

3. **Verify Installation**:
   ```powershell
   docker --version
   docker info
   ```

## Step 2: Connect to Your Docker Hub Account

Once Docker Desktop is installed, login with your credentials:

```powershell
# Login to Docker Hub
docker login -u 2024aa05871

# You'll be prompted to enter your password
# After successful login, you'll see: "Login Succeeded"
```

## Step 3: Build and Push Your Image

```powershell
# Navigate to your project directory
cd 'c:\Users\navpahal\OneDrive - Keysight Technologies\Desktop\Gemini PCN Delivery File\Personel Doc\WILP\Semester3\MLops\Assignments\MLOps-Assignment-1-main'

# Build the Docker image
docker build -t 2024aa05871/heart-disease-api:latest .

# Push to Docker Hub
docker push 2024aa05871/heart-disease-api:latest

# Verify the push
docker images
```

## Step 4: Run Locally (Optional)

```powershell
# Run the container
docker run -d -p 8000:8000 --name heart-disease-api 2024aa05871/heart-disease-api:latest

# Test the API
curl http://localhost:8000/health

# View logs
docker logs heart-disease-api

# Stop and remove
docker stop heart-disease-api
docker rm heart-disease-api
```

---

## Alternative: Use Docker Hub Web Interface

If you don't want to install Docker Desktop, you can use **Automated Builds** on Docker Hub:

1. **Link GitHub to Docker Hub**:
   - Go to: https://hub.docker.com/
   - Login with username: `2024aa05871`
   - Go to: Account Settings → Linked Accounts
   - Link your GitHub account

2. **Create Automated Build**:
   - Repositories → Create Repository
   - Name: `heart-disease-api`
   - Link to GitHub repository
   - Enable automated builds from main/master branch

This way, Docker Hub will automatically build your image when you push to GitHub!

---

## Troubleshooting Docker Desktop

### WSL 2 Backend Error
```powershell
# Enable WSL 2
wsl --install

# Set WSL 2 as default
wsl --set-default-version 2
```

### Docker Daemon Not Running
- Open Docker Desktop application
- Wait for it to fully start (whale icon in system tray should be steady)

### Permission Issues
- Run PowerShell as Administrator
- Or add your user to the "docker-users" group

---

## Next Steps After Docker Hub Login

Once your image is on Docker Hub (either by pushing locally or automated builds), you can deploy to Kubernetes as described in the deployment guides.
