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

    def _add_labeled_entry(self, parent: ttk.LabelFrame, label: str, variable: tk.StringVar, row: int) -> ttk.Entry:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=6)
        entry = ttk.Entry(parent, textvariable=variable, width=34)
        entry.grid(row=row, column=1, columnspan=2, sticky="ew", pady=6)
        parent.columnconfigure(1, weight=1)
        return entry

    def generate_new_password(self) -> None:
        self.password_var.set(generate_password(16))
        self.password_entry.configure(show="")
        self.password_visible = True

    def toggle_password_visibility(self) -> None:
        self.password_visible = not self.password_visible
        self.password_entry.configure(show="" if self.password_visible else "*")

    def add_entry(self) -> None:
        entry = self._form_to_entry()
        if not entry:
            return
        entry["id"] = str(uuid.uuid4())
        self.vault_data.setdefault("entries", []).append(entry)
        self.persist_and_refresh("Credential saved successfully.")

    def update_entry(self) -> None:
        if not self.selected_entry_id:
            messagebox.showwarning("No Selection", "Select a row from the table first.")
            return
        updated = self._form_to_entry()
        if not updated:
            return
        updated["id"] = self.selected_entry_id
        entries = self.vault_data.setdefault("entries", [])
        for index, entry in enumerate(entries):
            if entry.get("id") == self.selected_entry_id:
                entries[index] = updated
                self.persist_and_refresh("Credential updated successfully.")
                return

    def delete_entry(self) -> None:
        if not self.selected_entry_id:
            messagebox.showwarning("No Selection", "Select a row from the table first.")
            return
        if not messagebox.askyesno("Confirm Delete", "Delete selected credential?"):
            return
        self.vault_data["entries"] = [e for e in self.vault_data.get("entries", []) if e.get("id") != self.selected_entry_id]
        self.clear_form()
        self.persist_and_refresh("Credential deleted successfully.")

    def _form_to_entry(self) -> dict | None:
        website = self.website_var.get().strip()
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        category = self.category_var.get().strip() or "Uncategorized"

        if not website or not username or not password:
            messagebox.showwarning("Missing Fields", "Website, username, and password are required.")
            return None

        return {
            "website": website,
            "username": username,
            "password": password,
            "category": category,
        }

    def persist_and_refresh(self, success_message: str) -> None:
        save_vault(self.vault_data, self.master_password)
        self.update_category_filter()
        self.refresh_table()
        messagebox.showinfo("Success", success_message)

    def refresh_table(self) -> None:
        for row in self.tree.get_children():
            self.tree.delete(row)

        query = self.search_var.get().lower().strip() if hasattr(self, "search_var") else ""
        selected_category = self.filter_category_var.get() if hasattr(self, "filter_category_var") else "All"

        for entry in self.vault_data.get("entries", []):
            category = entry.get("category", "Uncategorized")
            searchable = f"{entry.get('website', '')} {entry.get('username', '')} {category}".lower()
            if query and query not in searchable:
                continue
            if selected_category != "All" and category != selected_category:
                continue
            masked_password = "•" * min(len(entry.get("password", "")), 12)
            self.tree.insert(
                "",
                "end",
                iid=entry.get("id"),
                values=(entry.get("website", ""), entry.get("username", ""), masked_password, category),
            )

    def update_category_filter(self) -> None:
        categories = sorted({entry.get("category", "Uncategorized") for entry in self.vault_data.get("entries", [])})
        values = ["All"] + categories
        self.category_filter["values"] = values
        if self.filter_category_var.get() not in values:
            self.filter_category_var.set("All")

    def on_row_select(self, _event) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        entry_id = selected[0]
        entry = next((e for e in self.vault_data.get("entries", []) if e.get("id") == entry_id), None)
        if not entry:
            return
        self.selected_entry_id = entry_id
        self.website_var.set(entry.get("website", ""))
        self.username_var.set(entry.get("username", ""))
        self.password_var.set(entry.get("password", ""))
        self.category_var.set(entry.get("category", "Uncategorized"))
        self.password_entry.configure(show="*")
        self.password_visible = False

    def clear_form(self) -> None:
        self.selected_entry_id = None
        self.website_var.set("")
        self.username_var.set("")
        self.password_var.set("")
        self.category_var.set("")
        self.password_entry.configure(show="*")
        self.password_visible = False
        self.tree.selection_remove(self.tree.selection())

    def export_current_vault(self) -> None:
        destination = filedialog.asksaveasfilename(
            title="Export Encrypted Vault",
            defaultextension=".enc",
            filetypes=[("Encrypted vault", "*.enc"), ("All files", "*.*")],
        )
        if not destination:
            return
        try:
            export_vault(destination)
            messagebox.showinfo("Export Complete", "Encrypted vault exported successfully.")
        except Exception as exc:
            messagebox.showerror("Export Failed", str(exc))

    def import_existing_vault(self) -> None:
        source = filedialog.askopenfilename(
            title="Import Encrypted Vault",
            filetypes=[("Encrypted vault", "*.enc"), ("All files", "*.*")],
        )
        if not source:
            return
        answer = messagebox.askyesno("Import Vault", "This will replace the current vault.enc file. Continue?")
        if not answer:
            return
        try:
            import_vault(source)
            messagebox.showinfo("Import Complete", "Vault imported. Please login again using its master password.")
            self.master_password = ""
            self.vault_data = {"entries": []}
            self.on_logout()
        except Exception as exc:
            messagebox.showerror("Import Failed", str(exc))