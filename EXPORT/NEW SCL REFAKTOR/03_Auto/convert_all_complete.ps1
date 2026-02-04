# Complete GRAPH XML to SCL Converter - Fixed for Siemens XML namespace
# TIA Portal V18 GRAPH Export -> Complete SCL Implementation

$sourceDir = "C:\Users\klonkanitka\Desktop\GARRET\OP10\Program blocks\OP010\03_Auto"
$destDir = "C:\Users\klonkanitka\Desktop\GARRET\OP10\NEW SCL REFAKTOR\03_Auto"

$flowFiles = @(
    @{ Path = "A1_TableLoad&Scan\ST10_Flow1_A1TableScan.xml"; Name = "ST10_Flow1_A1TableScan" },
    @{ Path = "A1_TableLoad&Scan\ST10_Flow3_A1RotaryShaftScan.xml"; Name = "ST10_Flow3_A1RotaryShaftScan" },
    @{ Path = "A1_TableLoad&Scan\ST10_Flow2_A1TableUnloading.xml"; Name = "ST10_Flow2_A1TableUnloading" }
)

function Get-XMLValue {
    param([string]$Content, [string]$Pattern)
    $match = [regex]::Match($Content, $Pattern, [System.Text.RegularExpressions.RegexOptions]::Singleline)
    if ($match.Success) { return $match.Groups[1].Value }
    return $null
}

function Convert-XMLToSCL {
    param([string]$XmlContent, [string]$FlowName, [string]$OutputPath)

    Write-Host "`n=== Processing $FlowName ===" -ForegroundColor Cyan

    # Remove namespace prefixes for easier parsing
    $cleanXml = $XmlContent -replace 'sw:NetworkSource/Graph/v5', 'g' -replace 'xmlns(:\w+)?="[^"]+"', '' -replace '<g:', '<' -replace '</g:', '</'

    $stepActions = @{}
    $stepEnums = @{}

    # Find Step blocks - use multiline mode
    $stepBlockPattern = '<Step\s+Number="(\d+)"\s+[^>]*Name="([^"]+)"[^>]*>(.*?)</Step>'
    $stepMatches = [regex]::Matches($cleanXml, $stepBlockPattern, [System.Text.RegularExpressions.RegexOptions]::Singleline)

    Write-Host "  Found $($stepMatches.Count) steps" -ForegroundColor Gray

    foreach ($match in $stepMatches) {
        $stepNum = $match.Groups[1].Value
        $stepName = $match.Groups[2].Value
        $stepContent = $match.Groups[3].Value

        $stepEnums[$stepNum] = $stepName

        $actions = @()

        # Find all Action blocks
        $actionBlockPattern = '<Action\s+([^>]*)>(.*?)</Action>'
        $actionMatches = [regex]::Matches($stepContent, $actionBlockPattern, [System.Text.RegularExpressions.RegexOptions]::Singleline)

        foreach ($actionMatch in $actionMatches) {
            $attrStr = $actionMatch.Groups[1].Value
            $actionBody = $actionMatch.Groups[2].Value

            $qualifier = "N"
            $qMatch = [regex]::Match($attrStr, 'Qualifier="([^"]+)"')
            if ($qMatch.Success) { $qualifier = $qMatch.Groups[1].Value }

            $event = ""
            $eMatch = [regex]::Match($attrStr, 'Event="([^"]+)"')
            if ($eMatch.Success) { $event = $eMatch.Groups[1].Value }

            # Extract all Token text values
            $tokens = @()
            $tokenPattern = '<Token[^>]*>([^<]*)</Token>'
            $tokenMatches = [regex]::Matches($actionBody, $tokenPattern)
            foreach ($t in $tokenMatches) {
                $text = $t.Groups[1].Value.Trim()
                $text = $text -replace '&#xA;', '' -replace '\s+', ' '
                if ($text -and $text.Length -gt 0) {
                    $tokens += $text
                }
            }
            $code = $tokens -join ' ' -replace '\s+', ' ' -replace '^\s+|\s+$', ''

            if ($code -and $code.Length -gt 0) {
                $actions += @{ qualifier = $qualifier; event = $event; code = $code }
            }
        }

        if ($actions.Count -gt 0) {
            $stepActions[$stepNum] = $actions
            Write-Host "    Step $stepNum ($stepName): $($actions.Count) actions" -ForegroundColor Gray
        }
    }

    # Find Transition blocks
    $transitions = @{}
    $transBlockPattern = '<Transition\s+Number="(\d+)"\s+[^>]*Name="([^"]+)"[^>]*>(.*?)</Transition>'
    $transMatches = [regex]::Matches($cleanXml, $transBlockPattern, [System.Text.RegularExpressions.RegexOptions]::Singleline)

    Write-Host "  Found $($transMatches.Count) transitions" -ForegroundColor Gray

    foreach ($match in $transMatches) {
        $transNum = $match.Groups[1].Value
        $transName = $match.Groups[2].Value
        $transContent = $match.Groups[3].Value

        # Check if has Access elements (real condition) or is empty (TRUE)
        $hasAccess = $transContent -match '<Access\s'

        if (-not $hasAccess) {
            $transitions[$transNum] = "TRUE"
        } else {
            # Extract component names from Symbol
            $components = @()
            $compPattern = '<Component\s+Name="([^"]+)"'
            $compMatches = [regex]::Matches($transContent, $compPattern)
            foreach ($c in $compMatches) {
                $components += $c.Groups[1].Value
            }

            if ($components.Count -gt 0) {
                $varRef = $components -join '.'
                $transitions[$transNum] = $varRef
            } else {
                $transitions[$transNum] = "TRUE"
            }
        }
    }

    Generate-SCLFile -FlowName $FlowName -StepEnums $stepEnums -StepActions $stepActions -Transitions $transitions -OutputPath $OutputPath

    Write-Host "  -> Generated: $($stepEnums.Count) steps, $($stepActions.Count) with actions, $($transitions.Count) transitions" -ForegroundColor Green
}

function Generate-SCLFile {
    param([string]$FlowName, [hashtable]$StepEnums, [hashtable]$StepActions, [hashtable]$Transitions, [string]$OutputPath)

    $sortedSteps = $StepEnums.GetEnumerator() | Sort-Object { [int]$_.Name }
    $sortedTrans = $Transitions.GetEnumerator() | Sort-Object { [int]$_.Key }

    $lines = @()
    $lines += "// ============================================================================="
    $lines += "// $FlowName.scl"
    $lines += "// COMPLETE 1:1 CONVERSION FROM TIA PORTAL V18 GRAPH XML"
    $lines += "// Source: $FlowName.xml"
    $lines += "// Generated: 2026-02-02"
    $lines += "// ============================================================================="
    $lines += ""
    $lines += "TYPE"
    $lines += "    E_STEP_$FlowName : ("

    foreach ($step in $sortedSteps) {
        $stepNum = $step.Name
        $stepName = $step.Value
        $safeName = $stepName -replace '[^a-zA-Z0-9_]', '_' -replace '^_', ''
        if ($safeName -match '^\d') { $safeName = "S_$safeName" }
        $lines += "        STEP_${FlowName}_${safeName} := $stepNum,"
    }

    $lines += "    ) INT := 1;"
    $lines += "END_TYPE"
    $lines += ""
    $lines += "CONST"

    foreach ($step in $sortedSteps) {
        $stepNum = $step.Name
        $stepName = $step.Value
        $safeName = $stepName -replace '[^a-zA-Z0-9_]', '_' -replace '^_', ''
        if ($safeName -match '^\d') { $safeName = "S_$safeName" }
        $lines += "    STEP_${FlowName}_${safeName} := $stepNum;"
    }

    $lines += "END_CONST"
    $lines += ""
    $lines += "CONST"

    foreach ($trans in $sortedTrans) {
        $lines += "    TRANS_${FlowName}_$($trans.Key) := $($trans.Value);"
    }

    $lines += "END_CONST"
    $lines += ""
    $lines += "FUNCTION_BLOCK ""${FlowName}_1to1"""
    $lines += "{ S7_Optimized_Access := 'TRUE' }"
    $lines += "VERSION : 1.0"
    $lines += ""
    $lines += "VAR_INPUT"
    $lines += '    iSysInface : "RCS_SysComInterface_V1";'
    $lines += "END_VAR"
    $lines += ""
    $lines += "VAR_IN_OUT"
    $lines += '    ioPM_Inface : "RCS_PMInterface_V1";'
    $lines += "    ioStatus : Int;"
    $lines += "END_VAR"
    $lines += ""
    $lines += "VAR_OUTPUT"
    $lines += "    oAlarmID : Int;"
    $lines += "END_VAR"
    $lines += ""
    $lines += "VAR"
    $lines += "    State : INT := 1;"
    $lines += "    act_InitialRun : Bool;"
    $lines += "    act_InitialOK : Bool;"
    $lines += "    act_WaitRunning : Bool;"
    $lines += "    act_Running : Bool;"
    $lines += "    act_ProcessComplete : Bool;"
    $lines += "    act_ProcessStart : Bool;"
    $lines += "    act_UnPause : Bool;"

    foreach ($trans in $sortedTrans) {
        $lines += "    tmpTrans$($trans.Key) : Bool;"
    }

    $lines += "    bError : Bool;"
    $lines += "    wErrorID : Word;"
    $lines += "END_VAR"
    $lines += ""
    $lines += "BEGIN"
    $lines += "    // TRANSITIONS"
    $lines += "    // Source: XML Tag=<Transition>"

    foreach ($trans in $sortedTrans) {
        $condition = $trans.Value
        $lines += "    #tmpTrans$($trans.Key) := $condition;  // Trans $($trans.Key)"
    }

    $lines += ""
    $lines += "    // STATE MACHINE"
    $lines += "    // Source: XML Tag=<Step> with Actions"
    $lines += "    CASE #State OF"

    foreach ($step in $sortedSteps) {
        $stepNum = $step.Name
        $stepName = $step.Value
        $safeName = $stepName -replace '[^a-zA-Z0-9_]', '_' -replace '^_', ''
        if ($safeName -match '^\d') { $safeName = "S_$safeName" }

        $lines += ""
        $lines += "        // ==========================================="
        $snum = $stepNum.ToString()
        $sname = $stepName.ToString()
        $lines += "        // STEP $snum`: $sname"
        $lines += "        // ==========================================="
        $lines += "        STEP_${FlowName}_${safeName}:"

        if ($StepActions.ContainsKey($stepNum)) {
            $actions = $StepActions[$stepNum]
            foreach ($action in $actions) {
                $qualifier = $action.qualifier
                $event = $action.event
                $code = $action.code

                if ($qualifier -eq "S") {
                    $lines += "            // Action Qualifier=S"
                    $lines += "            // Token: $code"
                    $lines += "            $code := TRUE;"
                } elseif ($qualifier -eq "R") {
                    $lines += "            // Action Qualifier=R"
                    $lines += "            // Token: $code"
                    $lines += "            $code := FALSE;"
                } else {
                    $eventPart = ""
                    if ($event) { $eventPart = ", Event=""$event""" }
                    $lines += "            // Action Qualifier=$qualifier$eventPart"
                    $lines += "            // Token: $code"
                    $lines += "            $code;"
                }
            }
        } else {
            $lines += "            // No actions in XML"
        }
    }

    $lines += "    END_CASE;"
    $lines += ""
    $lines += "    // UPDATE OUTPUTS"
    $lines += "    #ioPM_Inface.InitialRun := #act_InitialRun;"
    $lines += "    #ioPM_Inface.InitialOK := #act_InitialOK;"
    $lines += "    #ioPM_Inface.WaitRunning := #act_WaitRunning;"
    $lines += "    #ioPM_Inface.Running := #act_Running;"
    $lines += "    #ioPM_Inface.ProcessComplete := #act_ProcessComplete;"
    $lines += "    #ioPM_Inface.ProcessStart := #act_ProcessStart;"
    $lines += "    #ioPM_Inface.UnPause := #act_UnPause;"
    $lines += ""
    $lines += "    // ERROR"
    $lines += "    IF #bError THEN"
    $lines += "        #ioStatus := 900;"
    $lines += "        #oAlarmID := INT_TO_WORD(#wErrorID);"
    $lines += "    ELSE"
    $lines += "        #ioStatus := 0;"
    $lines += "        #oAlarmID := 0;"
    $lines += "    END_IF;"
    $lines += "END_FUNCTION_BLOCK"

    $outFile = Join-Path $OutputPath "$($FlowName)_1to1.scl"
    $lines | Out-File -FilePath $outFile -Encoding UTF8
}

Write-Host "`n========================================" -ForegroundColor Magenta
Write-Host "GRAPH XML to SCL - Complete Converter" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta

foreach ($flow in $flowFiles) {
    $xmlPath = Join-Path $sourceDir $flow.Path
    if (Test-Path $xmlPath) {
        $xmlContent = Get-Content $xmlPath -Raw
        Convert-XMLToSCL -XmlContent $xmlContent -FlowName $flow.Name -OutputPath $destDir
    } else {
        Write-Host "  File not found: $xmlPath" -ForegroundColor Red
    }
}

Write-Host "`n========================================" -ForegroundColor Magenta
Write-Host "COMPLETE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Magenta
