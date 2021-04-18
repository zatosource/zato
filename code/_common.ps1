Set-ExecutionPolicy Unrestricted -Scope Process
function Set-Patch {
    Param (
        [Parameter(Mandatory=$true)]  [String]$BasePath,
        [Parameter(Mandatory=$true)]  [String]$PatchFile,
        [Parameter(mandatory=$false)]  [Boolean]$IsBinary = $false
    )

    If(Test-Path "$PatchFile" -PathType Leaf) {
        $params = @('--forward', '-p0', '-d', $BasePath, '-i', $PatchFile)
        if($IsBinary -eq $true){
            $first += '--binary'
        }
        Start-Process -Filepath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList $params -Wait
    } else {
        Write-Output "Patch $PatchFile not found"
    }
}

function Invoke-ApplyPatches {
    Set-Patch -BasePath 'eggs' -PatchFile 'patches\butler\__init__.py.diff'
    Set-Patch -BasePath 'eggs' -PatchFile 'patches\configobj.py.diff'
    Set-Patch -BasePath 'eggs' -PatchFile 'patches\django\db\models\base.py.diff'
    Set-Patch -BasePath 'eggs' -PatchFile 'patches\ntlm\HTTPNtlmAuthHandler.py.diff' -IsBinary $true
    Set-Patch -BasePath 'eggs' -PatchFile 'patches\pykafka\topic.py.diff'
    Set-Patch -BasePath 'eggs' -PatchFile 'patches\redis\redis\connection.py.diff'
    Set-Patch -BasePath 'eggs' -PatchFile 'patches\requests\models.py.diff'
    Set-Patch -BasePath 'eggs' -PatchFile 'patches\requests\sessions.py.diff'
    Set-Patch -BasePath 'eggs' -PatchFile 'patches\ws4py\server\geventserver.py.diff'
    Set-Patch -BasePath 'eggs' -PatchFile 'patches\sqlalchemy\sql\dialects\postgresql\pg8000.py.diff'
    Set-Patch -BasePath 'eggs' -PatchFile 'patches\pg8000\core.py.diff'
    Set-Patch -BasePath 'eggs' -PatchFile 'patches\sqlalchemy\sql\crud.py.diff'
}
function Invoke-InstallAllWithPip {
    .\Scripts\pip.exe install -r .\requirements.txt
    .\Scripts\pip.exe install -e .\zato-common
    .\Scripts\pip.exe install -e .\zato-agent
    .\Scripts\pip.exe install -e .\zato-broker
    .\Scripts\pip.exe install -e .\zato-cli
    .\Scripts\pip.exe install -e .\zato-client
    .\Scripts\pip.exe install -e .\zato-cy
    .\Scripts\pip.exe install -e .\zato-distlock
    .\Scripts\pip.exe install -e .\zato-hl7
    .\Scripts\pip.exe install -e .\zato-lib
    .\Scripts\pip.exe install -e .\zato-scheduler
    .\Scripts\pip.exe install -e .\zato-server
    .\Scripts\pip.exe install -e .\zato-web-admin
    .\Scripts\pip.exe install -e .\zato-zmq
    .\Scripts\pip.exe install -e .\zato-sso
    .\Scripts\pip.exe install -e .\zato-testing
}

function New-Symlink {
    Param (
        [Parameter(Mandatory=$true)]  [String]$Target,
        [Parameter(Mandatory=$true)]  [String]$Link
    )

    If(-not(Test-Path $Target -PathType Any)) {
        New-Item -Path $Target -ItemType SymbolicLink -Value $Link -Force
    }
}

function Invoke-InstallIfNotInstalled {
    Param (
        [Parameter(Mandatory=$true)]  [String]$Name,
        [Parameter(Mandatory=$true)]  [String]$ExeFile,
        [Parameter(Mandatory=$true)]  [String]$URL,
        [Parameter(Mandatory=$true)]  [String]$InstalledRegistryRegExp,
        [Parameter(Mandatory=$false)]  [String[]]$ExeArgs
    )
    $installed = $null -ne (Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | Where-Object { $_.DisplayName -like $InstalledRegistryRegExp })
    If(-Not $installed) {
        Write-Output "Installing $Name"
        If(-not(Test-Path ".\$ExeFile" -PathType Leaf)){
            Invoke-WebRequest -Uri $URL -OutFile $ExeFile
        }
        If($ExeArgs) {
            Start-Process -Filepath "./$ExeFile" -ArgumentList $ExeArgs -Wait
        } else {
            Start-Process -Filepath "./$ExeFile" -Wait
        }
    } else {
        Write-Host "$Name is already installed."
    }
}