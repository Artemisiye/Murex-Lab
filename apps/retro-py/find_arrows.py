import pygame

def find_green_boxes(image_path):
    pygame.init()
    img = pygame.image.load(image_path)
    width, height = img.get_size()
    
    green_pixels = []
    for y in range(height):
        for x in range(width):
            color = img.get_at((x, y))
            r, g, b, a = color
            if g > 150 and r < 100 and b < 100:
                green_pixels.append((x, y))
    
    if not green_pixels:
        return []

    # Cluster green pixels into boxes
    boxes = []
    visited = set()
    
    for px, py in green_pixels:
        if (px, py) in visited:
            continue
            
        # BFS to find cluster
        cluster = []
        queue = [(px, py)]
        visited.add((px, py))
        
        while queue:
            curr_x, curr_y = queue.pop(0)
            cluster.append((curr_x, curr_y))
            
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = curr_x + dx, curr_y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    # Check if neighbor is green
                    c = img.get_at((nx, ny))
                    if c[1] > 150 and c[0] < 100 and c[2] < 100 and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
        
        # Found a cluster, get its bounding box
        min_x = min(p[0] for p in cluster)
        max_x = max(p[0] for p in cluster)
        min_y = min(p[1] for p in cluster)
        max_y = max(p[1] for p in cluster)
        
        # The user said boundaries are green. The content is inside.
        # But if the cluster IS the boundary, then the box is (min_x+1, min_y+1, w-2, h-2)
        boxes.append((min_x, min_y, max_x - min_x + 1, max_y - min_y + 1))
        
    return boxes

if __name__ == "__main__":
    boxes = find_green_boxes("e:/Emerald Vimana/Murex-Lab/apps/retro-py/assets/arrows.png")
    # Sort by y then x to identify Up, Left, Down, Right
    boxes.sort(key=lambda b: (b[1], b[0]))
    print(f"FOUND BOXES: {boxes}")
