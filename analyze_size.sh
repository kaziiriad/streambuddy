#!/bin/bash

# Script to analyze Docker image sizes and find what's taking space

echo "=== Docker Image Sizes ==="
docker images | grep -E "(streambuddy|python)"

echo -e "\n=== Layer Analysis ==="
# Replace 'your-image-name' with your actual image name
IMAGE_NAME="streambuddy-web"  # Change this to your image name

if docker image inspect $IMAGE_NAME &> /dev/null; then
    echo "Analyzing layers for $IMAGE_NAME..."
    docker history $IMAGE_NAME --format "table {{.CreatedBy}}\t{{.Size}}"
else
    echo "Image $IMAGE_NAME not found. Available images:"
    docker images
fi

echo -e "\n=== Container Analysis ==="
# Run container and analyze what's taking space
if docker image inspect $IMAGE_NAME &> /dev/null; then
    echo "Running size analysis inside container..."
    docker run --rm $IMAGE_NAME sh -c "
        echo '=== Root directory sizes ==='
        du -sh /* 2>/dev/null | sort -hr
        echo -e '\n=== Python packages taking most space ==='
        if [ -d /root/.local/lib/python3.12/site-packages ]; then
            du -sh /root/.local/lib/python3.12/site-packages/* 2>/dev/null | sort -hr | head -10
        fi
        echo -e '\n=== App directory size ==='
        du -sh /app/* 2>/dev/null | sort -hr
        echo -e '\n=== Total container size breakdown ==='
        df -h
    "
fi

echo -e "\n=== Requirements.txt Analysis ==="
if [ -f requirements.txt ]; then
    echo "Analyzing requirements.txt for heavy packages..."
    echo "Common heavy packages to watch for:"
    grep -E "(numpy|scipy|pandas|tensorflow|torch|opencv|pillow|matplotlib|jupyter)" requirements.txt || echo "No obviously heavy packages found"
fi

echo -e "\n=== Suggestions ==="
echo "1. Check if you have development/testing packages in requirements.txt"
echo "2. Consider using requirements-prod.txt for production"
echo "3. Large packages often include: numpy, scipy, pandas, ML libraries, image processing"
echo "4. Check for duplicate installations between system and pip packages"