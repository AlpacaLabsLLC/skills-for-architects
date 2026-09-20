param([Parameter(Mandatory=$true)][string]$Package, [Parameter(Mandatory=$true)][string]$Sha256, [Parameter(Mandatory=$true)][string]$Destination)
$ErrorActionPreference = 'Stop'
$asBootstrapTemp = Join-Path ([IO.Path]::GetTempPath()) ([Guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $asBootstrapTemp | Out-Null
try {
  switch ([Runtime.InteropServices.RuntimeInformation]::OSArchitecture.ToString()) {
    'Arm64' { $asUvUrl = 'https://github.com/astral-sh/uv/releases/download/0.12.13/uv-aarch64-pc-windows-msvc.zip'; $asUvHash = '1efb2654b06e7063d4ac1fc9d49a9bda9a6704d82f035b589a2751a592f14151' }
    'X64' { $asUvUrl = 'https://github.com/astral-sh/uv/releases/download/0.12.13/uv-x86_64-pc-windows-msvc.zip'; $asUvHash = 'a86c9dc7bad9b03f388583b7187c05fe9951c2e0d392217e8fd43d97787f6ec2' }
    default { throw 'Unsupported bootstrap architecture' }
  }
  $asArchive = Join-Path $asBootstrapTemp 'uv.zip'
  Invoke-WebRequest -Uri $asUvUrl -OutFile $asArchive
  if ((Get-FileHash -Algorithm SHA256 $asArchive).Hash.ToLowerInvariant() -ne $asUvHash) { throw 'Installer hash mismatch' }
  Expand-Archive -Path $asArchive -DestinationPath (Join-Path $asBootstrapTemp 'unpacked')
  $asUv = (Get-ChildItem (Join-Path $asBootstrapTemp 'unpacked') -Recurse -Filter uv.exe | Select-Object -First 1).FullName
  & $asUv run --no-project --python 3.13.7 --managed-python (Join-Path $PSScriptRoot 'install.py') --uv $asUv --package $Package --sha256 $Sha256 --destination $Destination
  if ($LASTEXITCODE -ne 0) { throw 'Arch Studio installation failed' }
} finally { Remove-Item -Recurse -Force $asBootstrapTemp }
