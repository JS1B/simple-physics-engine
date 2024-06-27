from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

from simplephysicsengine import String, Ball, CubeHitbox, Engine, World, glObject


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
    engine._children[0]._children[0].rotation_deg = (0, 0, -50)
    # engine._children[0]._children[0].assign_angular_velocity((0, 0, -50))

    engine.run()
