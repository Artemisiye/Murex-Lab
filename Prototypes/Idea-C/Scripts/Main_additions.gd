# Add this method to Main.gd to handle tile clicks

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
