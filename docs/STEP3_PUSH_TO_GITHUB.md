# Step 3: Push Code to GitHub - Complete Guide

## Option A: Install Git and Push from Desktop (Recommended)

### 1. Install Git for Windows

**Download and Install:**
- Go to: https://git-scm.com/download/win
- Download "64-bit Git for Windows Setup"
- Run the installer with default settings
- Restart PowerShell after installation

**Verify Installation:**
```powershell
git --version
```

### 2. Configure Git (First Time Only)

```powershell
# Set your name and email
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. Initialize and Push to GitHub

```powershell
# Navigate to your project directory
cd 'c:\Users\navpahal\OneDrive - Keysight Technologies\Desktop\Gemini PCN Delivery File\Personel Doc\WILP\Semester3\MLops\Assignments\MLOps-Assignment-1-main'

# Check if git is already initialized
git status

# If not initialized, initialize git repository
git init

# Add all new files
git add .

# Commit the changes
git commit -m "Add Phase 7 production deployment configuration"

# Add your GitHub repository as remote (replace with your actual repo URL)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Or if remote already exists, verify it:
git remote -v

# Push to GitHub (this will trigger GitHub Actions)
git push -u origin main

# If you're on 'master' branch instead of 'main':
git push -u origin master
```

### 4. Monitor GitHub Actions Build

1. Go to your GitHub repository in a browser
2. Click on the "Actions" tab
3. You should see the "Build and Push Docker Image" workflow running
4. Click on it to see the progress
5. Wait for it to complete (usually 5-10 minutes)

### 5. Verify Image on Docker Hub

1. Go to: https://hub.docker.com/r/2024aa05871/heart-disease-api
2. You should see your image with the "latest" tag
3. This confirms the build was successful!

---

## Option B: Upload Files via GitHub Web Interface (No Git Installation)

If you don't want to install Git, you can upload files directly through GitHub:

### 1. Go to Your GitHub Repository

Navigate to your repository on GitHub.com

### 2. Upload New Files

For each new file/directory we created:

**Upload these files one by one:**

1. **Dockerfile** (root directory)
   - Click "Add file" → "Upload files"
   - Upload the Dockerfile from your project root

2. **.dockerignore** (root directory)
   - Upload this file to project root

3. **k8s/** directory files:
   - Create folder: Click "Add file" → "Create new file"
   - Type: `k8s/deployment.yaml` (this creates the folder)
   - Copy content from your local `k8s/deployment.yaml`
   - Commit
   - Repeat for `k8s/service.yaml`

4. **.github/workflows/** directory:
   - Create: `.github/workflows/docker-build.yml`
   - Copy content from your local file
   - Commit

5. **docs/** directory files:
   - Upload: `PHASE7_PRODUCTION_DEPLOYMENT.md`
   - Upload: `PHASE7_QUICKSTART.md`
   - Upload: `DOCKER_SETUP_AND_LOGIN.md`

6. **scripts/** directory files:
   - Upload: `deploy_k8s.sh`
   - Upload: `deploy_k8s.ps1`

### 3. Commit Changes

After uploading all files, commit with message:
```
Add Phase 7 production deployment configuration
```

### 4. GitHub Actions Will Auto-Trigger

Once you commit the `.github/workflows/docker-build.yml` file, GitHub Actions will automatically start building your Docker image!

---

## Option C: Use GitHub Desktop (GUI Alternative)

### 1. Install GitHub Desktop

- Download from: https://desktop.github.com/
- Install and sign in with your GitHub account

### 2. Add Your Repository

- File → Add Local Repository
- Browse to your project folder
- Click "Add Repository"

### 3. Commit and Push

- Review changes in GitHub Desktop
- Add commit message: "Add Phase 7 production deployment configuration"
- Click "Commit to main"
- Click "Push origin"

---

## Troubleshooting

### Git Remote Already Exists Error

```powershell
# Remove existing remote
git remote remove origin

# Add correct remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

### Branch Name Issues

```powershell
# Check current branch
git branch

# Rename branch if needed
git branch -M main
```

### Authentication Issues

GitHub may require a Personal Access Token instead of password:

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` permissions
3. Use this token as password when pushing

### Large File Warning

If you see warnings about large files in the `models/` directory:

```powershell
# Add models to .gitignore if they're too large
echo "models/*.pkl" >> .gitignore
echo "models/*.joblib" >> .gitignore
git add .gitignore
git commit -m "Ignore large model files"
```

Note: You'll need to ensure models are in the Docker image or downloadable during deployment.

---

## Next Steps After Successful Push

1. ✅ Check GitHub Actions tab - workflow should be running
2. ✅ Wait for build to complete (5-10 minutes)
3. ✅ Verify image on Docker Hub: https://hub.docker.com/r/2024aa05871/heart-disease-api
4. ✅ Proceed to Kubernetes deployment using `PHASE7_QUICKSTART.md`

---

## Quick Command Reference

```powershell
# Navigate to project
cd 'c:\Users\navpahal\OneDrive - Keysight Technologies\Desktop\Gemini PCN Delivery File\Personel Doc\WILP\Semester3\MLops\Assignments\MLOps-Assignment-1-main'

# Add all files
git add .

# Commit
git commit -m "Add Phase 7 production deployment configuration"

# Push (triggers GitHub Actions)
git push -u origin main
```

That's it! Once pushed, GitHub Actions will automatically build and push your Docker image to `2024aa05871/heart-disease-api:latest` on Docker Hub.
