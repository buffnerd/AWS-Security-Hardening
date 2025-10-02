#!/bin/bash
# Lambda build script for packaging the AWS Security Toolkit

set -e

echo "🚀 Building AWS Security Toolkit Lambda package..."

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Create build and dist directories
BUILD_DIR="$SCRIPT_DIR/build"
DIST_DIR="$SCRIPT_DIR/dist"

echo "📁 Creating build directories..."
rm -rf "$BUILD_DIR" "$DIST_DIR"
mkdir -p "$BUILD_DIR" "$DIST_DIR"

echo "📦 Copying source code..."
# Copy the entire aws_sec_toolkit package
cp -r "$PROJECT_ROOT/src/aws_sec_toolkit" "$BUILD_DIR/"

echo "📚 Installing dependencies..."
# Install runtime dependencies into the build directory
pip install --target "$BUILD_DIR" --no-deps boto3 botocore colorama

# Install dependencies with their dependencies
pip install --target "$BUILD_DIR" -r "$SCRIPT_DIR/requirements.txt"

echo "🗜️  Creating deployment packages..."

# Create individual Lambda packages for each handler
HANDLERS=(
    "handler_cloudtrail"
    "handler_guardduty" 
    "handler_securityhub"
    "handler_s3_bpa"
    "handler_iam_mfa"
    "handler_sg_audit"
)

for handler in "${HANDLERS[@]}"; do
    echo "📦 Building package for $handler..."
    
    # Create a temporary directory for this specific handler
    HANDLER_BUILD_DIR="$BUILD_DIR/${handler}_build"
    mkdir -p "$HANDLER_BUILD_DIR"
    
    # Copy all dependencies and source code
    cp -r "$BUILD_DIR/aws_sec_toolkit" "$HANDLER_BUILD_DIR/"
    cp -r "$BUILD_DIR"/*.dist-info "$HANDLER_BUILD_DIR/" 2>/dev/null || true
    cp -r "$BUILD_DIR"/boto* "$HANDLER_BUILD_DIR/" 2>/dev/null || true
    cp -r "$BUILD_DIR"/colorama* "$HANDLER_BUILD_DIR/" 2>/dev/null || true
    
    # Create the zip file
    cd "$HANDLER_BUILD_DIR"
    zip -r "$DIST_DIR/${handler}.zip" . -x "*.pyc" "*__pycache__*" "*.git*"
    cd "$SCRIPT_DIR"
    
    # Clean up handler build directory
    rm -rf "$HANDLER_BUILD_DIR"
    
    echo "✅ Created $DIST_DIR/${handler}.zip"
done

# Create a combined package with all handlers
echo "📦 Creating combined Lambda package..."
cd "$BUILD_DIR"
zip -r "$DIST_DIR/aws-security-toolkit-lambda.zip" . -x "*.pyc" "*__pycache__*" "*.git*"
cd "$SCRIPT_DIR"

echo "🧹 Cleaning up build directory..."
rm -rf "$BUILD_DIR"

echo "📊 Package sizes:"
ls -lh "$DIST_DIR"/*.zip

echo ""
echo "🎉 Lambda package build completed successfully!"
echo "📁 Packages available in: $DIST_DIR"
echo ""
echo "📋 Available packages:"
for zip_file in "$DIST_DIR"/*.zip; do
    if [ -f "$zip_file" ]; then
        echo "  • $(basename "$zip_file")"
    fi
done

echo ""
echo "🚀 Deployment instructions:"
echo "  1. Upload packages to AWS Lambda"
echo "  2. Use CloudFormation templates in infra/cfn/ for infrastructure"
echo "  3. Set handler to: aws_sec_toolkit.lambda_handlers.<handler_name>.lambda_handler"