"""
Ternary Search Tree (TST) - basic version
No classes, no __init__, plain functions and dictionaries only.

Each node is just a dictionary with these keys:
    "char"   -> the character stored at this node
    "left"   -> node for characters smaller than "char"
    "middle" -> node for the next character in the same word
    "right"  -> node for characters bigger than "char"
    "end"    -> True if a word ends at this node
    "value"  -> the Urdu translation, only used when "end" is True
"""


def make_node(char):
    node = {}
    node["char"] = char
    node["left"] = None
    node["middle"] = None
    node["right"] = None
    node["end"] = False
    node["value"] = None
    return node


def insert(node, word, i, value):
    char = word[i]

    if node is None:
        node = make_node(char)

    if char < node["char"]:
        node["left"] = insert(node["left"], word, i, value)
    elif char > node["char"]:
        node["right"] = insert(node["right"], word, i, value)
    else:
        if i + 1 == len(word):
            node["end"] = True
            node["value"] = value
        else:
            node["middle"] = insert(node["middle"], word, i + 1, value)

    return node


def find_node(node, word, i):
    if node is None:
        return None

    char = word[i]

    if char < node["char"]:
        return find_node(node["left"], word, i)
    elif char > node["char"]:
        return find_node(node["right"], word, i)
    else:
        if i + 1 == len(word):
            return node
        return find_node(node["middle"], word, i + 1)


def search(root, word):
    word = word.lower()
    node = find_node(root, word, 0)
    if node is not None and node["end"] is True:
        return node["value"]
    return None


def collect_words(node, prefix, results):
    if node is None:
        return

    collect_words(node["left"], prefix, results)

    if node["end"] is True:
        results.append((prefix + node["char"], node["value"]))

    collect_words(node["middle"], prefix + node["char"], results)
    collect_words(node["right"], prefix, results)


def prefix_search(root, prefix):
    prefix = prefix.lower()
    results = []

    node = find_node(root, prefix, 0)
    if node is None:
        return results

    if node["end"] is True:
        results.append((prefix, node["value"]))

    collect_words(node["middle"], prefix, results)
    return results
