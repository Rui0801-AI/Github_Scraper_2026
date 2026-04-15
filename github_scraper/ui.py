from __future__ import annotations

import asyncio
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from github_scraper.exporter import export_profiles_to_csv
from github_scraper.models import SearchFilters
from github_scraper.scraper import scrape_users


RESULT_CSV_PATH = Path(__file__).resolve().parent.parent / "result.csv"


class GitHubScraperApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("GitHub Talent Scraper")
        self.root.geometry("1120x920")
        self.root.minsize(900, 760)
        self.root.configure(bg="#eef3f9")

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self._configure_styles()
        self._create_variables()
        self._build_layout()

        self.is_running = False

    def _configure_styles(self) -> None:
        self.style.configure(".", font=("Segoe UI", 10))
        self.style.configure("Surface.TFrame", background="#f7f9fc")
        self.style.configure("Card.TFrame", background="#ffffff")
        self.style.configure("Hero.TFrame", background="#dce8f9")
        self.style.configure(
            "SectionTitle.TLabel",
            font=("Segoe UI Semibold", 12),
            background="#ffffff",
            foreground="#15304d",
        )
        self.style.configure(
            "Body.TLabel",
            font=("Segoe UI", 10),
            background="#ffffff",
            foreground="#425466",
        )
        self.style.configure(
            "HeroTitle.TLabel",
            font=("Segoe UI Semibold", 24),
            background="#dce8f9",
            foreground="#0f2740",
        )
        self.style.configure(
            "HeroText.TLabel",
            font=("Segoe UI", 11),
            background="#dce8f9",
            foreground="#3d556f",
        )
        self.style.configure(
            "FieldLabel.TLabel",
            font=("Segoe UI Semibold", 10),
            background="#ffffff",
            foreground="#2a3f55",
        )
        self.style.configure(
            "Hint.TLabel",
            font=("Segoe UI", 9),
            background="#ffffff",
            foreground="#6a7f95",
        )
        self.style.configure(
            "Modern.TEntry",
            fieldbackground="#f6f8fb",
            background="#f6f8fb",
            foreground="#12263a",
            bordercolor="#d7e1ec",
            lightcolor="#d7e1ec",
            darkcolor="#d7e1ec",
            borderwidth=1,
            padding=8,
        )
        self.style.map(
            "Modern.TEntry",
            bordercolor=[("focus", "#2f6fed")],
            lightcolor=[("focus", "#2f6fed")],
            darkcolor=[("focus", "#2f6fed")],
        )
        self.style.configure(
            "Primary.TButton",
            font=("Segoe UI Semibold", 10),
            padding=(18, 12),
            background="#2f6fed",
            foreground="#ffffff",
            borderwidth=0,
        )
        self.style.map(
            "Primary.TButton",
            background=[("active", "#1f5cd2"), ("disabled", "#aabfe7")],
            foreground=[("disabled", "#f3f7ff")],
        )
        self.style.configure(
            "Secondary.TButton",
            font=("Segoe UI Semibold", 10),
            padding=(16, 12),
            background="#edf3ff",
            foreground="#2857b7",
            borderwidth=0,
        )
        self.style.map("Secondary.TButton", background=[("active", "#dde9ff")])
        self.style.configure(
            "Modern.Horizontal.TProgressbar",
            troughcolor="#e7edf5",
            background="#2f6fed",
            thickness=10,
            borderwidth=0,
            lightcolor="#2f6fed",
            darkcolor="#2f6fed",
        )

    def _create_variables(self) -> None:
        self.token_var = tk.StringVar()
        self.specific_query_var = tk.StringVar()
        self.location_var = tk.StringVar()
        self.created_var = tk.StringVar()
        self.min_repos_var = tk.StringVar()
        self.max_repos_var = tk.StringVar()
        self.min_followers_var = tk.StringVar()
        self.max_followers_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready to search GitHub profiles.")
        self.progress_text_var = tk.StringVar(value="0 / 0")
        self.result_var = tk.StringVar(value=f"Appends to\n{RESULT_CSV_PATH}")

    def _build_layout(self) -> None:
        shell = ttk.Frame(self.root, style="Surface.TFrame", padding=14)
        shell.pack(fill="both", expand=True)
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(0, weight=1)

        outer = ttk.Frame(shell, style="Surface.TFrame", padding=16)
        outer.grid(row=0, column=0, sticky="nsew")

        outer.columnconfigure(0, weight=7)
        outer.columnconfigure(1, weight=4)
        outer.rowconfigure(1, weight=1)

        self._build_hero(outer)
        self._build_form_card(outer)
        self._build_info_card(outer)

    def _build_hero(self, parent: ttk.Frame) -> None:
        hero = ttk.Frame(parent, style="Hero.TFrame", padding=18)
        hero.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        hero.columnconfigure(0, weight=1)

        ttk.Label(hero, text="GitHub Talent Scraper", style="HeroTitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            hero,
            text=(
                "Search by location, activity, and audience size, then export a clean CSV "
                "with emails and LinkedIn links when available."
            ),
            style="HeroText.TLabel",
            wraplength=740,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(8, 0))

    def _build_form_card(self, parent: ttk.Frame) -> None:
        card = ttk.Frame(parent, style="Card.TFrame", padding=18)
        card.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)

        ttk.Label(card, text="Search Filters", style="SectionTitle.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(
            card,
            text="Define the audience you want to export. Required filters are called out separately from optional ones.",
            style="Body.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 14))

        ttk.Label(card, text="Required Option", style="SectionTitle.TLabel").grid(
            row=2, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(
            card,
            text="Location is required. All other fields below are optional and help narrow the search.",
            style="Hint.TLabel",
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(4, 12))

        field_specs = [
            ("GitHub Token", self.token_var, "Optional, but recommended to avoid rate limits.", True, False, 4, 0),
            ("Specific String Query", self.specific_query_var, "Optional. Add keywords like python recruiter or react.", False, False, 4, 1),
            ("Location", self.location_var, "Required. Example: New York or Germany", False, True, 7, 0),
            ("Creation Date", self.created_var, "Optional. Use YYYY-MM-DD", False, False, 7, 1),
            ("Min Repos", self.min_repos_var, "Optional. Whole number", False, False, 10, 0),
            ("Max Repos", self.max_repos_var, "Optional. Whole number", False, False, 10, 1),
            ("Min Followers", self.min_followers_var, "Optional. Whole number", False, False, 13, 0),
            ("Max Followers", self.max_followers_var, "Optional. Whole number", False, False, 13, 1),
        ]

        for label, variable, hint, masked, required, row, column in field_specs:
            self._build_field(card, row, column, label, variable, hint, masked, required)

        action_row = 16
        actions = ttk.Frame(card, style="Card.TFrame")
        actions.grid(row=action_row, column=0, columnspan=2, sticky="ew", pady=(12, 14))
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=0)

        self.start_button = ttk.Button(
            actions,
            text="Export Profiles",
            command=self._start_scrape,
            style="Primary.TButton",
        )
        self.start_button.grid(row=0, column=0, sticky="w")

        ttk.Button(
            actions,
            text="Clear Filters",
            command=self._clear_filters,
            style="Secondary.TButton",
        ).grid(row=0, column=1, sticky="e")

        status_frame = ttk.Frame(card, style="Card.TFrame")
        status_frame.grid(row=action_row + 1, column=0, columnspan=2, sticky="ew")
        status_frame.columnconfigure(0, weight=1)

        ttk.Label(status_frame, text="Status", style="FieldLabel.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(status_frame, textvariable=self.status_var, style="Body.TLabel").grid(
            row=1, column=0, sticky="w", pady=(4, 12)
        )

        self.progress = ttk.Progressbar(
            status_frame,
            mode="determinate",
            style="Modern.Horizontal.TProgressbar",
            maximum=100,
            value=0,
        )
        self.progress.grid(row=2, column=0, sticky="ew")

        ttk.Label(status_frame, textvariable=self.progress_text_var, style="Hint.TLabel").grid(
            row=3, column=0, sticky="e", pady=(8, 0)
        )

    def _build_info_card(self, parent: ttk.Frame) -> None:
        card = ttk.Frame(parent, style="Card.TFrame", padding=18)
        card.grid(row=1, column=1, sticky="nsew")
        card.columnconfigure(0, weight=1)

        ttk.Label(card, text="Workspace", style="SectionTitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            card,
            text=(
                "Results are appended to the local result.csv file. Only profiles with a "
                "public email or LinkedIn value are saved."
            ),
            style="Body.TLabel",
            wraplength=280,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(4, 14))

        summary = ttk.Frame(card, style="Hero.TFrame", padding=14)
        summary.grid(row=2, column=0, sticky="ew")
        summary.columnconfigure(0, weight=1)

        ttk.Label(summary, text="Last Result", style="HeroText.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            summary,
            textvariable=self.result_var,
            style="HeroTitle.TLabel",
            wraplength=250,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(8, 0))

        tips = ttk.Frame(card, style="Card.TFrame")
        tips.grid(row=3, column=0, sticky="ew", pady=(20, 0))
        tips.columnconfigure(0, weight=1)

        ttk.Label(tips, text="Search Tips", style="SectionTitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )

        tip_lines = [
            "Add a token for better GitHub API limits.",
            "Use a recent created date to find newer profiles.",
            "Follower and repo filters help narrow strong candidates.",
        ]

        for index, tip in enumerate(tip_lines, start=1):
            ttk.Label(
                tips,
                text=f"- {tip}",
                style="Body.TLabel",
                wraplength=280,
                justify="left",
            ).grid(row=index, column=0, sticky="w", pady=(8 if index == 1 else 6, 0))

    def _build_field(
        self,
        parent: ttk.Frame,
        row: int,
        column: int,
        label: str,
        variable: tk.StringVar,
        hint: str,
        masked: bool,
        required: bool,
    ) -> None:
        field = ttk.Frame(parent, style="Card.TFrame")
        field.grid(
            row=row,
            column=column,
            sticky="ew",
            padx=(0, 8) if column == 0 else (8, 0),
            pady=2,
        )
        field.columnconfigure(0, weight=1)

        field_label = f"{label} *" if required else label
        ttk.Label(field, text=field_label, style="FieldLabel.TLabel").grid(row=0, column=0, sticky="w")
        entry = ttk.Entry(
            field,
            textvariable=variable,
            show="*" if masked else "",
            style="Modern.TEntry",
        )
        entry.grid(row=1, column=0, sticky="ew", pady=(6, 0), ipady=2)
        ttk.Label(field, text=hint, style="Hint.TLabel").grid(row=2, column=0, sticky="w", pady=(4, 0))

    def _clear_filters(self) -> None:
        if self.is_running:
            return

        for variable in (
            self.token_var,
            self.specific_query_var,
            self.location_var,
            self.created_var,
            self.min_repos_var,
            self.max_repos_var,
            self.min_followers_var,
            self.max_followers_var,
        ):
            variable.set("")

        self.status_var.set("Ready to search GitHub profiles.")
        self.progress_text_var.set("0 / 0")
        self.progress.configure(value=0, maximum=100)

    def _collect_filters(self) -> SearchFilters:
        return SearchFilters(
            location=self.location_var.get().strip(),
            specific_query=self.specific_query_var.get().strip(),
            created_after=self.created_var.get().strip(),
            min_repos=self.min_repos_var.get().strip(),
            max_repos=self.max_repos_var.get().strip(),
            min_followers=self.min_followers_var.get().strip(),
            max_followers=self.max_followers_var.get().strip(),
        )

    def _start_scrape(self) -> None:
        if self.is_running:
            return

        filters = self._collect_filters()
        error = filters.validate()
        if error:
            messagebox.showerror("Invalid Filters", error)
            return

        self._set_running_state(True)
        self.status_var.set("Preparing GitHub search...")
        self.progress_text_var.set("0 / 0")
        self.progress.configure(value=0, maximum=100)

        worker = threading.Thread(
            target=self._scrape_worker,
            args=(filters, self.token_var.get().strip()),
            daemon=True,
        )
        worker.start()

    def _scrape_worker(self, filters: SearchFilters, token: str) -> None:
        try:
            details = asyncio.run(scrape_users(filters, token, self._queue_progress))
            exported_count = export_profiles_to_csv(details, str(RESULT_CSV_PATH))
            self.root.after(0, lambda: self._handle_success(exported_count))
        except Exception as exc:  # noqa: BLE001
            error_message = str(exc)
            self.root.after(0, lambda: self._handle_error(error_message))

    def _queue_progress(self, current: int, total: int, message: str) -> None:
        self.root.after(0, lambda: self._update_progress(current, total, message))

    def _update_progress(self, current: int, total: int, message: str) -> None:
        maximum = total if total > 0 else 1
        self.progress.configure(maximum=maximum, value=current)
        self.progress_text_var.set(f"{current} / {total}")
        self.status_var.set(message)

    def _handle_success(self, exported_count: int) -> None:
        self._set_running_state(False)
        self.progress.configure(value=self.progress["maximum"])
        self.progress_text_var.set(f"{exported_count} appended")
        self.status_var.set("Export complete.")
        self.result_var.set(f"{exported_count} profiles appended\n{RESULT_CSV_PATH}")
        messagebox.showinfo(
            "Export Complete",
            f"Appended {exported_count} new profiles to:\n{RESULT_CSV_PATH}",
        )

    def _handle_error(self, error_message: str) -> None:
        self._set_running_state(False)
        self.status_var.set("The export could not be completed.")
        messagebox.showerror("Export Failed", error_message)

    def _set_running_state(self, is_running: bool) -> None:
        self.is_running = is_running
        self.start_button.configure(state="disabled" if is_running else "normal")

    def run(self) -> None:
        self.root.mainloop()


def launch_app() -> None:
    GitHubScraperApp().run()
