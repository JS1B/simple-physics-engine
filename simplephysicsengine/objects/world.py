from ..gl_object import glObject
from ..mixins import HasCollisionMixin


class World(glObject, HasCollisionMixin):
    def on_collision(self, other1, other2):
        obj1 = other1.parent.parent
        obj2 = other2.parent.parent

        print(f"{obj1} collided with {obj2}") if self.debug else ...

        obj1.assign_angular_velocity(obj2.angular_velocity)
        obj2.assign_angular_velocity(obj1.angular_velocity)
