# Build Lambda Layer with Python dependencies

$layerDir = "backend/lambda/layer"
$pythonDir = "$layerDir/python"

# Clean up existing layer
if (Test-Path $layerDir) {
    Remove-Item -Recurse -Force $layerDir
}

# Create layer directory structure
New-Item -ItemType Directory -Force -Path $pythonDir | Out-Null

# Install dependencies
Write-Host "Installing Lambda layer dependencies..."
pip install -r backend/lambda/layer_requirements.txt -t $pythonDir --upgrade

Write-Host "Lambda layer built successfully at: $layerDir"
