"""Retro-Py entrypoint for the Murex Lab UI runtime."""

import importlib
import os
import sys


def _ensure_lab_path():
    """Ensure murex_lab is available on sys.path for gameplay modules."""
    base_dir = os.path.dirname(__file__)
    lab_path = os.path.abspath(os.path.join(base_dir, '../murex_lab'))
    if lab_path not in sys.path:
        sys.path.append(lab_path)


_ensure_lab_path()

from engine import MurexEngine  # noqa: E402

import views.inventory_view  # noqa: E402
import views.map_view  # noqa: E402
import views.minions_view  # noqa: E402
import views.settings_view  # noqa: E402
import views.test_ui_view  # noqa: E402
import views.workshop_view  # noqa: E402

def bootstrap_views(engine):
    """
    Initializes/Reloads all UI views.
    Passed as a callback to support F2 Hot-Reload.
    """
    print("Engine: Initializing/Reloading View Layer...")
    
    # Reload modules to pick up code changes
    importlib.reload(views.map_view)
    importlib.reload(views.workshop_view)
    importlib.reload(views.inventory_view)
    importlib.reload(views.minions_view)
    importlib.reload(views.settings_view)
    importlib.reload(views.test_ui_view)

    v_inst = {
        "MAP": views.map_view.MapView(engine),
        "WORKSHOP": views.workshop_view.WorkshopView(engine),
        "INVENTORY": views.inventory_view.InventoryView(engine),
        "MINIONS": views.minions_view.MinionsView(engine),
        "SETTINGS": views.settings_view.SettingsView(engine),
        "TEST": views.test_ui_view.TestUIView(engine)
    }
    tabs = ["MAP", "WORKSHOP", "INVENTORY", "MINIONS", "SETTINGS", "TEST"]
    return v_inst, tabs

def main():
    """Boot the engine, create views, and start the main loop."""
    # 1. Instantiate Engine (Dormant)
    engine = MurexEngine()
    
    # 2. "Wake Up" Sequence (Config -> Assets -> State)
    engine.boot(title="Murex Lab - Retro Engine")

    # 3. Bootstrap Views
    view_instances, tabs = bootstrap_views(engine)
    
    # 4. Run Engine
    engine.run(view_instances, tabs, on_hot_reload=lambda: bootstrap_views(engine))

if __name__ == "__main__":
    main()
    
