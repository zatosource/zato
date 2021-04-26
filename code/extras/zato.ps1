Try
{
    $CURDIR = (Split-Path $myInvocation.MyCommand.Path) -join "`n"

    . $CURDIR\..\_common.ps1
    
    $params = "$CURDIR\zato-windows.py "
    $params += $args
    Write-Output "*** Running $CURDIR\python.exe $params ***"
    
    Start-Process -FilePath $CURDIR\python.exe -ArgumentList $params -Wait
}
Catch
{
    Write-Output "Ran into an issue: $($PSItem.ToString())"
}