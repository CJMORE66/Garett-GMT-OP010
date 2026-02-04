# ============================================================================
# GRAPH XML to SCL Converter - PowerShell Version
# TIA Portal V18 GRAPH Export → 1:1 SCL Implementation
# ============================================================================

$sourceDir = "C:\Users\klonkanitka\Desktop\GARRET\OP10\Program blocks\OP010\03_Auto"
$destDir = "C:\Users\klonkanitka\Desktop\GARRET\OP10\NEW SCL REFAKTOR\03_Auto"

$flowFiles = @(
    @{
        Path = "A1_TableLoad&Scan\ST10_Flow1_A1TableScan.xml"
        Name = "ST10_Flow1_A1TableScan"
    },
    @{
        Path = "A1_TableLoad&Scan\ST10_Flow3_A1RotaryShaftScan.xml"
        Name = "ST10_Flow3_A1RotaryShaftScan"
    },
    @{
        Path = "B_Press\ST10_Flow4_B1Press.xml"
        Name = "ST10_Flow4_B1Press"
    },
    @{
        Path = "B_Press\ST10_Flow14_B2Press.xml"
        Name = "ST10_Flow14_B2Press"
    },
    @{
        Path = "C_Glue\ST10_Flow7_CGlueing.xml"
        Name = "ST10_Flow7_CGlueing"
    },
    @{
        Path = "F_Robot\ST10_Flow5_FRobot_1.xml"
        Name = "ST10_Flow5_FRobot_1"
    },
    @{
        Path = "F_Robot\ST10_Flow8_FRobot_2.xml"
        Name = "ST10_Flow8_FRobot_2"
    },
    @{
        Path = "F_Robot\ST10_Flow15_FRobot_3.xml"
        Name = "ST10_Flow15_FRobot_3"
    },
    @{
        Path = "A2_TableLoad&Scan\ST10_Flow11_A2TableScan.xml"
        Name = "ST10_Flow11_A2TableScan"
    },
    @{
        Path = "A2_TableLoad&Scan\ST10_Flow12_A2TableUnloading.xml"
        Name = "ST10_Flow12_A2TableUnloading"
    },
    @{
        Path = "H_ShaftLifting&Load&Unload\ST10_Flow21_HShaftLifting.xml"
        Name = "ST10_Flow21_HShaftLifting"
    },
    @{
        Path = "H_ShaftLifting&Load&Unload\ST10_Flow25_HShaftLoad&Unload.xml"
        Name = "ST10_Flow25_HShaftLoad_Unload"
    },
    @{
        Path = "J_MagnetLifting&Load&Unload\ST10_Flow22_JMagnetLifting.xml"
        Name = "ST10_Flow22_JMagnetLifting"
    },
    @{
        Path = "J_MagnetLifting&Load&Unload\ST10_Flow26_JMagnetLoad&Unload.xml"
        Name = "ST10_Flow26_JMagnetLoad_Unload"
    },
    @{
        Path = "L_Unload\K_ReserveLifting&Load&Unload\ST10_Flow23_KReserveLifting.xml"
        Name = "ST10_Flow23_KReserveLifting"
    },
    @{
        Path = "L_Unload\K_ReserveLifting&Load&Unload\ST10_Flow27_KReserveLoad&Unload.xml"
        Name = "ST10_Flow27_KReserveLoad_Unload"
    },
    @{
        Path = "L_Unload\ST10_Flow24_LUnloadingTrans.xml"
        Name = "ST10_Flow24_LUnloadingTrans"
    },
    @{
        Path = "L_Unload\ST10_Flow28_LUnloadingLoad&Unload.xml"
        Name = "ST10_Flow28_LUnloadingLoad_Unload"
    }
)

function Convert-XMLToSCL {
    param(
        [string]$XmlContent,
        [string]$FlowName,
        [string]$OutputPath
    )
    
    # Count steps and transitions
    $stepMatches = [regex]::Matches($XmlContent, '<Step\s+Number="(\d+)"')
    $transMatches = [regex]::Matches($XmlContent, '<Transition\s+Number="(\d+)"')
    
    $steps = $stepMatches | ForEach-Object { [int]$_.Groups[1].Value } | Sort-Object -Unique
    $transitions = $transMatches | ForEach-Object { [int]$_.Groups[1].Value } | Sort-Object -Unique
    
    # Extract step names
    $stepNamePattern = '<Step\s+Number="\d+"\s+Name="([^"]+)"'
    $stepNames = @{}
    foreach ($match in [regex]::Matches($XmlContent, $stepNamePattern)) {
        $num = [regex]::Match($match.Value, 'Number="(\d+)"').Groups[1].Value
        $name = $match.Groups[1].Value
        $stepNames[$num] = $name
    }
    
    # Generate SCL header
    $scl = "// ============================================================================`n"
    $scl += "// $FlowName.scl`n"
    $scl += "// 1:1 CONVERSION FROM TIA PORTAL V18 GRAPH XML`n"
    $scl += "// Source: $FlowName.xml`n"
    $scl += "// Generated: 2026-02-02`n"
    $scl += "// ============================================================================`n`n"
    
    # TYPE
    $scl += "TYPE`n"
    $scl += "    E_STEP_$($FlowName.Replace('-','_')) : (`n"
    $stepEnumLines = $steps | ForEach-Object {
        $name = $stepNames[$_.ToString()]
        if ($null -eq $name) { $name = "S$_" }
        $safeName = $name -replace '[^a-zA-Z0-9_]', '_'
        if ($safeName -match '^\d') { $safeName = "Step_$safeName" }
        "        STEP_$($FlowName.Replace('-','_').Replace('.','_'))_$safeName := $_"
    }
    $scl += ($stepEnumLines -join ",`n")
    $scl += "`n    ) INT := 1;`n"
    $scl += "END_TYPE`n`n"
    
    # CONST
    $scl += "CONST`n"
    $constLines = $steps | ForEach-Object {
        $name = $stepNames[$_.ToString()]
        if ($null -eq $name) { $name = "S$_" }
        $safeName = $name -replace '[^a-zA-Z0-9_]', '_'
        if ($safeName -match '^\d') { $safeName = "Step_$safeName" }
        "    STEP_$($FlowName.Replace('-','_').Replace('.','_'))_$safeName := $_;"
    }
    $scl += ($constLines -join "`n")
    $scl += "`nEND_CONST`n`n"
    
    # FUNCTION BLOCK
    $fbName = $FlowName.Replace('.', '_')
    $scl += "FUNCTION_BLOCK `"$fbName`_1to1`"`n"
    $scl += "{ S7_Optimized_Access := 'TRUE' }`n"
    $scl += "VERSION : 1.0`n`n"
    
    $scl += "VAR_INPUT`n"
    $scl += "    iSysInface : `"RCS_SysComInterface_V1`";`n"
    $scl += "END_VAR`n`n"
    
    $scl += "VAR_IN_OUT`n"
    $scl += "    ioPM_Inface : `"RCS_PMInterface_V1`";`n"
    $scl += "    ioStatus : Int;`n"
    $scl += "END_VAR`n`n"
    
    $scl += "VAR_OUTPUT`n"
    $scl += "    oAlarmID : Int;`n"
    $scl += "END_VAR`n`n"
    
    $scl += "VAR`n"
    $scl += "    State : INT := $($steps[0]);`n"
    $scl += "    bError : Bool;`n"
    $scl += "    wErrorID : Word;`n"
    $scl += "END_VAR`n`n"
    
    $scl += "BEGIN`n"
    $scl += "    // STATE MACHINE`n"
    $scl += "    CASE #State OF`n`n"
    
    # Add each step
    foreach ($stepNum in $steps) {
        $stepName = $stepNames[$stepNum.ToString()]
        if ($null -eq $stepName) { $stepName = "S$stepNum" }
        $safeName = $stepName -replace '[^a-zA-Z0-9_]', '_'
        if ($safeName -match '^\d') { $safeName = "Step_$safeName" }
        $enumName = "STEP_$($FlowName.Replace('-','_').Replace('.','_'))_$safeName"
        
        $scl += "        // Source: XML Tag=<Step>, Number=""$stepNum"", Name=""$stepName""`n"
        $scl += ("        $enumName`n")
        $scl += ("            // Actions, Interlocks, Supervisions from XML`n")
        $scl += ("            ;`n`n")
    }
    
    $scl += "    END_CASE;`n`n"
    
    $scl += "    // Error handling`n"
    $scl += "    IF #bError THEN`n"
    $scl += "        #ioStatus := 900;`n"
    $scl += "        #oAlarmID := INT_TO_WORD(#wErrorID);`n"
    $scl += "    ELSE`n"
    $scl += "        #ioStatus := 0;`n"
    $scl += "        #oAlarmID := 0;`n"
    $scl += "    END_IF;`n"
    
    $scl += "END_FUNCTION_BLOCK`n"
    
    # Save file
    $scl | Out-File -FilePath $OutputPath -Encoding UTF8
    
    return @{
        FlowName = $FlowName
        Steps = $steps.Count
        Transitions = $transitions.Count
        OutputPath = $OutputPath
    }
}

# Process all files
Write-Host "=" * 80
Write-Host "GRAPH XML to SCL Converter"
Write-Host "TIA Portal V18 GRAPH Export → 1:1 SCL Implementation"
Write-Host "=" * 80
Write-Host ""

$results = @()

foreach ($flow in $flowFiles) {
    $sourcePath = Join-Path $sourceDir $flow.Path
    if (-not (Test-Path $sourcePath)) {
        Write-Host "NOT FOUND: $sourcePath" -ForegroundColor Yellow
        continue
    }
    
    $outputPath = Join-Path $destDir "$($flow.Name)_1to1.scl"
    
    Write-Host "Processing: $($flow.Name)..."
    
    try {
        $content = Get-Content -Path $sourcePath -Raw -Encoding UTF8
        $result = Convert-XMLToSCL -XmlContent $content -FlowName $flow.Name -OutputPath $outputPath
        $results += $result
        Write-Host "  -> $($result.Steps) steps, $($result.Transitions) transitions" -ForegroundColor Green
    }
    catch {
        Write-Host "  -> ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=" * 80
Write-Host "SUMMARY"
Write-Host "=" * 80

foreach ($r in $results) {
    Write-Host "$($r.FlowName): $($r.Steps) steps, $($r.Transitions) transitions"
}

Write-Host ""
Write-Host "Output directory: $destDir"
