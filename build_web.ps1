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

# Exclude unused binary helper archive from web package.
$binarySpriteArchive = Join-Path $stage "assets\sprites\obstacle_car.zip"
if (Test-Path $binarySpriteArchive) {
    Remove-Item $binarySpriteArchive -Force
}

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

    # Build archive directly for itch upload with conservative runtime settings.
    Invoke-Expression "$pygbagCmd --build --archive --ume_block 0 --PYBUILD 3.11 ."
    if ($LASTEXITCODE -ne 0) {
        throw "pygbag failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}

$webOutDir = Join-Path $stage "build\web"
$webZip = Join-Path $stage "build\web.zip"

if (Test-Path $webOutDir) {
    $indexPath = Join-Path $webOutDir "index.html"
    if (Test-Path $indexPath) {
        $html = Get-Content -Raw -Encoding UTF8 $indexPath

        # Avoid browser startup getting stuck on media-engagement gate.
        $html = $html -replace 'if not platform\.window\.MM\.UME:', 'if False and not platform.window.MM.UME:'
        $html = $html -replace 'ume_block\s*:\s*1', 'ume_block : 0'
        $html = $html -replace 'autorun\s*:\s*0', 'autorun : 1'

        # Always use APK loading path to avoid host-based tar/apk branch mismatches.
        $html = $html -replace "if platform\.window\.location\.host\.find\('\.itch\.zone'\)>0:", 'if True:'

                # Add a small on-page error overlay to avoid silent gray screens.
                if ($html -notmatch 'id="pygbag-error-overlay"') {
                        $errorOverlayScript = @"
<script>
(function () {
    function ensureOverlay() {
        var existing = document.getElementById('pygbag-error-overlay');
        if (existing) return existing;
        var box = document.createElement('pre');
        box.id = 'pygbag-error-overlay';
        box.style.position = 'fixed';
        box.style.left = '8px';
        box.style.right = '8px';
        box.style.bottom = '8px';
        box.style.maxHeight = '45vh';
        box.style.overflow = 'auto';
        box.style.padding = '10px';
        box.style.margin = '0';
        box.style.background = 'rgba(120,0,0,0.92)';
        box.style.color = '#fff';
        box.style.font = '12px/1.35 monospace';
        box.style.zIndex = '2147483647';
        box.style.display = 'none';
        document.body.appendChild(box);
        return box;
    }

    function show(msg) {
        var box = ensureOverlay();
        box.style.display = 'block';
        box.textContent += (box.textContent ? '\n\n' : '') + msg;
    }

    window.addEventListener('error', function (e) {
        show('[window.error] ' + (e.message || 'unknown') + '\n' + (e.filename || '') + ':' + (e.lineno || 0));
    });

    window.addEventListener('unhandledrejection', function (e) {
        var reason = (e && e.reason) ? (e.reason.stack || e.reason.message || String(e.reason)) : 'unknown';
        show('[unhandledrejection] ' + reason);
    });

    setTimeout(function () {
        var c = document.querySelector('canvas');
        if (!c) {
            show('No canvas found after startup. Runtime may have failed before initialization.');
        }
    }, 6000);
})();
</script>
"@
                        $html = $html -replace '</body>', ($errorOverlayScript + "`n</body>")
                }

        Set-Content -Encoding UTF8 $indexPath $html
    }

    # Rebuild archive from finalized web output so both apk and tar.gz are always present.
    if (Test-Path $webZip) {
        Remove-Item $webZip -Force
    }
    Compress-Archive -Path (Join-Path $webOutDir '*') -DestinationPath $webZip -Force

    $destBuild = Join-Path $root "build"
    if (-not (Test-Path $destBuild)) {
        New-Item -ItemType Directory -Path $destBuild | Out-Null
    }

    $destZip = Join-Path $destBuild "web.zip"
    $itchZip = Join-Path $destBuild "web_itch.zip"

    Copy-Item $webZip $destZip -Force
    Copy-Item $webZip $itchZip -Force

    if (-not (Test-Path $destZip)) {
        throw "Expected output zip was not created: $destZip"
    }
    if (-not (Test-Path $itchZip)) {
        throw "Expected output zip was not created: $itchZip"
    }

    Write-Host "Web build ready: $destZip"
    Write-Host "Itch upload zip: $itchZip"
    Write-Host "Staging folder: $stage"
} else {
    throw "Web output folder not found at expected path: $webOutDir"
}
