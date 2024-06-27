from abc import abstractmethod

from .gl_object import glObject


class HasCollisionMixin:
    @abstractmethod
    def on_collision(self, other1: glObject, other2: glObject):
        pass