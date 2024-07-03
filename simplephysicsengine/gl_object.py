from abc import ABC
from typing import List
import numpy as np


class glObject(ABC):
    def __init__(
        self,
        x: float,
        y: float,
        z: float,
        size: float,
        *,
        rotation_deg: tuple[float] = (0.0, 0.0, 0.0),
        color: tuple[float] = (1.0, 1.0, 1.0),
        debug: bool = False
    ):
        self.debug = debug

        self.x = x
        self.y = y
        self.z = z

        assert len(rotation_deg) == 3, "Rotation must be a 3-tuple"
        self.rotation_deg = np.array(rotation_deg)

        self.angular_velocity = np.array([0.0, 0.0, 0.0])
        self.__future_angular_velocity = self.angular_velocity
        self.assign_angular_velocity((0.0, 0.0, 0.0))
        self.__update_variables()

        self.size = size
        self.color = color
        self.parent: glObject | None = None
        self._children: List[glObject] = []

    def add_child(self, child: "glObject"):
        child.setparent(self)
        self._children.append(child)

    def add_children(self, children: List["glObject"]):
        for child in children:
            self.add_child(child)

    def setparent(self, parent: "glObject"):
        self.parent = parent

    def __update_variables(self):
        if np.any(self.__future_angular_velocity != self.angular_velocity):
            self.angular_velocity = self.__future_angular_velocity

    def update(self, dt: float) -> None:
        self.__update_variables()

        self.rotation_deg = (
            np.array(self.rotation_deg) + np.array(self.angular_velocity) * dt
        )
        self.rotation_deg %= 360
        self.rotation_deg = tuple(self.rotation_deg)

        for child in self._children:
            child.update(dt)

    def assign_angular_velocity(self, angular_velocity: tuple[float]):
        assert len(angular_velocity) == 3, "Angular velocity must be a 3-tuple"
        self.__future_angular_velocity = np.array(angular_velocity)

    def draw(self) -> None:
        for child in self._children:
            child.draw()

    def get_position_within(self, ancestor: "glObject"):
        def apply_rotation(x, y, z, rotation_deg):
            # Convert degrees to radians
            rx, ry, rz = np.radians(rotation_deg)

            # Rotation matrices for x, y, z
            rot_x = np.array(
                [[1, 0, 0], [0, np.cos(rx), -np.sin(rx)], [0, np.sin(rx), np.cos(rx)]]
            )

            rot_y = np.array(
                [[np.cos(ry), 0, np.sin(ry)], [0, 1, 0], [-np.sin(ry), 0, np.cos(ry)]]
            )

            rot_z = np.array(
                [[np.cos(rz), -np.sin(rz), 0], [np.sin(rz), np.cos(rz), 0], [0, 0, 1]]
            )

            # Combined rotation matrix
            rotation_matrix = np.dot(rot_z, np.dot(rot_y, rot_x))

            # Apply rotation
            pos = np.array([x, y, z])
            rotated_pos = np.dot(rotation_matrix, pos)

            return rotated_pos[0], rotated_pos[1], rotated_pos[2]

        x = 0.0
        y = 0.0
        z = 0.0
        current = self

        safety_counter = 0
        while (
            current is not ancestor and safety_counter < 10
        ):  # Safety counter to prevent infinite loops, maybe raise an error/warn instead
            safety_counter += 1
            x, y, z = apply_rotation(x, y, z, current.rotation_deg)
            x += current.x
            y += current.y
            z += current.z
            current = current.parent

        return x, y, z
