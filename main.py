from tst import insert, search, prefix_search

import tkinter
from tkinter import messagebox


def show_popup(title, message):
    """Displays a simple, temporary Tkinter popup message box."""
    window = tkinter.Tk()
    window.withdraw()                       # Hide the main root window
    messagebox.showinfo(title, message)     # Show the info popup with the given title and message
    window.destroy()                        # Close the hidden root window completely after dismissal


def load_dataset(path):
    """Loads CSV data from the specified path and inserts words into the TST root."""
    root = None
    file = open(path, "r", encoding="utf-8") # Open dataset file in read mode with UTF-8 encoding
    lines = file.readlines()                 # Read all lines from the file
    file.close()                             # Close the file safely

    first_line = True
    for line in lines:
        line = line.strip()                  # Remove leading/trailing whitespaces and newlines
        if line == "":
            continue                         # Skip empty lines
        if first_line:
            first_line = False
            continue                         # Skip header row ("word,translation")

        parts = line.split(",")              # Split the CSV line by comma into word and translation
        if len(parts) < 2:
            continue                         # Skip malformed lines

        word = parts[0].strip()              # Extract and clean the English word
        translation = parts[1].strip()       # Extract and clean the Urdu translation

        if word != "":
            root = insert(root, word.lower(), 0, translation)  # Insert lowercase word into the TST

    return root                              # Return the root node of the populated TST


def print_menu():
    """Prints the command-line interface menu options."""
    print("")
    print("===== English -> Urdu Pocket Dictionary =====")
    print("1. Translate a word")
    print("2. Autocomplete / prefix suggestions")
    print("3. Exit")


def main():
    """Main function to run the console menu loop and manage user interactions."""
    print("Loading dictionary...")
    root = load_dataset("dataset.csv")       #Load the dictionary dataset into the TST
    print("Dictionary loaded.")

    running = True
    while running:
        print_menu()
        choice = input("Select an option (1-3): ").strip()  # Read user choice

        if choice == "1":
            word = input("Enter an English word: ").strip()
            translation = search(root, word) # Search for word in the TST

            if translation is not None:
                message = word + "  ->  " + translation
                print("  " + message)
                show_popup("Translation", message)  #popup if word is found
            else:
                message = "'" + word + "' was not found in the dictionary."
                print("  " + message)
                show_popup("Not Found", message)    #popup if word is missing

        elif choice == "2":
            prefix = input("Enter a prefix: ").strip()
            matches = prefix_search(root, prefix)   #matching words for the prefix

            if len(matches) == 0:
                message = "No words found starting with '" + prefix + "'."
                print("  " + message)
                show_popup("No Matches", message)   #popup if no matches exist
            else:
                print("  " + str(len(matches)) + " match(es) found:")
                message = str(len(matches)) + " match(es) found:\n\n"
                for pair in matches:
                    word = pair[0]                  #matched word from the pair
                    translation = pair[1]           # Urdu translation
                    print("    " + word + "  ->  " + translation) 
                    message = message + word + "  ->  " + translation + "\n"  # Append to popup 
                show_popup("Autocomplete Results", message)  # Show popup with all match results

        elif choice == "3":
            print("Goodbye!")
            running = False                         #exit loop

        else:
            print("Invalid option, please choose 1, 2, or 3.")  #invalid inputs


main()