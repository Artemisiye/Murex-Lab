extends Node

# Settler Manager - handles settler expeditions

class Settler:
	var name: String
	var health: int = 100
	var max_health: int = 100
	var weapon_quality: int = 0  # 0 = unarmed, 1-3 = weapon tier
	var status: String = "idle"  # idle, exploring, returning
	var current_tile = null
	var expedition_timer: float = 0.0
	var expedition_duration: float = 5.0
	
	func _init(settler_name: String):
		name = settler_name
	
	func equip_weapon(quality: int):
		weapon_quality = quality
	
	func can_survive(danger_level: int) -> bool:
		return weapon_quality >= danger_level - 1

var settlers = []
var active_expeditions = []

@onready var map_system = get_parent().get_node("HexMap")
@onready var game_manager = get_parent()

func _ready():
	# Create initial settlers
	settlers.append(Settler.new("Brave"))
	settlers.append(Settler.new("Scout"))
	settlers.append(Settler.new("Explorer"))

func _process(delta):
	# Update active expeditions
	for expedition in active_expeditions:
		expedition["timer"] += delta
		
		if expedition["timer"] >= expedition["duration"]:
			# Expedition complete - return home
			complete_expedition(expedition)

func send_settler(settler: Settler, tile):
	"""Send a settler on an expedition"""
	if settler.status != "idle":
		game_manager.show_status(settler.name + " is already on an expedition!")
		return false
	
	if not tile.discovered:
		map_system.discover_tile(tile.coords)
	
	# Check if settler can survive
	if not settler.can_survive(tile.danger_level):
		game_manager.show_status("⚠️ " + settler.name + " needs better gear! (Danger: " + str(tile.danger_level) + ")")
		return false
	
	# Start expedition
	settler.status = "exploring"
	settler.current_tile = tile
	
	var expedition = {
		"settler": settler,
		"tile": tile,
		"timer": 0.0,
		"duration": 3.0 + tile.danger_level * 1.5
	}
	
	active_expeditions.append(expedition)
	map_system.set_settler_at_tile(tile.coords, settler)
	
	game_manager.show_status(settler.name + " exploring " + tile.biome + "... (" + str(int(expedition["duration"])) + "s)")
	return true

func complete_expedition(expedition):
	var settler = expedition["settler"]
	var tile = expedition["tile"]
	
	# Calculate loot based on danger level
	var loot_multiplier = 1.0 + (tile.danger_level * 0.3)
	var gathered_resources = {}
	
	for resource in tile.resources:
		var amount = int(tile.resources[resource] * loot_multiplier)
		gathered_resources[resource] = amount
	
	# Add resources to game
	game_manager.add_resources(gathered_resources)
	
	# Return settler to idle
	settler.status = "idle"
	settler.current_tile = null
	map_system.clear_settler_at_tile(tile.coords)
	
	# Remove from active expeditions
	active_expeditions.erase(expedition)
	
	# Show completion message
	var resource_text = ""
	for resource in gathered_resources:
		resource_text += resource.replace("_", " ").capitalize() + ": " + str(gathered_resources[resource]) + " "
	
	game_manager.show_status("✅ " + settler.name + " returned! Gathered: " + resource_text)

func get_idle_settler():
	"""Get first idle settler"""
	for settler in settlers:
		if settler.status == "idle":
			return settler
	return null

func get_settler_status_text() -> String:
	var text = "SETTLERS:\n"
	for settler in settlers:
		text += settler.name + " (" + settler.status + ")"
		if settler.weapon_quality > 0:
			text += " [Armed +" + str(settler.weapon_quality) + "]"
		text += "\n"
	return text
