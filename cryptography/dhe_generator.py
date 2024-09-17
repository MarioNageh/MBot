import random


class DHEGenerator:
    def __init__(self, p, g):
        self.g = g
        self.p = p

        self.a = random.randint(1, self.p - 1)

        self.public = pow(self.g, self.a, self.p)  # g**a % p
        self.key = 0

    def get_public_key(self) -> int:
        return self.public

    def compute_key(self, other_public_key):
        return pow(other_public_key, self.a, self.p)
