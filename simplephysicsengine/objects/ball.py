from OpenGL.GL import *
from OpenGL.GLU import *

from ..gl_object import glObject


class Ball(glObject):
    def __init__(
        self, x, y, z, size, rotation_deg: tuple[float], *, color=(1.0, 0.0, 0.0)
    ):
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
