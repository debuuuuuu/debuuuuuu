# Daily job: rebuild the Claude usage banner and push it to the GitHub profile repo.
# Registered in Windows Task Scheduler as "GitHub profile usage banner".
Set-Location -LiteralPath $PSScriptRoot
$log = Join-Path $PSScriptRoot "update_usage.log"
function Log($msg) { "$(Get-Date -Format s) $msg" | Out-File -FilePath $log -Append -Encoding utf8 }

python build_usage.py 2>&1 | ForEach-Object { Log $_ }
git add assets/claude-usage.svg
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m "chore: update claude usage banner" 2>&1 | ForEach-Object { Log $_ }
}
# push every run, so a failed push yesterday gets retried today
git push 2>&1 | ForEach-Object { Log $_ }
if ($LASTEXITCODE -eq 0) { Log "ok" } else { Log "push failed" }
