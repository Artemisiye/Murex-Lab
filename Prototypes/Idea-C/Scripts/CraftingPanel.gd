extends Panel

# Crafting UI System

var recipes = {
	"copper_ingot": {
		"name": "Copper Ingot",
		"inputs": {"copper_ore": 2},
		"output": {"copper_ingot": 1},
		"station": "smelter"
	},
	"iron_blade": {
		"name": "Iron Blade",
		"inputs": {"iron_ore": 3},
		"output": {"iron_blade": 1},
		"station": "forge"
	},
	"copper_sword": {
		"name": "Copper Sword (+1)",
		"inputs": {"copper_ingot": 2},
		"output": {"copper_sword": 1},
		"weapon_quality": 1,
		"station": "forge"
	}
}

@onready var recipe_list = $VBoxContainer/RecipeList
@onready var craft_button = $VBoxContainer/CraftButton
@onready var game_manager = get_parent().get_parent()

var selected_recipe = null

func _ready():
	populate_recipes()
	craft_button.pressed.connect(_on_craft_button_pressed)

func populate_recipes():
	"""Populate recipe list"""
	recipe_list.clear()
	for recipe_id in recipes:
		recipe_list.add_item(recipes[recipe_id]["name"])
		recipe_list.set_item_metadata(recipe_list.get_item_count() - 1, recipe_id)

func _on_craft_button_pressed():
	if recipe_list.get_selected_items().size() == 0:
		game_manager.show_status("Select a recipe first!")
		return
	
	var selected_idx = recipe_list.get_selected_items()[0]
	var recipe_id = recipe_list.get_item_metadata(selected_idx)
	var recipe = recipes[recipe_id]
	
	# Check if we have resources
	if not game_manager.has_resources(recipe["inputs"]):
		game_manager.show_status("❌ Not enough resources!")
		return
	
	# Consume resources
	game_manager.consume_resources(recipe["inputs"])
	
	# Add output
	game_manager.add_resources(recipe["output"])
	
	# Equip weapon if applicable
	if "weapon_quality" in recipe:
		var settler = game_manager.settler_manager.get_idle_settler()
		if settler:
			settler.equip_weapon(recipe["weapon_quality"])
			game_manager.show_status("✅ Crafted " + recipe["name"] + "! Equipped to " + settler.name)
		else:
			game_manager.show_status("✅ Crafted " + recipe["name"] + "!")
	else:
		game_manager.show_status("✅ Crafted " + recipe["name"] + "!")
