import importlib
import os
import sys

from engine import MurexEngine

import views.inventory_view
import views.map_view
import views.minions_view
import views.settings_view
import views.test_ui_view
import views.workshop_view


def _ensure_lab_path():
    base_dir = os.path.dirname(__file__)
    lab_path = os.path.abspath(os.path.join(base_dir, '../murex_lab'))
    if lab_path not in sys.path:
        sys.path.append(lab_path)

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
        "MAP": views.map_view.MapView(),
        "WORKSHOP": views.workshop_view.WorkshopView(),
        "INVENTORY": views.inventory_view.InventoryView(),
        "MINIONS": views.minions_view.MinionsView(),
        "SETTINGS": views.settings_view.SettingsView(),
        "TEST": views.test_ui_view.TestUIView()
    }
    tabs = ["MAP", "WORKSHOP", "INVENTORY", "MINIONS", "SETTINGS", "TEST"]
    return v_inst, tabs

def main():
    _ensure_lab_path()
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
    
