# Building and Publishing to Docker Hub

This guide explains how to build and push the Home Assistant add-on to Docker Hub.

## Prerequisites

1. **Docker installed** and running
2. **Docker Hub account** (username: `georghenzler` based on config.yaml)
3. **Docker Hub login**:
   ```bash
   docker login
   ```

## Method 1: Using the Build Script (Recommended)

The easiest way is to use the provided `build.sh` script:

```bash
# Build and push for current version (from config.yaml)
./build.sh

# Or specify a version
./build.sh 2.4
```

This script will:
- Build Docker images for all architectures (amd64, aarch64, armv7, armhf, i386)
- Tag them with both the version and `latest`
- Push all images to Docker Hub

## Method 2: Manual Build

If you prefer to build manually or need more control:

### Build for a specific architecture

```bash
# Set variables
ARCH="amd64"
VERSION="2.4"
BASE_IMAGE="ghcr.io/home-assistant/amd64-base:3.18"
IMAGE_NAME="georghenzler/addon-homeassistant-samsung-frame-art-${ARCH}"

# Build
docker build \
  --build-arg BUILD_FROM="${BASE_IMAGE}" \
  --platform linux/${ARCH} \
  -t "${IMAGE_NAME}:${VERSION}" \
  -t "${IMAGE_NAME}:latest" \
  .

# Push
docker push "${IMAGE_NAME}:${VERSION}"
docker push "${IMAGE_NAME}:latest"
```

### Build for all architectures

Repeat the above for each architecture:
- `amd64` → `ghcr.io/home-assistant/amd64-base:3.18`
- `aarch64` → `ghcr.io/home-assistant/aarch64-base:3.18`
- `armv7` → `ghcr.io/home-assistant/armv7-base:3.18`
- `armhf` → `ghcr.io/home-assistant/armhf-base:3.18`
- `i386` → `ghcr.io/home-assistant/i386-base:3.18`

## Method 3: Using Docker Buildx (Multi-arch in one command)

For advanced users, you can use Docker Buildx to build all architectures at once:

```bash
# Create a buildx builder (if not exists)
docker buildx create --name multiarch --use

# Build and push all architectures
docker buildx build \
  --platform linux/amd64,linux/aarch64,linux/arm/v7,linux/arm/v6,linux/386 \
  --build-arg BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.18 \
  -t georghenzler/addon-homeassistant-samsung-frame-art-amd64:2.4 \
  -t georghenzler/addon-homeassistant-samsung-frame-art-amd64:latest \
  --push \
  .
```

**Note:** Buildx requires careful handling of the `BUILD_FROM` argument per architecture, so Method 1 or 2 is recommended.

## Image Naming Convention

The images follow this pattern (as defined in `config.yaml`):
```
georghenzler/{arch}-addon-homeassistant-samsung-frame-art:{version}
```

Where:
- `{arch}` is one of: `amd64`, `aarch64`, `armv7`, `armhf`, `i386`
- `{version}` matches the version in `config.yaml`

## Verifying the Push

After pushing, verify on Docker Hub:
- https://hub.docker.com/r/georghenzler/addon-homeassistant-samsung-frame-art-amd64
- https://hub.docker.com/r/georghenzler/addon-homeassistant-samsung-frame-art-aarch64
- etc.

## Updating the Version

1. Update the `version:` field in `config.yaml`
2. Run `./build.sh` (it will automatically use the new version)
3. Or specify the version: `./build.sh 2.5`

## Troubleshooting

### "Cannot connect to Docker daemon"
- Make sure Docker is running: `docker info`

### "unauthorized: authentication required"
- Login to Docker Hub: `docker login`

### "platform linux/arm/v7 is not supported"
- Some architectures may not be buildable on your machine
- Use the build script which handles this gracefully
- Or use Docker Buildx with QEMU emulation

### Build fails for specific architecture
- Check if the base image exists: `docker pull ghcr.io/home-assistant/{arch}-base:3.18`
- Some architectures may require emulation (use Docker Buildx)

