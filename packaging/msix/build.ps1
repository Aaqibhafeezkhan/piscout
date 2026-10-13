<#
  Build an MSIX for Microsoft Store submission.

  Prerequisites: Windows SDK (makeappx.exe), and dist\piscout.exe already built.
  The Identity values come from Partner Center after you reserve the app name.

  Example:
    .\packaging\msix\build.ps1 `
      -IdentityName "12345Publisher.piscout" `
      -Publisher "CN=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX" `
      -PublisherDisplayName "MilkteaTW1" `
      -Version "0.1.1.0"
#>
param(
  [Parameter(Mandatory = $true)][string]$IdentityName,
  [Parameter(Mandatory = $true)][string]$Publisher,
  [Parameter(Mandatory = $true)][string]$PublisherDisplayName,
  [string]$Version = "0.1.1.0",
  [string]$Exe = "dist\piscout.exe",
  [string]$Out = "dist\piscout.msix"
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$stage = Join-Path $root "build\msix"

if (-not (Test-Path (Join-Path $root $Exe))) { throw "Not found: $Exe (build the exe first)" }

$makeappx = Get-ChildItem "${env:ProgramFiles(x86)}\Windows Kits\10\bin" -Recurse -Filter makeappx.exe -ErrorAction SilentlyContinue |
  Where-Object { $_.FullName -match "x64" } | Sort-Object FullName -Descending | Select-Object -First 1
if (-not $makeappx) { throw "makeappx.exe not found. Install the Windows 10/11 SDK." }

Remove-Item -Recurse -Force $stage -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force "$stage\Assets" | Out-Null
Copy-Item (Join-Path $root $Exe) "$stage\piscout.exe"
Copy-Item "$PSScriptRoot\Assets\*.png" "$stage\Assets\"

$m = Get-Content "$PSScriptRoot\AppxManifest.xml" -Raw -Encoding UTF8
$m = $m.Replace("{{IDENTITY_NAME}}", $IdentityName).
        Replace("{{PUBLISHER}}", $Publisher).
        Replace("{{PUBLISHER_DISPLAY_NAME}}", $PublisherDisplayName).
        Replace("{{VERSION}}", $Version)
Set-Content "$stage\AppxManifest.xml" $m -Encoding UTF8

$outPath = Join-Path $root $Out
& $makeappx.FullName pack /d $stage /p $outPath /o
Write-Host "Built $outPath (unsigned; the Store signs it on submission)"
