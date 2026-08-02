"""
English -> Urdu Pocket Dictionary - "Old Library" Front End
Basic style: plain functions only, no custom classes.

Same search + autocomplete features as gui_app.py, but:
    - styled to look like an old library reading room (parchment,
      dark wood, brass/gold accents, serif fonts)
    - if you look up a word that is a known animal (cat, dog, bird,
      etc.) a small emoji animation bounces across a "shelf" canvas

Run with:
    python3 gui_library.py
"""

import math
import tkinter
from tkinter import ttk

from tst import insert, search, prefix_search


# ----------------------------------------------------------------------
# Words that trigger the little bounce animation, and what to show
# ----------------------------------------------------------------------
ANIMAL_EMOJIS = {
    "cat": "\U0001F408",
    "dog": "\U0001F415",
    "bird": "\U0001F426",
    "fish": "\U0001F41F",
    "lion": "\U0001F981",
    "tiger": "\U0001F42F",
    "elephant": "\U0001F418",
    "horse": "\U0001F434",
    "rabbit": "\U0001F430",
    "snake": "\U0001F40D",
    "mouse": "\U0001F42D",
    "chicken": "\U0001F414",
}


# ----------------------------------------------------------------------
# Data loading (same as the other versions)
# ----------------------------------------------------------------------
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
            continue  # skip header row "word,translation"

        parts = line.split(",")
        if len(parts) < 2:
            continue

        word = parts[0].strip()
        translation = parts[1].strip()

        if word != "":
            root = insert(root, word.lower(), 0, translation)
            word_count = word_count + 1

    return root, word_count


# ----------------------------------------------------------------------
# Results panel helpers
# ----------------------------------------------------------------------
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


# ----------------------------------------------------------------------
# Shelf animation (bouncing emoji on a canvas)
# ----------------------------------------------------------------------
def clear_shelf(shelf_canvas):
    shelf_canvas.delete("critter")


def animate_step(window, shelf_canvas, item_id, step, total_steps, job_holder, my_token):
    # If a newer animation has started since this one was scheduled, stop.
    if job_holder["token"] != my_token:
        return

    if step > total_steps:
        return

    width = int(shelf_canvas["width"])
    ground_y = int(shelf_canvas["height"]) - 24

    # Horizontal position: move steadily left to right across the shelf.
    x = 30 + (width - 60) * (step / total_steps)

    # Vertical position: bounce using a bouncing-ball style curve
    # (a series of shrinking hops), purely from step count/math, no
    # physics libraries needed.
    bounce_progress = (step % 20) / 20.0
    hop_height = 40 * (1 - step / total_steps)
    y = ground_y - hop_height * math.sin(bounce_progress * math.pi)

    shelf_canvas.coords(item_id, x, y)

    next_step = step + 1
    job_id = window.after(
        30,
        lambda: animate_step(window, shelf_canvas, item_id, next_step, total_steps, job_holder, my_token)
    )
    job_holder["job"] = job_id


def start_animation(window, shelf_canvas, job_holder, emoji):
    clear_shelf(shelf_canvas)

    # Cancel any animation currently in flight.
    if job_holder["job"] is not None:
        window.after_cancel(job_holder["job"])
        job_holder["job"] = None

    job_holder["token"] = job_holder["token"] + 1
    my_token = job_holder["token"]

    ground_y = int(shelf_canvas["height"]) - 24
    item_id = shelf_canvas.create_text(
        30, ground_y, text=emoji, font=("Segoe UI Emoji", 32), tags="critter"
    )

    animate_step(window, shelf_canvas, item_id, 0, 60, job_holder, my_token)


# ----------------------------------------------------------------------
# Action handlers
# ----------------------------------------------------------------------
def on_translate(root, entry, results_box, status_label, window, shelf_canvas, job_holder):
    word = entry.get().strip()
    clear_results(results_box)

    if word == "":
        show_line(results_box, "The shelves have nothing without a word to search for.", "warning")
        lock_results(results_box)
        return

    translation = search(root, word.lower())

    if translation is not None:
        show_line(results_box, "English:   " + word, "label")
        show_line(results_box, "Urdu:         " + translation, "result")
        status_label.configure(text="Found an entry for \u201c" + word + "\u201d in the archive.")

        if word.lower() in ANIMAL_EMOJIS:
            start_animation(window, shelf_canvas, job_holder, ANIMAL_EMOJIS[word.lower()])
        else:
            clear_shelf(shelf_canvas)
    else:
        show_line(results_box, "No record of \u201c" + word + "\u201d in this library.", "warning")
        status_label.configure(text="No entry found for \u201c" + word + "\u201d.")
        clear_shelf(shelf_canvas)

    lock_results(results_box)


def on_autocomplete(root, entry, results_box, status_label, shelf_canvas):
    prefix = entry.get().strip()
    clear_results(results_box)
    clear_shelf(shelf_canvas)

    if prefix == "":
        show_line(results_box, "Please write a prefix to search the shelves.", "warning")
        lock_results(results_box)
        return

    matches = prefix_search(root, prefix.lower())

    if len(matches) == 0:
        show_line(results_box, "No entries begin with \u201c" + prefix + "\u201d.", "warning")
        status_label.configure(text="No matches for \u201c" + prefix + "\u201d.")
    else:
        show_line(results_box, str(len(matches)) + " entries found for \u201c" + prefix + "\u201d:", "label")
        show_line(results_box, "")
        for pair in matches:
            english_word = pair[0]
            urdu_translation = pair[1]
            show_line(results_box, english_word + "   ->   " + urdu_translation, "result")
        status_label.configure(text=str(len(matches)) + " entries found for \u201c" + prefix + "\u201d.")

    lock_results(results_box)


def on_enter_key(event, root, entry, results_box, status_label, window, shelf_canvas, job_holder):
    on_translate(root, entry, results_box, status_label, window, shelf_canvas, job_holder)


# ----------------------------------------------------------------------
# Build and run the window
# ----------------------------------------------------------------------
def main():
    root_node, word_count = load_dataset("dataset.csv")

    # Mutable holder so the animation functions can track/cancel jobs
    # without needing a class.
    job_holder = {"job": None, "token": 0}

    window = tkinter.Tk()
    window.title("The Old Library - English to Urdu Dictionary")
    window.geometry("600x620")
    window.minsize(520, 560)

    parchment = "#ece0c4"
    dark_wood = "#3b2a1a"
    mid_wood = "#5a3e26"
    brass = "#a97c33"
    ink = "#2c1e12"
    warn_color = "#8b1a1a"

    window.configure(bg=dark_wood)

    style = ttk.Style()
    style.theme_use("clam")

    style.configure("TFrame", background=dark_wood)
    style.configure("Header.TLabel", background=dark_wood, foreground=brass,
                    font=("Georgia", 20, "bold"))
    style.configure("Sub.TLabel", background=dark_wood, foreground="#cbb98a",
                    font=("Georgia", 11, "italic"))
    style.configure("TLabel", background=dark_wood, foreground=parchment,
                    font=("Georgia", 11))
    style.configure("TButton", font=("Georgia", 10, "bold"), padding=8,
                    background=brass, foreground=ink)
    style.map("TButton", background=[("active", "#c79a4b")])
    style.configure("Status.TLabel", background=mid_wood, foreground="#e7d9ad",
                    font=("Georgia", 9), padding=6)

    # --- Header ---
    header_frame = ttk.Frame(window, padding=(20, 18, 20, 6))
    header_frame.pack(fill="x")

    title_label = ttk.Label(header_frame, text="\U0001F4DA The Old Library \U0001F4DA",
                             style="Header.TLabel")
    title_label.pack(anchor="center")

    subtitle_label = ttk.Label(
        header_frame,
        text="An English to Urdu Archive, catalogued by Ternary Search Tree",
        style="Sub.TLabel"
    )
    subtitle_label.pack(anchor="center", pady=(2, 0))

    # --- Search bar ---
    search_frame = ttk.Frame(window, padding=(20, 10, 20, 6))
    search_frame.pack(fill="x")

    entry = tkinter.Entry(
        search_frame, font=("Georgia", 13), bg=parchment, fg=ink,
        insertbackground=ink, relief="flat", highlightthickness=1,
        highlightbackground=brass, highlightcolor=brass
    )
    entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))

    button_frame = ttk.Frame(window, padding=(20, 0, 20, 10))
    button_frame.pack(fill="x")

    translate_button = ttk.Button(
        button_frame, text="Consult the Archive",
        command=lambda: on_translate(root_node, entry, results_box, status_label,
                                      window, shelf_canvas, job_holder)
    )
    translate_button.pack(side="left", padx=(0, 8))

    autocomplete_button = ttk.Button(
        button_frame, text="Browse by Prefix",
        command=lambda: on_autocomplete(root_node, entry, results_box, status_label, shelf_canvas)
    )
    autocomplete_button.pack(side="left")

    # --- Results panel ---
    results_frame = ttk.Frame(window, padding=(20, 0, 20, 8))
    results_frame.pack(fill="both", expand=True)

    results_box = tkinter.Text(
        results_frame, wrap="word", font=("Georgia", 13),
        bg=parchment, fg=ink, relief="flat",
        insertbackground=ink, padx=16, pady=14,
        highlightthickness=1, highlightbackground=mid_wood
    )
    results_box.pack(fill="both", expand=True, side="left")

    scrollbar = ttk.Scrollbar(results_frame, command=results_box.yview)
    scrollbar.pack(side="right", fill="y")
    results_box.configure(yscrollcommand=scrollbar.set)

    results_box.tag_configure("label", font=("Georgia", 10, "bold"), foreground="#5a3e26")
    results_box.tag_configure("result", font=("Georgia", 15), foreground=ink)
    results_box.tag_configure("warning", font=("Georgia", 11, "italic"), foreground=warn_color)
    results_box.configure(state="disabled")

    # --- Shelf / animation canvas ---
    shelf_frame = ttk.Frame(window, padding=(20, 0, 20, 8))
    shelf_frame.pack(fill="x")

    shelf_label = ttk.Label(shelf_frame, text="The Reading Room Floor:", style="Sub.TLabel")
    shelf_label.pack(anchor="w", pady=(0, 4))

    shelf_canvas = tkinter.Canvas(
        shelf_frame, width=520, height=100, bg="#6b4a2e",
        highlightthickness=1, highlightbackground=mid_wood
    )
    shelf_canvas.pack(fill="x")
    # a simple wooden floorboard line for atmosphere
    shelf_canvas.create_line(0, 76, 600, 76, fill="#4a3220", width=2)
    shelf_canvas.create_line(0, 60, 600, 60, fill="#5a3e26", width=1)

    # --- Status bar ---
    status_label = ttk.Label(window, text="Loading the archive...", style="Status.TLabel", anchor="w")
    status_label.pack(fill="x", side="bottom")
    status_label.configure(
        text=str(word_count) + " entries catalogued. Try looking up \u201ccat\u201d."
    )

    entry.bind(
        "<Return>",
        lambda event: on_enter_key(event, root_node, entry, results_box, status_label,
                                    window, shelf_canvas, job_holder)
    )
    entry.focus()

    window.mainloop()


if __name__ == "__main__":
    main()