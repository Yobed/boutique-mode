# run_fashion_3d.ps1
# Pipeline Automatisé Image-to-3D pour Boutique Mode
# Usage:
#   npm run 3d:model
#   npm run 3d:model -- -ImagePath "inputs/product_images/mon_article.jpg" -Id "mon_produit"
#   .\scripts\3d_pipeline\run_fashion_3d.ps1 -ImagePath "inputs/product_images/sac.jpg" -Id "sac_cuir"

param(
    [Parameter(Mandatory=$false)]
    [string]$ImagePath = "",

    [Parameter(Mandatory=$false)]
    [string]$Id = "",

    [Parameter(Mandatory=$false)]
    [string]$Category = "",

    [Parameter(Mandatory=$false)]
    [switch]$ForceCategory = $false
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

# Image par défaut si non spécifiée
if (-not $ImagePath) {
    $DefaultDemo = Join-Path $ProjectRoot "inputs\product_images\sac_demo.jpg"
    if (Test-Path $DefaultDemo) {
        $ImagePath = $DefaultDemo
        Write-Host "Aucune image spécifiée : utilisation de l'image de démonstration ($DefaultDemo)" -ForegroundColor Yellow
    } else {
        Write-Error "Veuillez fournir une image via -ImagePath 'inputs/product_images/mon_image.jpg'"
        exit 1
    }
}

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
Write-Host "  PIPELINE IMAGE-TO-3D FASHION (BOUTIQUE-MODE v1.2)" -ForegroundColor Cyan
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

# Étape 1 : Analyse d'image & Décomposition spatiale multi-composants
Write-Host "`n[1/3] Analyse visuelle spatiale & inférence géométrique (Mission 32/33 Engine)..." -ForegroundColor Yellow
$AnalyzerScript = Join-Path $ScriptDir "component_analyzer.py"

$AnalyzerArgs = @("--image", $ImagePath, "--output", $SpecPath)
if ($Category) {
    $AnalyzerArgs += @("--category", $Category)
}
if ($ForceCategory) {
    $AnalyzerArgs += @("--force-category")
}

& $BlenderPy $AnalyzerScript @AnalyzerArgs
if ($LASTEXITCODE -ne 0) {
    Write-Error "Échec de l'analyseur de composants."
    exit $LASTEXITCODE
}

$SpecCheck = Get-Content $SpecPath -Raw | ConvertFrom-Json
if ($SpecCheck.semantic_classification) {
    $sc = $SpecCheck.semantic_classification
    Write-Host "  -> Catégorie certifiée   : $($SpecCheck.category) (confiance: $($sc.final_confidence))" -ForegroundColor Green
    if ($sc.contradiction_detected) {
        Write-Host "  -> [ANTI-CONTAMINATION] Contradiction sémantique détectée et corrigée par vision !" -ForegroundColor Magenta
        if ($sc.contradiction_details) {
            Write-Host "     $($sc.contradiction_details)" -ForegroundColor DarkGray
        }
    }
}

# Étape 2 : Modélisation procédurale Blender, Shaders PBR & Export GLB
Write-Host "`n[2/3] Modélisation 3D Blender, Shaders PBR Luxe & Rendu Studio..." -ForegroundColor Yellow
$OrchestratorScript = Join-Path $ScriptDir "orchestrator.py"

& $BlenderExe --factory-startup -b -P $OrchestratorScript -- --spec $SpecPath --output-dir $OutputDir
if ($LASTEXITCODE -ne 0) {
    Write-Error "Échec de l'orchestrateur Blender."
    exit $LASTEXITCODE
}

# Étape 3 : Déploiement des actifs GLB & Poster pour Product3DViewer (Next.js)
Write-Host "`n[3/3] Déploiement du modèle GLB et du poster dans public/models/..." -ForegroundColor Yellow

$SpecJson = Get-Content $SpecPath -Raw | ConvertFrom-Json
$TargetGlb = Join-Path $OutputDir "$($SpecJson.object_id).glb"
if (-not (Test-Path $TargetGlb)) {
    $TargetGlb = (Get-ChildItem -Path $OutputDir -Filter "*.glb" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
}

if ($TargetGlb -and (Test-Path $TargetGlb)) {
    $DestGlb = Join-Path $PublicModelsDir "$Id.glb"
    Copy-Item -Path $TargetGlb -Destination $DestGlb -Force
    $GlbSize = (Get-Item $DestGlb).Length
    Write-Host "  -> Modèle GLB déployé : $DestGlb ($GlbSize octets)" -ForegroundColor Green
    Write-Host "  -> URL du modèle 3D : /models/$Id.glb" -ForegroundColor Cyan
} else {
    Write-Warning "Aucun fichier GLB trouvé dans $OutputDir"
}

# Déploiement du poster studio (vue hero)
$PreviewDir = Join-Path $OutputDir "previews"
$TargetHero = Join-Path $PreviewDir "$($SpecJson.object_id)_render_hero.png"
if (-not (Test-Path $TargetHero)) {
    $TargetHero = (Get-ChildItem -Path $PreviewDir -Filter "*hero.png" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
}

if ($TargetHero -and (Test-Path $TargetHero)) {
    $DestPoster = Join-Path $PublicModelsDir "$Id-poster.png"
    Copy-Item -Path $TargetHero -Destination $DestPoster -Force
    Write-Host "  -> Poster déployé      : $DestPoster" -ForegroundColor Green
    Write-Host "  -> URL du poster       : /models/$Id-poster.png" -ForegroundColor Cyan
}

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "  SUCCÈS : Article modélisé et prêt pour la boutique !" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "Pour l'afficher dans une page Next.js :" -ForegroundColor White
Write-Host "  <Product3DViewer modelSrc='/models/$Id.glb' posterSrc='/models/$Id-poster.png' />`n" -ForegroundColor Gray
