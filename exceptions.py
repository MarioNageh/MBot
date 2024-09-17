class BotBaseException(Exception):
    def __init__(self, client, message, re_login=True):
        self.client = client
        self.message = message
        self.re_login = re_login

    def __str__(self):
        return self.client.main_app.printer.get_fail_format(self.message)


class UserNotHaveEnoughCps(BotBaseException):
    pass


class UserNotHaveThisItem(BotBaseException):
    def __init__(self, client, item_id):
        message = f"User not have item with id {item_id}"
        super().__init__(client, message, re_login=True)
        self.item_id = item_id


class InventoryFull(BotBaseException):
    pass


class PlayerNotTeleport(BotBaseException):
    pass


class AStarPathCalculationError(BotBaseException):
    pass


class ReceiveInCompletePacket(BotBaseException):
    def __init__(self, client, message, last_read_position, data):
        self.client = client
        self.message = message
        self.last_read_position = last_read_position
        self.data = data

    pass


class AccountServerRefuseConnection(BotBaseException):
    pass


class UsernameOrPasswordInvalid(BotBaseException):
    pass
