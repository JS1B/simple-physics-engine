from OpenGL.GL import *
from OpenGL.GLU import *

from ..gl_object import glObject


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