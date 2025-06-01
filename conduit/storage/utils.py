from typing import List

from .models import Object


def handle_directory_depth(assets: List[Object]) -> List[Object]:

    population = 0
    directories: List[Object] = []
    for obj in assets:
        if obj.is_directory:
            directories.append(obj)
            population += 1

    spread = (population / len(assets)) * 100
    if round(spread) > 30:
        return directories

    return None
