# run_fashion_3d.ps1
# Pipeline Automatisé Image-to-3D pour Boutique Mode
# Usage:
#   .\scripts\3d_pipeline\run_fashion_3d.ps1 -ImagePath "inputs/product_images/sac.png" -Id "sac_cuir"

param(
    [Parameter(Mandatory=$true)]
    [string]$ImagePath,

    [Parameter(Mandatory=$false)]
    [string]$Id = ""
)

$ErrorActionPreference = "Stop"

# Chemins Blender 5.2.2 Portable
$BlenderExe = "C:\Users\WILFRIED\Downloads\Blender-5.2.2-Portable\blender-5.2.2-windows-x64\blender.exe"
$BlenderPy  = "C:\Users\WILFRIED\Downloads\Blender-5.2.2-Portable\blender-5.2.2-windows-x64\5.2\python\bin\python.exe"

if (-not (Test-Path $BlenderExe)) {
    Write-Error "Blender portable introuvable à : $BlenderExe"
    exit 1
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path (Join-Path $ScriptDir "..\..")

if (-not (Test-Path $ImagePath)) {
    # Tenter chemin relatif au projet
    $ResolvedImg = Join-Path $ProjectRoot $ImagePath
    if (-not (Test-Path $ResolvedImg)) {
        Write-Error "Image introuvable : $ImagePath"
        exit 1
    }
    $ImagePath = $ResolvedImg
}

if (-not $Id) {
    $Id = [System.IO.Path]::GetFileNameWithoutExtension($ImagePath).ToLower() -replace '[^a-z0-9_]', '_'
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  PIPELINE IMAGE-TO-3D FASHION (BOUTIQUE-MODE)" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Image source : $ImagePath"
Write-Host "Identifiant  : $Id"

$SpecDir = Join-Path $ProjectRoot "config\specs\3d"
$OutputDir = Join-Path $ProjectRoot "outputs\3d_studio\$Id"
$PublicModelsDir = Join-Path $ProjectRoot "public\models"

New-Item -ItemType Directory -Force -Path $SpecDir | Out-Null
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
New-Item -ItemType Directory -Force -Path $PublicModelsDir | Out-Null

$SpecPath = Join-Path $SpecDir "$Id`_spec.json"

# Étape 1 : Analyse d'image & Décomposition multi-composants
Write-Host "`n[1/3] Analyse visuelle et décomposition multi-composants..." -ForegroundColor Yellow
$AnalyzerScript = Join-Path $ScriptDir "component_analyzer.py"

& $BlenderPy $AnalyzerScript --image $ImagePath --output $SpecPath
if ($LASTEXITCODE -ne 0) {
    Write-Error "Échec de l'analyseur de composants."
    exit $LASTEXITCODE
}

# Étape 2 : Modélisation procédurale Blender, Shaders PBR & Export GLB
Write-Host "`n[2/3] Modélisation 3D Blender, Shaders PBR & Rendu Studio..." -ForegroundColor Yellow
$OrchestratorScript = Join-Path $ScriptDir "orchestrator.py"

& $BlenderExe --factory-startup -b -P $OrchestratorScript -- --spec $SpecPath --output $OutputDir
if ($LASTEXITCODE -ne 0) {
    Write-Error "Échec de l'orchestrateur Blender."
    exit $LASTEXITCODE
}

# Étape 3 : Déploiement du modèle GLB dans public/models/ pour Next.js
Write-Host "`n[3/3] Déploiement du modèle GLB pour la boutique web..." -ForegroundColor Yellow
$GeneratedGlb = Get-ChildItem -Path $OutputDir -Filter "*.glb" | Select-Object -First 1

if ($GeneratedGlb) {
    $DestGlb = Join-Path $PublicModelsDir "$Id.glb"
    Copy-Item -Path $GeneratedGlb.FullName -Destination $DestGlb -Force
    Write-Host "  -> Modèle GLB déployé : $DestGlb ($($GeneratedGlb.Length) octets)" -ForegroundColor Green
    Write-Host "  -> URL dans le site web : /models/$Id.glb" -ForegroundColor Cyan
} else {
    Write-Warning "Aucun fichier GLB trouvé dans $OutputDir"
}

Write-Host "`nSUCCÈS : Article modélisé avec succès !" -ForegroundColor Green
Write-Host "Rendus studio disponibles dans : $OutputDir\previews"
