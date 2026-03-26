import pygame
from ui import *

class WorkshopView(BaseView):
    """
    The Workshop station view where players can craft items from blueprints.
    Utilizes a multi-panel layout for blueprints, stations, and component selection.
    """
    def __init__(self):
        super().__init__()
        self.selection_index = 0

        # Building components as children of the view
        
        # 1. Blueprint Panel (Left)
        self.blueprint_list = ScrollContainer(x=0, y=2, w=16, h=27)
        self.blueprint_panel = Panel(title="BLUEPRINTS", x=0, y=0, w=16, h=30, children=[
            self.blueprint_list
        ])
        
        # 2. Station Tabs (Top Right)
        self.station_bench = Panel(title="BENCH")
        self.stattion_firepit = Panel(title="FIREPIT")
        self.panel_stack = PanelStack(x=16, y=0, w=44, h=2, panels=[
            self.station_bench,
            self.stattion_firepit
        ])
        
        # 3. Component Details & Selection
        self.component_list = Panel(title="not", x=16, y=2, w=22, h=28)
        self.component_selector = Panel(title="SEL: com", x=38, y=2, w=22, h=28)
        
        # 4. Craft Button
        self.craft_button = Button(text="CRAFT", x=3, y=20, w=8, h=3)
        self.component_selector.add_child(self.craft_button)

        # Build final hierarchy
        self.add_child(self.blueprint_panel)
        self.add_child(self.panel_stack)
        self.add_child(self.component_list)
        self.add_child(self.component_selector)

    def handle_event(self, event, mx, my):
        # 1. Standard Widget Interception
        if super().handle_event(event, mx, my):
            return True

        # 2. Key Input (Blueprint Navigation)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selection_index += 1
                return True
            if event.key == pygame.K_UP:
                self.selection_index = max(0, self.selection_index - 1)
                return True
            if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                blueprint_system = self.game_state.get('crafting_system')
                if blueprint_system:
                    blueprints = blueprint_system.get_all_blueprints()
                    if 0 <= self.selection_index < len(blueprints):
                        bp = blueprints[self.selection_index]
                        print(f"Crafting selected: {bp.name}")
                return True
        return False

    def draw_view(self, buffer, game_state):
        # 1. Standard widget hierarchy draw
        super().draw_view(buffer, game_state)
        
        # 2. Dynamic Blueprint List (Populated only once if empty)
        if not self.blueprint_list.children:
            blueprint_system = game_state.get('crafting_system')
            if blueprint_system:
                blueprints = blueprint_system.get_all_blueprints()
                for i, bp in enumerate(blueprints):
                    self.blueprint_list.add_child(RowItem(text=bp.name.lower(), x=0.5, y=i*2, w=12, h=1, padding=0.5))
