import tkinter
from tkinter import ttk

from tst import insert, search, prefix_search


# Load data
def load_dataset(path):
    root = None
    word_count = 0
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

        word = parts[0].strip()
        translation = parts[1].strip()

        if word != "":
            root = insert(root, word.lower(), 0, translation)
            word_count = word_count + 1

    return root, word_count


# Result helpers
def clear_results(results_box):
    results_box.configure(state="normal")
    results_box.delete("1.0", tkinter.END)


def show_line(results_box, text, tag=None):
    if tag is not None:
        results_box.insert(tkinter.END, text + "\n", tag)
    else:
        results_box.insert(tkinter.END, text + "\n")


def lock_results(results_box):
    results_box.configure(state="disabled")


# Buttons functionality
def on_translate(root, entry, results_box, status_label):
    word = entry.get().strip()
    clear_results(results_box)

    if word == "":
        show_line(results_box, "Please enter a word to search.", "warning")
        lock_results(results_box)
        return

    translation = search(root, word.lower())

    if translation is not None:
        show_line(results_box, "English:    " + word, "label")
        show_line(results_box, "Urdu:       " + translation, "result")
        status_label.configure(text=f"Found entry for '{word}'.")
    else:
        show_line(results_box, f"No record of '{word}' found.", "warning")
        status_label.configure(text=f"No entry found for '{word}'.")

    lock_results(results_box)


def on_autocomplete(root, entry, results_box, status_label):
    prefix = entry.get().strip()
    clear_results(results_box)

    if prefix == "":
        show_line(results_box, "Please enter a prefix to browse matches.", "warning")
        lock_results(results_box)
        return

    matches = prefix_search(root, prefix.lower())

    if len(matches) == 0:
        show_line(results_box, f"No entries begin with '{prefix}'.", "warning")
        status_label.configure(text=f"No matches for '{prefix}'.")
    else:
        show_line(results_box, f"{len(matches)} matches found for '{prefix}':", "label")
        show_line(results_box, "")
        for pair in matches:
            show_line(results_box, f"{pair[0]}  ->  {pair[1]}", "result")
        status_label.configure(text=f"{len(matches)} prefix matches found.")

    lock_results(results_box)


def on_enter_key(event, root, entry, results_box, status_label):
    on_translate(root, entry, results_box, status_label)


# Main application Layout
def main():
    root_node, word_count = load_dataset("dataset.csv")

    window = tkinter.Tk()
    window.title("English to Urdu Dictionary")
    window.geometry("640x680")
    window.minsize(540, 600)

    bg_color = "#12151c"
    card_color = "#1a1f2c"
    input_color = "#232938"
    accent_primary = "#4f46e5"
    accent_hover = "#6366f1"
    accent_secondary = "#334155"
    accent_secondary_hover = "#475569"
    text_main = "#f8fafc"
    text_muted = "#94a3b8"
    result_color = "#38bdf8"
    warn_color = "#f43f5e"
    border_color = "#334155"

    window.configure(bg=bg_color)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background=bg_color)

    # Header Section
    header_frame = ttk.Frame(window, padding=(28, 24, 28, 12))
    header_frame.pack(fill="x")

    title_label = tkinter.Label(
        header_frame, text="English \u2192 Urdu Dictionary",
        font=("Segoe UI", 20, "bold"), bg=bg_color, fg=text_main
    )
    title_label.pack(anchor="center")

    subtitle_label = tkinter.Label(
        header_frame, text="Powered by Ternary Search Tree",
        font=("Segoe UI", 10), bg=bg_color, fg=text_muted
    )
    subtitle_label.pack(anchor="center", pady=(4, 0))

    # Search Box Frame
    search_outer = ttk.Frame(window, padding=(28, 8, 28, 12))
    search_outer.pack(fill="x")

    entry = tkinter.Entry(
        search_outer, font=("Segoe UI", 14), bg=input_color, fg=text_main,
        insertbackground=text_main, relief="flat", highlightthickness=1,
        highlightbackground=border_color, highlightcolor=accent_primary
    )
    entry.pack(fill="x", ipady=10, ipadx=10)

    # Action Buttons Frame
    btn_frame = ttk.Frame(window, padding=(28, 0, 28, 16))
    btn_frame.pack(fill="x")

    translate_btn = tkinter.Button(
        btn_frame, text="Search Translation", font=("Segoe UI", 10, "bold"),
        bg=accent_primary, fg="#ffffff", activebackground=accent_hover,
        activeforeground="#ffffff", relief="flat", padx=18, pady=10, cursor="hand2",
        command=lambda: on_translate(root_node, entry, results_box, status_label)
    )
    translate_btn.pack(side="left", padx=(0, 12))

    autocomplete_btn = tkinter.Button(
        btn_frame, text="Prefix Autocomplete", font=("Segoe UI", 10, "bold"),
        bg=accent_secondary, fg=text_main, activebackground=accent_secondary_hover,
        activeforeground="#ffffff", relief="flat", padx=18, pady=10, cursor="hand2",
        command=lambda: on_autocomplete(root_node, entry, results_box, status_label)
    )
    autocomplete_btn.pack(side="left")

    # Results Display Frame
    results_frame = ttk.Frame(window, padding=(28, 0, 28, 16))
    results_frame.pack(fill="both", expand=True)

    results_box = tkinter.Text(
        results_frame, wrap="word", font=("Segoe UI", 12),
        bg=card_color, fg=text_main, relief="flat",
        insertbackground=text_main, padx=18, pady=18,
        highlightthickness=1, highlightbackground=border_color
    )
    results_box.pack(fill="both", expand=True, side="left")

    scrollbar = ttk.Scrollbar(results_frame, command=results_box.yview)
    scrollbar.pack(side="right", fill="y")
    results_box.configure(yscrollcommand=scrollbar.set)

    results_box.tag_configure("label", font=("Segoe UI", 10, "bold"), foreground=text_muted)
    results_box.tag_configure("result", font=("Segoe UI", 15), foreground=result_color)
    results_box.tag_configure("warning", font=("Segoe UI", 11, "italic"), foreground=warn_color)
    results_box.configure(state="disabled")

    # Status Bar
    status_label = tkinter.Label(
        window, text=f"Ready — {word_count} entries indexed.",
        font=("Segoe UI", 9), bg="#0d0f14", fg=text_muted, anchor="w", padx=16, pady=8
    )
    status_label.pack(fill="x", side="bottom")

    entry.bind(
        "<Return>",
        lambda event: on_enter_key(event, root_node, entry, results_box, status_label)
    )
    entry.focus()

    window.mainloop()

main()