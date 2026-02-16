import pygame
from ui_components import Widget, Panel, Label, RowItem, Button, ScrollContainer, Slider, Dropdown, TextField, PanelStack, styles

class TestUIView:
    def __init__(self):
        self.root = Widget(0, 24, 480, 240)
        
        # 1. Multi-Title Panel with Dividers
        main_panel = Panel(title="MAIN")
        main_panel.dividers = [
            (200, True, styles.get_color("dim")), # Vertical at x=200
            (150, False, styles.get_color("dim")) # Horizontal at y=150
        ]
        
        # # 2. Controls in Left Section
        main_panel.add_child(Button("Test", x=28, y=20,
                                        w=None, h=None, 
                                        callback=lambda: print("Test"), 
                                        i_padding=4))

        main_panel.add_child(Label("Opacity Level:", x=28, y=52))
        slider = Slider(30, 60, 144, val_min=0, val_max=100, current=75)
        main_panel.add_child(slider)
        
        main_panel.add_child(Label("System Mode:", x=28, y=84))
        dropdown = Dropdown(28, 100, 144, options=["Manual", "Auto", "Safe", "Override"])
        main_panel.add_child(dropdown)
        
        main_panel.add_child(Label("Command Input:", x=28, y=136))
        input_field = TextField(28, 152, 144, text="superuser")
        main_panel.add_child(input_field)

        main_panel.add_child(RowItem(x=204, y=156, w=264, h=16, text="Test Row Item"))
        main_panel.add_child(RowItem(x=204, y=172, w=264, h=16, text="Test Row Item"))
        main_panel.add_child(RowItem(x=204, y=188, w=264, h=16, text="Test Row Item"))
        main_panel.add_child(RowItem(x=204, y=204, w=264, h=16, text="Test Row Item"))

        # 3. Scroll Container in Right Section
        self.scroll_area = ScrollContainer(200, 4, 240, 144)
        self.scroll_area.add_child(Label("LOG OUPUT STREAM", x=4 , y=4, role="H2"))
        
        for i in range(20):
            y_pos = 20 + i * 16
            self.scroll_area.add_child(Label(f"Log Entry #{i:03d}: System check OK", x=4, y=y_pos, color=styles.get_color("dim")))
            
        main_panel.add_child(self.scroll_area)
        
        # self.tab_stack.add_tab("CONTROL", self.main_panel)
        
        # Tab 1: Stats
        view_stats = Panel(title="STATS")
        view_stats.add_child(Label("System Statistics", x=20, y=40, role="H2"))
        view_stats.add_child(Label("CPU: 12%", x=20, y=70))
        view_stats.add_child(Label("MEM: 456MB", x=20, y=90))
        
        # # Tab 2: Net
        view_net = Panel(title="NETWORK")
        view_net.add_child(Label("Network Config", x=20, y=40, role="H2"))
        view_net.add_child(Label("IP: 192.168.1.101", x=20, y=70))

        self.panel_stack = PanelStack(panels=[main_panel, view_stats, view_net])
        self.root.add_child(self.panel_stack)

    def handle_event(self, event, game_state):
        mx, my = pygame.mouse.get_pos()
        scale = game_state.get('config', {}).get('scale', 1)
        vmx, vmy = mx // scale, my // scale
        
        # Pass event to root widget hierarchy with virtual coordinates
        self.root.handle_event(event, vmx, vmy)

    def draw(self, buffer, game_state):
        # Draw root widget hierarchy
        self.root.draw(buffer)
