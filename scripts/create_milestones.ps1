param (
    [Parameter(Mandatory=$true)]
    [string]$Token,
    
    [Parameter(Mandatory=$true)]
    [string]$Repo
)

$milestones = @(
    "Phase 0: Initialization & Core Infrastructure",
    "Phase 1: Authentication & Incident Management",
    "Phase 2: Log Ingestion & Parsing",
    "Phase 3: Automated IOC Extraction & Enrichment",
    "Phase 4: Event Correlation & MITRE ATT&CK Mapping",
    "Phase 5: Autonomous Investigation & Reporting",
    "Phase 6: Conversational Assistant (RAG)",
    "Phase 7: UI / Frontend Integration",
    "Phase 8: Polish, Performance, & Launch"
)

$headers = @{
    "Authorization" = "Bearer $Token"
    "Accept" = "application/vnd.github.v3+json"
}

foreach ($milestone in $milestones) {
    $body = @{
        title = $milestone
    } | ConvertTo-Json
    
    try {
        Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/milestones" -Method Post -Headers $headers -Body $body
        Write-Host "Created milestone: $milestone" -ForegroundColor Green
    } catch {
        Write-Host "Failed to create milestone: $milestone. Error: $_" -ForegroundColor Red
    }
}
