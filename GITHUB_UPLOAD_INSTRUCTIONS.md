# Quick Upload Guide for GitHub Web Interface

## Your GitHub Repository
https://github.com/naveenpahal31/MLOPS_Assignments_1

## Files to Upload

Follow these steps to upload the Phase 7 files directly through GitHub:

### Step 1: Upload Dockerfile (Root Directory)

1. Go to: https://github.com/naveenpahal31/MLOPS_Assignments_1
2. Click "Add file" → "Upload files"
3. Drag and drop or select: `Dockerfile`
4. Commit message: "Add Dockerfile for Phase 7"
5. Click "Commit changes"

### Step 2: Upload .dockerignore (Root Directory)

1. Click "Add file" → "Upload files"
2. Upload: `.dockerignore`
3. Commit message: "Add .dockerignore"
4. Click "Commit changes"

### Step 3: Create GitHub Actions Workflow

1. Click "Add file" → "Create new file"
2. Name: `.github/workflows/docker-build.yml`
3. Copy and paste this content:

```yaml
name: Build and Push Docker Image to Docker Hub

on:
  push:
    branches: [ main, master ]
    paths:
      - 'src/**'
      - 'models/**'
      - 'Dockerfile'
      - 'requirements.txt'
  workflow_dispatch:

env:
  DOCKER_USERNAME: 2024aa05871
  IMAGE_NAME: heart-disease-api

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ env.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_HUB_TOKEN }}

      - name: Extract metadata for Docker
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.DOCKER_USERNAME }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push Docker image
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64

      - name: Image digest
        run: echo ${{ steps.meta.outputs.digest }}

      - name: Update deployment status
        run: |
          echo "✅ Docker image built and pushed successfully!"
          echo "Image: ${{ env.DOCKER_USERNAME }}/${{ env.IMAGE_NAME }}:latest"
          echo "Digest: ${{ steps.meta.outputs.digest }}"
```

4. Commit message: "Add GitHub Actions workflow for Docker build"
5. Click "Commit changes"

### Step 4: Create k8s Directory and Files

**4a. Create deployment.yaml:**
1. Click "Add file" → "Create new file"
2. Name: `k8s/deployment.yaml`
3. Copy content from your local `k8s/deployment.yaml` file
4. Commit message: "Add Kubernetes deployment manifest"
5. Click "Commit changes"

**4b. Create service.yaml:**
1. Click "Add file" → "Create new file"
2. Name: `k8s/service.yaml`
3. Copy content from your local `k8s/service.yaml` file
4. Commit message: "Add Kubernetes service manifest"
5. Click "Commit changes"

### Step 5: Upload Documentation Files

1. Navigate to the `docs` folder in your repository
2. Click "Add file" → "Upload files"
3. Upload these files from your local `docs/` directory:
   - `PHASE7_PRODUCTION_DEPLOYMENT.md`
   - `PHASE7_QUICKSTART.md`
   - `DOCKER_SETUP_AND_LOGIN.md`
   - `STEP3_PUSH_TO_GITHUB.md`
4. Commit message: "Add Phase 7 documentation"
5. Click "Commit changes"

### Step 6: Upload Deployment Scripts

1. Navigate to the `scripts` folder
2. Click "Add file" → "Upload files"
3. Upload these files from your local `scripts/` directory:
   - `deploy_k8s.sh`
   - `deploy_k8s.ps1`
4. Commit message: "Add Kubernetes deployment scripts"
5. Click "Commit changes"

## Verify GitHub Actions

After uploading the workflow file (`.github/workflows/docker-build.yml`):

1. Go to: https://github.com/naveenpahal31/MLOPS_Assignments_1/actions
2. You should see "Build and Push Docker Image to Docker Hub" workflow
3. Click on it to see the build progress
4. Wait for it to complete (5-10 minutes)

## Check Docker Hub

Once the workflow completes successfully:

1. Go to: https://hub.docker.com/r/2024aa05871/heart-disease-api
2. You should see your image with tag "latest"
3. This means your API is ready to deploy to Kubernetes!

## Alternative: Manual Trigger Workflow

If the workflow doesn't auto-trigger:

1. Go to: https://github.com/naveenpahal31/MLOPS_Assignments_1/actions
2. Click on "Build and Push Docker Image to Docker Hub"
3. Click "Run workflow" button
4. Select branch: main (or master)
5. Click "Run workflow"

## Next Steps

Once your Docker image is on Docker Hub, proceed to:
- `docs/PHASE7_QUICKSTART.md` for deployment instructions
- Choose your Kubernetes platform (GKE, Minikube, or Play with Kubernetes)
- Deploy and test your API

---

## File Locations Reference

Your local files are at:
```
C:\Users\navpahal\OneDrive - Keysight Technologies\Desktop\Gemini PCN Delivery File\Personel Doc\WILP\Semester3\MLops\Assignments\MLOps-Assignment-1-main\
```

New files to upload:
- `Dockerfile`
- `.dockerignore`
- `.github/workflows/docker-build.yml`
- `k8s/deployment.yaml`
- `k8s/service.yaml`
- `docs/PHASE7_*.md` files
- `scripts/deploy_k8s.*` files
