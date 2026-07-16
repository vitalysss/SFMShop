$source = $PSScriptRoot
$parent = Split-Path $source -Parent

$target = Join-Path $parent "SFMShop_clean"
$archive = Join-Path $parent "SFMShop_clean.zip"

Remove-Item `
    -Path $target `
    -Recurse `
    -Force `
    -ErrorAction SilentlyContinue

Remove-Item `
    -Path $archive `
    -Force `
    -ErrorAction SilentlyContinue

robocopy `
    $source `
    $target `
    /E `
    /XD `
    ".git" `
    ".idea" `
    "__pycache__" `
    ".venv" `
    "venv" `
    /XF `
    "*.pyc" `
    ".env" `
    "make_clean_archive.ps1"

if ($LASTEXITCODE -ge 8) {
    Write-Host ""
    Write-Host "Ошибка при создании чистой копии."
    exit $LASTEXITCODE
}

Compress-Archive `
    -Path $target `
    -DestinationPath $archive

Write-Host ""
Write-Host "Готово."
Write-Host "Чистая папка:"
Write-Host $target
Write-Host ""
Write-Host "Архив:"
Write-Host $archive