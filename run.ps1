$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

$nodeHome = "C:\Program Files\nodejs"
if (Test-Path $nodeHome) {
    $env:Path = "$nodeHome;$env:Path"
}

$backendCommand = "Set-Location '$projectRoot'; python -m pip install -r requirements.txt; if (-not (Test-Path 'models\skill_classifier.joblib')) { python src\prepare_dataset.py --samples-per-skill 24; python src\train_model.py }; python app.py"
$frontendCommand = "Set-Location '$projectRoot\frontend'; `$env:Path = '$nodeHome;' + `$env:Path; npm.cmd install; npm.cmd start"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand
Start-Sleep -Seconds 3
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCommand
