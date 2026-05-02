$APP_NAME = "ArabicEngLearn"
$BASE = "C:\langapp-automation"

function Check-Dependencies {
    Write-Host "`n[1/4] Checking Python..." -ForegroundColor Cyan
    python --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Python not found. Install from python.org" -ForegroundColor Red
        return $false
    }

    Write-Host "[2/4] Installing Python packages..." -ForegroundColor Cyan
    pip install -r "$BASE\requirements.txt" --quiet

    Write-Host "[3/4] Checking ffmpeg..." -ForegroundColor Cyan
    ffmpeg -version 2>$null | Select-Object -First 1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ffmpeg not found. Install with: winget install ffmpeg" -ForegroundColor Yellow
    }

    Write-Host "[4/4] Checking config..." -ForegroundColor Cyan
    $configContent = Get-Content "$BASE\config.py" -Raw
    if ($configContent -match "YOUR_KEY_HERE") {
        Write-Host "IMPORTANT: Edit config.py and set your API keys!" -ForegroundColor Yellow
        Write-Host "  - FIREWORKS_API_KEY (required) — get from fireworks.ai" -ForegroundColor Yellow
        Write-Host "  - REDDIT_* (optional for Reddit bot)" -ForegroundColor Yellow
        Write-Host "  - TIKTOK_* (optional, will prompt on first login)" -ForegroundColor Yellow
        return $false
    }

    return $true
}

function Run-Pipeline {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "  ArabicEngLearn — Full Pipeline" -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Green

    Write-Host "Step 1/3: Generating scenarios with AI..." -ForegroundColor Cyan
    python "$BASE\scripts\01_generate_scenarios.py"
    if ($LASTEXITCODE -ne 0) { Write-Host "Step 1 FAILED" -ForegroundColor Red; return }

    Write-Host "`nStep 2/3: Generating video frames..." -ForegroundColor Cyan
    python "$BASE\scripts\02_generate_frames.py"
    if ($LASTEXITCODE -ne 0) { Write-Host "Step 2 FAILED" -ForegroundColor Red; return }

    Write-Host "`nStep 3/3: Assembling videos..." -ForegroundColor Cyan
    python "$BASE\scripts\03_assemble_videos.py"
    if ($LASTEXITCODE -ne 0) { Write-Host "Step 3 FAILED" -ForegroundColor Red; return }

    Write-Host "`nDONE! Videos saved to $BASE\output\videos\" -ForegroundColor Green
    Write-Host "Next: Run menu to post them — python $BASE\scripts\run.py" -ForegroundColor Green
}

function Post-Next {
    python "$BASE\scripts\04_autopost_tiktok.py"
}

function Reddit-Respond {
    python "$BASE\scripts\05_reddit_responder.py"
}

function Comment-Reply {
    python "$BASE\scripts\06_comment_responder.py"
}

function Analytics {
    python "$BASE\scripts\07_analytics_report.py"
}

function Show-Menu {
    Clear-Host
    Write-Host ""
    Write-Host "  ╔══════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "  ║   ArabicEngLearn — Automation Suite       ║" -ForegroundColor Cyan
    Write-Host "  ╚══════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  1. Setup & check dependencies" -ForegroundColor White
    Write-Host "  2. Full pipeline (scenarios → frames → videos)" -ForegroundColor White
    Write-Host "  3. Generate scenarios only" -ForegroundColor White
    Write-Host "  4. Generate frames only" -ForegroundColor White
    Write-Host "  5. Assemble videos only" -ForegroundColor White
    Write-Host "  6. Post next video to TikTok" -ForegroundColor White
    Write-Host "  7. Reddit auto-respond" -ForegroundColor White
    Write-Host "  8. Comment auto-reply" -ForegroundColor White
    Write-Host "  9. Analytics report" -ForegroundColor White
    Write-Host "  10. Login to TikTok (first time)" -ForegroundColor White
    Write-Host "  0. Exit" -ForegroundColor White
    Write-Host ""
}

$running = $true
while ($running) {
    Show-Menu
    $choice = Read-Host "Choose (0-10)"
    
    switch ($choice) {
        "0" { $running = $false }
        "1" { Check-Dependencies; Read-Host "Press Enter" }
        "2" { Run-Pipeline; Read-Host "Press Enter" }
        "3" { python "$BASE\scripts\01_generate_scenarios.py"; Read-Host "Press Enter" }
        "4" { python "$BASE\scripts\02_generate_frames.py"; Read-Host "Press Enter" }
        "5" { python "$BASE\scripts\03_assemble_videos.py"; Read-Host "Press Enter" }
        "6" { Post-Next; Read-Host "Press Enter" }
        "7" { Reddit-Respond; Read-Host "Press Enter" }
        "8" { Comment-Reply; Read-Host "Press Enter" }
        "9" { Analytics; Read-Host "Press Enter" }
        "10" { python "$BASE\scripts\04_autopost_tiktok.py" --login; Read-Host "Press Enter" }
        default { Write-Host "Invalid choice" -ForegroundColor Red; Start-Sleep 1 }
    }
}
