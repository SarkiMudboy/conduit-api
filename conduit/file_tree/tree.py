def print_tree(T, line=""):

    if not T.children:
        return line

    for index, child in enumerate(T.children):
        line += child.val + " " + "\n"
        line = print_tree(child, line)

    return line
