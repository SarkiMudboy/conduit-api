from typing import List, Literal, Set

from django.db import models


class Node:
    """Represents a single object (File or Folder) in the whoke directory"""

    def __init__(self, name: str, size: int, type: Literal["child", "root"] = "child"):
        self.name = name
        self.size = size
        self.type = type
        self.path = name if self.type == "root" else ""
        self._children: Set[Node] = set()

        self.db_instance: models.Model = None

    def add_node(self, *node: list) -> set:

        if not node:
            raise ValueError("Invalid Node")

        new_nodes = {*node} - self._children
        self._children = self._children.union({*node})

        return new_nodes

    def add_path(self, parent_path: str) -> None:
        self.path += parent_path + "/" + self.name

    def __repr__(self):
        return self.name


class Tree:
    def __init__(self):
        self.nodes: List[Node] = []
        self.node_ids: List[str] = []

    def __iadd__(self, val: Node):
        self.nodes.append(val)
        self.node_ids.append(val.name)

        return self

    def __contains__(self, val: str):
        return val in self.node_ids

    def __getitem__(self, val: str) -> Node:
        for node in self.nodes:
            if node.name == val:
                return node
        return False

    def __str__(self):
        return self.node_ids.__str__() if self.node_ids else "None"

    def set_root(self, S: List[str]) -> List[str]:
        root = S[0]
        if not self[root]:
            self += Node(root, 0, "root")
            self.node_ids.append(root)
            S.pop(0)
        return S
