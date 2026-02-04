# Enhanced GRAPH XML to SCL Converter
# Extracts Actions and Transitions from XML

$sourceDir = "C:\Users\klonkanitka\Desktop\GARRET\OP10\Program blocks\OP010\03_Auto"
$destDir = "C:\Users\klonkanitka\Desktop\GARRET\OP10\NEW SCL REFAKTOR\03_Auto"

$flowFiles = @(
    @{ Path = "A1_TableLoad&Scan\ST10_Flow2_A1TableUnloading.xml"; Name = "ST10_Flow2_A1TableUnloading" }
)

function Convert-XMLToSCL {
    param(
        [string]$XmlContent,
        [string]$FlowName,
        [string]$OutputPath
    )

    # Extract all Actions with Qualifier and Token
    $actionPattern = '<Action[^>]*>(.*?)</Action>'
    $actionMatches = [regex]::Matches($XmlContent, $actionPattern, [System.Text.RegularExpressions.RegexOptions]::Singleline)

    $actionsByStep = @{}
    foreach ($match in $actionMatches) {
        $actionContent = $match.Groups[1].Value

        # Find which step this action belongs to
        $stepMatch = [regex]::Match($actionContent, 'Number="(\d+)"')
        if (-not $stepMatch.Success) {
            # Try finding step from context
            $stepMatch = [regex]::Match($XmlContent, "<Step[^>]*Number=""(\d+)""[^>]*>.*?<Actions>.*?<Action[^>]*>(.*?)</Action>", [System.Text.RegularExpressions.RegexOptions]::Singleline)
        }

        # Extract qualifier
        $qualifier = "N"
        $qualifierMatch = [regex]::Match($actionContent, 'Qualifier="([^"]+)"')
        if ($qualifierMatch.Success) {
            $qualifier = $qualifierMatch.Groups[1].Value
        }

        # Extract event (S1, etc)
        $event = ""
        $eventMatch = [regex]::Match($actionContent, 'Event="([^"]+)"')
        if ($eventMatch.Success) {
            $event = $eventMatch.Groups[1].Value
        }

        # Extract Token text
        $tokens = @()
        $tokenMatches = [regex]::Matches($actionContent, '<Token[^>]*>([^<]*)</Token>')
        foreach ($token in $tokenMatches) {
            $tokenText = $token.Groups[1].Value.Trim()
            if ($tokenText -and $tokenText -ne "&#xA;") {
                $tokens += $tokenText
            }
        }

        if ($tokens.Count -gt 0) {
            $actionCode = $tokens -join " " -replace '\s+', ' ' -replace '&#xA;', '' -replace '\s+', ' '
            Write-Host "  Action: Qualifier=$qualifier, Event=$event, Code=$actionCode"
        }
    }

    # Extract all Transitions
    $transPattern = '<Transition[^>]*Number="(\d+)"[^>]*Name="([^"]+)"[^>]*>(.*?)</Transition>'
    $transMatches = [regex]::Matches($XmlContent, $transPattern, [System.Text.RegularExpressions.RegexOptions]::Singleline)

    $transitions = @{}
    foreach ($match in $transMatches) {
        $transNum = $match.Groups[1].Value
        $transName = $match.Groups[2].Value
        $transContent = $match.Groups[3].Value

        # Check if empty (TRUE condition)
        $isEmpty = $transContent -match '<FlgNet>\s*<Parts>\s*<Part Name="TrCoil"'

        if ($isEmpty) {
            $transitions[$transNum] = "TRUE"
        } else {
            # Extract Access symbols
            $accessPattern = '<Symbol>\s*<Component Name="([^"]+)"[^/>]*(?:/>|</Component>)(.*?)</Symbol>'
            $accessMatches = [regex]::Matches($transContent, $accessPattern, [System.Text.RegularExpressions.RegexOptions]::Singleline)

            $components = @()
            foreach ($am in $accessMatches) {
                $components += $am.Groups[1].Value
            }

            if ($components.Count -gt 0) {
                $transitions[$transNum] = '"' + ($components -join '"."') + '"'
            } else {
                $transitions[$transNum] = "TRUE"
            }
        }
        Write-Host "  Transition $transNum ($transName): $($transitions[$transNum])"
    }

    return @{ Actions = $actionsByStep; Transitions = $transitions }
}

foreach ($flow in $flowFiles) {
    $xmlPath = Join-Path $sourceDir $flow.Path
    Write-Host "`nProcessing: $($flow.Name)..."

    if (Test-Path $xmlPath) {
        $xmlContent = Get-Content $xmlPath -Raw
        $result = Convert-XMLToSCL -XmlContent $xmlContent -FlowName $flow.Name -OutputPath $destDir
    } else {
        Write-Host "  File not found: $xmlPath"
    }
}
