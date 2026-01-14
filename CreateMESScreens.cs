using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Siemens.Engineering;
using Siemens.Engineering.Hmi;
using Siemens.Engineering.Hmi.Screen;
using Siemens.Engineering.Hmi.Tag;
using Siemens.Engineering.Hmi.Globalization;
using Siemens.Engineering.Hmi.Communication;
using Siemens.Engineering.Hmi.Screen.ScreenItems;
using Siemens.Engineering.Hmi.Screen.ScreenItems.Button;
using Siemens.Engineering.Hmi.Screen.ScreenItems.TextField;
using Siemens.Engineering.Hmi.Screen.ScreenItems.Circle;
using Siemens.Engineering.Hmi.Screen.ScreenItems.IOField;
using Siemens.Engineering.Hmi.Screen.ScreenItems.GroupBox;
using Siemens.Engineering.Hmi.Screen.ScreenItems.Rectangle;
using Siemens.Engineering.Hmi.Dynamic;
using Siemens.Engineering.Hmi.Event;
using Siemens.Engineering.Hmi.Script;
using System.IO;

namespace MESDiagnosticsScreenAutomation
{
    class Program
    {
        static void Main(string[] args)
        {
            // TIA Portal project path - UPDATE THIS PATH
            string projectPath = @"D:\AI_ANALYZE\GARRET\TRACING\OP10\EXPORT"; // Your project path

            // Initialize TIA Portal
            TiaPortal tiaPortal = new TiaPortal(TiaPortalMode.WithoutUserInterface);

            try
            {
                // Open the project
                Project project = tiaPortal.Projects.Open(new FileInfo(projectPath));

                // Get the HMI device
                Device hmiDevice = project.Devices.FirstOrDefault(d => d.Name.Contains("HMI") || d.Name.Contains("TP700"));
                if (hmiDevice == null)
                {
                    Console.WriteLine("HMI device not found!");
                    return;
                }

                // Get the HMI target
                HmiTarget hmiTarget = hmiDevice.DeviceItems.OfType<HmiTarget>().FirstOrDefault();
                if (hmiTarget == null)
                {
                    Console.WriteLine("HMI target not found!");
                    return;
                }

                // Get the screen folder
                ScreenFolder screenFolder = hmiTarget.ScreenFolders.FirstOrDefault(f => f.Name == "Screens");
                if (screenFolder == null)
                {
                    Console.WriteLine("Screens folder not found!");
                    return;
                }

                // Find the OP010 folder
                ScreenFolder op010Folder = screenFolder.ScreenFolders.FirstOrDefault(f => f.Name == "OP010");
                if (op010Folder == null)
                {
                    Console.WriteLine("OP010 folder not found!");
                    return;
                }

                // Find the 9MES folder
                ScreenFolder mesFolder = op010Folder.ScreenFolders.FirstOrDefault(f => f.Name == "9MES");
                if (mesFolder == null)
                {
                    Console.WriteLine("9MES folder not found!");
                    return;
                }

                // Find the diagnostics folder
                ScreenFolder diagnosticsFolder = mesFolder.ScreenFolders.FirstOrDefault(f => f.Name == "920 MES Diagnostics");
                if (diagnosticsFolder == null)
                {
                    Console.WriteLine("920 MES Diagnostics folder not found!");
                    return;
                }

                Console.WriteLine("Starting MES Diagnostics screen creation...");

                // Step 1: Create the template screen
                CreateTemplateScreen(diagnosticsFolder, hmiTarget);

                // Step 2: Create station detail screens (ST1-ST8)
                for (int station = 1; station <= 8; station++)
                {
                    CreateStationDetailScreen(diagnosticsFolder, hmiTarget, station);
                }

                // Step 3: Update main screen with navigation buttons
                UpdateMainScreen(diagnosticsFolder, hmiTarget);

                Console.WriteLine("MES Diagnostics screens created successfully!");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
            }
            finally
            {
                tiaPortal.Dispose();
            }
        }

        static void CreateTemplateScreen(ScreenFolder diagnosticsFolder, HmiTarget hmiTarget)
        {
            // Create new screen
            Screen templateScreen = diagnosticsFolder.Screens.Create("921MES_Diagnostics_DetailTemplate", 921);

            // Set screen properties
            templateScreen.Width = 1280;
            templateScreen.Height = 800;
            templateScreen.BackColor = System.Drawing.Color.FromArgb(205, 215, 225);

            // Add title
            TextField title = templateScreen.ScreenItems.CreateTextField("Title", 20, 18, 1240, 50);
            title.BackColor = System.Drawing.Color.FromArgb(24, 28, 49);
            title.ForeColor = System.Drawing.Color.White;
            title.Text = "Station ST1 - MES Diagnostics";
            title.HorizontalAlignment = Siemens.Engineering.Hmi.Screen.ScreenItems.HorizontalAlignment.Center;
            title.VerticalAlignment = Siemens.Engineering.Hmi.Screen.ScreenItems.VerticalAlignment.Middle;
            title.Font.Size = 28;
            title.Font.Bold = true;

            // Add CheckIn Handshake Matrix GroupBox
            GroupBox checkInGroup = templateScreen.ScreenItems.CreateGroupBox("GrpCheckIn", 20, 80, 610, 260);
            checkInGroup.BackColor = System.Drawing.Color.FromArgb(240, 245, 250);
            checkInGroup.BorderColor = System.Drawing.Color.FromArgb(24, 28, 49);
            checkInGroup.BorderWidth = 2;

            // Add CheckIn section title
            TextField checkInTitle = checkInGroup.ScreenItems.CreateTextField("TtlCheckIn", 15, 5, 200, 25);
            checkInTitle.Text = "Check-In Handshake";
            checkInTitle.Font.Size = 18;
            checkInTitle.Font.Bold = true;

            // Add background rectangle
            Rectangle checkInBg = checkInGroup.ScreenItems.CreateRectangle("RectCheckInBg", 0, 30, 610, 230);
            checkInBg.BackColor = System.Drawing.Color.FromArgb(217, 222, 232);
            checkInBg.FillStyle = Siemens.Engineering.Hmi.Screen.ScreenItems.FillStyle.Solid;

            // Add column headers
            string[] headers = { "Req", "OK", "NG", "Done", "TO" };
            int[] headerPositions = { 60, 115, 160, 205, 250 };

            for (int i = 0; i < headers.Length; i++)
            {
                TextField header = checkInGroup.ScreenItems.CreateTextField($"HdrCI_{headers[i]}", headerPositions[i], 35, 40, 20);
                header.Text = headers[i];
                header.HorizontalAlignment = Siemens.Engineering.Hmi.Screen.ScreenItems.HorizontalAlignment.Center;
                header.Font.Bold = true;
            }

            // Add CheckIn indicators (Req, OK, NG, Done, TO)
            string[] checkInSignals = { "Req", "OK", "NG", "Done", "Timeout" };
            System.Drawing.Color[] colors = {
                System.Drawing.Color.Yellow,    // Req
                System.Drawing.Color.Green,     // OK
                System.Drawing.Color.Red,       // NG
                System.Drawing.Color.Blue,      // Done
                System.Drawing.Color.Red        // Timeout
            };

            for (int i = 0; i < checkInSignals.Length; i++)
            {
                Circle indicator = checkInGroup.ScreenItems.CreateCircle($"IndCI_{checkInSignals[i]}", headerPositions[i], 65, 18, 18);
                indicator.BackColor = System.Drawing.Color.FromArgb(217, 217, 217);
                indicator.BorderColor = System.Drawing.Color.FromArgb(24, 28, 49);
                indicator.BorderWidth = 1;

                // Add animation
                RangeAppearanceAnimation animation = indicator.Animations.CreateRangeAppearanceAnimation("RangeAppearanceAnimation");
                TagElementTrigger trigger = animation.RangeTag;
                trigger.Tag = hmiTarget.TagTables.First().Tags.First(t => t.Name == $"MESMon_ST1_CI_{checkInSignals[i]}");

                Range inactiveRange = animation.RangeValues.Create(0, 0);
                inactiveRange.BackColor = System.Drawing.Color.FromArgb(217, 217, 217);

                Range activeRange = animation.RangeValues.Create(1, 1);
                activeRange.BackColor = colors[i];
                if (i == 4) // Timeout flashing
                    activeRange.FlashingType = Siemens.Engineering.Hmi.Dynamic.FlashingType.Medium;
            }

            // Continue with CheckOut section (similar pattern)
            // Add counters section
            // This is a simplified version - in practice, you'd add all elements

            Console.WriteLine("Template screen created.");
        }

        static void CreateStationDetailScreen(ScreenFolder diagnosticsFolder, HmiTarget hmiTarget, int station)
        {
            // Copy template screen
            Screen templateScreen = diagnosticsFolder.Screens.First(s => s.Name == "921MES_Diagnostics_DetailTemplate");
            Screen stationScreen = diagnosticsFolder.Screens.Create($"92{station + 1}MES_Diagnostics_ST{station}", 921 + station);

            // Copy all elements from template
            foreach (var item in templateScreen.ScreenItems)
            {
                // Deep copy logic would go here
                // For simplicity, recreate with station-specific changes
            }

            // Update title
            TextField title = stationScreen.ScreenItems.First(i => i.Name == "Title") as TextField;
            title.Text = $"Station ST{station} - MES Diagnostics";

            // Update all tag references from ST1 to ST{station}
            foreach (var item in stationScreen.ScreenItems)
            {
                if (item is Circle circle && circle.Animations.Any())
                {
                    var animation = circle.Animations.First() as RangeAppearanceAnimation;
                    if (animation != null && animation.RangeTag.Tag != null)
                    {
                        string tagName = animation.RangeTag.Tag.Name;
                        tagName = tagName.Replace("ST1", $"ST{station}");
                        animation.RangeTag.Tag = hmiTarget.TagTables.First().Tags.First(t => t.Name == tagName);
                    }
                }
            }

            Console.WriteLine($"Station ST{station} detail screen created.");
        }

        static void UpdateMainScreen(ScreenFolder diagnosticsFolder, HmiTarget hmiTarget)
        {
            Screen mainScreen = diagnosticsFolder.Screens.First(s => s.Name == "920MES_Diagnostics");

            // Add navigation buttons for each station
            int[] buttonPositions = { 150, 184, 218, 252, 286, 320, 354, 388 }; // Y positions for each station row

            for (int station = 1; station <= 8; station++)
            {
                Button navButton = mainScreen.ScreenItems.CreateButton($"BtnST{station}_Details", 430, buttonPositions[station - 1], 80, 30);
                navButton.Text = "Details...";
                navButton.BackColor = System.Drawing.Color.FromArgb(230, 240, 250);
                navButton.BorderColor = System.Drawing.Color.FromArgb(24, 28, 49);
                navButton.BorderWidth = 2;

                // Add click event to navigate to detail screen
                ScreenMouseClickEvent clickEvent = navButton.Events.CreateScreenMouseClickEvent();
                Screen targetScreen = diagnosticsFolder.Screens.First(s => s.Name == $"92{station + 1}MES_Diagnostics_ST{station}");
                clickEvent.Screen = targetScreen;
            }

            Console.WriteLine("Main screen updated with navigation buttons.");
        }
    }
}