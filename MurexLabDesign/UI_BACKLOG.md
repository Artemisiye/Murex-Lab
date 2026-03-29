# UI Infrastructure Enhancement Backlog

This document tracks identified gaps and prioritized enhancements for the Retro-UI component library (`ui_components.py`).

## 1. Layout Providers (`vbox` / `hbox`)
- **Problem**: Current widget positioning requires manual coordinate calculation (e.g., `y + i*4`).
- **Goal**: Implement `LayoutContainer` or `Column`/`Row` components that automatically manage child positions and spacing.

## 2. Standardized Property Binding
- **Problem**: Every `Slider` or `Dropdown` needs a custom manual callback to sync state with `game_state`.
- **Goal**: Implement a `bind(target_dict, "key")` hook to allow widgets to update and observe data directly with zero boilerplate.

## 3. Compound Property Widgets
- **Problem**: No built-in way to create "Label + Control" pairs as as a single unit.
- **Goal**: Create a `PropertyRow` or `ControlLabel` widget that handles the Label on the left and a generic widget (Slider/Dropdown/Button) on the right with unified focus/hover behavior.

## 4. State Obervation / Publisher System
- **Problem**: UI doesn't refresh automatically when global settings change.
- **Goal**: Introduce a simpler version of a "Publisher/Subscriber" pattern so the UI can respond to data changes without per-frame manual checks.

## 5. Input Stepping
- **Problem**: `Slider` currently returns values in a linear range.
- **Goal**: Add horizontal "stepped" navigation for sliders to handle values like [1, 2, 4, 8].

## 6. Standardized Widget Padding & Baseline Alignment
- **Problem**: Different widgets (Labels vs Dropdowns/Sliders) define their height and drawing baselines differently. A `Label`'s text baseline aligns differently than the text inside a padded `Dropdown`. This forces manual fractional `y` offsets (e.g., `y=1.5` vs `y=2`) to align adjacent elements visually, which breaks the consistency of the grid coordinate system.
- **Goal**: Standardize how widgets report their structural bounds versus their visual bounds. Introduce a uniform text baseline property across all widgets so they can be horizontally aligned via a Layout Provider without manual tweaking.

## 7. Tab Change Selection Reset
- **Problem**: Legacy behavior reset `selection_index` on tab changes; the engine currently preserves prior selection state across views.
- **Goal**: Decide whether tab transitions should reset selection to avoid stale focus in list-based views.
