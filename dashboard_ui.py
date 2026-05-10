from __future__ import annotations

import uuid
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Callable

from password_generator import generate_password
from storage import export_vault, import_vault, save_vault


class DashboardWindow:
    """Main dashboard for adding, viewing, searching, updating and deleting credentials."""

    def __init__(self, root: tk.Tk, master_password: str, vault_data: dict, on_logout: Callable[[], None]):
        self.root = root
        self.master_password = master_password
        self.vault_data = vault_data
        self.on_logout = on_logout
        self.selected_entry_id: str | None = None
        self.password_visible = False
        self.show()

    def _clear_root(self) -> None:
        for widget in self.root.winfo_children():
            widget.destroy()

    def show(self) -> None:
        self._clear_root()

        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(2, weight=1)

        title = ttk.Label(main, text="Password Manager Dashboard", font=("Segoe UI", 18, "bold"))
        title.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))

        form = ttk.LabelFrame(main, text="Credential Details", padding=12)
        form.grid(row=1, column=0, sticky="nsew", padx=(0, 12))

        self.website_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.category_var = tk.StringVar()

        self._add_labeled_entry(form, "Website/App:", self.website_var, 0)
        self._add_labeled_entry(form, "Username/Email:", self.username_var, 1)

        ttk.Label(form, text="Password:").grid(row=2, column=0, sticky="w", pady=6)
        self.password_entry = ttk.Entry(form, textvariable=self.password_var, show="*", width=34)
        self.password_entry.grid(row=2, column=1, sticky="ew", pady=6)
        ttk.Button(form, text="Show/Hide", command=self.toggle_password_visibility).grid(
            row=2, column=2, padx=(6, 0), pady=6
        )

        self._add_labeled_entry(form, "Category:", self.category_var, 3)

        ttk.Button(form, text="Generate Strong Password", command=self.generate_new_password).grid(
            row=4, column=0, columnspan=3, sticky="ew", pady=(10, 4)
        )
        ttk.Button(form, text="Save New", command=self.add_entry).grid(row=5, column=0, sticky="ew", pady=4)
        ttk.Button(form, text="Update Selected", command=self.update_entry).grid(
            row=5, column=1, sticky="ew", padx=6, pady=4
        )
        ttk.Button(form, text="Delete Selected", command=self.delete_entry).grid(row=5, column=2, sticky="ew", pady=4)
        ttk.Button(form, text="Clear Form", command=self.clear_form).grid(
            row=6, column=0, columnspan=3, sticky="ew", pady=4
        )

        tools = ttk.LabelFrame(main, text="Search, Filter & Sync", padding=12)
        tools.grid(row=1, column=1, columnspan=2, sticky="nsew")
        tools.columnconfigure(1, weight=1)

        self.search_var = tk.StringVar()
        self.filter_category_var = tk.StringVar(value="All")
        self.search_var.trace_add("write", lambda *_: self.refresh_table())
        self.filter_category_var.trace_add("write", lambda *_: self.refresh_table())

        ttk.Label(tools, text="Search:").grid(row=0, column=0, sticky="w", padx=(0, 6))
        ttk.Entry(tools, textvariable=self.search_var).grid(row=0, column=1, sticky="ew")
        ttk.Label(tools, text="Category:").grid(row=0, column=2, sticky="w", padx=(12, 6))
        self.category_filter = ttk.Combobox(tools, textvariable=self.filter_category_var, width=18, state="readonly")
        self.category_filter.grid(row=0, column=3, sticky="ew")

        ttk.Button(tools, text="Export Encrypted Vault", command=self.export_current_vault).grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0), padx=(0, 6)
        )
        ttk.Button(tools, text="Import Encrypted Vault", command=self.import_existing_vault).grid(
            row=1, column=2, columnspan=2, sticky="ew", pady=(10, 0)
        )

        table_frame = ttk.Frame(main)
        table_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(12, 0))
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        columns = ("website", "username", "password", "category")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        self.tree.heading("website", text="Website/App")
        self.tree.heading("username", text="Username/Email")
        self.tree.heading("password", text="Password")
        self.tree.heading("category", text="Category")
        self.tree.column("website", width=220)
        self.tree.column("username", width=250)
        self.tree.column("password", width=220)
        self.tree.column("category", width=150)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        ttk.Label(
            main,
            text="Security note: credentials are decrypted only after login and saved encrypted in vault.enc.",
            foreground="gray",
        ).grid(row=3, column=0, columnspan=3, sticky="w", pady=(8, 0))

        self.update_category_filter()
        self.refresh_table()

   