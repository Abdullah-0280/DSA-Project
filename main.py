"""
CLI English-to-Urdu Pocket Dictionary
Basic version - no classes, no csv module, plain file reading.

Also shows results in a small popup window (using tkinter) so that
Urdu text always displays correctly, even if the terminal you are
using does not render Arabic-script text properly.
"""

from tst import insert, search, prefix_search

try:
    import tkinter
    from tkinter import messagebox
    POPUP_AVAILABLE = True
except ImportError:
    POPUP_AVAILABLE = False


def show_popup(title, message):
    if POPUP_AVAILABLE is False:
        return
    window = tkinter.Tk()
    window.withdraw()          # hide the empty main window
    window.attributes("-topmost", True)  # bring popup to the front
    messagebox.showinfo(title, message)
    window.destroy()


def load_dataset(path):
    root = None
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
            continue  # skip header row "word,translation"

        parts = line.split(",")
        if len(parts) < 2:
            continue

        word = parts[0].strip()
        translation = parts[1].strip()

        if word != "":
            root = insert(root, word.lower(), 0, translation)

    return root


def print_menu():
    print("")
    print("===== English -> Urdu Pocket Dictionary =====")
    print("1. Translate a word")
    print("2. Autocomplete / prefix suggestions")
    print("3. Exit")
    if POPUP_AVAILABLE is False:
        print("(Note: tkinter not found - results will only print in terminal)")


def main():
    print("Loading dictionary...")
    root = load_dataset("dataset.csv")
    print("Dictionary loaded.")

    running = True
    while running:
        print_menu()
        choice = input("Select an option (1-3): ").strip()

        if choice == "1":
            word = input("Enter an English word: ").strip()
            translation = search(root, word)

            if translation is not None:
                message = word + "  ->  " + translation
                print("  " + message)
                show_popup("Translation", message)
            else:
                message = "'" + word + "' was not found in the dictionary."
                print("  " + message)
                show_popup("Not Found", message)

        elif choice == "2":
            prefix = input("Enter a prefix: ").strip()
            matches = prefix_search(root, prefix)

            if len(matches) == 0:
                message = "No words found starting with '" + prefix + "'."
                print("  " + message)
                show_popup("No Matches", message)
            else:
                print("  " + str(len(matches)) + " match(es) found:")
                message = str(len(matches)) + " match(es) found:\n\n"
                for pair in matches:
                    word = pair[0]
                    translation = pair[1]
                    print("    " + word + "  ->  " + translation)
                    message = message + word + "  ->  " + translation + "\n"
                show_popup("Autocomplete Results", message)

        elif choice == "3":
            print("Goodbye!")
            running = False

        else:
            print("Invalid option, please choose 1, 2, or 3.")


if __name__ == "__main__":
    main()