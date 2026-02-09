# Combat Design Specification: Murex Lab

This document defines the technical and mechanical architecture for the Active Turn Combat (ATC) system.

## 1. Core Mechanics: The ATC System
Murex Lab uses a **discrete tick-based Speed system** (Attack Bar / ATB) to determine turn order.

*   **Logic Ticks**: The engine processes discrete logical ticks (internally ~100ms).
*   **ATB Accumulation**: Every tick, each unit gains ATB equal to **7% of their Total Speed**.
*   **Turn Threshold**: A unit takes a turn when their ATB reaches **1000** (100%).
*   **Overflow Logic**: After a turn, 1000 ATB is subtracted from the unit's total (Overflow carries over).
*   **Tie-Breaking**: If multiple units cross the threshold in the same tick:
    1. Highest absolute ATB value.
    2. Highest Total Speed.

## 2. Character Stats & Scaling
Minions are the primary companions or servants who carry out the player's will. Their power comes entirely from their construction, natural traits, and equipment.

*   **Stat Sources**: Final Stat = `Base_Stat + Engraving_Bonuses`.
*   **No XP/Levels**: Level, Grade (Stars), and Experience mechanics are **removed**. All progression is gear-based.
*   **Stat Block**:
    *   **HP**: Total life.
    *   **ATK**: Power for damage calculations.
    *   **DEF**: Mitigation factor.
    *   **SPD**: Determines turn frequency.
    *   **CRIT**: Chance for critical hits (15% base).
    *   **CDMG**: Critical damage multiplier (50% base).

### Mitigation Formula
Murex Lab uses the Summoners War diminishing returns curve:
`Damage Factor = 1000 / (1140 + 3.5 * DEF)`

### Attack Scaling
Skills support hybrid scaling.
Example: `Damage = (ATK * Multi_1) + (HP * Multi_2)`

## 3. Combat Loop & AI
*   **Squad Size**: Up to 4 minions per expedition.
*   **Targeting**: Manual player selection in active combat. All units are targetable (no front/back split).
*   **Enemy AI**:
    - Prioritize using S2 (Special) over S1 (Basic) when available.
    - Target the player unit with the lowest current HP percentage.
*   **Rewards**: Loot depends on mob type (Hides, Fat, Crafting Materials). No XP.

## 4. Defeat & Recovery
Combat is high-stakes for the equipment and expedition progress.

*   **Fleeing**: Forfeiting combat results in the loss of the **Field Backpack** contents (raw materials).
*   **Minion Death**:
    - Defeated minions are **Out of Commission** upon return.
    - **Recovery Period**: 3 Days (72 hours real-time or cycle based).
    - **Expidition**: Recovery can be expedited via high Energy/Essence cost or rare materials.

## 5. Viewport Logic
*   **View Transition**: Combat is a full viewport switch—the Map is hidden and navigation is locked during combat.
*   **Feedback**: Floating damage indicators (numbers) and turn-bar visualizations are required.
