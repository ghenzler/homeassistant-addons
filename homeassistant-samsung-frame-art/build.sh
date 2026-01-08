#!/bin/bash
# Build and push Home Assistant add-on to Docker Hub
# Usage: ./build.sh [version]
# Example: ./build.sh 2.4

set -e

VERSION=${1:-$(grep '^version:' config.yaml | awk '{print $2}')}
DOCKER_USERNAME="georghenzler"
IMAGE_BASE="${DOCKER_USERNAME}/{arch}-addon-homeassistant-samsung-frame-art"

echo "Building version: ${VERSION}"
echo "Image base: ${IMAGE_BASE}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running"
    exit 1
fi

# Check if logged into Docker Hub
if ! docker info | grep -q "Username"; then
    echo "Please login to Docker Hub first:"
    echo "  docker login"
    exit 1
fi

# Build for each architecture
ARCHITECTURES=("amd64" "aarch64" "armv7" "armhf" "i386")

for arch in "${ARCHITECTURES[@]}"; do
    echo ""
    echo "========================================="
    echo "Building for architecture: ${arch}"
    echo "========================================="
    
    # Get the base image from build.yaml
    BASE_IMAGE=$(grep "^  ${arch}:" build.yaml | awk '{print $2}')
    if [ -z "$BASE_IMAGE" ]; then
        echo "Warning: No base image found for ${arch} in build.yaml, skipping..."
        continue
    fi
    
    # Replace {arch} placeholder with actual architecture
    IMAGE_NAME=$(echo "${IMAGE_BASE}" | sed "s/{arch}/${arch}/")
    IMAGE_TAG="${IMAGE_NAME}:${VERSION}"
    IMAGE_LATEST="${IMAGE_NAME}:latest"
    
    echo "Base image: ${BASE_IMAGE}"
    echo "Building: ${IMAGE_TAG}"
    
    # Build the image
    docker build \
        --build-arg BUILD_FROM="${BASE_IMAGE}" \
        --platform linux/${arch} \
        -t "${IMAGE_TAG}" \
        -t "${IMAGE_LATEST}" \
        .
    
    echo "Pushing ${IMAGE_TAG}..."
    docker push "${IMAGE_TAG}"
    docker push "${IMAGE_LATEST}"
    
    echo "✓ Successfully built and pushed ${arch}"
done

echo ""
echo "========================================="
echo "Build complete!"
echo "========================================="
echo "All images pushed to Docker Hub:"
for arch in "${ARCHITECTURES[@]}"; do
    IMAGE_NAME=$(echo "${IMAGE_BASE}" | sed "s/{arch}/${arch}/")
    echo "  - ${IMAGE_NAME}:${VERSION}"
    echo "  - ${IMAGE_NAME}:latest"
done

