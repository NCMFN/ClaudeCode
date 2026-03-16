#!/usr/bin/env pwsh
# uninstall.ps1 — Windows-native entrypoint for the ECC uninstaller.
#
# This wrapper resolves the real repo/package root when invoked through a
# symlinked path, then delegates to the Node-based uninstall runtime.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptPath = $PSCommandPath

while ($true) {
    $item = Get-Item -LiteralPath $scriptPath -Force
    if (-not $item.LinkType) {
        break
    }

    $targetPath = $item.Target
    if ($targetPath -is [array]) {
        $targetPath = $targetPath[0]
    }

    if (-not $targetPath) {
        break
    }

    if (-not [System.IO.Path]::IsPathRooted($targetPath)) {
        $targetPath = Join-Path -Path $item.DirectoryName -ChildPath $targetPath
    }

    $scriptPath = [System.IO.Path]::GetFullPath($targetPath)
}

$scriptDir = Split-Path -Parent $scriptPath
$uninstallerScript = Join-Path -Path (Join-Path -Path $scriptDir -ChildPath 'scripts') -ChildPath 'uninstall.js'

& node $uninstallerScript @args
exit $LASTEXITCODE
