#!/bin/bash

echo "=== DEEP ANALYSIS OF LARGE CONTAINER ==="

# Replace with your actual image name
IMAGE_NAME="streambuddy-backend"

echo "1. Layer-by-layer analysis:"
docker history $IMAGE_NAME --format "table {{.CreatedBy}}\t{{.Size}}" --no-trunc

echo -e "\n2. Running detailed size analysis inside container..."
docker run --rm $IMAGE_NAME sh -c "
    echo '=== TOP LEVEL DIRECTORIES ==='
    du -sh /* 2>/dev/null | sort -hr | head -20
    
    echo -e '\n=== PYTHON SITE-PACKAGES BREAKDOWN ==='
    if [ -d /usr/local/lib/python3.12/site-packages ]; then
        echo 'Main site-packages:'
        du -sh /usr/local/lib/python3.12/site-packages/* 2>/dev/null | sort -hr | head -20
    fi
    
    echo -e '\n=== CHECKING FOR DUPLICATE PYTHON INSTALLATIONS ==='
    find / -name 'site-packages' -type d 2>/dev/null
    
    echo -e '\n=== LARGE FILES (>100MB) ==='
    find / -type f -size +100M 2>/dev/null | head -20
    
    echo -e '\n=== APT CACHE AND TEMP FILES ==='
    du -sh /var/cache/apt/* 2>/dev/null || echo 'No apt cache'
    du -sh /tmp/* 2>/dev/null || echo 'No temp files'
    du -sh /var/tmp/* 2>/dev/null || echo 'No var temp files'
    
    echo -e '\n=== PIP CACHE ==='
    du -sh /root/.cache/* 2>/dev/null || echo 'No pip cache'
    du -sh /home/*/.cache/* 2>/dev/null || echo 'No user cache'
    
    echo -e '\n=== CHECKING FOR BUILD TOOLS STILL INSTALLED ==='
    dpkg -l | grep -E '(build-essential|gcc|g\+\+|make|cmake)' || echo 'No build tools found'
    
    echo -e '\n=== PYTHON PACKAGES WITH SIZES ==='
    python -c \"
import pkg_resources
import os
packages = []
for dist in pkg_resources.working_set:
    try:
        loc = dist.location
        if os.path.exists(loc):
            size = sum(os.path.getsize(os.path.join(dirpath, filename))
                      for dirpath, dirnames, filenames in os.walk(loc)
                      for filename in filenames)
            packages.append((dist.project_name, size))
    except:
        pass
packages.sort(key=lambda x: x[1], reverse=True)
for name, size in packages[:20]:
    print(f'{name}: {size/1024/1024:.1f}MB')
\"
"

echo -e "\n3. Checking your requirements.txt for hidden heavy packages:"
if [ -f requirements.txt ]; then
    echo "=== FULL REQUIREMENTS.TXT ==="
    cat requirements.txt
    echo -e "\n=== CHECKING FOR HEAVY PACKAGES (extended list) ==="
    grep -iE "(torch|tensorflow|numpy|scipy|pandas|opencv|pillow|matplotlib|jupyter|scikit|selenium|playwright|chromium|ffmpeg|gstreamer|qt|gtk|wxpython|kivy|arcade|pygame|pyglet|pycairo|reportlab|weasyprint|wkhtmltopdf)" requirements.txt || echo "No obviously heavy packages found"
else
    echo "requirements.txt not found in current directory"
fi

echo -e "\n4. Image layer breakdown:"
docker image inspect $IMAGE_NAME --format='{{range .RootFS.Layers}}{{println .}}{{end}}' | wc -l
echo "Number of layers: $(docker image inspect $IMAGE_NAME --format='{{range .RootFS.Layers}}{{println .}}{{end}}' | wc -l)"