param(
    [string]$OutputZip = "deploy/package.zip",
    [string]$S3Bucket = "",
    [string]$S3Key = "",
    [switch]$Upload
)

Write-Host "Packaging Lambda..."
if (-Not (Test-Path -Path (Split-Path $OutputZip))) {
    New-Item -ItemType Directory -Path (Split-Path $OutputZip) -Force | Out-Null
}

# Create zip of handler and prompts
if (Test-Path $OutputZip) { Remove-Item $OutputZip }
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory((Get-Location).Path, $OutputZip)
Write-Host "Created $OutputZip"

if ($Upload -and $S3Bucket -and $S3Key) {
    Write-Host "Uploading to s3://$S3Bucket/$S3Key ..."
    aws s3 cp $OutputZip "s3://$S3Bucket/$S3Key"
}

Write-Host "Done."