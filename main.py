import sys
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
# from OpenGL_accelerate import *
from typing import List
from abc import ABC, abstractmethod
from itertools import combinations
import numpy as np
import warnings


class glObject(ABC):
    def __init__(self, x: float, y: float, z: float, size: float, 
                 *, rotation_deg: tuple[float] = (0.0, 0.0, 0.0), color: tuple[float] = (1.0, 1.0, 1.0), debug: bool = False):
        self.debug = debug

        self.x = x
        self.y = y
        self.z = z

        assert len(rotation_deg) == 3, "Rotation must be a 3-tuple"
        self.rotation_deg = np.array(rotation_deg)

        self.angular_velocity = np.array([0.0, 0.0, 0.0])
        self.assign_angular_velocity((0.0, 0.0, 0.0))
        self.__future_angular_velocity = self.angular_velocity
        self.__update_variables()

        self.size = size
        self.color = color
        self._parent: glObject | None = None
        self._children: List[glObject] = []

    def add_child(self, child: "glObject"):
        child.set_parent(self)
        self._children.append(child)

    def add_children(self, children: List["glObject"]):
        for child in children:
            self.add_child(child)

    def set_parent(self, parent: "glObject"):
        self._parent = parent

    def __update_variables(self):
        if np.any(self.__future_angular_velocity != self.angular_velocity):
            self.angular_velocity = self.__future_angular_velocity

    def update(self, dt: float) -> None:
        self.__update_variables()

        self.rotation_deg = np.array(self.rotation_deg) + np.array(self.angular_velocity) * dt
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
            rot_x = np.array([[1, 0, 0],
                            [0, np.cos(rx), -np.sin(rx)],
                            [0, np.sin(rx), np.cos(rx)]])
            
            rot_y = np.array([[np.cos(ry), 0, np.sin(ry)],
                            [0, 1, 0],
                            [-np.sin(ry), 0, np.cos(ry)]])
            
            rot_z = np.array([[np.cos(rz), -np.sin(rz), 0],
                            [np.sin(rz), np.cos(rz), 0],
                            [0, 0, 1]])
            
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
        while current is not ancestor and safety_counter < 10: # Safety counter to prevent infinite loops, maybe raise an error/warn instead
            safety_counter += 1
            x, y, z = apply_rotation(x, y, z, current.rotation_deg)
            x += current.x
            y += current.y
            z += current.z
            current = current._parent

        return x, y, z


class Engine(glObject):
    def __init__(self, x, y, z=-50, *, debug = False):
        super().__init__(x, y, z, 0, rotation_deg=(0.0, 0.0, 0.0), debug=debug)

        warnings.filterwarnings("once", category=UserWarning, module="main")
        
        self.timer = pygame.time.Clock()
        
        pygame.init()
        
        self.display = (800, 600)
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        
        self.mouse_down = False
        self.left_button_down = False
        self.right_button_down = False
        self.last_mouse_pos = (0, 0)
        
    def update(self):
        dt = self.timer.tick(60) / 1000
        for child in self._children:
            child.update(dt)
        self.check_collisions()
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.MOUSEMOTION:
                if self.left_button_down:
                    self.rotation_deg[0] += (event.pos[1] - self.last_mouse_pos[1]) * 0.1
                    self.rotation_deg[1] += (event.pos[0] - self.last_mouse_pos[0]) * 0.1
                    self.last_mouse_pos = event.pos
                elif self.right_button_down:
                    self.x += (event.pos[0] - self.last_mouse_pos[0]) * 0.1
                    self.y -= (event.pos[1] - self.last_mouse_pos[1]) * 0.1
                    self.last_mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.left_button_down = True
                    self.last_mouse_pos = event.pos
                elif event.button == 3:
                    self.right_button_down = True
                    self.last_mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.left_button_down = False
                elif event.button == 3:
                    self.right_button_down = False

    def run(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, self.display[0] / self.display[1], 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Set up lighting
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        light_ambient = [0.1, 0.1, 0.1, 1.0]
        light_diffuse = [0.7, 0.7, 0.7, 1.0]
        light_position = [5.0, 5.0, 5.0, 1.0]
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)

        glEnable(GL_DEPTH_TEST)
        
        # Enable antialiasing
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POLYGON_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        def enable_debug(obj):
            for child in obj._children:
                child.debug = self.debug
                enable_debug(child)
                
        if self.debug:
            enable_debug(self)

        while True:
            self.handle_events()
            
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            glLoadIdentity()
            glTranslatef(self.x, self.y, self.z)
            glRotatef(self.rotation_deg[0], 1, 0, 0)
            glRotatef(self.rotation_deg[1], 0, 1, 0)
            
            self.update()
            self.draw()
                
            pygame.display.flip()
            pygame.time.wait(10)

    def check_collisions(self):
        def find_closest_collision_handler(self):
            current = self
            while current is not None:
                if isinstance(current, HasCollisionMixin):
                    return current
                current = current._parent
            raise Error("No collision handler found in the hierarchy")
        
        def find_closest_common_ancestor(obj1, obj2) -> None | glObject:
            # Traverse up from obj1 and collect all its ancestors
            ancestors = set()
            current1 = obj1
            while current1 is not None:
                ancestors.add(current1)
                current1 = current1._parent

            # Traverse up from obj2 and find the first common ancestor
            current2 = obj2
            while current2 is not None:
                if current2 in ancestors:
                    return current2
                current2 = current2._parent
            
            # raise Error("No common ancestor found. Did you collide ")  # No common ancestor found, which should not happen if both objects belong to the same tree
            warnings.warn("No common ancestor found. Did you collide objects from different trees?", category=UserWarning)
            return None  # No common ancestor found, which should not happen if both objects belong to the same tree

        def get_flattened_objects(self):
            flattened_objects = []
            for child in self._children:
                flattened_objects.append(child)
                flattened_objects.extend(get_flattened_objects(child))
            return flattened_objects
        
        # Filter out objects that have no hitbox
        flattened_objects = get_flattened_objects(self)
        collidable_objects = [obj for obj in flattened_objects if isinstance(obj, Hitbox)]
        
        for obj1, obj2 in combinations(collidable_objects, 2):
            common_ancestor = find_closest_common_ancestor(obj1, obj2)
            if obj1.check_collision(obj2, common_ancestor):
                handler = find_closest_collision_handler(obj1)
                handler.on_collision(obj1._parent, obj2._parent)
                handler = find_closest_collision_handler(obj2)
                handler.on_collision(obj1._parent, obj2._parent)


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
            warnings.warn("No common ancestor for the collision found. Determining no collision.", "CollisionWarning")
            return False
        
        x, y, z = self.get_position_within(common_ancestor)
        xo, yo, zo = other.get_position_within(common_ancestor)

        distance = ((x - xo) ** 2 + (y - yo) ** 2 + (z - zo) ** 2) ** 0.5
        print(f"Distance: {distance} < {self.size/2 + other.size/2} of {self} and {other} within {common_ancestor}") if self.debug else ...
    
        return distance < self.size/2 + other.size/2


class HasCollisionMixin:
    @abstractmethod
    def on_collision(self, other1: glObject, other2: glObject):
        pass


class Ball(glObject):
    def __init__(self, x, y, z, size, rotation_deg, *, color=(1.0, 0.0, 0.0)):
        super().__init__(x, y, z, size, rotation_deg=rotation_deg, color=color)

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.rotation_deg[1], 0, 1, 0)
        glColor3f(self.color[0], self.color[1], self.color[2])
        
        sphere = gluNewQuadric()
        gluQuadricNormals(sphere, GLU_SMOOTH)
        gluSphere(sphere, self.size / 2, 32, 32)
        gluDeleteQuadric(sphere)
        
        glPopMatrix()

        super().draw()


class String(glObject):
    def __init__(self, x, y, z, length, thickness, rotation_deg, *, 
                 color=(1.0, 1.0, 1.0)):
        super().__init__(x, y, z, thickness, rotation_deg=rotation_deg, color=color)
        self.length = length

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.rotation_deg[0], 1, 0, 0)
        glColor3f(self.color[0], self.color[1], self.color[2])
        
        glBegin(GL_QUADS)
        glVertex3f(-self.size, 0, 0)
        glVertex3f(self.size, 0, 0)
        glVertex3f(self.size, -self.length, 0)
        glVertex3f(-self.size, -self.length, 0)
        glEnd()
        
        glPopMatrix()

        super().draw()


class StringyBall(glObject):
    def __init__(self, x, y, z, size, length, thickness):
        super().__init__(x, y, z, size, rotation_deg=(0.0, 0.0, 0.0), color=(1.0, 0.0, 1.0))
        self.length = length

        self.string = String(0, 0, 0, length, thickness, (0.0, 0.0, 0.0), color=(0.9, 0.2, 0.2))
        self.add_child(self.string)

        ball = Ball(0, -length, 0, size, (0.0, 0.0, 0.0))
        hitbox = CubeHitbox(0, -length, 0, size)

        ball.add_child(hitbox)
        self.string.add_child(ball)

    def update(self, dt):
        super().update(dt)

        g = 9.81
        theta = np.radians(self.rotation_deg[2])

        # Angular acceleration (only for one axis)
        alpha = - (g / self.length) * np.sin(theta)
        
        # Update angular velocity
        new_angular_velocity = self.angular_velocity[2] + alpha * 100*dt
        new_angular_velocity = new_angular_velocity * (1 - 0.1*dt)
        self.assign_angular_velocity((self.angular_velocity[0], self.angular_velocity[1], new_angular_velocity))

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.rotation_deg[2], 0, 0, 1)

        super().draw()

        glPopMatrix()


class World(glObject, HasCollisionMixin):
    def on_collision(self, other1, other2):
        # m1 = self.size  # Assuming mass is proportional to the size
        # m2 = other.size

        # # Velocity components (only x-axis)
        # v1x = self.vx
        # v2x = other.vx

        # # Calculate the new velocities after the collision (only x-axis)
        # new_v1x = (m1-m2)/(m1+m2) * v1x + 2*m2/(m1+m2) * v2x
        # new_v2x = 2*m1/(m1+m2) * v1x + (m2-m1)/(m1+m2) * v2x

        # # # Update velocities (only x-axis)
        # # self.assing_velocity(vx = new_v1x)
        # # other.assing_velocity(vx = -new_v2x)

        # # Convert linear velocity to angular velocity
        # angular_velocity1 = new_v1x / self.length
        # angular_velocity2 = -new_v2x / other.length

        # Update angular velocities
        # self.assign_angular_velocity(angular_velocity1)
        # other.assign_angular_velocity(angular_velocity2)
        obj1 = other1._parent._parent
        obj2 = other2._parent._parent

        print(f"{obj1} collided with {obj2}") if self.debug else ...
        cpy = obj1.angular_velocity
        obj1.assign_angular_velocity(obj2.angular_velocity)
        obj2.assign_angular_velocity(cpy)


if __name__ == "__main__":
    engine = Engine(-10, 15, debug=False)
    world = World(0.0, 0.0, 0.0, 0.0)

    size = 7
    string_len = 30
    for i in range(5):
        stringyBall = StringyBall(i * size, 0, 0, size, string_len, 0.3)
        world.add_child(stringyBall)
    
    engine.add_child(world)

    # Give an initial velocity
    engine._children[0]._children[0].rotation_deg = (0, 0, -45)
    # engine._children[0]._children[0].assign_angular_velocity((0, 0, 10))

    engine.run()
