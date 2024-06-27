# import pytest
from simplephysicsengine import Engine, World

class TestEngine:
    def test_initialization(self):
        engine = Engine(0, 0, -50)
        assert engine.x == 0
        assert engine.y == 0
        assert engine.z == -50
        assert engine._children == []

    def test_add_child(self):
        engine = Engine(0, 0, -50)
        world = World(0.0, 0.0, 0.0, 0.0)
        engine.add_child(world)
        assert len(engine._children) == 1
        assert engine._children[0] == world
        assert world.parent == engine
