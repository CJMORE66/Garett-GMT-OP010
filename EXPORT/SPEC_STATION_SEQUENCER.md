# SPEC — FB_OP010_Sequencer (Next/Prev/Goto) + SafeBaseline

## Goal
Create a deterministic station sequencer that can be:
- AutoRun (normal)
- Hold (pause)
- StepMode with CmdNext / CmdPrev
- CmdGoto(step) with safety gating

Key rule: **Prev/Goto must be safe**. If a step cannot be reversed directly, transition through SafeBaseline.

## Inputs (recommended)
- iEStopOK : BOOL
- iSafetyInterlockOK : BOOL
- iGateClosedOK : BOOL
- iServoNotMoving : BOOL
- iRobotSafePosOK : BOOL (per robot or aggregated)
- iModeAuto : BOOL
- iModeManual : BOOL
- iModeStep : BOOL

## Commands
- CmdNext : BOOL (edge)
- CmdPrev : BOOL (edge)
- CmdGoto : BOOL (edge)
- GotoStep : INT

## State variables
- Step : INT
- StepReq : INT
- StepReqID / StepAckID : UDINT (token handshake for step changes)
- Mode : (AutoRun/Hold/StepMode)
- Dir : (Forward/Backward)

## SafeBaseline step (mandatory)
Define a dedicated step, e.g. Step = 0:
- stop all motions requests
- set outputs to safe
- wait until: iServoNotMoving AND iRobotSafePosOK AND interlocks OK
Then allow stepping to target step.

## ReverseMap concept
ReverseMap[Step] -> previous safe step.
Rules:
- If step is logically reversible: map to previous process step
- If not reversible: map to SafeBaseline (0)

## StepID proposal (station-level buckets)
Based on GRAPH flows present in OP010:
- 10..59   A1_TableLoad&Scan (ST10_Flow1..3)
- 60..99   B_Press (ST10_Flow4, ST10_Flow14)
- 100..129 C_Glue (ST10_Flow7)
- 130..159 A2_TableLoad&Scan (ST10_Flow11..13)
- 160..189 F_Robot (ST10_Flow15_*)
- 190..209 Unload / lift / magnet / reserve (ST10_Flow21..28)
- 900..    Fault handling

This is a **station-level map**; each bucket maps to one or more GRAPH steps internally.

## What to do next (analysis needed)
For each ST10_Flow*:
- map Graph Step names to the station StepID buckets above
- identify required interlocks and done conditions
- define which steps are non-reversible (=> SafeBaseline)

Deliverable: a table (StepID, Name, FlowFB, GraphStepName, EntryReq, DoneCond, ReverseStepID, FaultID).
