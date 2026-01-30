# Docker Deployment 🐳

This guide covers how to deploy `gitthread` using Docker Compose, optimized for managers like **Dockge** or standard CLI.

## Docker Compose Configuration

Copy and paste the following into your `docker-compose.yml` or your Dockge stack configuration:

```yaml
services:
  gitthread:
    image: ghcr.io/abduznik/gitthread:latest
    build: 
      context: https://github.com/abduznik/gitthread.git#main
      dockerfile: Dockerfile
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
