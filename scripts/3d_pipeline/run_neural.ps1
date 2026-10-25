# run_neural.ps1 — Lance le pipeline image -> 3D neuronal avec un Python qui a les bons paquets.
#   npm run 3d:catalog                                  tous les sacs/chaussures/accessoires du catalogue
#   npm run 3d:product -- --article art-009             un article du catalogue
#   npm run 3d:product -- --image photo.jpg --id mon-sac
# Installation (poids ~1,9 Go + paquets) : npm run 3d:setup
# Variable ELSI_PYTHON : chemin d'un interpréteur précis (sinon détection automatique).

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "..\..")
$Probe = "import PIL, torch, trimesh, onnxruntime, transformers, scipy, skimage, omegaconf, einops, fast_simplification, xatlas"

function Find-Python {
    $candidates = @()
    if ($env:ELSI_PYTHON) { $candidates += $env:ELSI_PYTHON }
    $candidates += "python", "python3"
    $candidates += Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WindowsApps" -Directory -Filter "PythonSoftwareFoundation.Python.*" -ErrorAction SilentlyContinue |
        ForEach-Object { Join-Path $_.FullName "python.exe" }
    $candidates += Get-ChildItem "$env:LOCALAPPDATA\Python" -Directory -Filter "pythoncore-*" -ErrorAction SilentlyContinue |
        ForEach-Object { Join-Path $_.FullName "python.exe" }
    $previous = $ErrorActionPreference
    $ErrorActionPreference = "Continue"  # PS 5.1 : le stderr d'un Python incomplet ne doit pas lever d'exception
    try {
        foreach ($c in $candidates) {
            if (-not $c) { continue }
            & $c -c $Probe *> $null
            if ($LASTEXITCODE -eq 0) { return $c }
        }
    } finally {
        $ErrorActionPreference = $previous
    }
    return $null
}

$Python = Find-Python
if (-not $Python) {
    Write-Error "Aucun Python avec les paquets requis. Lancez : npm run 3d:setup"
    exit 1
}

# Les poids sont locaux : aucun accès Hugging Face à l'exécution (le client xet se bloque sur certaines machines).
$env:HF_HUB_OFFLINE = "1"
$env:HF_HUB_DISABLE_SYMLINKS_WARNING = "1"

& $Python (Join-Path $ProjectRoot "scripts\3d_pipeline\image_to_3d.py") @args
exit $LASTEXITCODE
