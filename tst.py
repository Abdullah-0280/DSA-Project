def make_node(char):
    node = {}                              
    node["char"] = char                     # Store the character
    node["left"] = None                     # Left pointer 
    node["middle"] = None                  
    node["right"] = None                   
    node["end"] = False                     # mark if this node completes a valid word
    node["value"] = None                    # Store the translation value
    return node                           


def insert(node, word, i, value):
    char = word[i]                          #character at the current index 

    if node is None:
        node = make_node(char)              #new node if the current branch is empty

    if char < node["char"]:
        node["left"] = insert(node["left"], word, i, value)      #insert into the left subtree
    elif char > node["char"]:
        node["right"] = insert(node["right"], word, i, value)   
    else:
        if i + 1 == len(word):
            node["end"] = True              # Mark when final
            node["value"] = value           #translation value
        else:
            node["middle"] = insert(node["middle"], word, i + 1, value)  #Move to the middle child

    return node                            


def find_node(node, word, i):
    if node is None:
        return None                         #if the node does not exist

    char = word[i]                          #character at the current index

    if char < node["char"]:
        return find_node(node["left"], word, i)          # Search in the left subtree
    elif char > node["char"]:
        return find_node(node["right"], word, i)         # Search in the right subtree
    else:
        if i + 1 == len(word):
            return node                     #Return the node if last char
        return find_node(node["middle"], word, i + 1)    # Move down the middle subtree for the next character


def search(root, word):
    word = word.lower()                     # Convertto lowercase
    node = find_node(root, word, 0)         #find node
    if node is not None and node["end"] is True:
        return node["value"]                # Return the translation
    return None                             # Return None if the word is not found


def collect_words(node, prefix, results):
    if node is None:
        return                              #stop if the node is empty

    collect_words(node["left"], prefix, results)         #collect words from the left subtree

    if node["end"] is True:
        results.append((prefix + node["char"], node["value"]))  #Add complete word and its value to results

    collect_words(node["middle"], prefix + node["char"], results)  #middle subtree
    collect_words(node["right"], prefix, results)        # words from the right subtree


def prefix_search(root, prefix):
    prefix = prefix.lower()                 
    results = []                            #empty list for same

    node = find_node(root, prefix, 0)       #node where the prefix ends
    if node is None:
        return results                     

    if node["end"] is True:
        results.append((prefix, node["value"]))  #include the prefix

    collect_words(node["middle"], prefix, results)  #
    return results                          #Return matching words