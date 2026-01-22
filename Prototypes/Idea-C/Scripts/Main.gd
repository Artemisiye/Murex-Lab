extends Node2D

# Game Manager - Central hub for all game systems

@onready var settler_manager = $SettlerManager
@onready var crafting_ui = $UI/CraftingPanel
@onready var status_label = $UI/StatusLabel
@onready var resources_label = $UI/ResourcesPanel/ResourcesList

# Game state
var resources = {
	"wood": 0,
	"copper_ore": 0,
	"iron_ore": 0,
	"stone": 0,
	"copper_ingot": 0,
	"iron_blade": 0,
	"copper_sword": 0
}

var discovered_tiles = []

func _ready():
	update_resource_display()
	status_label.text = "Welcome to Settler's Expedition! Send settlers to explore."

func add_resources(resource_dict):
	"""Add resources from exploration"""
	for resource in resource_dict:
		if resource in resources:
			resources[resource] += resource_dict[resource]
		else:
			resources[resource] = resource_dict[resource]
	update_resource_display()

func has_resources(resource_dict):
	"""Check if we have enough resources"""
	for resource in resource_dict:
		if resources.get(resource, 0) < resource_dict[resource]:
			return false
	return true

func consume_resources(resource_dict):
	"""Consume resources for crafting"""
	if not has_resources(resource_dict):
		return false
	
	for resource in resource_dict:
		resources[resource] -= resource_dict[resource]
	
	update_resource_display()
	return true

func update_resource_display():
	var text = ""
	for resource in resources:
		if resources[resource] > 0:
			text += resource.replace("_", " ").capitalize() + ": " + str(resources[resource]) + "\n"
	resources_label.text = text if text != "" else "No resources yet..."

func show_status(message: String):
	status_label.text = message
	# Auto-clear after 3 seconds
	await get_tree().create_timer(3.0).timeout
	if status_label.text == message:  # Only clear if hasn't changed
		status_label.text = ""

func _on_hex_map_tile_clicked(tile):
	"""Handle clicking on a hex tile"""
	var settler = settler_manager.get_idle_settler()
	
	if settler == null:
		show_status("❌ All settlers are busy!")
		return
	
	# Send settler to tile
	settler_manager.send_settler(settler, tile)
	
	# Update settler display
	update_settler_display()

func update_settler_display():
	var settler_label = $UI/SettlersPanel/SettlersList
	settler_label.text = settler_manager.get_settler_status_text()

func _process(delta):
	# Update settler status display continuously
	update_settler_display()
