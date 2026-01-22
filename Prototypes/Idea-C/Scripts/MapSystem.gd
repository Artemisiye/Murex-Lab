extends Node2D

# Hex Map System with clickable tiles

signal tile_clicked(tile_data)

const HEX_SIZE = 50
const HEX_OFFSET_X = HEX_SIZE * 1.5
const HEX_OFFSET_Y = HEX_SIZE * sqrt(3.0)

var map_data = {}

class HexTile:
	var coords: Vector2i
	var biome: String
	var danger_level: int
	var resources: Dictionary
	var discovered: bool = false
	var settler_here = null
	
	func _init(c: Vector2i, b: String, d: int, r: Dictionary):
		coords = c
		biome = b
		danger_level = d
		resources = r

func _ready():
	generate_map()
	queue_redraw()

func generate_map():
	"""Generate a hex map with different biomes"""
	var biomes = [
		{"name": "forest", "danger": 1, "resources": {"wood": 3, "stone": 1}},
		{"name": "mine", "danger": 2, "resources": {"copper_ore": 2, "stone": 2}},
		{"name": "deep_mine", "danger": 3, "resources": {"iron_ore": 2, "copper_ore": 1}},
		{"name": "ruins", "danger": 4, "resources": {"iron_ore": 1, "stone": 3}},
	]
	
	# Create central safe tile
	map_data[Vector2i(0, 0)] = HexTile.new(
		Vector2i(0, 0), 
		"camp", 
		0, 
		{}
	)
	map_data[Vector2i(0, 0)].discovered = true
	
	# Generate surrounding tiles in rings
	for ring in range(1, 4):
		for i in range(ring * 6):
			var angle = (i / float(ring * 6)) * TAU
			var q = int(ring * cos(angle))
			var r_coord = int(ring * sin(angle))
			var coords = Vector2i(q, r_coord)
			
			if coords in map_data:
				continue
			
			# Biome based on distance from center
			var biome_data = biomes[min(ring - 1, biomes.size() - 1)]
			
			map_data[coords] = HexTile.new(
				coords,
				biome_data["name"],
				biome_data["danger"],
				biome_data["resources"].duplicate()
			)

func _draw():
	for coords in map_data:
		var tile = map_data[coords]
		var pos = hex_to_pixel(coords)
		
		# Determine color based on biome
		var color = get_biome_color(tile.biome)
		
		# Darken if not discovered
		if not tile.discovered:
			color = color.darkened(0.5)
		
		# Draw hexagon
		draw_hexagon(pos, HEX_SIZE, color)
		
		# Draw danger skulls
		if tile.danger_level > 0 and tile.discovered:
			var skull_count = tile.danger_level
			var skull_text = ""
			for i in range(skull_count):
				skull_text += "X"  # Using X instead of emoji for compatibility
			draw_string(ThemeDB.fallback_font, pos - Vector2(20, -5), skull_text, HORIZONTAL_ALIGNMENT_CENTER, -1, 16, Color.RED)
		
		# Draw settler if present
		if tile.settler_here != null:
			draw_circle(pos, 10, Color.YELLOW)

func draw_hexagon(center: Vector2, size: float, color: Color):
	var points = PackedVector2Array()
	for i in range(6):
		var angle_rad = (i / 6.0) * TAU + PI / 6.0
		points.append(center + Vector2(cos(angle_rad), sin(angle_rad)) * size)
	
	draw_colored_polygon(points, color)
	draw_polyline(points + PackedVector2Array([points[0]]), Color.BLACK, 2.0)

func get_biome_color(biome: String) -> Color:
	match biome:
		"camp": return Color.GREEN
		"forest": return Color.DARK_GREEN
		"mine": return Color.GRAY
		"deep_mine": return Color.DIM_GRAY
		"ruins": return Color.PURPLE
		_: return Color.WHITE

func hex_to_pixel(coords: Vector2i) -> Vector2:
	var x = HEX_OFFSET_X * coords.x
	var y = HEX_OFFSET_Y * (coords.y + coords.x * 0.5)
	return Vector2(x, y) + Vector2(640, 360)  # Center on screen

func pixel_to_hex(pixel: Vector2) -> Vector2i:
	"""Convert pixel position to hex coordinates (approximate)"""
	pixel = pixel - Vector2(640, 360)
	var q = (pixel.x / HEX_OFFSET_X)
	var r_coord = (pixel.y / HEX_OFFSET_Y) - (q * 0.5)
	return Vector2i(round(q), round(r_coord))

func _input(event):
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		var hex_coords = pixel_to_hex(event.position)
		if hex_coords in map_data:
			tile_clicked.emit(map_data[hex_coords])

func discover_tile(coords: Vector2i):
	if coords in map_data:
		map_data[coords].discovered = true
		queue_redraw()

func set_settler_at_tile(coords: Vector2i, settler):
	if coords in map_data:
		map_data[coords].settler_here = settler
		queue_redraw()

func clear_settler_at_tile(coords: Vector2i):
	if coords in map_data:
		map_data[coords].settler_here = null
		queue_redraw()
