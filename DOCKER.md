# Docker Deployment 🐳

This guide covers how to deploy `gitthread` using Docker Compose, optimized for managers like **Dockge** or standard CLI.

## Docker Compose Configuration

### Option A: Using the Pre-built Image (Fastest)
Use this if the package is public or you have logged in to `ghcr.io`.

```yaml
services:
  gitthread:
    image: ghcr.io/abduznik/gitthread:latest
    container_name: gitthread
    ports:
      - "8095:8095"
    environment:
      # Required for private repositories and higher rate limits
      - GITHUB_TOKEN=${GITHUB_TOKEN} 
    restart: unless-stopped
```

### Option B: Build from Source (Best for local/private use)
Use this if you encounter "authentication" or "could not read username" errors.

```yaml
services:
  gitthread:
    build: .
    container_name: gitthread
    ports:
      - "8095:8095"
    environment:
      - GITHUB_TOKEN=${GITHUB_TOKEN:-}
    restart: unless-stopped
```

## Deployment Steps

### Using Dockge
1. Click **Compose** to create a new stack.
2. Name it `gitthread`.
3. Paste the YAML provided above into the editor.
4. (Optional) Add your `GITHUB_TOKEN` in the **Environment Variables** section to avoid rate limits.
5. Click **Deploy**.

### Using Command Line
1. Save the snippet above into a file named `docker-compose.yml`.
2. Run the following command:
   ```bash
   docker-compose up -d
   ```

The application will be accessible at `http://<your-ip>:8095`.
