Try
{
    $CURDIR = (Split-Path $myInvocation.MyCommand.Path) -join "`n"

    . $CURDIR\..\_common.ps1
    
    $params = "$CURDIR\zato-windows.py "
    $params += $args
    
    Invoke-Process -FilePath $CURDIR\python.exe -ArgumentList $params -DisplayLevel "Verbose"
}
Catch
{
    Write-Output "Ran into an issue: $($PSItem.ToString())"
}