# Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/luphysics/PyMODA/dev/dist/windows/install.ps1')) 

Write-Output "Downloading PyMODA. Please wait, this may take over a minute..."

$url = "https://github.com/luphysics/PyMODA/releases/latest/download/PyMODA-win64.zip"

$targetDir = "$env:AppData\PyMODA"
$targetFile = "$targetDir\pymoda.zip"

### Download the .zip file ###

$uri = New-Object "System.Uri" "$url"

$request = [System.Net.HttpWebRequest]::Create($uri)
$request.set_Timeout(15000)
$response = $request.GetResponse()

$totalLength = [System.Math]::Floor($response.get_ContentLength()/1024)
$responseStream = $response.GetResponseStream()
$targetStream = New-Object -TypeName System.IO.FileStream -ArgumentList $targetFile, Create

$buffer = new-object byte[] 10KB
$count = $responseStream.Read($buffer,0,$buffer.length)
$downloadedBytes = $count

while ($count -gt 0)
{
    $targetStream.Write($buffer, 0, $count)
    $count = $responseStream.Read($buffer,0,$buffer.length)
    $downloadedBytes = $downloadedBytes + $count
    Write-Progress -activity "Downloading file '$($url.split('/') | Select -Last 1)'" -status "Downloaded ($([System.Math]::Floor($downloadedBytes/1024))K of $($totalLength)K): " -PercentComplete ((([System.Math]::Floor($downloadedBytes/1024)) / $totalLength)  * 100)
}

Write-Progress -activity "Finished downloading file '$($url.split('/') | Select -Last 1)'"

$targetStream.Flush()
$targetStream.Close()
$targetStream.Dispose()
$responseStream.Dispose()

### Extract the .zip file ###

Write-Output "Extracting PyMODA..."

mkdir -Force "$targetDir\PyMODA"
rm -r "$targetDir\PyMODA"

Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory($targetFile, $targetDir)

Write-Output "Cleaning up..."
rm $targetFile

Write-Output "Launching PyMODA..."
& "$targetDir\PyMODA\PyMODA.exe" --create-shortcut