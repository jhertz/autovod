#By BigTeddy 05 September 2011  <https://gallery.technet.microsoft.com/scriptcenter/Powershell-FileSystemWatche-dfd7084b>
#modified by jhertz

$folder = 'X:\Vods\pm' # Enter the root path you want to monitor.
$filter = '*.mp4'  # You can enter a wildcard filter here.

# In the following line, you can change 'IncludeSubdirectories to $true if required.                          
$fsw = New-Object IO.FileSystemWatcher $folder, $filter -Property @{IncludeSubdirectories = $false;NotifyFilter = [IO.NotifyFilters]'FileName, LastWrite'}

Register-ObjectEvent $fsw Created -SourceIdentifier FileCreated -Action {
$name = $Event.SourceEventArgs.Name
$changeType = $Event.SourceEventArgs.ChangeType
$timeStamp = $Event.TimeGenerated
Write-Host "The file '$name' was $changeType at $timeStamp" -fore green
& 'C:\Users\NYCPM\Desktop\autovod\uploader_pm.py' "--file" $name
}