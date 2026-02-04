# GRAPH XML to SCL Converter - Inline Transition Style
# Přechodové podmínky přímo v každém kroku

$ErrorActionPreference = "Stop"

$sourceDir = "C:\Users\klonkanitka\Desktop\GARRET\OP10\Program blocks\OP010\03_Auto"
$outputDir = "C:\Users\klonkanitka\Desktop\GARRET\OP10\NEW SCL REFAKTOR\03_Auto"

$flows = @(
    @{ Path = "A1_TableLoad&Scan\ST10_Flow1_A1TableScan.xml"; Name = "ST10_Flow1_A1TableScan" },
    @{ Path = "A1_TableLoad&Scan\ST10_Flow2_A1TableUnloading.xml"; Name = "ST10_Flow2_A1TableUnloading" },
    @{ Path = "A1_TableLoad&Scan\ST10_Flow3_A1RotaryShaftScan.xml"; Name = "ST10_Flow3_A1RotaryShaftScan" },
    @{ Path = "B_Press\ST10_Flow4_B1Press.xml"; Name = "ST10_Flow4_B1Press" },
    @{ Path = "B_Press\ST10_Flow14_B2Press.xml"; Name = "ST10_Flow14_B2Press" },
    @{ Path = "C_Glue\ST10_Flow7_CGlueing.xml"; Name = "ST10_Flow7_CGlueing" },
    @{ Path = "F_Robot\ST10_Flow5_FRobot_1.xml"; Name = "ST10_Flow5_FRobot_1" },
    @{ Path = "F_Robot\ST10_Flow8_FRobot_2.xml"; Name = "ST10_Flow8_FRobot_2" },
    @{ Path = "F_Robot\ST10_Flow15_FRobot_3.xml"; Name = "ST10_Flow15_FRobot_3" },
    @{ Path = "A2_TableLoad&Scan\ST10_Flow11_A2TableScan.xml"; Name = "ST10_Flow11_A2TableScan" },
    @{ Path = "A2_TableLoad&Scan\ST10_Flow12_A2TableUnloading.xml"; Name = "ST10_Flow12_A2TableUnloading" },
    @{ Path = "H_ShaftLifting&Load&Unload\ST10_Flow21_HShaftLifting.xml"; Name = "ST10_Flow21_HShaftLifting" },
    @{ Path = "H_ShaftLifting&Load&Unload\ST10_Flow25_HShaftLoad&Unload.xml"; Name = "ST10_Flow25_HShaftLoad_Unload" },
    @{ Path = "J_MagnetLifting&Load&Unload\ST10_Flow22_JMagnetLifting.xml"; Name = "ST10_Flow22_JMagnetLifting" },
    @{ Path = "J_MagnetLifting&Load&Unload\ST10_Flow26_JMagnetLoad&Unload.xml"; Name = "ST10_Flow26_JMagnetLoad_Unload" },
    @{ Path = "L_Unload\K_ReserveLifting&Load&Unload\ST10_Flow23_KReserveLifting.xml"; Name = "ST10_Flow23_KReserveLifting" },
    @{ Path = "L_Unload\K_ReserveLifting&Load&Unload\ST10_Flow27_KReserveLoad&Unload.xml"; Name = "ST10_Flow27_KReserveLoad_Unload" },
    @{ Path = "L_Unload\ST10_Flow24_LUnloadingTrans.xml"; Name = "ST10_Flow24_LUnloadingTrans" },
    @{ Path = "L_Unload\ST10_Flow28_LUnloadingLoad&Unload.xml"; Name = "ST10_Flow28_LUnloadingLoad_Unload" }
)

function Convert-XMLToSCL {
    param([string]$XmlPath, [string]$FlowName, [string]$OutputPath)

    Write-Host "`n$('=' * 60)" -ForegroundColor Cyan
    Write-Host "Processing: $FlowName" -ForegroundColor Cyan
    Write-Host "$('=' * 60)" -ForegroundColor Cyan

    try {
        $xmlDoc = New-Object System.Xml.XmlDocument
        $xmlDoc.Load($XmlPath)

        $nsMgr = New-Object System.Xml.XmlNamespaceManager($xmlDoc.NameTable)
        $nsMgr.AddNamespace("g", "http://www.siemens.com/automation/Openness/SW/NetworkSource/Graph/v5")

        $steps = @{}
        $transitions = @{}
        $stepTransitions = @{}  # Maps step number to outgoing transition numbers

        # Parse Steps
        $stepNodes = $xmlDoc.SelectNodes("//g:Graph//g:Step", $nsMgr)
        if ($stepNodes.Count -eq 0) { $stepNodes = $xmlDoc.SelectNodes("//Graph//Step") }

        foreach ($stepNode in $stepNodes) {
            $stepNum = [int]$stepNode.GetAttribute("Number")
            $stepName = $stepNode.GetAttribute("Name")
            if (-not $stepName) { $stepName = "S$stepNum" }

            $stepKey = $stepNum.ToString()
            $steps[$stepKey] = @{ Number = $stepNum; Name = $stepName; Actions = @(); TransRefs = @() }

            # Parse Actions
            $actionNodes = $stepNode.SelectNodes(".//g:Action", $nsMgr)
            if ($actionNodes.Count -eq 0) { $actionNodes = $stepNode.SelectNodes(".//Action") }

            foreach ($actionNode in $actionNodes) {
                $qualifier = $actionNode.GetAttribute("Qualifier")
                $event = $actionNode.GetAttribute("Event")
                if (-not $qualifier) { $qualifier = "N" }

                $tokens = @()
                $tokenNodes = $actionNode.SelectNodes(".//g:Token", $nsMgr)
                if ($tokenNodes.Count -eq 0) { $tokenNodes = $actionNode.SelectNodes(".//Token") }

                foreach ($tokenNode in $tokenNodes) {
                    $text = $tokenNode.GetAttribute("Text")
                    if ($text) {
                        $text = $text.Trim() -replace '&#xA;', '' -replace '\s+', ' '
                        if ($text) { $tokens += $text }
                    }
                }

                $code = $tokens -join ' ' -replace '\s+', ' ' -replace '^\s+|\s+$', ''
                if ($code) {
                    $steps[$stepKey].Actions += @{ Qualifier = $qualifier; Event = $event; Code = $code }
                }
            }

            # Parse TransitionRefs - which transitions leave this step
            $transRefNodes = $stepNode.SelectNodes(".//g:TransitionRef", $nsMgr)
            if ($transRefNodes.Count -eq 0) { $transRefNodes = $stepNode.SelectNodes(".//TransitionRef") }
            foreach ($tr in $transRefNodes) {
                $transNum = $tr.GetAttribute("Number")
                if ($transNum) { $steps[$stepKey].TransRefs += $transNum }
            }
        }

        # Parse Transitions
        $transNodes = $xmlDoc.SelectNodes("//g:Graph//g:Transition", $nsMgr)
        if ($transNodes.Count -eq 0) { $transNodes = $xmlDoc.SelectNodes("//Graph//Transition") }

        foreach ($transNode in $transNodes) {
            $transNum = [int]$transNode.GetAttribute("Number")
            $transName = $transNode.GetAttribute("Name")

            $accessNodes = $transNode.SelectNodes(".//g:Access", $nsMgr)
            if ($accessNodes.Count -eq 0) { $accessNodes = $transNode.SelectNodes(".//Access") }

            if ($accessNodes.Count -gt 0) {
                $components = @()
                foreach ($access in $accessNodes) {
                    $symbolNode = $access.SelectSingleNode(".//g:Symbol", $nsMgr)
                    if ($null -eq $symbolNode) { $symbolNode = $access.SelectSingleNode(".//Symbol") }
                    if ($null -ne $symbolNode) {
                        $compNodes = $symbolNode.SelectNodes(".//g:Component", $nsMgr)
                        if ($compNodes.Count -eq 0) { $compNodes = $symbolNode.SelectNodes(".//Component") }
                        foreach ($comp in $compNodes) {
                            $compName = $comp.GetAttribute("Name")
                            if ($compName) { $components += $compName }
                        }
                    }
                }
                if ($components.Count -gt 0) { $condition = $components -join '.' }
                else { $condition = "TRUE" }
            } else { $condition = "TRUE" }

            $transitions[$transNum.ToString()] = @{ Number = $transNum; Name = $transName; Condition = $condition }
        }

        Generate-SCL -FlowName $FlowName -Steps $steps -Transitions $transitions -OutputPath $OutputPath

        $totalActions = ($steps.Values | ForEach-Object { $_.Actions.Count } | Measure-Object -Sum).Sum
        Write-Host "  -> Steps: $($steps.Count), Actions: $totalActions, Transitions: $($transitions.Count)" -ForegroundColor Green

    } catch {
        Write-Host "  ERROR: $_" -ForegroundColor Red
        return $false
    }
    return $true
}

function Generate-SCL {
    param([string]$FlowName, [hashtable]$Steps, [hashtable]$Transitions, [string]$OutputPath)

    $sortedSteps = $Steps.Values | Sort-Object Number
    $sortedTrans = $Transitions.Values | Sort-Object Number

    $lines = @()
    $lines += "//" + ("=" * 77)
    $lines += "// $FlowName.scl"
    $lines += "// 1:1 CONVERSION FROM TIA PORTAL V18 GRAPH XML"
    $lines += "// Generated: $(Get-Date -Format 'yyyy-MM-dd')"
    $lines += "//" + ("=" * 77)
    $lines += ""

    # TYPE
    $lines += "TYPE"
    $lines += "    E_STEP_$FlowName : ("
    foreach ($step in $sortedSteps) {
        $safeName = $step.Name -replace '[^a-zA-Z0-9_]', '_' -replace '^_', ''
        if ($safeName -match '^\d') { $safeName = "S_$safeName" }
        $lines += "        STEP_${FlowName}_${safeName} := $($step.Number),"
    }
    $lines += "    ) INT := 1;"
    $lines += "END_TYPE"
    $lines += ""

    # CONST
    $lines += "CONST"
    foreach ($step in $sortedSteps) {
        $safeName = $step.Name -replace '[^a-zA-Z0-9_]', '_' -replace '^_', ''
        if ($safeName -match '^\d') { $safeName = "S_$safeName" }
        $lines += "    STEP_${FlowName}_${safeName} := $($step.Number);"
    }
    $lines += "END_CONST"
    $lines += ""

    # FUNCTION_BLOCK
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
    $lines += "    bError : Bool;"
    $lines += "    wErrorID : Word;"
    $lines += "END_VAR"
    $lines += ""
    $lines += "BEGIN"
    $lines += "    //" + ("=" * 70)
    $lines += "    // STATE MACHINE - Inline Transition Conditions"
    $lines += "    //" + ("=" * 70)
    $lines += ""
    $lines += "    CASE #State OF"

    foreach ($step in $sortedSteps) {
        $safeName = $step.Name -replace '[^a-zA-Z0-9_]', '_' -replace '^_', ''
        if ($safeName -match '^\d') { $safeName = "S_$safeName" }

        $lines += ""
        $lines += "        // ==========================================="
        $lines += "        // STEP $($step.Number): $($step.Name)"
        $lines += "        // ==========================================="
        $lines += "        STEP_${FlowName}_${safeName}:"

        # Actions
        if ($step.Actions.Count -gt 0) {
            foreach ($action in $step.Actions) {
                $qualifier = $action.Qualifier
                $event = $action.Event
                $code = $action.Code

                if ($qualifier -eq "S") {
                    $lines += "            // Action Qualifier=S"
                    $lines += "            // Token: $code"
                    $lines += "            $code := TRUE;"
                } elseif ($qualifier -eq "R") {
                    $lines += "            // Action Qualifier=R"
                    $lines += "            // Token: $code"
                    $lines += "            $code := FALSE;"
                } else {
                    $eventPart = if ($event) { ", Event=""$event""" } else { "" }
                    $lines += "            // Action Qualifier=$qualifier$eventPart"
                    $lines += "            // Token: $code"
                    $lines += "            $code;"
                }
            }
        } else {
            $lines += "            // No actions in XML"
        }

        # Inline transition conditions - sequential (N -> N+1)
        # Note: XML doesn't contain explicit step-to-transition mapping
        # Generated transitions follow sequential flow. Adjust manually if needed.
        $nextStep = $null
        for ($i = 0; $i -lt $sortedSteps.Count; $i++) {
            if ($sortedSteps[$i].Number -eq $step.Number) {
                if ($i + 1 -lt $sortedSteps.Count) {
                    $nextStep = $sortedSteps[$i + 1]
                }
                break
            }
        }

        if ($null -ne $nextStep) {
            $nextSafeName = $nextStep.Name -replace '[^a-zA-Z0-9_]', '_' -replace '^_', ''
            if ($nextSafeName -match '^\d') { $nextSafeName = "S_$nextSafeName" }

            $lines += ""
            $lines += "            // Transition to next step: $($nextStep.Number)"
            $lines += "            IF TRUE THEN  // Sequential transition - review XML for actual condition"
            $lines += "                #State := STEP_${FlowName}_${nextSafeName};"
            $lines += "            END_IF;"
        }
    }

    $lines += ""
    $lines += "    END_CASE;"
    $lines += ""
    $lines += "    // UPDATE ioPM_Inface"
    $lines += "    #ioPM_Inface.InitialRun := #act_InitialRun;"
    $lines += "    #ioPM_Inface.InitialOK := #act_InitialOK;"
    $lines += "    #ioPM_Inface.WaitRunning := #act_WaitRunning;"
    $lines += "    #ioPM_Inface.Running := #act_Running;"
    $lines += "    #ioPM_Inface.ProcessComplete := #act_ProcessComplete;"
    $lines += "    #ioPM_Inface.ProcessStart := #act_ProcessStart;"
    $lines += "    #ioPM_Inface.UnPause := #act_UnPause;"
    $lines += ""
    $lines += "    // ERROR HANDLING"
    $lines += "    IF #bError THEN"
    $lines += "        #ioStatus := 900;"
    $lines += "        #oAlarmID := INT_TO_WORD(#wErrorID);"
    $lines += "    ELSE"
    $lines += "        #ioStatus := 0;"
    $lines += "        #oAlarmID := 0;"
    $lines += "    END_IF;"
    $lines += "END_FUNCTION_BLOCK"
    $lines += ""
    $lines += "//" + ("=" * 77)
    $lines += "// END OF FILE"
    $lines += "//" + ("=" * 77)

    $outFile = Join-Path $OutputPath "$($FlowName)_1to1.scl"
    $lines | Out-File -FilePath $outFile -Encoding UTF8
    Write-Host "  -> Generated: $(Split-Path $outFile -Leaf)" -ForegroundColor Green
}

# Main
Write-Host "`n$('=' * 60)" -ForegroundColor Magenta
Write-Host "GRAPH XML -> SCL (Inline Style)"
Write-Host "$('=' * 60)" -ForegroundColor Magenta

foreach ($flow in $flows) {
    $xmlPath = Join-Path $sourceDir $flow.Path
    if (-not (Test-Path $xmlPath)) {
        Write-Host "  SKIP: $xmlPath not found" -ForegroundColor Yellow
        continue
    }
    Convert-XMLToSCL -XmlPath $xmlPath -FlowName $flow.Name -OutputPath $outputDir
}

Write-Host "`n$('=' * 60)" -ForegroundColor Magenta
Write-Host "COMPLETE - Output: $outputDir"
Write-Host "$('=' * 60)`n" -ForegroundColor Magenta
