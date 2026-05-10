from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from login_ui import LoginWindow


def main() -> None:
    root = tk.Tk()
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")
    LoginWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
