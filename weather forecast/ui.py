import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
import io
import config
from api import WeatherAPI

class WeatherUI:
    def __init__(self, root):
        self.root = root
        self.api = WeatherAPI()
        self.setup_ui()
        self.current_city = "Delhi"
        self.load_weather(self.current_city)

    def setup_ui(self):
        self.root.title(config.APP_TITLE)
        self.root.geometry("500x700")
        self.root.configure(bg=config.BG_COLOR)
        # Prevent resizing if desired
        # self.root.resizable(False, False)

        # Main Scrollable Container (Optional, but good for smaller screens)
        self.main_frame = tk.Frame(self.root, bg=config.BG_COLOR)
        self.main_frame.pack(expand=True, fill="both", padx=30, pady=30)

        # Header Search Area
        self.search_frame = tk.Frame(self.main_frame, bg=config.BG_COLOR)
        self.search_frame.pack(fill="x", pady=(0, 20))

        self.city_entry = tk.Entry(
            self.search_frame, 
            bg=config.CARD_COLOR, 
            fg=config.TEXT_COLOR,
            insertbackground=config.TEXT_COLOR,
            font=("Segoe UI", 12),
            relief="flat",
            border=0
        )
        self.city_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))
        self.city_entry.insert(0, "Search City...")
        self.city_entry.bind("<FocusIn>", lambda e: self.city_entry.delete(0, "end") if self.city_entry.get() == "Search City..." else None)
        self.city_entry.bind("<KeyRelease>", self.on_key_release)
        
        # Suggestions Dropdown (Listbox)
        self.suggestions_list = tk.Listbox(
            self.root, 
            bg=config.CARD_COLOR, 
            fg=config.TEXT_COLOR,
            selectbackground=config.ACCENT_COLOR,
            selectforeground=config.BG_COLOR,
            font=("Segoe UI", 10),
            relief="flat",
            borderwidth=1,
            highlightthickness=0,
            activestyle="none"
        )
        self.suggestions_list.bind("<<ListboxSelect>>", self.on_suggestion_select)
        self.suggestions_list.bind("<Return>", self.on_suggestion_select)
        self.suggestions_data = []
        self.hide_suggestions()

        self.search_btn = tk.Button(
            self.search_frame,
            text="Search",
            bg=config.ACCENT_COLOR,
            fg=config.BG_COLOR,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            command=self.on_search,
            cursor="hand2"
        )
        self.search_btn.pack(side="right", ipady=5, ipadx=15)

        self.loc_btn = tk.Button(
            self.search_frame,
            text="📍",
            bg=config.CARD_COLOR,
            fg=config.ACCENT_COLOR,
            font=("Segoe UI", 12),
            relief="flat",
            command=self.on_auto_locate,
            cursor="hand2"
        )
        self.loc_btn.pack(side="right", padx=5)

        # Current Weather Card
        self.weather_card = tk.Frame(self.main_frame, bg=config.CARD_COLOR, padx=20, pady=20)
        self.weather_card.pack(fill="both", pady=10)

        self.location_lbl = tk.Label(
            self.weather_card,
            text="---",
            bg=config.CARD_COLOR,
            fg=config.SECONDARY_TEXT,
            font=("Segoe UI", 12)
        )
        self.location_lbl.pack(anchor="w")

        self.main_temp_lbl = tk.Label(
            self.weather_card,
            text="--°C",
            bg=config.CARD_COLOR,
            fg=config.TEXT_COLOR,
            font=("Segoe UI Black", 48)
        )
        self.main_temp_lbl.pack(pady=10)

        self.icon_lbl = tk.Label(self.weather_card, bg=config.CARD_COLOR)
        self.icon_lbl.pack()

        self.desc_lbl = tk.Label(
            self.weather_card,
            text="---",
            bg=config.CARD_COLOR,
            fg=config.ACCENT_COLOR,
            font=("Segoe UI", 14, "bold"),
            wraplength=350
        )
        self.desc_lbl.pack()

        # Stats Grid (Humidity, Wind, etc)
        self.stats_frame = tk.Frame(self.weather_card, bg=config.CARD_COLOR)
        self.stats_frame.pack(fill="x", pady=20)

        self.h_cont, self.humidity_lbl = self.create_stat_label(self.stats_frame, "Humidity", "--%")
        self.h_cont.grid(row=0, column=0, sticky="ew", padx=10)

        self.w_cont, self.wind_lbl = self.create_stat_label(self.stats_frame, "Wind Speed", "-- km/h")
        self.w_cont.grid(row=0, column=1, sticky="ew", padx=10)

        self.stats_frame.grid_columnconfigure((0, 1), weight=1)

        # Forecast Title
        tk.Label(
            self.main_frame,
            text="5-Day Forecast",
            bg=config.BG_COLOR,
            fg=config.TEXT_COLOR,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(20, 10))

        # Forecast Container
        self.forecast_outer = tk.Frame(self.main_frame, bg=config.BG_COLOR)
        self.forecast_outer.pack(fill="x")
        self.forecast_items = [] # Store references to update

        for i in range(5):
            f_frame = tk.Frame(self.forecast_outer, bg=config.CARD_COLOR, padx=10, pady=10)
            f_frame.pack(side="left", fill="both", expand=True, padx=2)
            
            day_lbl = tk.Label(f_frame, text="Day", bg=config.CARD_COLOR, fg=config.SECONDARY_TEXT, font=("Segoe UI", 8))
            day_lbl.pack()
            
            icon_lbl = tk.Label(f_frame, bg=config.CARD_COLOR)
            icon_lbl.pack()
            
            temp_lbl = tk.Label(f_frame, text="--°C", bg=config.CARD_COLOR, fg=config.TEXT_COLOR, font=("Segoe UI", 10, "bold"))
            temp_lbl.pack()
            
            self.forecast_items.append({"day": day_lbl, "icon": icon_lbl, "temp": temp_lbl})

        self.root.bind('<Return>', lambda e: self.on_search())
        self.root.bind('<Button-1>', self.hide_suggestions_on_click)

    def hide_suggestions_on_click(self, event):
        if event.widget != self.suggestions_list and event.widget != self.city_entry:
            self.hide_suggestions()

    def on_key_release(self, event):
        if event.keysym == "Down":
            if self.suggestions_list.winfo_ismapped():
                self.suggestions_list.focus_set()
                self.suggestions_list.selection_set(0)
            return
            
        if event.keysym in ("Up", "Return"):
            return
            
        query = self.city_entry.get().strip()
        if len(query) < 2:
            self.hide_suggestions()
            return
            
        # Optional: Debounce or throttle API calls (for simplicity, we'll call it directly)
        self.suggestions_data = self.api.get_location_suggestions(query)
        if self.suggestions_data:
            self.show_suggestions()
        else:
            self.hide_suggestions()

    def show_suggestions(self):
        self.suggestions_list.delete(0, tk.END)
        for sug in self.suggestions_data:
            self.suggestions_list.insert(tk.END, sug["display"])
        
        # Position the listbox exactly below the entry
        x = self.city_entry.winfo_rootx() - self.root.winfo_rootx()
        y = self.city_entry.winfo_rooty() - self.root.winfo_rooty() + self.city_entry.winfo_height()
        w = self.city_entry.winfo_width()
        
        self.suggestions_list.place(x=x, y=y, width=w, height=len(self.suggestions_data) * 25 + 5)
        self.suggestions_list.lift()

    def hide_suggestions(self):
        self.suggestions_list.place_forget()

    def on_suggestion_select(self, event):
        selected_index = self.suggestions_list.curselection()
        if selected_index:
            suggestion = self.suggestions_data[selected_index[0]]
            self.city_entry.delete(0, tk.END)
            self.city_entry.insert(0, suggestion["city"])
            self.hide_suggestions()
            self.on_search()

    def create_stat_label(self, parent, label_text, value_text):
        container = tk.Frame(parent, bg=config.CARD_COLOR)
        tk.Label(container, text=label_text, bg=config.CARD_COLOR, fg=config.SECONDARY_TEXT, font=("Segoe UI", 9)).pack()
        value_lbl = tk.Label(container, text=value_text, bg=config.CARD_COLOR, fg=config.TEXT_COLOR, font=("Segoe UI", 12, "bold"))
        value_lbl.pack()
        return container, value_lbl

    def on_auto_locate(self):
        city = self.api.get_auto_location()
        if city:
            self.load_weather(city)
        else:
            messagebox.showwarning("Warning", "Could not detect location automatically.")

    def on_search(self):
        city = self.city_entry.get().strip()
        if city and city != "Search City...":
            self.load_weather(city)

    def load_weather(self, city):
        try:
            # Current Weather
            current_data = self.api.get_current_weather(city)
            self.update_current_ui(current_data)
            
            # Forecast (if possible)
            try:
                forecast_data = self.api.get_forecast(city)
                self.update_forecast_ui(forecast_data)
            except:
                pass # Silent fail for forecast if API restricted
                
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_current_ui(self, data):
        self.location_lbl.config(text=f"{data['name']}, {data['sys']['country']}")
        self.main_temp_lbl.config(text=f"{round(data['main']['temp'])}°C")
        self.desc_lbl.config(text=data['weather'][0]['description'].capitalize())
        self.humidity_lbl.config(text=f"{data['main']['humidity']}%")
        self.wind_lbl.config(text=f"{data['wind']['speed']} m/s")

        # Load icon
        icon_code = data['weather'][0]['icon']
        self.set_icon(self.icon_lbl, icon_code, (120, 120))

    def update_forecast_ui(self, data):
        # OWM forecast is every 3 hours. Let's take one per day (around 12:00)
        daily_list = []
        for entry in data['list']:
            if "12:00:00" in entry['dt_txt']:
                daily_list.append(entry)
        
        # If we have less than 5 (due to current time), just take first few unique days
        if len(daily_list) < 5:
            days_seen = set()
            daily_list = []
            for entry in data['list']:
                day = entry['dt_txt'].split()[0]
                if day not in days_seen:
                    daily_list.append(entry)
                    days_seen.add(day)
                if len(daily_list) == 5: break

        import datetime
        for idx, entry in enumerate(daily_list[:5]):
            dt = datetime.datetime.strptime(entry['dt_txt'], "%Y-%m-%d %H:%M:%S")
            day_name = dt.strftime("%a")
            temp = round(entry['main']['temp'])
            icon_code = entry['weather'][0]['icon']
            
            self.forecast_items[idx]["day"].config(text=day_name)
            self.forecast_items[idx]["temp"].config(text=f"{temp}°C")
            self.set_icon(self.forecast_items[idx]["icon"], icon_code, (40, 40))

    def set_icon(self, label, icon_code, size):
        icon_url = self.api.get_icon_url(icon_code)
        try:
            resp = requests.get(icon_url, timeout=5)
            img = Image.open(io.BytesIO(resp.content))
            # Compatibility fix for older Pillow versions
            resample_method = getattr(Image, 'Resampling', Image).LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS
            img = img.resize(size, resample_method)
            photo = ImageTk.PhotoImage(img)
            label.config(image=photo)
            label.image = photo 
        except:
            pass
