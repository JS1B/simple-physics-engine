import pytest
import pygame

from simplephysicsengine.config_loader import load_key_mappings


def test_load_key_mappings():
    key_mappings = load_key_mappings("simplephysicsengine/config/key_mappings.json")
    key_map = {mapping.action: mapping.key for mapping in key_mappings.mappings}
    assert key_map["left"] == pygame.K_a
    assert key_map["right"] == pygame.K_d
    assert key_map["forward"] == pygame.K_w
    assert key_map["backward"] == pygame.K_s
    assert key_map["up"] == pygame.K_LSHIFT
    assert key_map["down"] == pygame.K_LCTRL
    assert key_map["quit"] == pygame.K_q
    assert key_map["reset"] == pygame.K_SPACE
    assert key_map["debug"] == pygame.K_F1
