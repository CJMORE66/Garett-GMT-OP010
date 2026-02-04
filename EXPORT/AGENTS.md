# AGENTS.md - OP10 PLC Project Guidelines

## Project Overview

This is a Siemens TIA Portal PLC project for manufacturing Station OP10. The project contains:
- **XML exports**: TIA Portal block exports (FB, FC, DB, OB, UDT)
- **SCL source files**: Structured Control Language source code (NEW SCL REFAKTOR folder)
- **CSV documentation**: Call graphs, interface maps, inventories
- **Database files**: Process parameter databases

## Development Workflow

### TIA Portal Integration
1. **Export blocks from TIA Portal** as XML before editing outside TIA
2. **Import XML files** back to TIA Portal after modifications
3. **SCL files** in `NEW SCL REFAKTOR/` are source files for new development
4. Never edit XML blocks directly - edit SCL source then export XML to TIA

### Key Paths
| Path | Purpose |
|------|---------|
| `Program blocks/OP010/` | Main station logic (XML exports) |
| `Program blocks/OP010/10_Device/` | Device control blocks |
| `PLC data types/` | UDT definitions (XML) |
| `NEW SCL REFAKTOR/` | New SCL source code for refactoring |
| `DOKUMENTACE/` | Project documentation |

## Build/Lint/Test Commands

**No traditional software build commands exist.** This is PLC code.

### TIA Portal Compilation
- Use TIA Portal "Compile" function to validate all blocks
- Check for compilation errors before deploying to PLC
- Use "Consistency Check" to find interface mismatches

### Simulation
- Use TIA Portal PLCSIM for offline testing
- No command-line simulation available

### Code Validation
- Review `CALL_GRAPH.md` for block dependencies
- Review `LEGACY_INTERFACE_MAP.md` for interface contracts
- Check `STEP_MAP.md` for GRAPH sequence flow

## Code Style Guidelines

### Naming Conventions

| Prefix | Meaning | Example |
|--------|---------|---------|
| `ST10_` | Station 10 blocks | `ST10_Main.xml` |
| `ST10_FlowX_` | Process flow step X | `ST10_Flow1_A1TableScan.xml` |
| `FB_` | Function Block | `FB_NG_Box_Control` |
| `FC_` | Function | `FC_Save_Values` |
| `DB_` | Data Block | `DB_MES_Monitoring` |
| `UDT_` | User Data Type | `UDT_RECIPE` |
| `iDB/` | Instance DB folder | Instance data blocks |
| `i` | Input variable prefix | `iCmd_WorkPos` |
| `o` | Output variable prefix | `oValve_WorkPos` |
| `t` | Time variable prefix | `tTimeoutConfig` |
| `R_Trig_` | Rising edge trigger | `R_Trig_Next` |
| `TON_` / `TOF_` | Timer instances | `TON_Timeout` |

### File Naming
- **XML exports**: Use exact TIA Portal names with `.xml` extension
- **SCL files**: PascalCase with `.scl` extension
- **Device folders**: `NN_Description/` format (e.g., `25_V90/`)
- **Flow blocks**: `ST10_Flow[Number]_[Description].xml`

### SCL Code Style

#### Block Declaration
```scl
FUNCTION_BLOCK "FB_Dev_Cylinder"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 1.0
VAR_INPUT
    iCmd_WorkPos : Bool;
    iSensor_WorkPos : Bool;
END_VAR
```

#### Variable Declaration Order
1. VAR_INPUT
2. VAR_OUTPUT
3. VAR (static variables)
4. VAR_TEMP (temporary)
5. VAR CONSTANT

#### State Machine Pattern
```scl
CASE #State OF
    0:  // IDLE
        #Out := FALSE;
        IF #Condition THEN #State := 10; END_IF;
    10: // ACTION
        #Out := TRUE;
    ...
END_CASE;
```

#### Comments
- Use `//` for single-line comments
- Czech comments appear in legacy code, English in new refactored code
- Document state machine transitions with step numbers
- Use headers for section separation:
```scl
// =============================================================
// SECTION TITLE
// =============================================================
```

#### Indentation and Spacing
- 4-space indentation (convert tabs to spaces)
- Spaces around operators: `#a := #b + #c;`
- No space before `(` in calls: `#Instance(Command := TRUE);`
- Colons in type declarations: `Timer : TON_TIME;`

### Variable Naming
- Use descriptive names: `iCmd_HomePos` not `iCmd`
- Arrays: `Array[1..15] OF Bool` (1-based indexing common)
- Timer declarations include LibVersion:
```scl
Timer {InstructionName := 'TON_TIME'; LibVersion := '1.0'} : TON_TIME;
```

### Error Handling
- Set error flags and status strings: `oError := TRUE; oStatus := 'TIMEOUT';`
- Use safety interlocks: `IF NOT #iSafetyOK THEN ... RETURN; END_IF;`
- Timeout timers on motion commands
- Reset inputs for error recovery: `iResetError : Bool;`

### I/O Tag Conventions
| Prefix | Type | Example |
|--------|------|---------|
| `iE1-` | Input from device 1 | `iE1-UnloadingShaftPressNG_1` |
| `oE-` | Output to device | `oE-NG-01NGLocationCylinderToWP` |
| `"ClockMemory0.4s"` | System clock memory | Bit for 0.4s blink |

## Folder Structure Guidelines

### New Device Type (UDT)
Location: `PLC data types/03 FunctionBlocks/`
```
[NNN] [DeviceName]/
└── [NNN].1 UDT/
    └── DeviceName.xml
```

### New Device Instance
Location: `Program blocks/OP010/10_Device/`
```
[NN]_[DeviceName]/
├── FB_DeviceName.xml
└── iDB/
    └── FB_DeviceName_iDB.xml
```

### New Process Flow Step
Location: `Program blocks/OP010/03_Auto/`
```
ST10_Flow[X]_[Description].xml
M_iDB/ST10_Flow[X]_[Description]_iDB.xml
```

### New SCL Development
Location: `NEW SCL REFAKTOR/`
- Prefix new FBs with `FB_Dev_` for device library
- Prefix new sequencers with `FB_Seq_`
- Include VERSION declaration and Optimized_Access attribute

## Important Notes

1. **OLD SHIT folders**: Deprecated/legacy code - do not use for new development
2. **Z_Reserve folder**: Temporary/commissioning blocks only
3. **Flow numbers**: Not sequential (gaps at 9, 10, 13, 16-20, etc.)
4. **Two V90 technologies**: Standard telegram 111 (active) vs TO_BasicPos (not used)
5. **Safety first**: Always include safety interlocks and timeout monitoring
6. **Graph sequences**: Use GRAPH blocks where appropriate (see STEP_MAP.md)

## Documentation References

| File | Purpose |
|------|---------|
| `PROJECT_STRUCTURE_OVERVIEW.md` | Complete project structure |
| `CALL_GRAPH.md` | Block call dependencies |
| `LEGACY_INTERFACE_MAP.md` | Interface definitions |
| `STEP_MAP.md` | GRAPH sequence steps |
| `SPEC_STATION_SEQUENCER.md` | Sequencer specifications |
