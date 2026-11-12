param(
    [string]$Python = 'python',
    [string]$OutputDir = (Join-Path $PSScriptRoot 'dist'),
    [string]$BuildDir = (Join-Path $PSScriptRoot 'build')
)

$ErrorActionPreference = 'Stop'
$OutputDir = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutputDir)
$BuildDir = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($BuildDir)
$compiler = Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
if (-not (Test-Path -LiteralPath $compiler -PathType Leaf)) {
    throw 'The Windows .NET Framework x64 compiler was not found.'
}
New-Item -ItemType Directory -Path $BuildDir,$OutputDir -Force | Out-Null
$releaseVersion = (& $Python -B (Join-Path $PSScriptRoot 'room_version.py') | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or $releaseVersion -notmatch '^\d+\.\d+(\.\d+){0,2}$') {
    throw 'Invalid application version.'
}
$parsedVersion = [Version]::Parse($releaseVersion)
$assemblyVersion = '{0}.{1}.{2}.{3}' -f $parsedVersion.Major,$parsedVersion.Minor,([Math]::Max(0,$parsedVersion.Build)),([Math]::Max(0,$parsedVersion.Revision))
$metadata = Join-Path $BuildDir 'AssemblyInfo.cs'
@"
using System.Reflection;
[assembly: AssemblyTitle("Model Room")]
[assembly: AssemblyProduct("Model Room")]
[assembly: AssemblyDescription("Multi-model group chat for Windows")]
[assembly: AssemblyVersion("$assemblyVersion")]
[assembly: AssemblyFileVersion("$assemblyVersion")]
[assembly: AssemblyInformationalVersion("$releaseVersion")]
"@ | Set-Content -LiteralPath $metadata -Encoding UTF8
$payload = Join-Path $BuildDir 'runtime.zip'
& $Python -B (Join-Path $PSScriptRoot 'build_payload.py') $payload
if ($LASTEXITCODE -ne 0) {
    throw "Runtime bundle creation failed with exit code $LASTEXITCODE."
}

$exe = Join-Path $OutputDir 'ModelRoom.exe'
$icon = Join-Path $PSScriptRoot 'ModelRoom.ico'
& $compiler /nologo /target:winexe /platform:x64 /optimize+ "/out:$exe" "/win32icon:$icon" `
    "/resource:$payload,ModelRoom.Runtime" /reference:System.IO.Compression.FileSystem.dll `
    /reference:System.Windows.Forms.dll (Join-Path $PSScriptRoot 'WindowsLauncher.cs') $metadata
if ($LASTEXITCODE -ne 0) {
    throw "Windows launcher compilation failed with exit code $LASTEXITCODE."
}
Write-Output $exe
