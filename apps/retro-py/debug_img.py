import pygame

def print_box(img, x, y, w, h):
    print(f"BOX at {x},{y} ({w}x{h}):")
    for ty in range(y, y + h):
        line = ""
        for tx in range(x, x + w):
            c = img.get_at((tx, ty))
            r, g, b, a = c
            if a == 0: line += "." # Transparent
            elif g > 150 and r < 100: line += "G" # Green (boundary?)
            elif r > 150 and g > 150: line += "Y" # Yellow (arrow)
            else: line += "X"
        print(line)

if __name__ == "__main__":
    pygame.init()
    img = pygame.image.load("e:/Emerald Vimana/Murex-Lab/apps/retro-py/assets/arrows2.png")
    # Using the boxes from the previous run
    boxes = [(1, 1, 5, 5), (7, 1, 5, 5), (13, 1, 5, 5), (19, 1, 5, 5),
             (1, 10, 7, 7), (9, 10, 7, 7), (17, 10, 7, 7), (25, 10, 7, 7)]
    for b in boxes:
        print_box(img, b[0], b[1], b[2], b[3])
