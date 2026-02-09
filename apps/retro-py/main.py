import pygame
import sys
import os
from renderer import SpriteFont

def main():
    pygame.init()
    
    # Virtual resolution (Retro native)
    V_WIDTH, V_HEIGHT = 480, 270
    SCALE = 4
    
    screen = pygame.display.set_mode((V_WIDTH * SCALE, V_HEIGHT * SCALE))
    pygame.display.set_caption("Murex Lab - Retro")
    
    video_buffer = pygame.Surface((V_WIDTH, V_HEIGHT))
    
    # Font Management
    font_dir = os.path.join(os.path.dirname(__file__), "assets", "fonts")
    fonts = {}
    current_font_name = None
    
    if os.path.exists(font_dir):
        files = [f for f in os.listdir(font_dir) if f.endswith(".json")]
        for f in files:
            name = f.replace(".json", "")
            try:
                fonts[name] = SpriteFont(os.path.join(font_dir, f))
                if current_font_name is None:
                    current_font_name = name
            except Exception as e:
                print(f"Error loading {f}: {e}")
    
    # UI State
    tabs = ["DASHBOARD", "FLEET", "CRAFTING", "SETTINGS"]
    active_tab = "DASHBOARD"
    test_text = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
    input_focus = False
    
    clock = pygame.time.Clock()
    DEBUG = True
    
    while True:
        mx, my = pygame.mouse.get_pos()
        # Scale mouse to virtual coords
        vmx, vmy = mx // SCALE, my // SCALE
        click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1: # Toggle debug
                    DEBUG = not DEBUG
                if active_tab == "SETTINGS" and input_focus:
                    if event.key == pygame.K_BACKSPACE:
                        test_text = test_text[:-1]
                    elif event.key == pygame.K_RETURN:
                        input_focus = False
                    else:
                        if len(test_text) < 40:
                            test_text += event.unicode.upper()

        # --- RENDER LOGIC ---
        video_buffer.fill((15, 13, 11))
        
        # 5x5 Debug Grid
        if DEBUG:
            for i in range(0, V_WIDTH, 5):
                pygame.draw.line(video_buffer, (25, 22, 20), (i, 0), (i, V_HEIGHT))
            for i in range(0, V_HEIGHT, 5):
                pygame.draw.line(video_buffer, (25, 22, 20), (0, i), (V_WIDTH, i))
        
        # UI Colors
        COLOR_BG = (15, 13, 11)
        COLOR_PANEL = (25, 22, 19)
        COLOR_ACCENT = (230, 200, 100)
        COLOR_DIM = (100, 90, 80)
        COLOR_FG = (220, 210, 190)

        main_font = fonts.get(current_font_name)
        
        # Header & Tabs
        pygame.draw.rect(video_buffer, COLOR_PANEL, (0, 0, V_WIDTH, 30))
        if main_font:
            main_font.draw(video_buffer, "MUREX OS", 10, 20, COLOR_ACCENT)
        
        tab_x = 100
        for tab in tabs:
            is_active = (active_tab == tab)
            tab_w = 60
            tab_rect = pygame.Rect(tab_x, 5, tab_w, 20)
            
            if is_active:
                pygame.draw.rect(video_buffer, COLOR_ACCENT, tab_rect, 1)
            
            if tab_rect.collidepoint(vmx, vmy):
                if not is_active:
                    pygame.draw.rect(video_buffer, (40, 35, 30), tab_rect)
                if click:
                    active_tab = tab
            
            if main_font:
                # Small label for tabs
                main_font.draw(video_buffer, tab[:4], tab_x + 5, 20, COLOR_FG if is_active else COLOR_DIM)
            
            tab_x += tab_w + 5

        # Content Area
        if active_tab == "DASHBOARD":
            if main_font:
                main_font.draw(video_buffer, "SYSTEM STATUS: NOMINAL", 20, 60, COLOR_FG)
                main_font.draw(video_buffer, "REACTOR OUTPUT: 88% [||||||  ]", 20, 80, (100, 255, 100))
                main_font.draw(video_buffer, "CURRENT SECTOR: ARTEMIS-7B", 20, 100, COLOR_DIM)
        
        elif active_tab == "FLEET":
            if main_font:
                main_font.draw(video_buffer, "NO MINIONS ASSIGNED", 20, 60, COLOR_DIM)
        
        elif active_tab == "SETTINGS":
            # Font Selector
            if main_font:
                main_font.draw(video_buffer, "ACTIVE FONT / BAKE:", 20, 60, COLOR_ACCENT)
                
                # List Fonts (Simple Scroll/Select)
                fy = 80
                for f_name in list(fonts.keys()):
                    font_obj = fonts[f_name]
                    eff_h = font_obj.metadata.get("effective_h", 0)
                    
                    sel = (f_name == current_font_name)
                    # Wider box to accommodate the height display
                    f_rect = pygame.Rect(20, fy - 12, 195, 15)
                    if f_rect.collidepoint(vmx, vmy):
                        pygame.draw.rect(video_buffer, (40, 35, 30), f_rect)
                        if click:
                            current_font_name = f_name
                    
                    if sel:
                        pygame.draw.rect(video_buffer, COLOR_ACCENT, f_rect, 1)
                    
                    # Display font name
                    main_font.draw(video_buffer, f_name[:18], 25, fy, COLOR_FG if sel else COLOR_DIM)
                    # Display Effective Height on the right
                    h_label = f"H:{eff_h}"
                    main_font.draw(video_buffer, h_label, 175, fy, (0, 255, 150) if eff_h > 0 else COLOR_DIM)
                    
                    fy += 18

                # Text Preview Area
                input_rect = pygame.Rect(220, 80, 240, 30)
                pygame.draw.rect(video_buffer, COLOR_PANEL, input_rect)
                if input_focus:
                    pygame.draw.rect(video_buffer, COLOR_ACCENT, input_rect, 1)
                
                if click and input_rect.collidepoint(vmx, vmy):
                    input_focus = True
                elif click:
                    input_focus = False

                main_font.draw(video_buffer, "PREVIEW TEST:", 220, 70, COLOR_DIM)
                
                # Render using the SELECTED font for preview!
                preview_font = fonts.get(current_font_name)
                if preview_font:
                    display_text = test_text + ("_" if input_focus and (pygame.time.get_ticks() // 500 % 2) else "")
                    # Draw actual preview with the font itself
                    preview_font.draw(video_buffer, display_text, 225, 105, COLOR_FG)
                    
                    # Larger sample below
                    preview_font.draw(video_buffer, "1234567890 !@#$%^&*", 220, 150, COLOR_DIM)
                    preview_font.draw(video_buffer, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", 220, 180, COLOR_FG)
                    preview_font.draw(video_buffer, "abcdefghijklmnopqrstuvwxyz", 220, 210, COLOR_FG)

        # 2. Scale and Blit to screen
        pygame.transform.scale(video_buffer, (V_WIDTH * SCALE, V_HEIGHT * SCALE), screen)
        
        # 3. HIGH-RES DEBUG OVERLAY (Screen Resolution, not native)
        if DEBUG:
            sys_f = pygame.font.SysFont("monospace", 14)
            # Performance stats
            stats = [
                f"FPS: {int(clock.get_fps())}",
                f"RES: {V_WIDTH}x{V_HEIGHT} (VIRT)",
                f"SCALE: {SCALE}x",
                f"FONT: {current_font_name}",
                f"ACTIVE TAB: {active_tab}"
            ]
            for i, line in enumerate(stats):
                txt = sys_f.render(line, True, (255, 255, 255))
                # Shadow
                screen.blit(sys_f.render(line, True, (0,0,0)), (12, 12 + i*16))
                screen.blit(txt, (10, 10 + i*16))
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
