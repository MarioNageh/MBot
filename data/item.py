from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from packets.game.item_info import ItemLocation


class Item:
    def __init__(self, item_unique_id: int, item_id: int, durability: int, max_durability: int
                 , identify: int, location: 'ItemLocation', unknown1: int, gem1: int, gem2: int,
                 magic1: int, magic2: int, plus: int, bless: int, enchant: int, locked: int, color: int):
        self.item_unique_id = item_unique_id
        self.item_id = item_id
        self.durability = durability
        self.max_durability = max_durability
        self.identify = identify
        self.location = location
        self.unknown1 = unknown1
        self.gem1 = gem1
        self.gem2 = gem2
        self.magic1 = magic1
        self.magic2 = magic2
        self.plus = plus
        self.bless = bless
        self.enchant = enchant
        self.locked = locked
        self.color = color

    def __str__(self):
        return f"Item: {self.item_id}, Location: {self.location}, Unique ID: {self.item_unique_id}"
