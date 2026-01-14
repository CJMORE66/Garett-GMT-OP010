# Parameter Extraction Report - OP10 (FINAL)

## Summary of Findings
Consolidated 3 different data sources into one unified Recipe structure:
1.  **Code Logic:** Timers (`T#10s`, `T#300ms`), Station IDs (`350`), Limits (`Retry=5`).
2.  **Existing Recipes (`ST10_RecipeActiveDB`):** Press curves, ATEQ limits, Vision programs, Fixture strings.
3.  **Motion DBs (`IAI_Ax`, `ServoV90_Ax`):** Axis positions and velocities.

## Created Files
1.  **`UDT_ST10_Recipe.scl`**: The "Master" UDT.
    -   Includes nested types: `UDT_Motion_Point_IAI`, `UDT_Motion_Point_V90`, `UDT_Recipe_PressCurve`, `UDT_Recipe_ATEQ`, `UDT_Recipe_Fixtures`.
    -   Organized into `Config`, `General`, `Process` (Press, Vision, ATEQ), `Production` (Fixtures), and `Motion`.
2.  **`DB_ST10_Recipe.scl`**: The Instance DB.
    -   Populated with values extracted from `ST10_Flow*` (logic), `ST10_RecipeDB` (strings), and `IAI/Servo` DBs (motion).

## Migration Plan (Critical)
The existing project uses `ST10_RecipeActiveDB` for MES data and `IAI_Ax` DBs for motion. To migrate without breaking the machine:

1.  **Import** the new SCL files.
2.  **Modify `FC_ChangeOver` (or `ST10_ChangeOver`):**
    -   Instead of loading `ST10_RecipeActiveDB` fields directly, map them *from* `DB_ST10_RecipeActive` (which should now be of type `UDT_ST10_Recipe`).
    -   **Motion:** Add logic to copy `DB_ST10_RecipeActive.Motion.IAI_A1` -> `"IAI_A1".Auto.Pos`.
    -   **Timers:** Replace `T#10s` in GRAPH with `DB_ST10_RecipeActive.General.StepTimeout`.

This provides a "Single Source of Truth" while maintaining compatibility with the low-level block interfaces.