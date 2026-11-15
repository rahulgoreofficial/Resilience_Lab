$ErrorActionPreference = "Stop"
$SetupExe = "C:\DM\CP\release\RESILIENCE_LAB_Setup.exe"
$LogFile = "C:\DM\CP\test_install.log"
$InstallDir = "C:\DM\CP\dist\test_install"

Write-Host "Starting silent installer test..."
$args = "/VERYSILENT /SUPPRESSMSGBOXES /LOG=`"$LogFile`" /DIR=`"$InstallDir`""
$p = Start-Process -FilePath $SetupExe -ArgumentList $args -Wait -PassThru
Write-Host "Installer finished with ExitCode: $($p.ExitCode)"

if (Test-Path $LogFile) {
    Write-Host "Log file contents:"
    Get-Content $LogFile
} else {
    Write-Host "Log file was not generated."
}

if (Test-Path $InstallDir) {
    Write-Host "Installed files count:" (Get-ChildItem -Path $InstallDir -Recurse).Count
} else {
    Write-Host "Install directory does not exist."
}

