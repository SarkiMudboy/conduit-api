from typing import List

from ..storage.models import Object
from .tree import Node, Tree


def build_tree(paths: List[str]) -> Tree:

    nodes: Tree = Tree()

    for path in paths:

        tree: List[Node] = []
        ids: List[str] = []
        ids += path.split("/")

        # set the root if its not set yet
        ids = nodes.set_root(ids)

        for obj in ids:
            if obj not in nodes:
                n = Node(obj, 0, "child")
                nodes += n
                n.db_instance = Object.objects.create()
            else:
                n = nodes[obj]  # it already has the created instance just fetch it

            if tree:
                new_node = tree[-1].add_node(
                    n
                )  # add the node to the children and save it to db
                if new_node:
                    new_node.add_path(n.path)
                    tree[-1].db_instance.content.add(n.db_instance)

            tree.append(n)
    return nodes


# owner
# is dir -> check len(children)
# drive
# resource
