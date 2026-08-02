"""
Benchmark: Ternary Search Tree vs plain Python List
Improved version - basic style (plain loops, no comprehensions/zip).

Two experiments:
  1. Small, real dataset (dataset.csv) - averaged over MANY words per
     length instead of a single random word, to reduce noise.
  2. Large synthetic dataset (thousands of words) - to reveal the
     crossover point where the TST's algorithmic advantage clearly
     beats the list, even for exact-word lookup.
"""

import time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from tst import insert, search, prefix_search


# ----------------------------------------------------------------------
# Loading the real dataset
# ----------------------------------------------------------------------
def load_pairs(path):
    pairs = []
    file = open(path, "r", encoding="utf-8")
    lines = file.readlines()
    file.close()

    first_line = True
    for line in lines:
        line = line.strip()
        if line == "":
            continue
        if first_line:
            first_line = False
            continue

        parts = line.split(",")
        if len(parts) < 2:
            continue

        word = parts[0].strip().lower()
        translation = parts[1].strip()
        if word != "":
            pairs.append([word, translation])

    return pairs


# ----------------------------------------------------------------------
# Plain list-based "naive" implementations (linear scan)
# ----------------------------------------------------------------------
def list_search(pairs, word):
    word = word.lower()
    for i in range(len(pairs)):
        if pairs[i][0] == word:
            return pairs[i][1]
    return None


def list_prefix_search(pairs, prefix):
    prefix = prefix.lower()
    results = []
    for i in range(len(pairs)):
        word = pairs[i][0]
        if word.startswith(prefix):
            results.append([word, pairs[i][1]])
    return results


# ----------------------------------------------------------------------
# Timing helpers
# ----------------------------------------------------------------------
def time_search(structure, query, use_tst, repeats):
    start = time.perf_counter()
    for i in range(repeats):
        if use_tst is True:
            search(structure, query)
        else:
            list_search(structure, query)
    end = time.perf_counter()
    return (end - start) / repeats * 1000000  # microseconds


def time_prefix(structure, query, use_tst, repeats):
    start = time.perf_counter()
    for i in range(repeats):
        if use_tst is True:
            prefix_search(structure, query)
        else:
            list_prefix_search(structure, query)
    end = time.perf_counter()
    return (end - start) / repeats * 1000000


def group_words_by_length(pairs):
    groups = {}
    for i in range(len(pairs)):
        word = pairs[i][0]
        length = len(word)
        if length not in groups:
            groups[length] = []
        groups[length].append(word)
    return groups


# ----------------------------------------------------------------------
# Build a Ternary Search Tree from a list of [word, translation] pairs
# ----------------------------------------------------------------------
def build_tree(pairs):
    root = None
    for i in range(len(pairs)):
        word = pairs[i][0]
        translation = pairs[i][1]
        root = insert(root, word, 0, translation)
    return root


# ----------------------------------------------------------------------
# Experiment 1: averaged benchmark on the real dataset
# ----------------------------------------------------------------------
def run_averaged_benchmark(pairs, root, repeats_per_word, max_words_per_length):
    groups = group_words_by_length(pairs)
    lengths = list(groups.keys())
    lengths.sort()

    exact_lengths = []
    exact_tst_times = []
    exact_list_times = []

    prefix_lengths = []
    prefix_tst_times = []
    prefix_list_times = []

    for length in lengths:
        words_of_this_length = groups[length]

        words_to_use = []
        count = 0
        for word in words_of_this_length:
            if count >= max_words_per_length:
                break
            words_to_use.append(word)
            count = count + 1

        total_tst_exact = 0
        total_list_exact = 0
        total_tst_prefix = 0
        total_list_prefix = 0
        num_words = len(words_to_use)

        half_length = length // 2
        if half_length < 1:
            half_length = 1

        for word in words_to_use:
            total_tst_exact = total_tst_exact + time_search(root, word, True, repeats_per_word)
            total_list_exact = total_list_exact + time_search(pairs, word, False, repeats_per_word)

            prefix = word[0:half_length]
            total_tst_prefix = total_tst_prefix + time_prefix(root, prefix, True, repeats_per_word)
            total_list_prefix = total_list_prefix + time_prefix(pairs, prefix, False, repeats_per_word)

        exact_lengths.append(length)
        exact_tst_times.append(total_tst_exact / num_words)
        exact_list_times.append(total_list_exact / num_words)

        prefix_lengths.append(half_length)
        prefix_tst_times.append(total_tst_prefix / num_words)
        prefix_list_times.append(total_list_prefix / num_words)

    result = {}
    result["exact_lengths"] = exact_lengths
    result["exact_tst_times"] = exact_tst_times
    result["exact_list_times"] = exact_list_times
    result["prefix_lengths"] = prefix_lengths
    result["prefix_tst_times"] = prefix_tst_times
    result["prefix_list_times"] = prefix_list_times
    return result


# ----------------------------------------------------------------------
# Experiment 2: synthetic large dataset (to reveal the crossover point)
# ----------------------------------------------------------------------
def generate_synthetic_pairs(base_pairs, target_size):
    synthetic = []
    suffix_number = 0
    while len(synthetic) < target_size:
        for i in range(len(base_pairs)):
            if len(synthetic) >= target_size:
                break
            base_word = base_pairs[i][0]
            base_translation = base_pairs[i][1]
            new_word = base_word + str(suffix_number)
            synthetic.append([new_word, base_translation])
        suffix_number = suffix_number + 1
    return synthetic


def run_synthetic_benchmark(base_pairs, sizes, repeats_per_word, words_per_size):
    dataset_sizes = []
    tst_times = []
    list_times = []

    for size in sizes:
        synthetic_pairs = generate_synthetic_pairs(base_pairs, size)
        synthetic_root = build_tree(synthetic_pairs)

        total_tst = 0
        total_list = 0

        for i in range(words_per_size):
            index = (i * 37) % len(synthetic_pairs)  # spread out sample words
            word = synthetic_pairs[index][0]
            total_tst = total_tst + time_search(synthetic_root, word, True, repeats_per_word)
            total_list = total_list + time_search(synthetic_pairs, word, False, repeats_per_word)

        dataset_sizes.append(size)
        tst_times.append(total_tst / words_per_size)
        list_times.append(total_list / words_per_size)

        print("Synthetic size " + str(size) + " done.")

    result = {}
    result["sizes"] = dataset_sizes
    result["tst_times"] = tst_times
    result["list_times"] = list_times
    return result


# ----------------------------------------------------------------------
# Printing and plotting
# ----------------------------------------------------------------------
def print_averaged_results(result):
    print("")
    print("Exact Word Lookup - averaged over multiple words per length")
    print("Length    TST (us)    List (us)")
    for i in range(len(result["exact_lengths"])):
        length = result["exact_lengths"][i]
        tst_time = round(result["exact_tst_times"][i], 3)
        list_time = round(result["exact_list_times"][i], 3)
        print(str(length) + "    " + str(tst_time) + "    " + str(list_time))

    print("")
    print("Prefix Autocomplete - averaged over multiple words per length")
    print("Length    TST (us)    List (us)")
    for i in range(len(result["prefix_lengths"])):
        length = result["prefix_lengths"][i]
        tst_time = round(result["prefix_tst_times"][i], 3)
        list_time = round(result["prefix_list_times"][i], 3)
        print(str(length) + "    " + str(tst_time) + "    " + str(list_time))


def print_synthetic_results(result):
    print("")
    print("Synthetic Large Dataset - Exact Word Lookup")
    print("N (words)    TST (us)    List (us)")
    for i in range(len(result["sizes"])):
        size = result["sizes"][i]
        tst_time = round(result["tst_times"][i], 3)
        list_time = round(result["list_times"][i], 3)
        print(str(size) + "    " + str(tst_time) + "    " + str(list_time))


def plot_averaged_results(result, out_path):
    figure, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].plot(result["exact_lengths"], result["exact_list_times"],
                 marker="o", color="red", label="List (linear scan)")
    axes[0].plot(result["exact_lengths"], result["exact_tst_times"],
                 marker="o", color="blue", label="Ternary Search Tree")
    axes[0].set_xlabel("Query (word) length")
    axes[0].set_ylabel("Average time (microseconds)")
    axes[0].set_title("Exact Word Lookup (averaged)")
    axes[0].legend()
    axes[0].grid(True)

    axes[1].plot(result["prefix_lengths"], result["prefix_list_times"],
                 marker="o", color="red", label="List (linear scan)")
    axes[1].plot(result["prefix_lengths"], result["prefix_tst_times"],
                 marker="o", color="blue", label="Ternary Search Tree")
    axes[1].set_xlabel("Prefix length")
    axes[1].set_ylabel("Average time (microseconds)")
    axes[1].set_title("Prefix Autocomplete (averaged)")
    axes[1].legend()
    axes[1].grid(True)

    figure.tight_layout()
    figure.savefig(out_path, dpi=150)
    print("")
    print("Saved plot to " + out_path)


def plot_synthetic_results(result, out_path):
    figure, axis = plt.subplots(figsize=(7, 5))

    axis.plot(result["sizes"], result["list_times"],
              marker="o", color="red", label="List (linear scan) - O(N)")
    axis.plot(result["sizes"], result["tst_times"],
              marker="o", color="blue", label="Ternary Search Tree - O(log N)")
    axis.set_xlabel("Dataset size N (number of words)")
    axis.set_ylabel("Average time (microseconds)")
    axis.set_title("Exact Word Lookup vs Dataset Size\n(crossover point)")
    axis.legend()
    axis.grid(True)

    figure.tight_layout()
    figure.savefig(out_path, dpi=150)
    print("Saved plot to " + out_path)


def main():
    pairs = load_pairs("dataset.csv")
    root = build_tree(pairs)

    # --- Experiment 1: real dataset, averaged over multiple words ---
    averaged_result = run_averaged_benchmark(
        pairs, root, repeats_per_word=300, max_words_per_length=25
    )
    print_averaged_results(averaged_result)
    plot_averaged_results(averaged_result, "growth_curves.png")

    # --- Experiment 2: synthetic large dataset, showing the crossover ---
    sizes_to_test = [200, 500, 1000, 2000, 4000, 8000, 16000]
    synthetic_result = run_synthetic_benchmark(
        pairs, sizes_to_test, repeats_per_word=100, words_per_size=15
    )
    print_synthetic_results(synthetic_result)
    plot_synthetic_results(synthetic_result, "growth_curves_large.png")


if __name__ == "__main__":
    main()