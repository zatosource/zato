Try
{
    $CURDIR = (Split-Path $myInvocation.MyCommand.Path) -join "`n"
    Push-Location $CURDIR
    
    $LocalAppDataPath = $env:LocalAppData
    $PythonPathVersion = "Python39"

    . .\_common.ps1

    # Git
    Invoke-InstallIfNotInstalled -ExeFile "Git-2.31.1-64-bit.exe" -URL 'https://github.com/git-for-windows/git/releases/download/v2.31.1.windows.1/Git-2.31.1-64-bit.exe' -Name "Git for Windows" -InstalledRegistryRegExp "Git version*" -ExeArgs @('/VERYSILENT', '/NORESTART', '/NOCANCEL', '/SP-', '/CLOSEAPPLICATIONS', '/RESTARTAPPLICATIONS', '/COMPONENTS="icons,ext\reg\shellhere,assoc,assoc_sh"')
    # Git PATH
    If(-Not ("$env:PATH" -like "*$env:ProgramFiles\Git\usr\bin*")) {
        Write-Output 'Adding Git\usr\bin to PATH'
        $Env:Path += ";$env:ProgramFiles\Git\usr\bin\"
    }

    # C++ Build tools
    Invoke-InstallIfNotInstalled -ExeFile "vs_buildtools.exe" -URL "https://aka.ms/vs/16/release/vs_buildtools.exe" -Name "Visual C++ Build tools" -InstalledRegistryRegExp "*Visual C++*"

    # Python
    Invoke-InstallIfNotInstalled -ExeFile "python-3.9.4-amd64.exe" -URL 'https://www.python.org/ftp/python/3.9.4/python-3.9.4-amd64.exe' -Name "Python" -InstalledRegistryRegExp "Python*" -ExeArgs @('/quiet', 'SimpleInstall=1', 'PrependPath=1')
    # Python PATH
    If(-Not ("$env:PATH" -like "*\Python*")) {
        Write-Output 'Adding Python to PATH'
        $INCLUDE = "$LocalAppDataPath\Programs\$PythonPathVersion;$LocalAppDataPath\Programs\$PythonPathVersion\Scripts"
        If(Test-Path "$LocalAppDataPath\Programs\Python\$PythonPathVersion") {
            $INCLUDE = "$LocalAppDataPath\Programs\Python\$PythonPathVersion;$LocalAppDataPath\Programs\Python\$PythonPathVersion\Scripts"
        }
        $Env:Path += ";$INCLUDE"
    }
    # Add Python permanently to PATH
    $oldPATH = $Env:Path
    $Env:Path = $oldPATH.Replace('-', '&')
    Set-ItemProperty -Path 'Registry::HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\Environment' -Name PATH -Value $env:PATH

    Write-Output "*** Downloading updates ***"
    Start-Process -Filepath (Get-Command "git.exe" | Select-Object -ExpandProperty Definition) -ArgumentList @('pull') -Wait

    Set-ExecutionPolicy Unrestricted -Scope Process

    .\Scripts\activate.ps1
    Write-Output "*** Updating dependencies ***"
    Invoke-InstallAllWithPip

    Write-Output "*** Applying patches ***"
    Push-Location .\Lib\site-packages\
    Invoke-ApplyPatches -CurDir "$CURDIR"
    Pop-Location
}
Catch
{
    Write-Output "Ran into an issue: $($PSItem.ToString())"
    Pop-Location
}