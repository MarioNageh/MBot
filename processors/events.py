import random
from typing import TYPE_CHECKING, List

from constants import ConstantItems, Maps, SobNpcToSearch, Coordinate
from data.item import Item
from data.player import Player
from data.rectangle import Rectangle
from data.sob_npc import SobNpc
from exceptions import UserNotHaveThisItem, PlayerNotTeleport, InventoryFull, AStarPathCalculationError
from packets.game.item_info import ItemLocation
from processors.kernel import Event
from threads.astar_cals import AStarWorkerThread

if TYPE_CHECKING:
    from client.game_client import GameClient


def SetInterval(interval: int, periodic: bool):
    def decorator(func):
        func.interval = interval
        func.periodic = periodic
        return func

    return decorator


@SetInterval(.1, False)
async def attack_sob_npc(event: Event, c):
    client: GameClient = c
    player: Player = client.player
    target_object: SobNpc = player.target_object
    if target_object is None:
        return
    from packets.game.interact import InteractMsg, InteractAction

    x = player.map_x
    y = player.map_y

    if not client.player.is_archer() and Coordinate.distance_between_points(player.position,
                                                                            target_object.position) != 1:
        e: Event = Event.create_event_from_callback(client, choose_rnd_sob_npc)
        e.event_args["target"] = target_object
        client.main_app.printer.print_info(f"Player Distance From SobNpc Is Too Far, Try To Find Another SobNpc")
        client.main_app.kernel.add_event(e)
        return

    if player.is_warrior():
        x += random.randint(-1, 1)

    attack_packet = InteractMsg(client
                                , player.user_id
                                , target_object.sob_uuid
                                , x
                                , y
                                , InteractAction.Attack, 0)

    await client.send(attack_packet)
    client.main_app.printer.print_info(
        f"Player Attack SobNpc: {target_object.sob_uuid} at {target_object.position} from ({x}, {y})")

    player.is_attacking = True


@SetInterval(800 / 1000, False)
async def move_to_sob_npc(event: Event, c):
    client: GameClient = c
    player: Player = client.player
    target: Coordinate = player.target_coordinates  # Is Selected From choose_rnd_sob_npc step
    if target is None:
        return
    '''
    This Fro Debugging to Check If The Event Called More Than 30 Times
    To not Busy The Event Loop Consider it as Timeout
    '''
    event.calls_count += 1
    if event.calls_count > 30:
        print("There Is Error")

    '''
    if the player is not path finding his way to the target, stop the event
    '''
    if not player.player_finding_his_way:
        event.is_finished = True
        return

    distance = Coordinate.distance_between_points(player.position, target)

    limit = player.is_archer() and random.randint(4, 8) or random.randint(1, 1)
    if player.invalid_coordinates:  # If We Receive Invalid Coordinates
        '''
         in A* algorithm, if the player can't find his way to the target
         Error In Calculating Path
        '''
        raise AStarPathCalculationError(client, f"Error In Calculating Path {player.path}")

    if player.path is None:
        raise AStarPathCalculationError(client, f"Error In Calculating")

    if distance <= limit:
        event.is_finished = True
        player.player_finding_his_way = False
        player.last_target_coordinates = player.target_coordinates
        target_son_npc = Coordinate(player.target_coordinates.x, player.target_coordinates.y)
        player.target_coordinates = None
        sob_npc = player.sobNpcController.get_nearest_sob_npc(target_son_npc)
        player.target_object = sob_npc
        client.main_app.kernel.add_event(Event.create_event_from_callback(client, attack_sob_npc))
        return

    from packets.game.walk import Walk
    from packets.game.action import ActionMsg

    if len(player.path) > 8:
        end_point = player.path[8]
        player.path = player.path[8:]
        jump_packet = ActionMsg.jump_packet(client, player.user_id, end_point)
        await client.send(jump_packet)
    elif len(player.path) > 0:
        end_point = player.path[0]
        player.path = player.path[1:]
        direction = Coordinate.get_direction(player.position, end_point)
        walk_packet = Walk(client, player.user_id, direction, 1)
        await client.send(walk_packet)
    elif len(player.path) == 0 and not player.is_archer():
        event.is_finished = True
        raise AStarPathCalculationError(client,
                                        f"Player Not Reach The Target Player Position: {player.position} Target: {target}")


@SetInterval(1 / 1000, False)
async def received_finish_astar(event: Event, c):
    client: GameClient = c
    player: Player = client.player
    client.main_app.printer.print_info(f"Player Received Path From Astar")

    path = event.event_args["path"]

    if path is None:
        client.main_app.printer.print_fail(f"Cant Find Path To -->: {player.target_coordinates}")
        client.main_app.printer.print_info(f"Try To Rnd Jump Again")
        client.main_app.kernel.add_event(Event.create_event_from_callback(client, rnd_jump))
        return

    '''
    Path Found Start Moving To The Target
    '''

    client.main_app.printer.print_info(f"Player Found Path To -->: {player.target_coordinates}")
    player.path = path
    player.player_finding_his_way = True
    client.main_app.kernel.add_event(Event.create_event_from_callback(client, move_to_sob_npc))


@SetInterval(5, True)
async def say_hello_world(event: Event, c):
    client: GameClient = c
    from packets.game import Talk
    talk_packet = Talk.talk_packet(client, "Controlled By Mario")
    await client.send(talk_packet)


@SetInterval(1, False)
async def rnd_jump(event: Event, c):
    client: GameClient = c
    player: Player = client.player
    rec: Rectangle = Rectangle(
        Coordinate(423, 362)
        , Coordinate(455, 394)
        , Coordinate(455, 362)
        , Coordinate(423, 394)
    )
    rnd_coords: Coordinate = rec.get_point_inside_to_jump_to(player.position)

    client.main_app.printer.print_info(f"Player Rnd Jump To: {rnd_coords}")
    from packets.game import ActionMsg
    jump_packet = ActionMsg.jump_packet(client, player.user_id, rnd_coords)
    await client.send(jump_packet)

    rnd_target = Coordinate(player.target_coordinates.x, player.target_coordinates.y)

    client.main_app.printer.print_info(f"Try To Find His Path To -->: {player.target_coordinates}")


    if player.user_id % 25 == 0:
        client.main_app.kernel.add_event(Event.create_event_from_callback(client, say_hello_world))

    AStarWorkerThread().enqueue(client, rnd_coords, rnd_target)


@SetInterval(1 / 1000, False)
async def choose_rnd_sob_npc(event: Event, c):
    client: GameClient = c
    player: Player = client.player
    sob_npc_coords = SobNpcToSearch.data
    rnd_idx = random.randint(0, len(sob_npc_coords) - 1)

    if "target" in event.event_args:
        npc_coordinates = event.event_args["target"]
    else:
        npc_coordinates = sob_npc_coords[rnd_idx]

    player.target_coordinates = npc_coordinates

    client.main_app.printer.print_info(f"Player Choose To Attack At: {npc_coordinates}")

    client.main_app.kernel.add_event(Event.create_event_from_callback(client, rnd_jump))

    # client.main_app.kernel.add_event(Event.create_event_from_callback(client, move_to_sob_npc))


@SetInterval(3, True)
async def check_if_player_teleported(event: Event, c):
    client: GameClient = c
    player: Player = client.player
    if player.map_id != Maps.TwinCity:
        raise PlayerNotTeleport(client, f"Player Not Teleported To TwinCity")

    """
    If Player In TwinCity, Stop The Event And Fire Other Event To Search For SobNpc To Attack
    """
    client.main_app.printer.print_info("Player Teleported To TwinCity")
    event.is_finished = True

    client.main_app.kernel.add_event(Event.create_event_from_callback(client, choose_rnd_sob_npc))


@SetInterval(5, False)
async def check_player_inventory(event: Event, c):
    client: GameClient = c
    player: Player = client.player
    twin_city_gate: List[Item] = player.item_holder.search_item(ItemLocation.Inventory, ConstantItems.TwinCityGate)
    if len(twin_city_gate) > 0:
        item = twin_city_gate[0]
        if item.item_id == ConstantItems.TwinCityGate and client.player.map_id != Maps.TwinCity:
            await client.player.item_holder.use_gate_item(item)
        else:
            await client.player.item_holder.use_gate_item(item)
    elif client.player.map_id != Maps.TwinCity:
        # If Player Not In TwinCity, Check If Player Have TwinCityGate Item
        raise UserNotHaveThisItem(client, ConstantItems.TwinCityGate)

    # if client.player.item_holder.is_inventory_full():
    #     raise InventoryFull(client, "Inventory Is Full")

    client.main_app.kernel.add_event(Event.create_event_from_callback(client, check_if_player_teleported))
