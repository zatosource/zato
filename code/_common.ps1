Set-ExecutionPolicy Unrestricted -Scope Process
function Invoke-Process {
    [CmdletBinding(SupportsShouldProcess)]
    param
        (
        [Parameter(Mandatory)]
        [ValidateNotNullOrEmpty()]
        [string]$FilePath,

        [Parameter()]
        [ValidateNotNullOrEmpty()]
        [string]$ArgumentList,

        [Parameter()]
        [string]$CurPath,

        [ValidateSet("Full","Verbose","StdOut","StdErr","ExitCode","None")]
        [string]$DisplayLevel
        )

    $ErrorActionPreference = 'Stop'

    try {
        $pinfo = New-Object System.Diagnostics.ProcessStartInfo
        $pinfo.FileName = $FilePath
        $pinfo.RedirectStandardError = $true
        $pinfo.RedirectStandardOutput = $true
        $pinfo.UseShellExecute = $false
        $pinfo.WindowStyle = 'Hidden'
        $pinfo.CreateNoWindow = $true
        $pinfo.Arguments = $ArgumentList
        If(-Not($CurPath -eq "") -and -Not($CurPath -eq $null)) {
            $pinfo.WorkingDirectory = $CurPath
        }
        $p = New-Object System.Diagnostics.Process
        $p.StartInfo = $pinfo
        $p.Start() | Out-Null
        $result = [pscustomobject]@{
            Title = ($MyInvocation.MyCommand).Name
            Command = $FilePath
            Arguments = $ArgumentList
            StdOut = $p.StandardOutput.ReadToEnd()
            StdErr = $p.StandardError.ReadToEnd()
            ExitCode = $p.ExitCode
        }
        $p.WaitForExit()

        if (-not([string]::IsNullOrEmpty($DisplayLevel))) {
            switch($DisplayLevel) {
                "Full" { return $result; break }
                "Verbose" { return $result.StdOut + $result.StdErr; break }
                "StdOut" { return $result.StdOut; break }
                "StdErr" { return $result.StdErr; break }
                "ExitCode" { return $result.ExitCode; break }
                }
            }
        }
    catch {
        exit
        }
}

function Set-Patch {
    Param (
        [Parameter(Mandatory=$true)]  [String]$BasePath,
        [Parameter(Mandatory=$true)]  [String]$PatchFile,
        [Parameter(mandatory=$false)]  [Boolean]$IsBinary = $false,
        [Parameter(mandatory=$false)]  [Boolean]$IsVerbose = $false
    )
    $outputLevel = "StdErr"
    If($IsVerbose -eq $true) {
        $outputLevel = "Verbose"
    }
    Write-Output "Patching $PatchFile"
    If(Test-Path "$PatchFile" -PathType Leaf) {
        $params = "--forward -p0 -d $BasePath -i $PatchFile"
        # $params = @('--forward', '-p0', '-d', $BasePath, '-i', $PatchFile)
        if($IsBinary -eq $true){
            $params = "--forward -p0 -d $BasePath -i $PatchFile --binary"
        }
        $GitPath = (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition)
        If($IsVerbose -eq $true) {
            Write-Output "Running $GitPath $params"
        }
        Invoke-Process -FilePath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList "$params" -DisplayLevel "$outputLevel"
        # Start-Process -Filepath (Get-Command "$env:ProgramFiles\Git\usr\bin\patch.exe" | Select-Object -ExpandProperty Definition) -ArgumentList $params -Wait
    } else {
        Write-Output "Patch $PatchFile not found"
    }
}

function Invoke-ApplyPatches {
    Param (
        [Parameter(Mandatory=$true)]  [String]$CurDir
    )
    
    Write-Output "Invoke-ApplyPatches:"
    Write-Output '    patches\butler\__init__.py.diff'
    Set-Patch -BasePath "$CurDir\Lib\site-packages\" -PatchFile "$CurDir\patches\butler\__init__.py.diff"
    Write-Output '    patches\configobj.py.diff'
    Set-Patch -BasePath "$CurDir\Lib\site-packages\" -PatchFile "$CurDir\patches\configobj.py.diff"
    Write-Output '    patches\django\db\models\base.py.diff'
    Set-Patch -BasePath "$CurDir\Lib\site-packages\" -PatchFile "$CurDir\patches\django\db\models\base.py.diff"
    Write-Output '    patches\ntlm\HTTPNtlmAuthHandler.py.diff'
    Set-Patch -BasePath "$CurDir\Lib\site-packages\" -PatchFile "$CurDir\patches\ntlm\HTTPNtlmAuthHandler.py.diff" -IsBinary $true
    Write-Output '    patches\pykafka\topic.py.diff'
    Set-Patch -BasePath "$CurDir\Lib\site-packages\" -PatchFile "$CurDir\patches\pykafka\topic.py.diff"
    Write-Output '    patches\redis\redis\connection.py.diff'
    Set-Patch -BasePath "$CurDir\Lib\site-packages\" -PatchFile "$CurDir\patches\redis\redis\connection.py.diff"
    Write-Output '    patches\requests\models.py.diff'
    Set-Patch -BasePath "$CurDir\Lib\site-packages\" -PatchFile "$CurDir\patches\requests\models.py.diff"
    Write-Output '    patches\requests\sessions.py.diff'
    Set-Patch -BasePath "$CurDir\Lib\site-packages\" -PatchFile "$CurDir\patches\requests\sessions.py.diff"
    Write-Output '    patches\ws4py\server\geventserver.py.diff'
    Set-Patch -BasePath "$CurDir\Lib\site-packages\" -PatchFile "$CurDir\patches\ws4py\server\geventserver.py.diff"
    Write-Output '    patches\sqlalchemy\sql\dialects\postgresql\pg8000.py.diff'
    Set-Patch -BasePath "$CurDir\Lib\site-packages\" -PatchFile "$CurDir\patches\sqlalchemy\sql\dialects\postgresql\pg8000.py.diff"
    Write-Output '    patches\pg8000\core.py.diff'
    Set-Patch -BasePath "$CurDir\Lib\site-packages\" -PatchFile "$CurDir\patches\pg8000\core.py.diff"
    Write-Output '    patches\sqlalchemy\sql\crud.py.diff'
    Set-Patch -BasePath "$CurDir\Lib\site-packages\" -PatchFile "$CurDir\patches\sqlalchemy\sql\crud.py.diff"
}

function Invoke-InstallAllWithPip {
    Write-Output "Invoke-InstallAllWithPip"
    Write-Output '    .\requirements.txt'
    .\Scripts\pip.exe install -r .\requirements.txt
    Write-Output '    .\zato-common'
    .\Scripts\pip.exe install -e .\zato-common
    Write-Output '    .\zato-agent'
    .\Scripts\pip.exe install -e .\zato-agent
    Write-Output '    .\zato-broker'
    .\Scripts\pip.exe install -e .\zato-broker
    Write-Output '    .\zato-cli'
    .\Scripts\pip.exe install -e .\zato-cli
    Write-Output '    .\zato-client'
    .\Scripts\pip.exe install -e .\zato-client
    Write-Output '    .\zato-cy'
    .\Scripts\pip.exe install -e .\zato-cy
    Write-Output '    .\zato-distlock'
    .\Scripts\pip.exe install -e .\zato-distlock
    Write-Output '    .\zato-hl7'
    .\Scripts\pip.exe install -e .\zato-hl7
    Write-Output '    .\zato-lib'
    .\Scripts\pip.exe install -e .\zato-lib
    Write-Output '    .\zato-scheduler'
    .\Scripts\pip.exe install -e .\zato-scheduler
    Write-Output '    .\zato-server'
    .\Scripts\pip.exe install -e .\zato-server
    Write-Output '    .\zato-web-admin'
    .\Scripts\pip.exe install -e .\zato-web-admin
    Write-Output '    .\zato-zmq'
    .\Scripts\pip.exe install -e .\zato-zmq
    Write-Output '    .\zato-sso'
    .\Scripts\pip.exe install -e .\zato-sso
    Write-Output '    .\zato-testing'
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