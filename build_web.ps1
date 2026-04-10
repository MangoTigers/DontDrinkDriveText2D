Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$stage = Join-Path $root ("webbuild_src_" + (Get-Date -Format "yyyyMMdd_HHmmss"))

New-Item -ItemType Directory -Path $stage | Out-Null

# Copy only runtime files needed by the game/web build.
Copy-Item (Join-Path $root "main.py") $stage
Copy-Item (Join-Path $root "requirements.txt") $stage -ErrorAction SilentlyContinue
Copy-Item (Join-Path $root "requirements-web.txt") $stage -ErrorAction SilentlyContinue
Copy-Item (Join-Path $root "pygbag.ini") $stage -ErrorAction SilentlyContinue
Copy-Item (Join-Path $root "pygbag.toml") $stage -ErrorAction SilentlyContinue
Copy-Item (Join-Path $root "src") $stage -Recurse
Copy-Item (Join-Path $root "assets") $stage -Recurse

Push-Location $stage
try {
    $pygbagCmd = $null
    $localPygbag = Join-Path $root ".venv\Scripts\pygbag.exe"
    if (Test-Path $localPygbag) {
        $pygbagCmd = "& `"$localPygbag`""
    } elseif (Get-Command pygbag -ErrorAction SilentlyContinue) {
        $pygbagCmd = "pygbag"
    } else {
        throw "pygbag was not found. Install with: pip install -r requirements-web.txt"
    }

    # Build archive directly for itch upload.
    Invoke-Expression "$pygbagCmd --build --archive ."
}
finally {
    Pop-Location
}

$webZip = Join-Path $stage "build\web.zip"
if (Test-Path $webZip) {
    $destBuild = Join-Path $root "build"
    if (-not (Test-Path $destBuild)) {
        New-Item -ItemType Directory -Path $destBuild | Out-Null
    }
    Copy-Item $webZip (Join-Path $destBuild "web.zip") -Force
    Write-Host "Web build ready: $destBuild\web.zip"
    Write-Host "Staging folder: $stage"
} else {
    Write-Warning "Web zip not found at expected path: $webZip"
}
