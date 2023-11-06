"""This module contains the PlayerCharacter class."""
from enum import Enum
import osrlib.ability
from osrlib.ability import (
    AbilityType,
    Charisma,
    Constitution,
    Dexterity,
    Intelligence,
    ModifierType,
    Strength,
    Wisdom,
)
from osrlib.character_classes import (
    CharacterClass,
    CharacterClassType,
    ClassLevel,
)
from osrlib.inventory import Inventory
from osrlib import (
    dice_roller,
    game_manager as gm,
)


class Alignment(Enum):
    """Represents the alignment of a player character (PC) or monster."""

    LAWFUL = "Lawful"
    NEUTRAL = "Neutral"
    CHAOTIC = "Chaotic"


class PlayerCharacter:
    """Represents a player character (PC) in the game.

    Attributes:
        name (str): The name of the character.
        abilities (dict): A dictionary of the character's abilities.
        character_class (CharacterClass): The character's class.
        inventory (Inventory): The character's inventory.
    """

    def __init__(
        self,
        name: str,
        character_class_type: CharacterClassType,
        level: int = 1,
    ):
        """Initialize a new PlayerCharacter (PC) instance."""
        self.name = name
        self.abilities = {}
        self.roll_abilities()  # TODO: Should NOT roll abilities when loading a saved character
        self.character_class = None
        self.set_character_class(character_class_type, level)

        self.inventory = Inventory(self)

    def __str__(self):
        """Get a string representation of the PlayerCharacter instance.

        Returns:
            str: A string representation of the PlayerCharacter instance.
        """
        ability_str = ", ".join(
            f"{ability.name}: {attr.score:>2}"
            for ability, attr in self.abilities.items()
        )
        return (
            f"Name: {self.name}, "
            f"Class: {self.character_class.class_type.name}, "
            f"Level: {self.character_class.current_level.level_num}, "
            f"HP: {self.character_class.hp}, "
            f"AC: {self.armor_class}, "
            f"XP: {self.character_class.xp}, "
            f"{ability_str}"
        )

    @property
    def is_alive(self) -> bool:
        """Returns True if the character is alive.

        The character is considered alive if their hit points are greater than 0.

        Returns:
            bool: True if the character is alive (hit points > 0), False otherwise.
        """
        return self.hit_points > 0

    @property
    def level(self):
        return (
            self.character_class.current_level.level_num
            if self.character_class.current_level.level_num is not None
            else None
        )

    @property
    def hit_points(self):
        return self.character_class.hp

    @property
    def armor_class(self):
        """Get the armor class of the character."""
        armor_class = 9
        armor_class += self.abilities[AbilityType.DEXTERITY].modifiers[ModifierType.AC]
        armor_class += sum(
            armor_item.ac_modifier
            for armor_item in self.inventory.armor
            if armor_item.is_equipped
        )
        return armor_class

    def get_ability_roll(self):
        """Rolls a 4d6 and returns the sum of the three highest rolls."""
        roll = dice_roller.roll_dice("4d6", drop_lowest=True)
        return roll.total

    def get_initiative_roll(self):
        """Rolls a 1d6, adds the character's Dexterity modifier, and returns the total."""
        modifier_value = self.abilities[AbilityType.DEXTERITY].modifiers[
            ModifierType.INITIATIVE
        ]
        roll = dice_roller.roll_dice("1d6", modifier_value=modifier_value)
        return roll.total_with_modifier

    def set_character_class(
        self, character_class_type: CharacterClassType, level: int = 1
    ):
        """Sets the character class of the character."""
        # TODO: Add validation to prevent setting a class if the class' ability score prerequisites aren't met
        self.character_class = CharacterClass(
            character_class_type,
            level,
            self.abilities[AbilityType.CONSTITUTION].modifiers[ModifierType.HP],
        )
        return self.character_class

    def grant_xp(self, xp: int) -> ClassLevel:
        """Grants XP to the character, taking into account their Constitution ability modifier, if any."""
        self.character_class.xp += xp
        try:
            # Need to pass the character's Constitution modifier all the way down to the roll_hp method
            return self.character_class.level_up(
                self.abilities[AbilityType.CONSTITUTION].modifiers[ModifierType.HP]
            )
        except ValueError as e:
            print(e)

    def roll_abilities(self):
        """Rolls the ability scores of the character."""
        self.abilities = {}
        for ability_class in [
            Strength,
            Intelligence,
            Wisdom,
            Dexterity,
            Constitution,
            Charisma,
        ]:
            roll = self.get_ability_roll()
            ability_instance = ability_class(roll)
            self.abilities[ability_instance.ability_type] = ability_instance
            gm.logger.debug(
                f"{self.name} rolled {roll} for {ability_instance.ability_type.name}"
            )

    def roll_hp(self) -> dice_roller.DiceRoll:
        """Rolls the character's hit points, taking into account their Constitution modifier, if any.

        The total value of the roll with modifier can be negative after if the roll was low and the character has a
        negative Constitution modifier. You should clamp the value to 1 before applying it to the character's HP.

        Returns:
            DiceRoll: The result of the HP roll. Value with modifiers can be negative.
        """
        hp_modifier = self.abilities[AbilityType.CONSTITUTION].modifiers[
            ModifierType.HP
        ]
        hp_roll = self.character_class.roll_hp(hp_modifier)
        gm.logger.debug(
            f"{self.name} rolled {hp_roll} for HP and got {hp_roll.total_with_modifier} ({hp_roll.total} {hp_modifier})."
        )
        return self.character_class.roll_hp(hp_modifier)

    def to_dict(self):
        return {
            "name": self.name,
            "character_class_type": self.character_class.class_type.name,
            "level": self.character_class.current_level.level_num,
            "hit_points": self.character_class.hp,
            "experience_points": self.character_class.xp,
            "abilities": {k.value: v.to_dict() for k, v in self.abilities.items()},
            "inventory": self.inventory.to_dict(),
        }

    @classmethod
    def from_dict(cls, data_dict: dict):
        pc = cls(
            name=data_dict["name"],
            character_class_type=CharacterClassType[data_dict["character_class_type"]],
            level=data_dict["level"],
        )
        pc.abilities = {
            AbilityType[k.upper()]: getattr(
                osrlib.ability, AbilityType[v["ability_type"]].value
            )(score=v["score"])
            for k, v in data_dict["abilities"].items()
        }
        pc.character_class.hp = data_dict["hit_points"]
        pc.character_class.xp = data_dict["experience_points"]
        pc.inventory = Inventory.from_dict(data_dict["inventory"], pc)

        return pc
