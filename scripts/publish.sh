#!/bin/bash
# OpenCar Publishing Script

set -e

echo "OpenCar Publishing Script"
echo "============================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Checking package integrity...${NC}"
twine check dist/*

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Package validation failed!${NC}"
    exit 1
fi

echo -e "${GREEN}Package validation passed!${NC}"

echo -e "${BLUE}Step 2: Publishing to Test PyPI...${NC}"
echo "This allows you to test the package before publishing to main PyPI"
read -p "Do you want to publish to Test PyPI first? (y/n): " test_pypi

if [ "$test_pypi" = "y" ] || [ "$test_pypi" = "Y" ]; then
    echo -e "${YELLOW}Publishing to Test PyPI...${NC}"
    twine upload --repository testpypi dist/*
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Successfully published to Test PyPI!${NC}"
        echo -e "${BLUE}Test your package with:${NC}"
        echo "pip install --index-url https://test.pypi.org/simple/ opencar"
        echo ""
        echo -e "${YELLOW}Test the installation and functionality before proceeding to main PyPI.${NC}"
        read -p "Press Enter to continue to main PyPI or Ctrl+C to exit..."
    else
        echo -e "${RED}❌ Failed to publish to Test PyPI!${NC}"
        exit 1
    fi
fi

echo -e "${BLUE}Step 3: Publishing to PyPI...${NC}"
echo -e "${YELLOW}⚠️  This will make your package publicly available on PyPI!${NC}"
read -p "Are you sure you want to publish to PyPI? (y/n): " main_pypi

if [ "$main_pypi" = "y" ] || [ "$main_pypi" = "Y" ]; then
    echo -e "${YELLOW}Publishing to PyPI...${NC}"
    twine upload dist/*
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Successfully published OpenCar to PyPI!${NC}"
        echo -e "${BLUE}Your package is now available at: https://pypi.org/project/opencar/${NC}"
        echo -e "${BLUE}Users can install it with: pip install opencar${NC}"
        
        # Create GitHub release
        echo -e "${BLUE}Step 4: Creating GitHub release...${NC}"
        if command -v gh &> /dev/null; then
            gh release create v1.0.0 dist/* --title "OpenCar v1.0.0" --notes "Production-ready autonomous vehicle perception system with multimodal ML pipelines, real-time processing, and OpenAI integration."
            echo -e "${GREEN}GitHub release created!${NC}"
        else
            echo -e "${YELLOW}GitHub CLI not found. Please create a release manually at:${NC}"
            echo "https://github.com/yourusername/opencar/releases/new"
        fi
        
    else
        echo -e "${RED}❌ Failed to publish to PyPI!${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Publication cancelled.${NC}"
fi

echo -e "${GREEN}Publishing process completed!${NC}" 