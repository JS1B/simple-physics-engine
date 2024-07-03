import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

import warnings
import sys
from itertools import combinations

from .mixins import HasCollisionMixin
from .gl_object import glObject
from .physics import Hitbox


class Engine(glObject):
    def __init__(self, x, y, z=-50, *, debug=False):
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
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_q
            ):
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.MOUSEMOTION:
                if self.left_button_down:
                    self.rotation_deg[0] += (
                        event.pos[1] - self.last_mouse_pos[1]
                    ) * 0.1
                    self.rotation_deg[1] += (
                        event.pos[0] - self.last_mouse_pos[0]
                    ) * 0.1
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
                current = current.parent
            raise Error("No collision handler found in the hierarchy")

        def find_closest_common_ancestor(obj1, obj2) -> None | glObject:
            # Traverse up from obj1 and collect all its ancestors
            ancestors = set()
            current1 = obj1
            while current1 is not None:
                ancestors.add(current1)
                current1 = current1.parent

            # Traverse up from obj2 and find the first common ancestor
            current2 = obj2
            while current2 is not None:
                if current2 in ancestors:
                    return current2
                current2 = current2.parent

            # raise Error("No common ancestor found. Did you collide ")  # No common ancestor found, which should not happen if both objects belong to the same tree
            warnings.warn(
                "No common ancestor found. Did you collide objects from different trees?",
                category=UserWarning,
            )
            return None  # No common ancestor found, which should not happen if both objects belong to the same tree

        def get_flattened_objects(self):
            flattened_objects = []
            for child in self._children:
                flattened_objects.append(child)
                flattened_objects.extend(get_flattened_objects(child))
            return flattened_objects

        # Filter out objects that have no hitbox
        flattened_objects = get_flattened_objects(self)
        collidable_objects = [
            obj for obj in flattened_objects if isinstance(obj, Hitbox)
        ]

        for obj1, obj2 in combinations(collidable_objects, 2):
            common_ancestor = find_closest_common_ancestor(obj1, obj2)
            if obj1.check_collision(obj2, common_ancestor):
                handler = find_closest_collision_handler(obj1)
                handler.on_collision(obj1.parent, obj2.parent)
                handler = find_closest_collision_handler(obj2)
                handler.on_collision(obj1.parent, obj2.parent)
