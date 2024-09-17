from data.item import Item
from oop.patterns.singleton_meta import SingletonMeta

from packets.game.item_info import ItemLocation
from packets.game.item import MsgItem, ItemAction


class ItemsHolder(metaclass=SingletonMeta):
    def __init__(self, client):
        self.items = {}
        for location in ItemLocation:
            self.items[location] = []

    @property
    def inventory_items(self):
        return self.items[ItemLocation.Inventory]

    @property
    def inventory_length(self):
        return len(self.inventory_items)


    def is_inventory_full(self):
        return self.inventory_length >= 40

    def add_item(self, item: Item):
        self.items[item.location].append(item)

    def remove_item(self, item: Item):
        self.items[item.location].remove(item)

    def get_items(self, location: ItemLocation):
        return self.items[location]

    def search_item(self, location: ItemLocation, item_id: int):
        results = []
        for item in self.items[location]:
            if item.item_id == item_id:
                results.append(item)
        return results

    async def buy_item(self, shop_id: int, item_id: int, amount: int):
        bought_item_packet = MsgItem(self.client, shop_id, item_id, ItemAction.BuyFromNPC, amount, 0)
        await self.client.send(bought_item_packet)

    async def use_gate_item(self, item: Item):
        use_gate_packet = MsgItem(self.client,
                                  item.item_unique_id, 0, ItemAction.EquipItem, 0)
        await self.client.send(use_gate_packet)
