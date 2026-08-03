import random
import time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from tst import insert, search


def load_pairs(path):
    pairs = []                             # Store pairs
    file = open(path, "r", encoding="utf-8")  # Open file
    lines = file.readlines()               # Read
    file.close()                           # Close

    first_line = True
    for line in lines:
        line = line.strip()                # Remove whitespace

        if line == "" or first_line:       # Skip empty line
            first_line = False
            continue

        parts = line.split(",")            # line into columns
        if len(parts) >= 2:
            word = parts[0].strip().lower()    # Extract and make word lowercase
            translation = parts[1].strip()     # translation

            if word != "":                 # empty words
                pairs.append([word, translation])  # Store pair

    return pairs


def list_search(pairs, word):              # Linear search
    word = word.lower()                    # lowercase

    for i in range(len(pairs)):
        if pairs[i][0] == word:            # Word found
            return pairs[i][1]             # Return translation

    return None


def build_tree(pairs):                     # Build TST
    root = None                            # Empty tree

    for i in range(len(pairs)):            # Insert word
        root = insert(root, pairs[i][0], 0, pairs[i][1])  # Insert into TST

    return root                            # Return tree root


def build_sorted(pairs):                   # Build sorted array for binary search
    sorted_pairs = sorted(pairs, key=lambda p: p[0])  # Sort by word
    return sorted_pairs


def binary_search(pairs, word):            # Binary search on sorted array
    word = word.lower()                    # lowercase
    low = 0
    high = len(pairs) - 1

    while low <= high:                     # Standard binary search loop
        mid = (low + high) // 2
        mid_word = pairs[mid][0]

        if mid_word == word:               # Word found
            return pairs[mid][1]           # Return translation
        elif mid_word < word:
            low = mid + 1
        else:
            high = mid - 1

    return None                            # Not found


def time_function(search_fn, structure, test_words, use_tst, repeats=500):
    start = time.time()                    # timer
    num_words = len(test_words)            # searches

    for i in range(repeats):
        for j in range(num_words):         # Search
            if use_tst is True:
                search_fn(structure, test_words[j])    # Search TST
            else:
                search_fn(structure, test_words[j])    # Search list/binary

    total_time = time.time() - start       # Totaltime
    average_time = total_time / (repeats * num_words) * 1000000  # Average time

    return average_time


def run_experiment():
    pairs = load_pairs("dataset.csv")      # Load data

    max_len = len(pairs)                   # size
    all_sizes = [50, 100, 250, 500, 1000, 2000, 5000]
    ns = []

    for s in all_sizes:                    # valid sizes
        if s <= max_len:
            ns.append(s)

    if len(ns) == 0:                       # If dataset is very small
        ns.append(max_len)

    # ---- Structures to compare ----
    # True  -> TST (search_fn expects a tree root)
    # False -> List (linear scan)
    # "bin" -> Binary search (sorted array)
    structures = [True, False, "bin"]
    labels = [
        "Ternary Search Tree - O(log N)",
        "List (Linear Scan - O(N))",
        "Binary Search (Sorted Array) - O(log N)",
    ]

    # Store results per structure so we can reuse them across both plots
    results = {}

    for index in range(len(structures)):
        use_tst = structures[index]        # Current structure flag
        label = labels[index]              # Current label

        times = []                         # Store timing results

        for size in ns:                    # Test each dataset size
            subset = []                    # Create subset

            for i in range(size):
                subset.append(pairs[i])

            if use_tst is True:            # create TST
                struct_obj = build_tree(subset)
                fn = search
            elif use_tst == "bin":         # create sorted array
                struct_obj = build_sorted(subset)
                fn = binary_search
            else:                          # plain list
                struct_obj = subset
                fn = list_search

            test_words = []
            step = size // 10              # Sample every 10%

            if step < 1:
                step = 1

            for i in range(0, size, step):  # test words
                test_words.append(subset[i][0])

            # time_function only needs a bool for its internal branching,
            # so treat "bin" the same as False (non-TST) there.
            avg_time = time_function(fn, struct_obj, test_words, use_tst is True)
            times.append(avg_time)

        results[label] = times

    # ---- Plot 1: original comparison (TST vs List) ----
    plt.figure(figsize=(8, 5))

    for label in labels[:2]:               # TST and List only
        plt.plot(ns, results[label], marker="o", label=label)

    plt.xlabel("Dataset Size (n)")
    plt.ylabel("Time (microseconds)")
    plt.title("Word Lookup: TST vs List")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("benchmark_comparison.png", dpi=150)
    plt.close()

    print("Saved plot to benchmark_comparison.png")

    # ---- Plot 2: new comparison including Binary Search ----
    plt.figure(figsize=(8, 5))

    for label in labels:                   # TST, List, and Binary Search
        plt.plot(ns, results[label], marker="o", label=label)

    plt.xlabel("Dataset Size (n)")
    plt.ylabel("Time (microseconds)")
    plt.title("Word Lookup: TST vs List vs Binary Search")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("benchmark_comparison_binary.png", dpi=150)
    plt.close()

    print("Saved plot to benchmark_comparison_binary.png")


if __name__ == "__main__":
    run_experiment()