# Sofia Espino-Frey

import random
import time

import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("lib/python3.12/site-packages")

    return os.path.join(base_path, relative_path)

# I created this dictionary to hold the ANSI color codes for readability.
COLORS = {
	'cyan': '\033[96m',  # Location information (Like current room names)
	'green': '\033[92m',  # Positive events and feedback (Restoring focus, winning battles)
	'red': '\033[91m',  # Negative events and feedback (Losing focus)
	'yellow': '\033[93m',  # Highlighting items in the inventory (Things found in rooms)
	'magenta': '\033[95m',  # Important prompts (Like "Would you like to get it")
	'reset': '\033[0m'  # This is to reset the color back to default.
}


# This is the function to print text in a specific color.
def print_color(text, color):
	# This checks if the color exists in the dictionary.
	if color in COLORS:
		# An f-string is used here to wrap the text with the color codes.
		print(f"{COLORS[color]}{text}{COLORS['reset']}")
	else:
		# If the color is invalid, the game just prints the text normally.
		print(text)


# This function is called once at the start of the game.
# It prints the main menu, game goal, and commands for the player.
def show_instructions():
	print_color("===============================================================", 'cyan')
	print("      Dr. Eaton vs. Ton Drump and the Evil Robots      ")
	print_color("===============================================================", 'cyan')
	print("\nAt the Hexagon, a petty workplace squabble over a parking spot has escalated. Dr. Eaton is")
	print("in town for a clean energy meeting a accidentally took Mr. Ton Drump's parking place, even though there")
	print("is no assigned parking. Mr. Drump threw a KING-sized temper tantrum and swore revenge against Dr. Eaton.")
	print("Now, Mr. Ton Drump has corrupted the building's helpful robots with his tantrum-fueled code! Dr. Eaton")
	print("must build a network wide healing device and she needs YOUR help retrieving the items needed to build")
	print("it and reprogram any evil robots you might encounter along the way!")
	print("\nYour Mission:")
	print_color("Collect the 7 missing components for Dr. Gucnew's network-wide healing device:", 'magenta')
	print_color("  A Peer-Reviewed Fact-Checker, The Civics 101 Patch, A De-Escalation Algorithm,", 'yellow')
	print_color("  The Green Energy Core, The Tax-the-Rich Capacitor, A Historical Context Drive,", 'yellow')
	print_color("and The Deregulation Lubricant", 'yellow')
	print_color("\nYour Starting Toolkit (Single Use):", 'magenta')
	print_color("  - A Civility Charm: Instantly restores 3 Focus during a Reprogramming Sequence.", 'yellow')
	print_color("  - The Executive Order: Doubles your reprogramming progress for one turn.", 'yellow')
	print_color("  - A Golden Parachute: Instantly escape a Reprogramming Sequence.", 'yellow')
	print("\nYou will also encounter several items during your quest. Some of these items will help, some")
	print("not so much - but you may only use these items one time per quest. Beware, Mr. Ton Drump's")
	print("evil corrupted robots lurk around every corner so use your items wisely!")
	print_color("\nOnce you obtain all 7 missing items, find Mr. Ton Drump and win the game!", 'magenta')
	print("\n'Good luck, ally,' Dr. Gucnew says with a determined look.")
	print("'This is a mission of restoration, not retribution. May your logic be sound, your sources peer-reviewed,")
	print(" and may you prove that civility is not, in fact, a weakness.'")
	print_color("\nControls:", 'magenta')
	print_color("  - Movement: NORTH, SOUTH, EAST, WEST", 'green')
	print_color("  - Actions: SEARCH, USE [item/feature]", 'green')
	print_color("  - Responses: YES, NO", 'green')
	print_color("  - Quit Game: EXIT", 'red')
	print_color("===============================================", 'cyan')
	input("\nPress Enter to begin your quest...")


# This displays the player's current status and controls at the start of each turn.
def show_status(game_map, current_location, inventory, player_stats, quest_items_to_win):
	print("\n---------------------------------------------------------------")
	room = game_map[current_location]
	print(f"> You are in the: {COLORS['cyan']}{room['room_name']}{COLORS['reset']}")
	print(f"> Your Focus: {COLORS['green']}{player_stats['focus']}{COLORS['reset']}")

	# Here is the logic to count how many quest items the player has collected.
	inventory_names = [item['name'] if isinstance(item, dict) else item for item in inventory]
	# This uses a generator expression to efficiently count matches.
	quest_items_found = sum(1 for item in quest_items_to_win if item in inventory_names)
	print(
		f"> Quest Progress: {COLORS['yellow']}{quest_items_found} of {len(quest_items_to_win)}{COLORS['reset']} components found.")

	# This is the list that will hold the formatted inventory strings for display.
	inventory_display = []
	for item in inventory:
		# This checks if the item is a dictionary (a starting item).
		if isinstance(item, dict):
			status = "(Used)" if item['used'] else "(Ready)"
			inventory_display.append(f"{item['name']} {status}")
		else:
			inventory_display.append(item)
	print(f"> Inventory: {COLORS['yellow']}{inventory_display}{COLORS['reset']}")

	# This is a status indicator for a temporary buff.
	if player_stats['logic_filter_active']:
		print(
			f"> {COLORS['magenta']}Status{COLORS['reset']}: Logic Filter is {COLORS['magenta']}ACTIVE{COLORS['reset']}")

	# This displays the controls every turn for easy reference
	print(
		f"\n> Controls: {COLORS['green']}SEARCH, USE, EXIT,{COLORS['reset']} or a direction {COLORS['green']}(NORTH, SOUTH, EAST, WEST){COLORS['reset']}")


# This function is to get the plyer input agaist a list of valid choices
def get_player_input(prompt, valid_choices):
	while True:
		user_input = input(prompt).strip().lower()
		if user_input in valid_choices:
			return user_input
		else:
			print(f"Invalid command. Please enter one of the following: {', '.join(valid_choices)}")


# This function handles the logic for using an item from the inventory
def handle_use_item(player_stats, inventory, potion_map, in_combat=False):
	print("\n> Your Inventory:")

	# This is an empty list that will be filled with only the items the player can currently use.
	usable_items = []
	for item in inventory:
		# This condition checks for unused starting items.
		if isinstance(item, dict) and not item['used']:
			usable_items.append(item)
		# This condition checks for any found items that are on the master list of usable wildcard items.
		elif isinstance(item, str) and item in ['Trickle-Down Economics Textbook', 'Subpoenaed Diary Logs',
		                                        'Logic Filter',
		                                        'Suspiciously Well-Preserved Snack Cake', 'An Old Sharpie',
		                                        'Blank Keycard'] + list(
			potion_map.keys()):
			usable_items.append(item)

	if not usable_items:
		print("  You have no usable items right now.")
		return 'no_action'

	# This is a dictionary of descriptions for the starting items.
	starting_item_effects = {
		'Civility Charm': 'Restores 3 Focus',
		'Executive Order': 'Doubles reprogramming progress for one turn',
		'Golden Parachute': 'Instantly escape a Reprogramming Sequence'
	}

	# This loop prints the numbered menu of usable items for the player.
	for i, item in enumerate(usable_items):
		item_name = item['name'] if isinstance(item, dict) else item
		if item_name in starting_item_effects:
			print(f"  {i + 1}. {item_name}: Effects - {starting_item_effects[item_name]}")
		else:
			print(f"  {i + 1}. {item_name}: Effects - Unknown")

	print(f"  {len(usable_items) + 1}. Cancel")

	# Here is where the game gets the player's choice.
	item_choices = [str(i + 1) for i in range(len(usable_items) + 1)]
	item_choice_num = int(get_player_input("> Use which item?: ", item_choices))

	if item_choice_num == len(usable_items) + 1:
		return 'no_action'

	selected_item_data = usable_items[item_choice_num - 1]
	item_name = selected_item_data['name'] if isinstance(selected_item_data, dict) else selected_item_data

	# This is the check to see if a combat-only item is being used outside of combat.
	if not in_combat and item_name in ['Executive Order', 'Golden Parachute', 'Civility Charm']:
		print(f"> The {item_name} can only be used during a Reprogramming Sequence.")
		return 'no_action'

	# This is the main block of logic that applies the effect of the chosen item.
	if item_name == 'Civility Charm':
		player_stats['focus'] += 3
		print(f"> You use the Civility Charm and restore 3 Focus.")
		selected_item_data['used'] = True
	elif item_name == 'Executive Order':
		player_stats['overclock_active'] = True
		print(f"> You enact an Executive Order. Your next scan will be supercharged.")
		selected_item_data['used'] = True
	elif item_name == 'Golden Parachute':
		print(f"> You use your Golden Parachute! You can now escape.")
		selected_item_data['used'] = True
		return 'flee'
	elif item_name == 'Trickle-Down Economics Textbook':
		player_stats['focus'] = max(1, player_stats['focus'] - 3)
		print(f"> You try to apply its flawed principles. It backfires, instantly draining 3 Focus.")
		inventory.remove(item_name)
	elif item_name == 'Subpoenaed Diary Logs':
		player_stats['subpoena_active'] = True
		print("> You activate the Subpoenaed Diary Logs! Your next reprogramming roll will have a +2 bonus.")
		inventory.remove(item_name)
	elif item_name == 'Logic Filter':
		player_stats['logic_filter_active'] = True
		print("> You activate the Logic Filter! It will block the next illogical statement.")
		inventory.remove(item_name)
	elif item_name == 'Suspiciously Well-Preserved Snack Cake':
		player_stats['focus'] = max(1, player_stats['focus'] - 4)
		print("> You eat the snack cake... a bold choice. You lose 4 Focus.")
		inventory.remove(item_name)
	elif item_name == 'An Old Sharpie':
		player_stats['focus'] = max(1, player_stats['focus'] - 3)
		print("> You feel a powerful urge to redraw the map to make your path shorter. The effort drains 3 Focus.")
		inventory.remove(item_name)
	elif item_name == 'Blank Keycard':
		print("\n> You hold up the Blank Keycard. It feels strangely important...")
		time.sleep(2)
		print("> ... and absolutely nothing happens.")
		inventory.remove(item_name)
	elif item_name in potion_map:
		effect = potion_map[item_name]
		new_focus = player_stats['focus'] + effect
		player_stats['focus'] = max(1, new_focus)
		print(f"> You drink the {item_name}." + (
			f" You gain {effect} Focus." if effect > 0 else f" You lose {-effect} Focus."))
		inventory.remove(item_name)

	return 'item_used'


# This function handles the "reprogramming" (battle) sequence.
def reprogramming_sequence(player_stats, robot, inventory, potion_map):
	# This is the introductory text for the encounter.
	print_color(f"\n! A {robot['name']} running corrupted code blocks your path!", 'magenta')
	print_color(f"! You must run a defragmenting sequence to pacify it.", 'magenta')
	print(
		f"! Your Focus: {COLORS['green']}{player_stats['focus']}{COLORS['reset']} | Robot's Corruption: {COLORS['red']}{robot['corruption']}{COLORS['reset']}")

	# This is the main loop for the encounter, continuing until it's won or lost.
	while robot['corruption'] > 0 and player_stats['focus'] > 0:
		print("\n--- Your Turn ---")
		print_color("Choose your action:", 'magenta')
		print("  1. Run Diagnostic Scan (This is your standard action to clear the robot's corrupted code")
		print("  2. Use an Item (This take you to your usable inventory")
		print("  3. Forfeit Turn (This skips your turn, but restores 2 Focus points)")

		# This gets the player's choice for their action.
		player_choice = get_player_input("> Choose (1, 2, or 3): ", ['1', '2', '3'])

		# This block handles the "Run Diagnostic Scan" action.
		if player_choice == '1':
			# This is the base progress roll, simulating a 5-sided die.
			progress = random.randint(1, 5)
			# This checks if the 'Executive Order' buff is active and applies its effect.
			if player_stats.get('overclock_active'):
				progress *= 2
				print("> Your Executive Order doubles your progress!")
				player_stats['overclock_active'] = False  # This consumes the buff.
			# This checks if the 'Subpoenaed Diary Logs' buff is active.
			if player_stats.get('subpoena_active'):
				progress += 2
				print("> The Subpoenaed Diary Logs enhance the scan! +2 progress!")
				player_stats['subpoena_active'] = False  # This consumes the buff.
			# This applies the final progress to the robot's corruption.
			robot['corruption'] -= progress
			print(f"> You make {progress} points of reprogramming progress.")

		# Using an item consumes the turn
		elif player_choice == '2':
			result = handle_use_item(player_stats, inventory, potion_map, in_combat=True)
			if result == 'flee':
				return 'flee'

		elif player_choice == '3':
			player_stats['focus'] += 2
			print("> You recalibrate, restoring 2 Focus points.")

		if robot['corruption'] <= 0:
			print(f"\n> Success! The {robot['name']}'s corruption is cleared.")
			return 'win'

		time.sleep(2)  # 2-second delay between player's turn and robot turn

		print("\n--- Robot's Turn ---")
		focus_drain = random.randint(1, robot['max_focus_drain'])

		# Funny robot resist messages (refocusing battle sequence)
		attack_messages = [
			f"> The robot's corrupted code pushes back! You lose {focus_drain} Focus.",
			f"> The robot insists its Corruption Level is actually zero, the best corruption level, and that everyone agrees. The blatant lie is disorienting. You lose {focus_drain} Focus.",
			f"> The robot runs a subroutine to calculate the number of dust particles in the room, then declares it to be the largest crowd of dust particles in history, period. The sheer illogicality of the statement drains {focus_drain} Focus."
		]

		if player_stats['logic_filter_active']:
			print(f"> The robot spews a stream of alternative facts, but your Logic Filter flags")
			print(f"them all as 'Pants on Fire' and blocks the disorienting effect!")
			player_stats['logic_filter_active'] = False
		else:
			player_stats['focus'] -= focus_drain
			print(random.choice(attack_messages))

		print(f"\n-- End of Turn --")
		print(f"> Your Focus: {player_stats['focus']} | Robot's Corruption: {robot['corruption']}")

	if player_stats['focus'] <= 0:
		return 'lose'

	return 'win'


# This sets up the game "world", static map, and randomized content.
def setup_game():
	# Here is the master dictionary that defines the static map layout and connections.
	game_map = {
		'Vestibule': {'exits': {'NORTH': 'Den', 'EAST': 'Nook'}, 'room_name': 'Vestibule'},
		'Nook': {'exits': {'WEST': 'Vestibule', 'NORTH': 'Study', 'EAST': 'Disco'}, 'room_name': 'Nook'},
		'Den': {'exits': {'SOUTH': 'Vestibule', 'NORTH': 'Alcove', 'EAST': 'Server Room', 'WEST': 'Atrium'},
		        'room_name': 'Den'},
		'Study': {'exits': {'WEST': 'Den', 'SOUTH': 'Nook', 'NORTH': 'Keep', 'EAST': 'Game Room'},
		          'room_name': 'Study'},
		'Atrium': {'exits': {'NORTH': 'Foundry', 'SOUTH': 'Server Room'}, 'room_name': 'Atrium'},
		'Server Room': {'exits': {'NORTH': 'Atrium', 'EAST': 'Den'}, 'room_name': 'Server Room'},
		'Foundry': {'exits': {'SOUTH': 'Atrium', 'EAST': 'Alcove'}, 'room_name': 'Foundry'},
		'Alcove': {'exits': {'WEST': 'Foundry', 'SOUTH': 'Den', 'EAST': 'Keep'}, 'room_name': 'Alcove',
		           'special_exit': 'Stairs Up'},
		'Keep': {'exits': {'WEST': 'Alcove', 'SOUTH': 'Study', 'EAST': 'Cannery'}, 'room_name': 'Keep'},
		'Cannery': {'exits': {'WEST': 'Keep', 'SOUTH': 'Game Room'}, 'room_name': 'Cannery'},
		'Game Room': {'exits': {'NORTH': 'Cannery', 'WEST': 'Study', 'SOUTH': 'Disco'}, 'room_name': 'Game Room'},
		'Disco': {'exits': {'NORTH': 'Game Room', 'WEST': 'Nook'}, 'room_name': 'Disco'},
		'Sanctuary': {'exits': {'WEST': 'Loft', 'EAST': 'Collection Room', 'SOUTH': 'Haven'}, 'room_name': 'Sanctuary',
		              'special_exit': 'Stairs Down'},
		'Loft': {'exits': {'EAST': 'Sanctuary', 'SOUTH': 'Retreat'}, 'room_name': 'Loft'},
		'Retreat': {'exits': {'NORTH': 'Loft', 'EAST': 'Haven'}, 'room_name': 'Retreat'},
		'Collection Room': {'exits': {'WEST': 'Sanctuary', 'SOUTH': 'Perch'}, 'room_name': 'Collection Room'},
		'Perch': {'exits': {'NORTH': 'Collection Room', 'WEST': 'Haven'}, 'room_name': 'Perch'},
		'Haven': {'exits': {'NORTH': 'Sanctuary', 'EAST': 'Perch', 'WEST': 'Retreat'}, 'room_name': 'Haven'}
	}

	# This loop ensures every room has the same set of keys to prevent errors later.
	for details in game_map.values():
		details.update({'item': None, 'robot': None, 'villain': False})
		if 'special_exit' not in details:
			details['special_exit'] = None

	# These are the lists of all possible content that can be placed in the game.
	quest_items = ['Peer-Reviewed Fact-Checker', 'Civics 101 Patch', 'De-Escalation Algorithm',
	               'Green Energy Core', 'Tax-the-Rich Capacitor', 'Historical Context Drive', 'Deregulation Lubricant']
	wildcard_items = ['Logic Filter', 'Trickle-Down Economics Textbook', 'Subpoenaed Diary Logs',
	                  'Suspiciously Well-Preserved Snack Cake', 'Blank Keycard', 'An Old Sharpie']
	focus_vials = ['Red Focus Vial', 'Blue Focus Vial', 'Purple Focus Vial']
	all_items = quest_items + wildcard_items + focus_vials

	robots = [
		{'name': 'Corrupted Floor Buffer', 'corruption': 2, 'max_focus_drain': 3},
		{'name': 'Malfunctioning Auto-Stapler', 'corruption': 2, 'max_focus_drain': 3},
		{'name': 'Aggressive BaristaBot', 'corruption': 4, 'max_focus_drain': 4},
		{'name': 'TPS Report Drone', 'corruption': 4, 'max_focus_drain': 4},
		{'name': 'Overzealous Scheduling Robot', 'corruption': 5, 'max_focus_drain': 5},
		{'name': 'Head of Synergy Enforcement Bot', 'corruption': 6, 'max_focus_drain': 6}
	]

	portals = ['Portal', 'Portal']

	# Shuffles which potion gets > or < effects
	potion_effects = [5, 3, -4]
	random.shuffle(potion_effects)
	potion_map = {
		'Red Focus Vial': potion_effects[0],
		'Blue Focus Vial': potion_effects[1],
		'Purple Focus Vial': potion_effects[2]
	}

	# This gets a list of all possible locations items and bots can be placed.
	all_locations = list(game_map.keys())
	all_locations.remove('Vestibule')

	# This is the list of rooms the villain cannot be placed in.
	villain_safe_zones = ['Vestibule', 'Alcove', 'Sanctuary']
	valid_villain_locations = [loc for loc in all_locations if loc not in villain_safe_zones]

	# This is where the villain is randomly placed.
	villain_location = random.choice(valid_villain_locations)
	game_map[villain_location]['villain'] = True

	# This creates the final list of rooms where content can be placed.
	available_rooms = [loc for loc in all_locations if loc != villain_location]
	random.shuffle(available_rooms)

	# This places all the items randomly.
	random.shuffle(all_items)
	item_placement_rooms = available_rooms[:len(all_items)]
	for i in range(len(all_items)):
		room_key = item_placement_rooms[i]
		game_map[room_key]['item'] = all_items[i]

	# This places all the robots randomly.
	random.shuffle(robots)
	robot_placement_rooms = available_rooms[:len(robots)]
	for i in range(len(robots)):
		room_key = robot_placement_rooms[i]
		game_map[room_key]['robot'] = robots[i]

	# This block places the portals in rooms that don't already have a robot.
	rooms_without_robots = [room for room in available_rooms if room not in robot_placement_rooms]
	random.shuffle(rooms_without_robots)
	portal_placement_rooms = rooms_without_robots[:len(portals)]
	for room_key in portal_placement_rooms:
		game_map[room_key]['special_exit'] = 'Portal'

	# This returns the fully randomized game state to the main function.
	return game_map, villain_location, potion_map


# This is the main function that runs the game and contains the game loop and logic.
def main():
	show_instructions()
	# Outer loop to control playing again
	while True:
		# Here is where the game calls setup_game() to get a new, randomized world for each game.
		game_map, villain_location, potion_map = setup_game()

		# This is the dictionary for the player's stats (resets every game).
		player_stats = {
			'focus': 15,
			'logic_filter_active': False,
			'overclock_active': False,
			'subpoena_active': False
		}
		# This is the player's starting inventory.
		inventory = [
			{'name': 'Civility Charm', 'used': False},  # Restores 3 focus
			{'name': 'Executive Order', 'used': False},  # Doubles reprogramming
			{'name': 'Golden Parachute', 'used': False},  # Instant flee
		]
		# This is the list of quest items, used for the win condition check.
		quest_items_to_win = ['Peer-Reviewed Fact-Checker', 'Civics 101 Patch', 'De-Escalation Algorithm',
		                      'Green Energy Core', 'Tax-the-Rich Capacitor', 'Historical Context Drive',
		                      'Deregulation Lubricant']

		# This is the dictionary for all the custom item descriptions.
		item_descriptions = {
			'Blank Keycard': "You find a beautifully framed, but completely blank, healthcare plan. Its sheer, unadulterated uselessness is almost an art form.",
			'An Old Sharpie': "You find a thick, black marker. It seems to hum with a strange, world-altering power.",
			'Subpoenaed Diary Logs': "You find a dusty old diary. The pages are filled with what looks like binary code and complaints about toner cartridges.",
			'Trickle-Down Economics Textbook': "This looks important, but it seems to be filled with flawed logic.",
			'Red Focus Vial': "A vial containing a swirling, crimson liquid. It smells faintly of cherries and determination.",
			'Blue Focus Vial': "A vial of calm, blue liquid. It bubbles gently, like a peaceful spring.",
			'Purple Focus Vial': "A vial of a deep, mysterious purple fluid. You're not entirely sure if it's supposed to be glowing like that."
		}

		current_location = 'Vestibule'
		game_running = True

		# This is the main loop for a single game session.
		while game_running:
			show_status(game_map, current_location, inventory, player_stats, quest_items_to_win)

			room = game_map[current_location]

			# This is the combined win/loss condition. It runs first every turn.
			if room['villain']:
				inventory_names = [item['name'] if isinstance(item, dict) else item for item in inventory]
				quest_items_present = all(item in inventory_names for item in quest_items_to_win)

				# This is the win condition check.
				if quest_items_present:
					print(
						"\nYou've entered a pristine, minimalist office. A single, perfectly polished nameplate reads 'Mr. Ton Drump'.")
					time.sleep(2)
					print(
						f"He looks up from a teetering stack of TPS reports, his {COLORS['red']}eyes{COLORS['reset']} narrowing.")
					time.sleep(2)
					print("'My parking spot,' he whispers with icy rage. 'You... you know what she did.'")
					time.sleep(2)
					print_color(
						"\nYou hold up the final component and say, 'Looks like your alternative facts just ran into a peer-reviewed reality.'",
						'green')
					time.sleep(3)
					print("\nAs he sputters in confusion, a wave of calming, green energy pulses through the walls.")
					print("On a monitor behind him, you see security footage of the corrupted robots slowing down,")
					print("whirring gently, and returning to their peaceful programming.")
					time.sleep(2)
					print_color("\n===============================================================", 'cyan')
					print_color("                 Y O U   W I N ! ! !                 ", 'green')
					print_color("===============================================================", 'cyan')
					print(
						f"You didn't win by {COLORS['red']}fighting{COLORS['reset']}, you won by {COLORS['cyan']}healing{COLORS['reset']}. Congratulations!")
					print_color("===============================================================", 'cyan')
					game_running = False

				# This is the lose condition.
				else:
					print(
						"\nYou've entered a pristine, minimalist office. A single, perfectly polished nameplate reads 'Mr. Ton Drump'.")
					time.sleep(2)
					print(
						f"He looks up from a teetering stack of TPS reports, his {COLORS['red']}eyes{COLORS['reset']} narrowing.")
					time.sleep(2)
					print("'My parking spot,' he whispers with icy rage. 'You... you know what she did.'")
					time.sleep(2)
					print("\nHe presses a button on his desk, and the door slams shut behind you.")
					print_color("GAME OVER.", 'red')
					game_running = False

				# This ends the turn after a win or loss.
				continue

			# This is the "ambush" check for robots (when the player enters a room with a robot).
			if room['robot'] is not None:
				robot_to_fight = room['robot']
				result = reprogramming_sequence(player_stats, robot_to_fight, inventory, potion_map)

				if result == 'win':
					room['robot'] = None
					print(f"\nThe {robot_to_fight['name']} has been pacified. The room is now safe.")
					continue
				elif result == 'flee':
					valid_exits = list(room['exits'].keys())
					flee_direction = random.choice(valid_exits)
					current_location = room['exits'][flee_direction]
					print(f"\nYou hastily flee {flee_direction} into the {game_map[current_location]['room_name']}...")
					continue
				elif result == 'lose':
					print_color("GAME OVER.", 'red')
					game_running = False
					continue

			# This is the loop for player actions within a single turn.
			action_taken_this_turn = False
			while not action_taken_this_turn:
				# Here is where the game builds the colored string for the available exits.
				colored_exits = [f"{COLORS['green']}{exit_dir}{COLORS['reset']}" for exit_dir in room['exits'].keys()]
				print("\n> Available exits:", ", ".join(colored_exits))

				command = input("> What do you do? ").upper().strip()

				# This block handles the SEARCH command.
				if command == 'SEARCH':
					print("\n> You search the room...")
					item_in_room = room.get('item')
					special_exit = room.get('special_exit')

					# This is the logic that runs if an item is found in the room.
					if item_in_room:
						# Here, the game checks if the item has a special description and print it if it does.
						if item_in_room in item_descriptions:
							print(f"  {item_descriptions[item_in_room]}")

						# This is the prompt asking the player if they want to collect the item.
						get_choice = get_player_input(
							f"> You see a {COLORS['yellow']}{item_in_room}{COLORS['reset']}. Would you like to get it? ({COLORS['green']}YES{COLORS['reset']}/{COLORS['red']}NO{COLORS['reset']}): ",
							['yes', 'no'])

						# This is the block that runs if the player says 'yes'.
						if get_choice == 'yes':
							# Here, the game adds the item to the inventory.
							inventory.append(item_in_room)
							# This is where the game removes the item from the room so it can't be picked up again.
							room['item'] = None
							print_color(f"> You picked up the {item_in_room}.", 'green')

							# This is the logic to tell the player what kind of item they found.
							if item_in_room in quest_items_to_win:
								print_color("> This looks like a crucial component for Dr. Gucnew's device!",
								            'magenta')
							elif item_in_room != 'Blank Keycard':
								print_color("> This item looks like it could be used once during your quest.",
								            'yellow')

					# This block handles finding stairs or portals.
					if special_exit:
						if 'Stairs' in special_exit:  # Stairs
							prompt = "> You see a grand, winding staircase. Use it? (YES/NO): "
						# This is the "portal"
						else:
							prompt = "> A shimmering portal hums in the corner. Enter it? (YES/NO): "

						use_choice = get_player_input(prompt, ['yes', 'no'])
						if use_choice == 'yes':
							if 'Stairs Up' in special_exit:
								current_location = 'Sanctuary'
							elif 'Stairs Down' in special_exit:
								current_location = 'Alcove'
							else:  # Portal
								print("\n> You step into the portal...")
								time.sleep(1)
								print("> A whirlwind of colors and strange noises envelops you.")
								time.sleep(1.5)
								print("> Things get weird.")
								time.sleep(1)
								print("> You stumble out into a strange room...")
								# This makes sure the player can't be transported to the Villains room
								safe_locs = [loc for loc in game_map.keys() if
								             loc not in [villain_location]]
								current_location = random.choice(safe_locs)
							action_taken_this_turn = True

					if not item_in_room and not special_exit:
						print("> You find nothing else of interest.")

				# This handles the USE command.
				elif command == 'USE':
					handle_use_item(player_stats, inventory, potion_map)

				# This handles all valid movement commands.
				elif command in room['exits']:
					current_location = room['exits'][command]
					action_taken_this_turn = True

				# This handles the EXIT command.
				elif command == 'EXIT':
					game_running = False
					action_taken_this_turn = True
				else:
					print("\nInvalid command.")

			# This check is to break out of the main loop if the game ended from an EXIT command.
			if not game_running:
				break

		# This is the "Play Again" feature that runs after a win, loss, or exit.
		play_again = get_player_input("\n> Would you like to play again? (YES/NO): ", ['yes', 'no'])
		if play_again == 'no':
			break  # This breaks the outermost loop and ends the program.

	print("\nThanks for playing!")


# It ensures that the main() function is called only when the game runs this file directly.
if __name__ == "__main__":
	main()
