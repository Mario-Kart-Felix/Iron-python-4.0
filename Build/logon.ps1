
param(
    [Parameter()]
    [switch]$RunPowershell
)

$ErrorActionPreference = "Stop"


try
{
    # Need to have network connection to continue, wait 30
    # seconds for the network to be active.
    start-sleep -s 30

        # Inject extra drivers if the infs directory is present on the attached iso
        if (Test-Path -Path "E:\infs")
        {
            # To install extra drivers the Windows Driver Kit is needed for dpinst.exe.
            # Sadly you cannot just download dpinst.exe. The whole driver kit must be
            # installed.

            # Download the WDK installer.
            $Host.UI.RawUI.WindowTitle = "Downloading Windows Driver Kit..."
            $webclient = New-Object System.Net.WebClient
            $wdksetup = [IO.Path]::GetFullPath("$ENV:TEMP\wdksetup.exe")
            $wdkurl = "http://download.microsoft.com/download/0/8/C/08C7497F-8551-4054-97DE-60C0E510D97A/wdk/wdksetup.exe"
            $webclient.DownloadFile($wdkurl, $wdksetup)

            # Run the installer.
            $Host.UI.RawUI.WindowTitle = "Installing Windows Driver Kit..."
            $p = Start-Process -PassThru -Wait -FilePath "$wdksetup" -ArgumentList "/features OptionId.WindowsDriverKitComplete /q /ceip off /norestart"
            if ($p.ExitCode -ne 0)
            {
                throw "Installing $wdksetup failed."
            }

            # Run dpinst.exe with the path to the drivers.
            $Host.UI.RawUI.WindowTitle = "Injecting Windows drivers..."
            $dpinst = "$programFilesDir\Windows Kits\8.1\redist\DIFx\dpinst\EngMui\$archDir\dpinst.exe"
            Start-Process -Wait -FilePath "$dpinst" -ArgumentList "/S /C /F /SA /Path E:\infs"

            # Uninstall the WDK
            $Host.UI.RawUI.WindowTitle = "Uninstalling Windows Driver Kit..."
            Start-Process -Wait -FilePath "$wdksetup" -ArgumentList "/features + /q /uninstall /norestart"
        }

        $Host.UI.RawUI.WindowTitle = "Installing Cloudbase-Init..."
    	wget "https://cloudbase.it/downloads/CloudbaseInitSetup_Stable_x64.msi" -outfile "c:\cloudbase.msi"
        $cloudbaseInitPath = "c:\cloudbase.msi"
        $cloudbaseInitLog = "$ENV:Temp\cloudbase_init.log"
        $serialPortName = @(Get-WmiObject Win32_SerialPort)[0].DeviceId
        $p = Start-Process -Wait -PassThru -FilePath msiexec -ArgumentList "/i $cloudbaseInitPath /qn /norestart /l*v $cloudbaseInitLog LOGGINGSERIALPORTNAME=$serialPortName RUN_SERVICE_AS_LOCAL_SYSTEM=1"
        if ($p.ExitCode -ne 0)
        {
            throw "Installing $cloudbaseInitPath failed. Log: $cloudbaseInitLog"
        }
        if (Test-Path -Path "E:\cloudbase\cloudbase_init.zip")
        {
            Add-Type -AssemblyName System.IO.Compression.FileSystem
            New-Item -Path "$ENV:TEMP\cloudbase-init" -Type directory
            [System.IO.Compression.ZipFile]::ExtractToDirectory("E:\cloudbase\cloudbase_init.zip", "$ENV:TEMP\cloudbase-init")

            Remove-Item -Recurse -Force "$ENV:ProgramFiles\Cloudbase Solutions\Cloudbase-Init\Python\Lib\site-packages\cloudbaseinit"
            Copy-Item -Recurse -Path "$ENV:TEMP\cloudbase-init\cloudbaseinit" -Destination "$ENV:ProgramFiles\Cloudbase Solutions\Cloudbase-Init\Python\Lib\site-packages\"
        }
        Set-Service -Name "cloudbase-init" -StartupType "Automatic"
    	# install virtio drivers
        certutil -addstore "TrustedPublisher" A:/rh.cer
    	[Net.ServicePointManager]::SecurityProtocol = "Tls, Tls11, Tls12, Ssl3"
    	wget "https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/archive-virtio/virtio-win-0.1.185-2/virtio-win-gt-x64.msi" -outfile "c:\virtio.msi"
    	wget "https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/archive-virtio/virtio-win-0.1.185-2/virtio-win-guest-tools.exe" -outfile "c:\virtio.exe"
    	$virtioPath = "c:\virtio.msi"
        $virtioLog = "$ENV:Temp\virtio.log"
        $serialPortName = @(Get-WmiObject Win32_SerialPort)[0].DeviceId
        $p = Start-Process -Wait -PassThru -FilePath msiexec -ArgumentList "/a $virtioPath /qn /quiet /norestart /l*v $virtioLog LOGGINGSERIALPORTNAME=$serialPortName"
	    Start-Process -Wait -FilePath C:\virtio.exe -Argument "/silent" -PassThru


        # We're done, remove LogonScript, disable AutoLogon
        Remove-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" -Name Unattend*
        Remove-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" -Name AutoLogonCount


        $Host.UI.RawUI.WindowTitle = "Running SetSetupComplete..."
        & "$ENV:ProgramFiles\Cloudbase Solutions\Cloudbase-Init\bin\SetSetupComplete.cmd"

        # Write success, this is used to check that this process made it this far
        New-Item -Path C:\success.tch -Type file -Force

        if ($RunPowershell) {
            $Host.UI.RawUI.WindowTitle = "Paused, waiting for user to finish work in other terminal"
            Write-Host "Spawning another powershell for the user to complete any work..."
            Start-Process -Wait -PassThru -FilePath powershell
        }

        $Host.UI.RawUI.WindowTitle = "Running Sysprep..."
        $unattendedXmlPath = "$ENV:ProgramFiles\Cloudbase Solutions\Cloudbase-Init\conf\Unattend.xml"
        & "$ENV:SystemRoot\System32\Sysprep\Sysprep.exe" `/generalize `/oobe `/shutdown `/unattend:"$unattendedXmlPath"
    
}
catch
{
    $_ | Out-File C:\error_log.txt
}
