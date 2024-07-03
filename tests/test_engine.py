import pytest
import pygame
from pygame.locals import *

from simplephysicsengine import Engine, World, Ball


class TestEngine:
    def test_initialization(self):
        engine = Engine(0, 0, -50)
        assert engine.x == 0
        assert engine.y == 0
        assert engine.z == -50
        assert engine._children == []

    def test_set_parent(self):
        engine = Engine(0, 0, -50)
        world = World(0.0, 0.0, 0.0, 0.0)
        world.set_parent(engine)
        assert world.parent == engine
        assert world not in engine._children

    def test_add_child(self):
        engine = Engine(0, 0, -50)
        world = World(0.0, 0.0, 0.0, 0.0)
        engine.add_child(world)
        assert len(engine._children) == 1
        assert engine._children[0] == world
        assert world.parent == engine

    def test_add_children(self):
        engine = Engine(0, 0, -50)
        world = World(0.0, 0.0, 0.0, 0.0)
        engine.add_children([world])
        assert len(engine._children) == 1
        assert engine._children[0] == world
        assert world.parent == engine

    def test_remove_child(self):
        engine = Engine(0, 0, -50)
        world = World(0.0, 0.0, 0.0, 0.0)
        engine.add_child(world)
        engine.remove_child(world)
        assert len(engine._children) == 0
        assert world.parent is None

    def test_remove_children(self):
        engine = Engine(0, 0, -50)
        world = World(0.0, 0.0, 0.0, 0.0)
        engine.add_child(world)
        engine.remove_children([world])
        assert len(engine._children) == 0
        assert world.parent is None

    def test_exit(self):
        engine = Engine(0, 0, -50)
        events = [
            pygame.event.Event(QUIT),
            pygame.event.Event(KEYDOWN, key=K_q),
        ]
        for event in events:
            pygame.event.post(event)
        with pytest.raises(SystemExit) as e:
            engine.run()
        assert e.type == SystemExit
        assert e.value.code == 0

    def test_enable_debug(self):
        engine = Engine(0, 0, -50, debug=True)
        world = World(0.0, 0.0, 0.0, 0.0)
        ball = Ball(0.0, 0.0, 0.0, 0.0, (0.0, 0.0, 0.0))

        world.add_child(ball)
        engine.add_child(world)
        pygame.event.post(pygame.event.Event(KEYDOWN, key=K_q))

        with pytest.raises(SystemExit) as e:
            engine.run()
        assert e.type == SystemExit

        assert engine.debug is True
        assert world.debug is True
        assert world._children[0].debug is True
