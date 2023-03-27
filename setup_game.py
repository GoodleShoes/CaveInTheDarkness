"""Handle the loading and initialization of game sessions."""
from __future__ import annotations

import copy
import lzma
import os
import pickle
import traceback
from typing import Optional

import engine
import tcod

import color
from engine import Engine
import entity_factories
from game_map import GameWorld
import input_handlers

# Load the background image and remove the alpha channel.
background_image = tcod.image.load("menu_background2.png")[:, :, :3]


def new_game(new_character_name) -> Engine:
    """Return a brand new game session as an Engine instance."""
    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    player = copy.deepcopy(entity_factories.player)

    engine = Engine(player=player)

    engine.player.name = new_character_name

    engine.game_world = GameWorld(
        engine=engine,
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
    )

    engine.game_world.generate_floor()
    engine.update_fov()

    engine.message_log.add_message(
        "Hello and welcome, adventurer, to yet another dungeon!", color.welcome_text
    )

    # dagger = copy.deepcopy(entity_factories.dagger)
    bow = copy.deepcopy(entity_factories.bow)
    arrow = copy.deepcopy(entity_factories.arrow)
    leather_armor = copy.deepcopy(entity_factories.leather_armor)

    bow.parent = player.inventory
    # dagger.parent = player.inventory
    leather_armor.parent = player.inventory

    player.inventory.items.append(bow)
    player.inventory.items.append(arrow)
    player.equipment.toggle_equip(bow, add_message=False)

    player.inventory.items.append(leather_armor)
    player.equipment.toggle_equip(leather_armor, add_message=False)

    return engine


def new_game_character_name_menu(self) -> Optional[str, Engine]:
    """Prompt user to create character name"""

    new_character_name = ""
    show_name_too_long_message = False

    self.console.clear()

    self.console.print(
        self.console.width // 2,
        self.console.height // 2,
        "Enter your character name:",
        fg=(255, 255, 255),
        bg=(0, 0, 0),
        alignment=tcod.CENTER,
    )

    self.context.present(self.console)

    while True:

        # Print the current name at a fixed position
        self.console.print(
            self.console.width // 2,
            self.console.height // 2 + 1,
            new_character_name,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
            alignment=tcod.CENTER,
        )

        if show_name_too_long_message:
            self.console.print(
                self.console.width // 2,
                self.console.height // 2 + 2,
                "This name is too long, sorry!",
                fg=(255, 0, 0),
                bg=(0, 0, 0),
                alignment=tcod.CENTER,
            )

        self.context.present(self.console)

        key = tcod.console_wait_for_keypress(flush=True)

        # Check if name is at limit
        if len(new_character_name) >= 15:
            show_name_too_long_message = True

        # Handle backspace
        if key.vk == tcod.KEY_BACKSPACE:
            new_character_name = new_character_name[:-1]
            show_name_too_long_message = False  # clear the message
            self.context.present(self.console)

        # Handle enter key
        elif key.vk == tcod.KEY_ENTER and new_character_name:
            return new_character_name

        # Handle alphanumeric input
        elif 32 <= key.vk <= 126 and len(new_character_name) < 15:
            new_character_name += chr(key.c)

        if key.vk == tcod.KEY_ESCAPE:
            return None

        self.console.clear()
        self.console.print(
            self.console.width // 2,
            self.console.height // 2,
            "Enter your character name:",
            fg=(255, 255, 255),
            bg=(0, 0, 0),
            alignment=tcod.CENTER,
        )
        self.console.print(
            self.console.width // 2,
            self.console.height // 2 + 1,
            new_character_name,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
            alignment=tcod.CENTER,
        )
        self.context.present(self.console)


def load_game(filename: str) -> Engine:
    """Load an Engine instance from a file."""
    with open(filename, "rb") as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    return engine


def load_saved_games_menu(self) -> Optional[str, Engine]:
    """Show a list of saved game files and prompt the user to choose one to load."""
    saved_games = []
    for filename in os.listdir("saves"):
        if filename.endswith(".sav"):
            saved_games.append(filename[:-4])

    if not saved_games:
        return None
    self.console.clear()

    self.console.print(
        self.console.width // 2,
        0,
        "Select a saved game to load",
        fg=color.menu_title,
        alignment=tcod.CENTER,
    )

    for i, saved_game_name in enumerate(saved_games):
        self.console.print(
            self.console.width // 2,
            i + 2,
            f"[{i + 1}] {saved_game_name}",
            fg=color.menu_text,
            alignment=tcod.CENTER,
        )

    self.context.present(self.console)

    while True:
        key = tcod.console_wait_for_keypress(flush=True)
        if key.vk == tcod.KEY_ESCAPE:
            return None

        try:
            choice = int(chr(key.c))
            if choice <= len(saved_games):
                return saved_games[choice - 1]
        except (ValueError, KeyError, IndexError):
            pass


class MainMenu(input_handlers.BaseEventHandler):
    """Handle the main menu rendering and input."""

    # def __init__(self, console):
    #     self.console = console
    def __init__(self, console: tcod.Console, context: tcod.Context):
        self.context = context
        self.console = console
        self.width = console.width
        self.height = console.height

    def on_render(self, console: tcod.Console) -> None:
        """Render the main menu on a background image."""
        console.draw_semigraphics(background_image, 0, 0)

        console.print(
            console.width // 2,
            console.height // 2 - 4,
            "Cave in the Darkness",
            fg=color.menu_title,
            alignment=tcod.CENTER,
        )
        console.print(
            console.width // 2,
            console.height - 2,
            "By GoodleShoes",
            fg=color.menu_title,
            alignment=tcod.CENTER,
        )

        menu_width = 24
        for i, text in enumerate(
                ["[N] Play a new game", "[L] Load a saved game", "[Q] Quit"]
        ):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg=color.menu_text,
                bg=color.black,
                alignment=tcod.CENTER,
                bg_blend=tcod.BKGND_ALPHA(64),
            )

    def ev_keydown(
            self, event: tcod.event.KeyDown
    ) -> Optional[input_handlers.BaseEventHandler]:
        if event.sym in (tcod.event.K_q, tcod.event.K_ESCAPE):
            raise SystemExit()
        elif event.sym == tcod.event.K_l:
            saved_game_name = load_saved_games_menu(self)
            if saved_game_name is None:
                return input_handlers.PopupMessage(self, "No saved game to load.")
            try:
                return input_handlers.MainGameEventHandler(load_game(f"saves/{saved_game_name}.sav"))
            except FileNotFoundError:
                return input_handlers.PopupMessage(self, "No saved game to load.")
            except Exception as exc:
                traceback.print_exc()  # Print to stderr.
                return input_handlers.PopupMessage(self, f"Failed to load save:\n{exc}")
        elif event.sym == tcod.event.K_n:
            new_character_name = new_game_character_name_menu(self)
            if new_character_name is None:
                return None  # User cancelled
            try:
                return input_handlers.MainGameEventHandler(new_game(new_character_name))
            except Exception as exc:
                traceback.print_exc()  # Print to stderr.
                return input_handlers.PopupMessage(self, f"Failed to start new game:\n{exc}")

        return None
