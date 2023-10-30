from textual.app import App, ComposeResult

from osrlib import CharacterClassType, PlayerCharacter, Armor, Item, Weapon
from screen import CharacterScreen, WelcomeScreen, ExploreScreen


class OSRConsole(App):
    CSS_PATH = "screen.tcss"

    BINDINGS = [
        ("c", "character", "Character"),
        ("e", "explore", "Explore"),
        ("q", "quit", "Quit"),
    ]

    player_character = PlayerCharacter(
        "Sckricko", CharacterClassType.FIGHTER
    )
    armor = Armor("Chain Mail", -5, usable_by_classes = {CharacterClassType.FIGHTER}, max_equipped = 2, gp_value = 40)
    shield = Armor("Shield", -1, usable_by_classes = {CharacterClassType.FIGHTER}, max_equipped = 2, gp_value = 10)
    sword = Weapon("Sword", "1d8", usable_by_classes = {CharacterClassType.FIGHTER}, max_equipped = 1, gp_value = 10)
    player_character.inventory.add_item(armor)
    player_character.inventory.add_item(shield)
    player_character.inventory.add_item(sword)
    player_character.inventory.equip_item(armor)
    player_character.inventory.equip_item(shield)
    player_character.inventory.equip_item(sword)

    backpack = Item("Backpack", gp_value = 5)
    wineskin = Item("Wineskin", gp_value = 1)
    iron_rations = Item("Iron Rations", gp_value = 15)
    torch = Item("Torch", gp_value = 1)
    player_character.inventory.add_item(backpack)
    player_character.inventory.add_item(wineskin)
    player_character.inventory.add_item(iron_rations)
    player_character.inventory.add_item(torch)

    SCREENS = {"scr_character": CharacterScreen(),
               "scr_welcome": WelcomeScreen(),
               "scr_explore": ExploreScreen()}

    def compose(self) -> ComposeResult:
        yield WelcomeScreen()

    def on_mount(self) -> None:
        self.title = "OSR Console"
        self.sub_title = "Adventures in turn-based text"

    def action_character(self) -> None:
        """Show the character screen."""
        self.push_screen("scr_character")

    def action_explore(self) -> None:
        """Show the explore screen."""
        self.push_screen("scr_explore")

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()


app = OSRConsole()
if __name__ == "__main__":
    app.run()
