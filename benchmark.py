
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

        parts = line.split(",")            #line into columns
        if len(parts) >= 2:                
            word = parts[0].strip().lower()    # Extract and make word lowercase
            translation = parts[1].strip()     #translation

            if word != "":                 #empty words
                pairs.append([word, translation])  # Store pair

    return pairs                           


def list_search(pairs, word):              # Linear search
    word = word.lower()                    #lowercase

    for i in range(len(pairs)):            
        if pairs[i][0] == word:            # Word found
            return pairs[i][1]             # Return translation

    return None                            


def build_tree(pairs):                     # Build TST
    root = None                            # Empty tree

    for i in range(len(pairs)):            # Insert word
        root = insert(root, pairs[i][0], 0, pairs[i][1])  # Insert into TST

    return root                            # Return tree root


def time_function(search_fn, structure, test_words, use_tst, repeats=500): 
    start = time.time()                    #timer
    num_words = len(test_words)            #searches

    for i in range(repeats):               
        for j in range(num_words):         # Search 
            if use_tst is True:           
                search_fn(structure, test_words[j])    # Search TST
            else:                         
                search_fn(structure, test_words[j])    # Search list

    total_time = time.time() - start       # Totaltime
    average_time = total_time / (repeats * num_words) * 1000000  # Average time

    return average_time                   


def run_experiment():                     
    pairs = load_pairs("dataset.csv")      # Load data

    max_len = len(pairs)                   #size
    all_sizes = [50, 100, 250, 500, 1000, 2000, 5000]  
    ns = []                                

    for s in all_sizes:                    #valid sizes
        if s <= max_len:
            ns.append(s)

    if len(ns) == 0:                       # If dataset is very small
        ns.append(max_len)

    structures = [True, False]             # Compare TST and list
    labels = ["Ternary Search Tree - O(log N)", "List (Linear Scan - O(N))"]

    plt.figure(figsize=(8, 5))             # Create figure

    for index in range(len(structures)):   # Test both structures
        use_tst = structures[index]        # Current structure
        label = labels[index]              # Current label

        times = []                         # Store timing results

        for size in ns:                    # Test each dataset size
            subset = []                    # Create subset

            for i in range(size):          
                subset.append(pairs[i])

            if use_tst is True:            #create structure
                struct_obj = build_tree(subset)
                fn = search
            else:
                struct_obj = subset
                fn = list_search

            test_words = []                
            step = size // 10              # Sample every 10%

            if step < 1:
                step = 1

            for i in range(0, size, step): #test words
                test_words.append(subset[i][0])

            avg_time = time_function(fn, struct_obj, test_words, use_tst)  # Measuretime
            times.append(avg_time)        

        plt.plot(ns, times, marker="o", label=label) 

    plt.xlabel("Dataset Size (n)")         
    plt.ylabel("Time (microseconds)")       
    plt.title("Word Lookup: TST vs List")   
    plt.legend()                           
    plt.grid(True)                         

    plt.tight_layout()                     
    plt.savefig("benchmark_comparison.png", dpi=150)  
    plt.close()                            

    print("Saved plot to benchmark_comparison.png")   


if __name__ == "__main__":                
    run_experiment()                      

