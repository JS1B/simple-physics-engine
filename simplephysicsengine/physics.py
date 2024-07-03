import warnings
from abc import abstractmethod

from .gl_object import glObject


class Hitbox(glObject):
    def __init__(self, x, y, z, size):
        super().__init__(x, y, z, size)

    @abstractmethod
    def check_collision(self, other: glObject, common_ancestor: glObject) -> bool:
        pass

    def draw(self):
        pass


class CubeHitbox(Hitbox):
    def check_collision(self, other, common_ancestor):
        if common_ancestor is None:
            warnings.warn(
                "No common ancestor for the collision found. Determining no collision.",
                "CollisionWarning",
            )
            return False

        x, y, z = self.get_position_within(common_ancestor)
        xo, yo, zo = other.get_position_within(common_ancestor)

        distance = ((x - xo) ** 2 + (y - yo) ** 2 + (z - zo) ** 2) ** 0.5
        (
            print(
                f"Distance: {distance} < {self.size/2 + other.size/2} of {self} and {other} within {common_ancestor}"
            )
            if self.debug
            else ...
        )

        return distance < self.size / 2 + other.size / 2
