from enum import Enum


class PlayerBackground(Enum):
    BARBARIAN = ("Barbarian", "Sword", "Chain Mail", None)
    RANGER = ("Ranger", "Bow", "Leather Armor", "Arrow")
    WIZARD = ("Wizard", "Staff", "Robe", None)

    def __init__(self, name, weapon, armor, consumable):
        self._name = name
        self._weapon = weapon
        self._armor = armor
        self._consumable = consumable

    @property
    def name(self):
        return self._name

    @property
    def weapon(self):
        return self._weapon

    @property
    def armor(self):
        return self._armor

    @property
    def consumable(self):
        return self._consumable
