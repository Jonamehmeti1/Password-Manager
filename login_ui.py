from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from crypto_utils import VaultCryptoError
from dashboard_ui import DashboardWindow
from storage import DEFAULT_VAULT_PATH, create_empty_vault, load_vault


class LoginWindow:
    """Login screen and master-password flow for the password manager."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AES Password Manager")
        self.root.geometry("980x620")
        self.root.minsize(880, 540)
        self.master_entry: ttk.Entry | None = None
        self.show()

    def _clear_root(self) -> None:
        for widget in self.root.winfo_children():
            widget.destroy()

    def show(self) -> None:
        self._clear_root()
        frame = ttk.Frame(self.root, padding=30)
        frame.pack(expand=True)

        ttk.Label(frame, text="AES Password Manager", font=("Segoe UI", 22, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 20)
        )
        ttk.Label(frame, text="Master Password:").grid(row=1, column=0, sticky="e", padx=8, pady=8)

        self.master_entry = ttk.Entry(frame, show="*", width=35)
        self.master_entry.grid(row=1, column=1, padx=8, pady=8)
        self.master_entry.focus()
        self.master_entry.bind("<Return>", lambda _event: self.login())

        ttk.Button(frame, text="Login", command=self.login).grid(row=2, column=0, pady=15, sticky="ew", padx=8)
        ttk.Button(frame, text="Create New Vault", command=self.create_vault).grid(
            row=2, column=1, pady=15, sticky="ew", padx=8
        )

        note = "Vault file: vault.enc | Data is encrypted locally with AES-256-GCM."
        ttk.Label(frame, text=note, foreground="gray").grid(row=3, column=0, columnspan=2, pady=(10, 0))

    def _get_master_password(self) -> str:
        if self.master_entry is None:
            return ""
        return self.master_entry.get().strip()

    def login(self) -> None:
        password = self._get_master_password()
        if not password:
            messagebox.showwarning("Missing Password", "Please enter the master password.")
            return
        try:
            vault_data = load_vault(password)
            DashboardWindow(self.root, password, vault_data, on_logout=self.show)
        except FileNotFoundError:
            messagebox.showerror("Vault Missing", "No vault.enc file found. Create a new vault first.")
        except VaultCryptoError:
            messagebox.showerror("Login Failed", "Wrong master password or corrupted vault file.")

    def create_vault(self) -> None:
        if DEFAULT_VAULT_PATH.exists():
            answer = messagebox.askyesno(
                "Vault Exists",
                "vault.enc already exists. Replace it with an empty new vault?",
            )
            if not answer:
                return

        password = self._get_master_password()
        if len(password) < 8:
            messagebox.showwarning("Weak Master Password", "Use at least 8 characters for the master password.")
            return

        confirm = simpledialog.askstring("Confirm Master Password", "Re-enter master password:", show="*")
        if confirm != password:
            messagebox.showerror("Mismatch", "Master passwords do not match.")
            return

        vault_data = create_empty_vault(password)
        messagebox.showinfo("Vault Created", "New encrypted vault created successfully.")
        DashboardWindow(self.root, password, vault_data, on_logout=self.show)
