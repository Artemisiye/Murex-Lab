import pygame
from ui_components import Panel, styles, Widget, PanelStack, ScrollContainer, Button

class WorkshopView:
    def __init__(self):
        self.selection_index = 0
        self.root = Widget(0, 24, 480, 240)

        self.blueprint_panel = Panel(title="BLUEPRINTS", w=128)
        self.blueprint_list = ScrollContainer(0, 0, 128, 232)
        self.blueprint_panel.add_child(self.blueprint_list)
        self.root.add_child(self.blueprint_panel)


        self.station_bench = Panel(title="BENCH", x=128, h=16, w=352)
        self.stattion_firepit = Panel(title="FIREPIT", x=128, h=16, w=352)
        self.panel_stack = PanelStack(panels=[
            self.station_bench,
            self.stattion_firepit])
        self.root.add_child(self.panel_stack)

        self.component_list = Panel(title="item", x=128, y=16, h=224, w=176)
        self.root.add_child(self.component_list)

        self.component_selector = Panel(title="SEL: com", x=304, y=16, h=224, w=176)
        self.root.add_child(self.component_selector)

        self.craft_button = Button(text="CRAFT", x=328, y=176, h=32, w=64)
        self.root.add_child(self.craft_button)



    def handle_event(self, event, game_state):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selection_index += 1
                return True
            if event.key == pygame.K_UP:
                self.selection_index = max(0, self.selection_index - 1)
                return True
            if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                blueprints = game_state['crafting_system'].get_all_blueprints()
                if 0 <= self.selection_index < len(blueprints):
                    bp = blueprints[self.selection_index]
                    print(f"Crafting selected: {bp.name}")
                return True
        return False

    def draw(self, buffer, game_state):
        COLOR_ACCENT = styles.get_color("accent")
        COLOR_FG = styles.get_color("fg")
        COLOR_DIM = styles.get_color("dim")
        
        self.root.draw(buffer)
        # self.blueprint_panel.draw(buffer)
        # self.panel_stack.draw(buffer)
        # self.component_list.draw(buffer)
        # self.component_selector.draw(buffer)
        # Grid Alignment (multiples of 8)
        px, py, pw, ph = 0, 32, 128, 232
        
        blueprints = game_state['crafting_system'].get_all_blueprints()
        body_f = styles.get_font("Body")
        small_f = styles.get_font("Small")
        
        for i, bp in enumerate(blueprints):
            if i > 10: break
            
            # Row baseline at 8px multiples. List starts at y=36.
            y_row = 36 + i * 16
            
            is_sel = (i == self.selection_index)
            color = COLOR_ACCENT if is_sel else COLOR_FG
            
            if is_sel:
                # Row highlight
                pygame.draw.rect(buffer, (40, 35, 30), (px + 8, y_row, pw - 16, 16))
            
            if body_f:
                # Vertical center text in 16px row (baseline approx +12)
                body_f.draw(buffer, f"{bp.name.upper()}", px + 16, y_row + 12, color)
