from client.client import Client


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, client: Client, *args, **kwargs):
        if client not in cls._instances or cls not in cls._instances[client]:
            instance = super(SingletonMeta, cls).__call__(client, *args, **kwargs)

            cls._instances[client] = {}
            cls._instances[client][cls] = instance
            instance.client = client
        return cls._instances[client][cls]
