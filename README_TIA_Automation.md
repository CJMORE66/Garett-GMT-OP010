# TIA Portal Openness API Setup Instructions

## Prerequisites
1. **TIA Portal V18** installed
2. **Visual Studio 2019/2022** with .NET Framework 4.8
3. **TIA Portal Openness API** assemblies

## Step 1: Create Visual Studio Project
1. Open Visual Studio
2. Create new **Console Application (.NET Framework)**
3. Set target framework to **.NET Framework 4.8**
4. Name: `MESDiagnosticsAutomation`

## Step 2: Add TIA Portal References
1. Right-click **References** → **Add Reference**
2. Browse to: `C:\Program Files\Siemens\Automation\Portal V18\PublicAPI\V18`
3. Add these assemblies:
   - `Siemens.Engineering.dll`
   - `Siemens.Engineering.Hmi.dll`
   - `Siemens.Engineering.Hmi.Screen.dll`
   - `Siemens.Engineering.Hmi.Tag.dll`
   - `Siemens.Engineering.Hmi.Globalization.dll`
   - `Siemens.Engineering.Hmi.Communication.dll`
   - `Siemens.Engineering.Hmi.Script.dll`
   - `Siemens.Engineering.Hmi.Dynamic.dll`
   - `Siemens.Engineering.Hmi.Event.dll`

## Step 3: Add the Code
1. Replace `Program.cs` content with the provided C# code
2. Update the project path in line 17:
   ```csharp
   string projectPath = @"D:\AI_ANALYZE\GARRET\TRACING\OP10\EXPORT"; // Your actual path
   ```

## Step 4: Build and Run
1. **Build** the project (F6)
2. **Close TIA Portal** (if open)
3. **Run** the application (F5)
4. The script will automatically create all screens

## Step 5: Verify in TIA Portal
1. Open your project in TIA Portal V18
2. Navigate to **Screens > OP010 > 9MES > 920 MES Diagnostics**
3. You should see:
   - `920MES_Diagnostics` (main screen with navigation buttons)
   - `921MES_Diagnostics_DetailTemplate` (template)
   - `922MES_Diagnostics_ST1` through `929MES_Diagnostics_ST8` (detail screens)

## Troubleshooting
- **Error: "TIA Portal not found"** → Ensure TIA Portal V18 is installed
- **Error: "Project not found"** → Check the project path
- **Error: "HMI device not found"** → Verify HMI device name in your project
- **Tag not found errors** → Ensure `0MES_Monitoring_DB_MES_Monitoring.xml` tag table exists

## What the Script Does
1. **Opens** your TIA Portal project
2. **Creates** template screen with complete handshake matrix layout
3. **Copies** template 8 times (one per station)
4. **Updates** tags, titles, and screen numbers for each station
5. **Adds** navigation buttons to main screen
6. **Saves** all changes automatically

This automation saves hours of manual work and ensures perfect consistency across all 9 screens!