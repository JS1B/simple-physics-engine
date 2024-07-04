from dataclasses import dataclass
from typing import List
import pygame


@dataclass
class KeyMapping:
    action: str
    key: int


@dataclass
class KeyMappings:
    mappings: List[KeyMapping]

    @staticmethod
    def from_dict(data):
        return KeyMappings(
            mappings=[
                KeyMapping(action=k, key=getattr(pygame, v)) for k, v in data.items()
            ]
        )
