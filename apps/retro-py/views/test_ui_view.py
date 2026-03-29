from ui import *

class TestUIView(BaseView):
    """
    A sandbox view for testing new UI components and layouts.
    Includes examples of Buttons, Sliders, Dropdowns, and ScrollContainers.
    """
    def __init__(self, engine=None):
        super().__init__()
        self.engine = engine
        
        # 1. Multi-Title Panel with Dividers
        main_panel = Panel(title="MAIN")
        main_panel.dividers = [
            (200, True, styles.get_color("dim")), # Vertical at x=200
            (150, False, styles.get_color("dim")) # Horizontal at y=150
        ]
        
        # # 2. Controls in Left Section
        main_panel.add_child(Button("Test", x=3.5, y=2,
                                        w=None, h=None, 
                                        callback=lambda: print("Test"), 
                                        i_padding=0.5))

        main_panel.add_child(Label("Opacity Level:", x=3.5, y=6.5))
        slider = Slider(3.5, 7.5, 18, val_min=0, val_max=100, current=75)
        main_panel.add_child(slider)
        
        main_panel.add_child(Label("System Mode:", x=3.5, y=10.5))
        dropdown = Dropdown(3.5, 12.5, 18, options=["Manual", "Auto", "Safe", "Override"])
        main_panel.add_child(dropdown)
        
        main_panel.add_child(Label("Command Input:", x=3.5, y=17))
        input_field = TextField(3.5, 19, 18, text="superuser")
        main_panel.add_child(input_field)

        main_panel.add_child(RowItem(x=25.5, y=19.5, w=33, h=2, text="Test Row Item"))
        main_panel.add_child(RowItem(x=25.5, y=21.5, w=33, h=2, text="Test Row Item"))
        main_panel.add_child(RowItem(x=25.5, y=23.5, w=33, h=2, text="Test Row Item"))
        main_panel.add_child(RowItem(x=25.5, y=25.5, w=33, h=2, text="Test Row Item"))

        # 3. Scroll Container in Right Section
        scroll_area = ScrollContainer(25, 0.5, 30, 18)
        scroll_area.add_child(Label("LOG OUPUT STREAM", x=0.5 , y=0.5, role="H2"))
        
        for i in range(20):
            y_pos = 2.5 + i * 2
            scroll_area.add_child(Label(f"Log Entry #{i:03d}: System check OK", 
                                        x=0.5, y=y_pos, 
                                        color=styles.get_color("dim"),
                                        can_focus=True))
            
        main_panel.add_child(scroll_area)
        
        # Tab 1: Stats
        view_stats = Panel(title="STATS")
        view_stats.add_child(Label("System Statistics", x=2.5, y=2, role="H2"))
        view_stats.add_child(Label("CPU: 12%", x=2.5, y=4))
        view_stats.add_child(Label("MEM: 456MB", x=2.5, y=6))
        
        # # Tab 2: Net
        view_net = Panel(title="NETWORK")
        view_net.add_child(Label("Network Config", x=2.5, y=2, role="H2"))
        view_net.add_child(Label("IP: 192.168.1.101", x=2.5, y=4))

        panel_stack = PanelStack(panels=[main_panel, view_stats, view_net])
        self.add_child(panel_stack)
