class Npc:
    def __init__(self
                 , npc_id: int
                 , npc_x: int
                 , npc_y: int
                 , npc_look_face: int
                 , npc_type: int
                 , npc_role: int
                 ):
        self.npc_id = npc_id
        self.npc_x = npc_x
        self.npc_y = npc_y
        self.npc_look_face = npc_look_face
        self.npc_type = npc_type
        self.npc_role = npc_role

    def __str__(self):
        return f"Npc ID: {self.npc_id}, X: {self.npc_x}, Y: {self.npc_y}, Look Face: {self.npc_look_face}, Type: {self.npc_type}, Role: {self.npc_role}"
