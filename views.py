import customtkinter as ctk
from tkinter import messagebox
import resort_theme as theme
from controllers import BookingController, AdminController
from models import TableModel, RoomModel, find_user, create_user, BookingModel
from ctk_multiselect import CTkMultiSelectDropdown
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import utils
import tkinter as tk
import tkinter.ttk as ttk
from datetime import datetime, timedelta
from PIL import Image, ImageTk


# Global Constants for GUI Standardization
INPUT_WIDTH = 280
FRAME_PADX = 20
FRAME_PADY = 15


def style_ctk(widget, bg=None, fg=None):
    try:
        if bg is not None:
            widget.configure(fg_color=bg)
        if fg is not None:
            widget.configure(text_color=fg)
    except Exception:
        pass


# LOGIN WINDOW
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode('light')
        self.title('Resort Login')
        self.geometry('520x360')
        style_ctk(self, bg=theme.BG)
        self.build()

    def build(self):
        outer = ctk.CTkFrame(self, corner_radius=12, width=480, height=320)
        outer.place(relx=0.5, rely=0.5, anchor='center')
        style_ctk(outer, bg=theme.PANEL)

        header = ctk.CTkFrame(outer, height=80, corner_radius=10)
        header.pack(fill='x', padx=16, pady=(12, 8))
        style_ctk(header, bg=theme.CARD)

        ctk.CTkLabel(header, text='⛱', font=('Helvetica', 24)).place(x=34, y=18)
        ctk.CTkLabel(header, text='Welcome to Paradise Resort', font=theme.TITLE_FONT, text_color=theme.TEXT).place(
            x=100, y=20)

        body = ctk.CTkFrame(outer, corner_radius=8)
        body.pack(fill='both', expand=True, padx=16, pady=(4, 12))
        style_ctk(body, bg=theme.PANEL)

        ctk.CTkLabel(body, text='Username', text_color=theme.MUTED).pack(anchor='w', padx=8, pady=(6, 0))
        self.user_e = ctk.CTkEntry(body, width=340)
        self.user_e.pack(padx=8, pady=(4, 8))
        style_ctk(self.user_e, bg=theme.ENTRY, fg=theme.TEXT)

        ctk.CTkLabel(body, text='Password', text_color=theme.MUTED).pack(anchor='w', padx=8)
        self.pw_e = ctk.CTkEntry(body, width=340, show='*')
        self.pw_e.pack(padx=8, pady=(4, 12))
        style_ctk(self.pw_e, bg=theme.ENTRY, fg=theme.TEXT)

        btnf = ctk.CTkFrame(body, fg_color='transparent')
        btnf.pack(fill='x', padx=8, pady=(6, 0))

        login_btn = ctk.CTkButton(btnf, text='Login', command=self.login, width=120, corner_radius=8)
        login_btn.pack(padx=6)
        style_ctk(login_btn, bg=theme.PRIMARY, fg=theme.PANEL)

    def login(self):
        username = self.user_e.get().strip()
        password = self.pw_e.get().strip()
        if not username or not password:
            return messagebox.showwarning('Missing', 'Enter credentials')
        r = find_user(username)
        if not r:
            return messagebox.showerror('Failed', 'Unknown user')
        if utils.verify_password(password, r['salt'], r['password_hash']):
            self.withdraw()
            app = MainApp(self)
            app.protocol('WM_DELETE_WINDOW', lambda: (app.destroy(), self.deiconify()))
        else:
            return messagebox.showerror('Failed', 'Wrong password')



# MAIN APP WRAPPER
class MainApp(ctk.CTkToplevel):
    def __init__(self, login_window):
        super().__init__(login_window)
        self.title('Paradise Resort Management System')
        self.geometry('1200x760')
        style_ctk(self, bg=theme.BG)

        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=8)
        self.sidebar.pack(side='left', fill='y', padx=(12, 6), pady=12)
        style_ctk(self.sidebar, bg=theme.PANEL)

        ctk.CTkLabel(self.sidebar, text='Paradise Resort', font=('Helvetica', 18, 'bold'), justify='left',
                     text_color=theme.TEXT).pack(pady=(18, 6), padx=12, anchor='w')

        self.book_btn = ctk.CTkButton(
            self.sidebar,
            text='Booking',
            width=180,
            height=40,
            command=self.open_booking,
            corner_radius=20,
            fg_color=theme.PRIMARY,
            hover_color=theme.PRIMARY_HOVER,
            text_color=theme.PANEL,
            anchor="w"
        )
        self.book_btn.pack(pady=(8, 4), padx=16)

        self.admin_btn = ctk.CTkButton(
            self.sidebar,
            text='Admin',
            width=180,
            height=40,
            command=self.open_admin,
            corner_radius=20,
            fg_color=theme.PRIMARY_HOVER,
            hover_color=theme.PRIMARY,
            text_color=theme.PANEL,
            anchor="w"
        )
        self.admin_btn.pack(pady=(4, 8), padx=16)

        self.logout_btn = ctk.CTkButton(self.sidebar, text='Logout', width=180, command=self.logout, corner_radius=8)
        self.logout_btn.pack(side='bottom', pady=18, padx=12)
        style_ctk(self.logout_btn, bg=theme.PRIMARY_HOVER, fg=theme.PANEL)

        self.content = ctk.CTkFrame(self, corner_radius=8)
        self.content.pack(side='left', fill='both', expand=True, padx=(6, 12), pady=12)
        style_ctk(self.content, bg=theme.BG)

        self.open_booking()

    def open_booking(self):
        for w in self.content.winfo_children():
            w.destroy()
        style_ctk(self.book_btn, bg=theme.PRIMARY, fg=theme.PANEL)
        style_ctk(self.admin_btn, bg=theme.PRIMARY_HOVER, fg=theme.PANEL)
        BookingView(self.content, self.open_admin)

    def open_admin(self):
        for w in self.content.winfo_children():
            w.destroy()
        style_ctk(self.book_btn, bg=theme.PRIMARY_HOVER, fg=theme.PANEL)
        style_ctk(self.admin_btn, bg=theme.PRIMARY, fg=theme.PANEL)
        AdminView(self.content)

    def logout(self):
        self.destroy()


# BOOKING VIEW
class BookingView(ctk.CTkFrame):
    def __init__(self, parent, open_admin_cb):
        super().__init__(parent)
        self.parent = parent
        self.open_admin_cb = open_admin_cb
        self.ctrl = BookingController()

        self._tables = []
        self._rooms = []
        self.selected_tables = []
        self.selected_rooms = []

        self.configure(fg_color=theme.BG)
        self.pack(fill="both", expand=True)

        self.build()
        self.refresh_all()
        self.on_package_change()

        '''# ---------------------------
        # RESORT BACKGROUND IMAGE
        # ---------------------------
        try:
            bg = Image.open("assets/resort_bg.jpg")
            bg = bg.resize((1400, 800), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg)

            self.bg_label = tk.Label(self, image=self.bg_photo)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print("Background image load failed:", e)'''

    def build(self):
        # ====== TOP HEADER ======
        header = ctk.CTkFrame(self, corner_radius=12, fg_color=theme.PANEL)
        header.pack(fill="x", padx=24, pady=(18, 12))

        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)

        title_block = ctk.CTkFrame(header, fg_color="transparent")
        title_block.grid(row=0, column=0, sticky="w", padx=18, pady=10)

        ctk.CTkLabel(
            title_block,
            text="Booking",
            font=("Helvetica", 20, "bold"),
            text_color=theme.TEXT
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_block,
            text="Paradise Resort • Check-in & Facilities",
            font=("Helvetica", 11),
            text_color=theme.MUTED
        ).pack(anchor="w", pady=(2, 0))

        self.date_time_lbl = ctk.CTkLabel(
            header,
            text=datetime.now().strftime("Date: %Y-%m-%d %H:%M:%S"),
            text_color=theme.MUTED,
            font=("Helvetica", 11)
        )
        self.date_time_lbl.grid(row=0, column=1, sticky="e", padx=18)

        # ====== MAIN CONTENT (2 COLUMNS) ======
        main_content = ctk.CTkFrame(self, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        main_content.grid_columnconfigure(0, weight=3, uniform="col")
        main_content.grid_columnconfigure(1, weight=2, uniform="col")
        main_content.grid_rowconfigure(0, weight=1)

        # LEFT COLUMN (Guest + Stay)
        left_col = ctk.CTkFrame(main_content, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # --- Guest Information Card ---
        guest_frame = ctk.CTkFrame(
            left_col,
            fg_color=theme.CARD,
            corner_radius=10,
            border_width=1,
            border_color=theme.BORDER,
        )
        guest_frame.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            guest_frame,
            text="Guest Information",
            font=theme.TITLE_FONT,
            text_color=theme.TEXT
        ).pack(anchor="w", padx=20, pady=(14, 4))

        ctk.CTkLabel(
            guest_frame,
            text="Basic guest details for this booking.",
            text_color=theme.MUTED,
            font=("Helvetica", 10)
        ).pack(anchor="w", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            guest_frame,
            text="Guest Name",
            text_color=theme.MUTED
        ).pack(anchor="w", padx=20, pady=(0, 4))

        self.name = ctk.CTkEntry(
            guest_frame,
            fg_color=theme.ENTRY,
            text_color=theme.TEXT
        )
        self.name.pack(fill="x", padx=20, pady=(0, 12))

        counts_row = ctk.CTkFrame(guest_frame, fg_color="transparent")
        counts_row.pack(fill="x", padx=20, pady=(0, 16))

        ctk.CTkLabel(counts_row, text="Adults", text_color=theme.MUTED).pack(
            side="left", padx=(0, 4)
        )
        self.adults = ctk.CTkEntry(
            counts_row,
            width=70,
            fg_color=theme.ENTRY,
            text_color=theme.TEXT
        )
        self.adults.insert(0, "1")
        self.adults.pack(side="left")

        ctk.CTkLabel(counts_row, text="Children", text_color=theme.MUTED).pack(
            side="left", padx=(18, 4)
        )
        self.children_e = ctk.CTkEntry(
            counts_row,
            width=70,
            fg_color=theme.ENTRY,
            text_color=theme.TEXT
        )
        self.children_e.insert(0, "0")
        self.children_e.pack(side="left")

        self.adults.bind("<KeyRelease>", lambda e: self.update_totals_display())
        self.children_e.bind("<KeyRelease>", lambda e: self.update_totals_display())

        # --- Stay Details Card ---
        package_frame = ctk.CTkFrame(
            left_col,
            fg_color=theme.CARD,
            corner_radius=10,
            border_width=1,
            border_color=theme.BORDER,
        )
        package_frame.pack(fill="x")

        ctk.CTkLabel(
            package_frame,
            text="Stay Details",
            font=("Helvetica", 14, "bold"),
            text_color=theme.TEXT
        ).pack(anchor="w", padx=20, pady=(14, 4))

        ctk.CTkLabel(
            package_frame,
            text="Choose the package for this guest.",
            text_color=theme.MUTED,
            font=("Helvetica", 10)
        ).pack(anchor="w", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            package_frame,
            text="Select Package",
            text_color=theme.MUTED
        ).pack(anchor="w", padx=20, pady=(0, 4))

        self.package = ctk.CTkComboBox(
            package_frame,
            values=["Day Tour", "Overnight", "Complete Stay"],
            width=260,
        )
        self.package.set("Day Tour")
        self.package.pack(anchor="w", padx=20, pady=(0, 18))
        self.package.configure(command=lambda v: self.on_package_change())

        # RIGHT COLUMN (Facilities + Billing)
        right_col = ctk.CTkFrame(main_content, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # --- Facilities Card ---
        facilities_frame = ctk.CTkFrame(
            right_col,
            fg_color=theme.CARD,
            corner_radius=10,
            border_width=1,
            border_color=theme.BORDER,
        )
        facilities_frame.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            facilities_frame,
            text="Facilities",
            font=("Helvetica", 14, "bold"),
            text_color=theme.TEXT
        ).pack(anchor="w", padx=20, pady=(14, 4))

        ctk.CTkLabel(
            facilities_frame,
            text="Assign tables and rooms for this stay.",
            text_color=theme.MUTED,
            font=("Helvetica", 10)
        ).pack(anchor="w", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            facilities_frame,
            text="Select Tables",
            text_color=theme.MUTED
        ).pack(anchor="w", padx=20, pady=(0, 4))

        self.table_multi = CTkMultiSelectDropdown(
            facilities_frame,
            values=[],
            command=self.on_tables_selected,
            width=260,
        )
        self.table_multi.pack(anchor="w", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            facilities_frame,
            text="Select Rooms",
            text_color=theme.MUTED
        ).pack(anchor="w", padx=20, pady=(4, 4))

        self.room_multi = CTkMultiSelectDropdown(
            facilities_frame,
            values=[],
            command=self.on_rooms_selected,
            width=260,
        )
        self.room_multi.pack(anchor="w", padx=20, pady=(0, 14))

        # --- Billing Summary Card ---
        billing_frame = ctk.CTkFrame(
            right_col,
            fg_color=theme.CARD,
            corner_radius=10,
            border_width=1,
            border_color=theme.BORDER,
        )
        billing_frame.pack(fill="x")

        ctk.CTkLabel(
            billing_frame,
            text="Billing Summary",
            font=("Helvetica", 14, "bold"),
            text_color=theme.TEXT
        ).pack(anchor="w", padx=20, pady=(14, 4))

        ctk.CTkLabel(
            billing_frame,
            text="Automatic calculation of fees based on guests and facilities.",
            text_color=theme.MUTED,
            font=("Helvetica", 10),
            wraplength=260,
            justify="left",
        ).pack(anchor="w", padx=20, pady=(0, 10))

        fees_grid = ctk.CTkFrame(billing_frame, fg_color="transparent")
        fees_grid.pack(fill="x", padx=20, pady=(0, 6))

        ctk.CTkLabel(fees_grid, text="Table Fee", text_color=theme.MUTED).grid(
            row=0, column=0, sticky="w", pady=2
        )
        self.table_fee = ctk.CTkEntry(
            fees_grid,
            width=110,
            state="readonly",
            fg_color=theme.ENTRY,
        )
        self.table_fee.grid(row=0, column=1, sticky="e", pady=2)

        ctk.CTkLabel(fees_grid, text="Room Fee", text_color=theme.MUTED).grid(
            row=1, column=0, sticky="w", pady=2
        )
        self.room_fee = ctk.CTkEntry(
            fees_grid,
            width=110,
            state="readonly",
            fg_color=theme.ENTRY,
        )
        self.room_fee.grid(row=1, column=1, sticky="e", pady=2)

        ctk.CTkLabel(fees_grid, text="Entrance Fee", text_color=theme.MUTED).grid(
            row=2, column=0, sticky="w", pady=(4, 6)
        )
        self.entrance_lbl = ctk.CTkLabel(
            fees_grid,
            text="₱0.00",
            text_color=theme.TEXT,
            font=("Helvetica", 12, "bold"),
        )
        self.entrance_lbl.grid(row=2, column=1, sticky="e", pady=(4, 6))

        ttk.Separator(billing_frame, orient="horizontal").pack(
            fill="x", padx=20, pady=(6, 8)
        )

        total_row = ctk.CTkFrame(billing_frame, fg_color="transparent")
        total_row.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            total_row,
            text="TOTAL DUE",
            text_color=theme.PRIMARY,
            font=("Helvetica", 15, "bold"),
        ).pack(side="left")

        self.total = ctk.CTkEntry(
            total_row,
            width=120,
            state="readonly",
            fg_color=theme.ENTRY,
            font=("Helvetica", 15, "bold"),
            text_color=theme.PRIMARY,
        )
        self.total.pack(side="right")

        self.register_btn = ctk.CTkButton(
            billing_frame,
            text="Confirm Registration",
            command=self.submit_booking,
            height=42,
            fg_color=theme.PRIMARY,
            hover_color=theme.PRIMARY_HOVER,
            font=("Helvetica", 13, "bold"),
            corner_radius=10,
        )
        self.register_btn.pack(fill="x", padx=20, pady=(4, 18))

        self.update_clock()

    def update_clock(self):
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.date_time_lbl.configure(text=f"Date: {now_str}")
        except:
            pass
        self.after(1000, self.update_clock)

    def get_guest_counts(self):
        a = utils.try_int_or_zero(self.adults.get())
        c = utils.try_int_or_zero(self.children_e.get())
        return a, c, a + c

    def update_totals_display(self):
        a, c, guests = self.get_guest_counts()
        table_fee_total = sum(float(t['price']) for t in self.selected_tables) if self.selected_tables else 0.0
        room_fee_total = sum(float(r['price']) for r in self.selected_rooms) if self.selected_rooms else 0.0
        entrance = self.ctrl.calculate_entrance(a, c)
        total, _ = self.ctrl.calculate_total(a, c, entrance, table_fee_total, room_fee_total, self.package.get())

        self.table_fee.configure(state='normal')
        self.table_fee.delete(0, 'end')
        self.table_fee.insert(0, f"{table_fee_total:.2f}")
        self.table_fee.configure(state='readonly')

        self.room_fee.configure(state='normal')
        self.room_fee.delete(0, 'end')
        self.room_fee.insert(0, f"{room_fee_total:.2f}")
        self.room_fee.configure(state='readonly')

        self.entrance_lbl.configure(text=f"₱{entrance:.2f}")

        self.total.configure(state='normal')
        self.total.delete(0, 'end')
        self.total.insert(0, f"{total:.2f}")
        self.total.configure(state='readonly')

    def on_package_change(self):
        pkg = self.package.get()
        if pkg == 'Day Tour':
            self.selected_rooms = []
            try:
                self.room_multi.dropdown_btn.configure(state='disabled')
            except:
                pass
            self.room_fee.configure(state='normal')
            self.room_fee.delete(0, 'end')
            self.room_fee.insert(0, '0')
            self.room_fee.configure(state='readonly')
        else:
            try:
                self.room_multi.dropdown_btn.configure(state='normal')
            except:
                pass
        self.update_totals_display()

    def refresh_all(self):
        date_today = datetime.now().strftime('%Y-%m-%d')
        all_tables = TableModel.list_available()
        all_rooms = RoomModel.list_available()
        available_tables = [t for t in all_tables if not TableModel.is_table_booked(t['id'], date_today)]
        available_rooms = [r for r in all_rooms if not RoomModel.is_room_booked(r['id'], date_today)]

        table_names = [f"{t['name']} (cap {t['capacity']}) — ₱{t['price']}" for t in available_tables]
        room_names = [f"{r['name']} (cap {r['capacity']}) — ₱{r['price']}" for r in available_rooms]

        self.table_multi.set_values(table_names)
        self.room_multi.set_values(room_names)
        self._tables = available_tables
        self._rooms = available_rooms

    def on_tables_selected(self, labels):
        selected = []
        for lab in labels:
            name = lab.split(' (cap')[0].strip()
            for t in self._tables:
                if t['name'] == name:
                    selected.append(t)
                    break
        self.selected_tables = selected
        self.update_totals_display()

    def on_rooms_selected(self, labels):
        selected = []
        for lab in labels:
            name = lab.split(' (cap')[0].strip()
            for r in self._rooms:
                if r['name'] == name:
                    selected.append(r)
                    break
        self.selected_rooms = selected
        self.update_totals_display()

    def submit_booking(self):
        name = self.name.get().strip()
        if not name:
            return messagebox.showwarning('Missing', 'Enter guest name.')

        a, c, guests = self.get_guest_counts()
        if a <= 0 and c <= 0:
            return messagebox.showerror('Error', 'Adults or Children count must be greater than zero.')

        pkg = self.package.get()

        now = datetime.now()
        current_time = now.time()

        day_start = datetime.strptime("08:00", "%H:%M").time()
        day_end = datetime.strptime("18:00", "%H:%M").time()
        overnight_start = datetime.strptime("18:00", "%H:%M").time()
        complete_start = datetime.strptime("08:00", "%H:%M").time()

        # Day Tour: 8 AM – 6 PM
        if pkg == "Day Tour":
            if not (day_start <= current_time <= day_end):
                return messagebox.showerror(
                    "Invalid Time",
                    "Day Tour can only be booked from 8:00 AM to 6:00 PM."
                )

        # Overnight: 6 PM onward
        elif pkg == "Overnight":
            if current_time < overnight_start:
                return messagebox.showerror(
                    "Invalid Time",
                    "Overnight can only be booked from 6:00 PM onward."
                )

        # Complete Stay: 8 AM onward
        elif pkg == "Complete Stay":
            if current_time < complete_start:
                return messagebox.showerror(
                    "Invalid Time",
                    "Complete Stay can only be booked starting at 8:00 AM."
                )
        # ----------------------------------------------------


        date = datetime.now().strftime('%Y-%m-%d')
        table_ids = [t['id'] for t in self.selected_tables]
        room_ids = [r['id'] for r in self.selected_rooms]

        if pkg == 'Day Tour':
            if not table_ids:
                return messagebox.showwarning('Missing', 'Please select table(s).')
            cap = sum(t['capacity'] for t in self.selected_tables)
            if cap < guests:
                return messagebox.showwarning('Capacity', f"Tables capacity {cap} < guests {guests}.")
            room_ids = []
        else:
            if not room_ids:
                return messagebox.showwarning('Missing', 'Please select room(s).')
            cap = sum(r['capacity'] for r in self.selected_rooms)
            if cap < guests:
                return messagebox.showwarning('Capacity', f"Rooms capacity {cap} < guests {guests}.")

        ok, msg = self.ctrl.validate_availability(date, table_ids or None, room_ids or None)
        if not ok:
            return messagebox.showerror('Unavailable', msg)

        try:
            table_fee = float(self.table_fee.get() or 0)
            room_fee = float(self.room_fee.get() or 0)
            total = float(self.total.get() or 0)
        except:
            return messagebox.showerror('Error', 'Invalid fee totals.')

        try:
            self.ctrl.create_booking(name, date, a, c, pkg, table_ids or None, room_ids or None, table_fee, room_fee,
                                     total, total)
        except Exception as e:
            return messagebox.showerror('Error', str(e))

        messagebox.showinfo('OK', f'Checked-in {name} ({guests} guests)')
        self.name.delete(0, 'end')
        self.adults.delete(0, 'end')
        self.adults.insert(0, '1')
        self.children_e.delete(0, 'end')
        self.children_e.insert(0, '0')
        self.package.set('Day Tour')
        self.refresh_all()
        self.update_totals_display()


class CreateUserDialog(ctk.CTkToplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.title("Create New Account")
        self.geometry("400x450")
        self.transient(parent)
        self.grab_set()
        style_ctk(self, bg=theme.BG)
        self.build()

    def build(self):
        main = ctk.CTkFrame(self, corner_radius=10)
        main.pack(fill='both', expand=True, padx=15, pady=15)
        style_ctk(main, bg=theme.PANEL)
        ctk.CTkLabel(main, text="Create Admin Account", font=theme.TITLE_FONT, text_color=theme.TEXT).pack(
            pady=(20, 15))
        ctk.CTkLabel(main, text="Username", text_color=theme.MUTED).pack(anchor='w', padx=25)
        self.user_entry = ctk.CTkEntry(main, width=300)
        self.user_entry.pack(pady=(5, 15), padx=25, fill='x')
        style_ctk(self.user_entry, bg=theme.ENTRY, fg=theme.TEXT)
        ctk.CTkLabel(main, text="Password", text_color=theme.MUTED).pack(anchor='w', padx=25)
        self.pass_entry = ctk.CTkEntry(main, width=300, show="*")
        self.pass_entry.pack(pady=(5, 15), padx=25, fill='x')
        style_ctk(self.pass_entry, bg=theme.ENTRY, fg=theme.TEXT)
        ctk.CTkLabel(main, text="Confirm Password", text_color=theme.MUTED).pack(anchor='w', padx=25)
        self.confirm_entry = ctk.CTkEntry(main, width=300, show="*")
        self.confirm_entry.pack(pady=(5, 10), padx=25, fill='x')
        style_ctk(self.confirm_entry, bg=theme.ENTRY, fg=theme.TEXT)
        req_text = "Password must consists of : \n• Minimum of 8 characters\n• UPPERCASE letters\n• Lowercase letters\n• Numbers"
        ctk.CTkLabel(main, text=req_text, text_color=theme.MUTED, font=("Helvetica", 10), justify="left").pack(
            anchor='w', padx=25, pady=(0, 15))
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(side='bottom', fill='x', padx=20, pady=10)
        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy, width=100, fg_color=theme.BORDER,
                                   text_color=theme.TEXT)
        cancel_btn.pack(side='left', padx=5)
        create_btn = ctk.CTkButton(btn_frame, text="Create Account", command=self.submit, width=140)
        create_btn.pack(side='right', padx=5)
        style_ctk(create_btn, bg=theme.PRIMARY, fg=theme.PANEL)

    def submit(self):
        user = self.user_entry.get().strip()
        pw = self.pass_entry.get().strip()
        confirm = self.confirm_entry.get().strip()
        if pw != confirm:
            messagebox.showerror("Error", "Passwords do not match.")
            return
        success, msg = self.controller.create_account(user, pw)
        if success:
            messagebox.showinfo("Success", msg)
            self.destroy()
        else:
            messagebox.showerror("Failed", msg)


# ADMIN VIEW (FIXED)
class AdminView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.ctrl = AdminController()  # <--- Corrected Here

        self.after(500, self.check_for_overdue_warning)
        self.graph_frame = None
        self.canvas_widget = None
        self.graph_visible = False
        self.filter_var = ctk.StringVar(value="Current Guests")
        self.search_var = ctk.StringVar()
        self.graph_type_var = ctk.StringVar(value="Daily")

        self.pack(fill='both', expand=True)
        style_ctk(self, bg=theme.BG)
        self.build()
        self.load_bookings()

    def _build_top_controls(self):
        top = ctk.CTkFrame(self, fg_color=theme.PANEL, corner_radius=12)
        top.pack(fill='x', pady=(10, 8), padx=10)

        # Header row
        header_row = ctk.CTkFrame(top, fg_color="transparent")
        header_row.pack(fill='x', padx=18, pady=(12, 6))

        title = ctk.CTkLabel(
            header_row,
            text='Admin Dashboard',
            font=('Helvetica', 20, 'bold'),
            text_color=theme.TEXT
        )
        title.pack(side='left')

        btn_row = ctk.CTkFrame(header_row, fg_color="transparent")
        btn_row.pack(side='right')

        checkout_btn = ctk.CTkButton(
            btn_row,
            text='Checkout Selection',
            width=150,
            fg_color=theme.PRIMARY,
            hover_color=theme.PRIMARY_HOVER,
            text_color=theme.PANEL,
            corner_radius=10,
            command=self.checkout_selected
        )
        checkout_btn.pack(side='left', padx=4)

        create_user_btn = ctk.CTkButton(
            btn_row,
            text='Create New Account',
            width=150,
            fg_color=theme.SECONDARY,
            text_color=theme.PANEL,
            corner_radius=10,
            command=self.open_create_account
        )
        create_user_btn.pack(side='left', padx=4)

        # Controls row
        ctrl_row = ctk.CTkFrame(top, fg_color="transparent")
        ctrl_row.pack(fill='x', padx=18, pady=(4, 12))

        search_entry = ctk.CTkEntry(
            ctrl_row,
            placeholder_text="Search guest name...",
            width=260,
            textvariable=self.search_var
        )
        search_entry.pack(side='left')
        search_entry.bind("<KeyRelease>", lambda e: self.load_bookings())

        filter_seg = ctk.CTkSegmentedButton(
            ctrl_row,
            values=["Current Guests", "Today's Arrivals", "All History"],
            variable=self.filter_var,
            command=lambda v: self.load_bookings()
        )
        filter_seg.pack(side='left', padx=16)

        self.graph_btn = ctk.CTkButton(
            ctrl_row,
            text='Show Graph',
            command=self.toggle_daily_graph,
            fg_color=theme.PRIMARY,
            width=120,
            corner_radius=10
        )
        self.graph_btn.pack(side='right')


    def _build_table_section(self, main_content):
        table_card = ctk.CTkFrame(
            main_content,
            fg_color=theme.CARD,
            corner_radius=10,
            border_width=1,
            border_color=theme.BORDER
        )
        table_card.grid(row=0, column=0, sticky='nsew', padx=(0, 8))

        title_row = ctk.CTkFrame(table_card, fg_color="transparent")
        title_row.pack(fill='x', padx=12, pady=(10, 4))

        ctk.CTkLabel(
            title_row,
            text="Guest List",
            font=("Helvetica", 13, "bold"),
            text_color=theme.TEXT
        ).pack(side="left")

        ctk.CTkLabel(
            title_row,
            text="Double-click a row to inspect, use filters above to narrow results.",
            font=("Helvetica", 10),
            text_color=theme.MUTED
        ).pack(side="left", padx=8)

        table_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        table_frame.pack(fill='both', expand=True, padx=8, pady=(4, 8))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview.Heading",
            background=theme.PRIMARY,
            foreground="white",
            relief="flat",
            font=("Helvetica", 11, "bold"),
        )
        style.map("Treeview.Heading", background=[('active', theme.PRIMARY_HOVER)])

        style.configure(
            "Treeview",
            background="white",
            fieldbackground="white",
            foreground=theme.TEXT,
            rowheight=34,
            font=("Helvetica", 10),
            borderwidth=0,
        )
        style.map(
            "Treeview",
            background=[('selected', theme.SECONDARY)],
            foreground=[('selected', 'white')],
        )

        columns = [
            "id", "guest_name", "booking_date", "checkin_time",
            "adults", "children", "guest_count", "package",
            "table_id", "room_id", "total_amount", "amount_paid", "status"
        ]

        vsb = ttk.Scrollbar(table_frame, orient='vertical')
        hsb = ttk.Scrollbar(table_frame, orient='horizontal')

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            selectmode="browse"
        )

        self.tree.tag_configure('overdue', background='#ffe5e5', foreground='#b00000')
        self.tree.tag_configure('evenrow', background=theme.BG)
        self.tree.tag_configure('oddrow', background="white")

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        self.tree.pack(fill='both', expand=True)

        for col in columns:
            self.tree.heading(col, text=col.replace('_', ' ').title())
            self.tree.column(col, width=100, anchor='center')

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("guest_name", width=180, anchor="w")
        self.tree.column("booking_date", width=110)
        self.tree.column("status", width=110)

    def _build_graph_section(self, main_content):
        self.graph_frame = ctk.CTkFrame(
            main_content,
            fg_color=theme.CARD,
            corner_radius=10,
            border_width=1,
            border_color=theme.BORDER
        )
        self.graph_frame.grid(row=0, column=1, sticky='nsew', padx=(8, 0))

        ctk.CTkLabel(
            self.graph_frame,
            text="Graph Area\n\nPress 'Show Graph' to view guest statistics.",
            text_color=theme.MUTED,
            justify="center"
        ).pack(expand=True, padx=10, pady=10)

    def build(self):
        self._build_top_controls()
        main_content = ctk.CTkFrame(self, fg_color='transparent')
        main_content.pack(fill='both', expand=True, padx=10, pady=10)
        style_ctk(main_content, bg=theme.BG)
        main_content.grid_columnconfigure(0, weight=3)
        main_content.grid_columnconfigure(1, weight=2)
        main_content.grid_rowconfigure(0, weight=1)
        self._build_table_section(main_content)
        self._build_graph_section(main_content)

    def open_create_account(self):
        CreateUserDialog(self, self.ctrl)

    def checkout_selected(self):
        item = self.tree.selection()
        if not item:
            return messagebox.showwarning('No Selection', 'Select a booking first.')
        values = self.tree.item(item, 'values')
        bid = int(values[0])
        status = values[12]
        if status != 'checked-in':
            return messagebox.showerror('Invalid', 'Only checked-in bookings can be checked out.')
        if messagebox.askyesno("Confirm", f"Checkout guest '{values[1]}' (ID: {bid})?"):
            self.ctrl.checkout(bid)
            messagebox.showinfo('OK', 'Guest checked out successfully.')
            self.load_bookings()

    def check_for_overdue_warning(self):
        try:
            overdue_ids = self.ctrl.check_auto_checkout()
        except Exception as e:
            print(f"Error checking for overdue guests: {e}")
            return
        if overdue_ids:
            id_list = ", ".join(map(str, overdue_ids))
            messagebox.showwarning("ACTION REQUIRED: Overdue Checkouts Detected!",
                                   f"🚨 There are {len(overdue_ids)} Overnight booking(s) past the 8 AM cutoff.\nBooking IDs: {id_list}\nPlease review the 'Current Guests' filter and manually check them out.")

    def check_overdue(self, r):
        if r['status'] != 'checked-in':
            return False

        if r['package'].lower() not in ('overnight', 'complete stay'):
            return False

        try:
            b_date = datetime.strptime(r['booking_date'], "%Y-%m-%d").date()
            deadline = datetime.combine(b_date + timedelta(days=1), datetime.min.time().replace(hour=8))
            return datetime.now() >= deadline
        except Exception:
            return False

    def load_bookings(self, *args):
        all_rows = self.ctrl.report_all()
        search_txt = self.search_var.get().lower()
        mode = self.filter_var.get()
        today_str = datetime.now().strftime("%Y-%m-%d")
        self.tree.delete(*self.tree.get_children())
        for r in all_rows:
            g_name = r['guest_name'].lower()
            if search_txt and search_txt not in g_name: continue
            if mode == "Current Guests" and r['status'] != 'checked-in':
                continue
            elif mode == "Today's Arrivals" and r['booking_date'] != today_str:
                continue

            row_tag = 'evenrow' if len(self.tree.get_children()) % 2 == 0 else 'oddrow'
            if self.check_overdue(r):
                tags = ('overdue',)
            else:
                tags = (row_tag,)

            checkin_time = r['checkin_time'] if r['checkin_time'] else ""
            guest_count = r['guest_count']
            table_id = r['table_id'] if r['table_id'] else "None"
            room_id = r['room_id'] if r['room_id'] else "None"

            self.tree.insert('', 'end', values=[r['id'], r['guest_name'], r['booking_date'], checkin_time, r['adults'],
                                                r['children'], guest_count, r['package'], table_id, room_id,
                                                r['total_amount'], r['amount_paid'], r['status']], tags=tags)

    def toggle_daily_graph(self):
        if self.graph_visible:
            if self.canvas_widget:
                self.canvas_widget.destroy()
                self.canvas_widget = None
            for w in self.graph_frame.winfo_children(): w.destroy()
            ctk.CTkLabel(self.graph_frame, text="Graph Area\n(Press 'Show Graph' to view)",
                         text_color=theme.MUTED).pack(expand=True)
            self.graph_btn.configure(text='Show Graph')
            self.graph_visible = False
        else:
            for w in self.graph_frame.winfo_children(): w.destroy()
            ctrl_frame = ctk.CTkFrame(self.graph_frame, fg_color="transparent")
            ctrl_frame.pack(fill='x', pady=5)
            seg = ctk.CTkSegmentedButton(ctrl_frame, values=["Daily", "Monthly"], variable=self.graph_type_var,
                                         command=lambda v: self.open_graph())
            seg.pack(pady=5)
            self.open_graph()
            self.graph_btn.configure(text='Hide Graph')
            self.graph_visible = True

    def _create_summary_plot(self, df, mode="Daily"):
        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)
        for col in ('adults', 'children'):
            if col not in df.columns: df[col] = 0
        df['adults'] = pd.to_numeric(df['adults'], errors='coerce').fillna(0)
        df['children'] = pd.to_numeric(df['children'], errors='coerce').fillna(0)
        df['guest_count'] = df['adults'] + df['children']
        df['booking_date'] = pd.to_datetime(df['booking_date'])

        if mode == "Monthly":
            df['period'] = df['booking_date'].dt.to_period('M').astype(str)
            summary = df.groupby('period')['guest_count'].sum().reset_index()
            x_col = 'period'
            title = "Total Guests Per Month"
            xlabel = "Month"
        else:
            summary = df.groupby('booking_date')['guest_count'].sum().reset_index()
            summary = summary.sort_values(by='booking_date')
            summary['date_str'] = summary['booking_date'].dt.strftime('%m-%d')
            x_col = 'date_str'
            title = "Guests Checked In Per Day"
            xlabel = "Date"

        ax.bar(summary[x_col], summary['guest_count'], color=theme.PRIMARY)
        ax.set_title(title, fontsize=12, fontweight='bold', color=theme.TEXT)
        ax.set_xlabel(xlabel, color=theme.MUTED)
        ax.set_ylabel('Total Guests', color=theme.MUTED)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        fig.set_facecolor(theme.PANEL)
        ax.set_facecolor(theme.CARD)
        fig.autofmt_xdate(rotation=45)
        return fig

    def open_graph(self):
        rows = self.ctrl.report_all()
        if not rows: return
        try:
            clean_rows = [dict(r) for r in rows]
            df = pd.DataFrame(clean_rows)
        except Exception:
            return
        mode = self.graph_type_var.get()
        fig = self._create_summary_plot(df, mode)
        if self.canvas_widget: self.canvas_widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        self.canvas_widget = canvas.get_tk_widget()
        self.canvas_widget.pack(fill='both', expand=True, padx=5, pady=5)