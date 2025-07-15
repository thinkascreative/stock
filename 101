import tkinter as tk
from tkinter import ttk
import pandas as pd
from datetime import datetime, timedelta
from nsepython import nsefetch
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

plt.style.use('dark_background')
STOCKS = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN",
          "HINDUNILVR", "BHARTIARTL", "AXISBANK", "KOTAKBANK", "WIPRO",
          "LT", "ASIANPAINT", "ITC", "MARUTI"]
REFRESH_MS = 3000  # 3 seconds

class StockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📈 Modern Stock Analyzer - NSE")
        self.root.geometry("1300x700")

        self.tabs = ttk.Notebook(root)
        self.pred_tab = ttk.Frame(self.tabs)
        self.live_tab = ttk.Frame(self.tabs)
        self.daily_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.pred_tab, text="📊 Predictions")
        self.tabs.add(self.live_tab, text="📡 Live Graph")
        self.tabs.add(self.daily_tab, text="🕔 Daily Performance")
        self.tabs.pack(fill="both", expand=True)

        self.build_prediction_ui()
        self.build_live_ui()
        self.build_daily_ui()
        self.load_predictions()
        self.load_daily_performance()
        self.update_live_graph_loop()

    def build_prediction_ui(self):
        cols = ("Stock", "Weekly %", "Suggestion")
        self.tree = ttk.Treeview(self.pred_tab, columns=cols, show="headings", height=18)
        for h, w in zip(cols, (150, 130, 150)):
            self.tree.heading(h, text=h); self.tree.column(h, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.top_lbl = tk.Label(self.pred_tab, text="", fg="white", bg="#1e1e1e", font=("Arial", 12, "bold"))
        self.top_lbl.pack(pady=10)
        ttk.Button(self.pred_tab, text="🔄 Refresh", command=self.load_predictions).pack(pady=6)

    def build_live_ui(self):
        top = ttk.Frame(self.live_tab); top.pack(fill="x", pady=5)
        self.sel = tk.StringVar(value=STOCKS[0])
        ttk.Combobox(top, values=STOCKS, textvariable=self.sel, state="readonly", width=12).pack(side="left", padx=6)
        tk.Button(top, text="🔍 Zoom In", command=lambda: self.zoom(0.8)).pack(side="left", padx=4)
        tk.Button(top, text="🔎 Zoom Out", command=lambda: self.zoom(1.25)).pack(side="left", padx=4)

        self.zoom_factor = 1.0
        self.price_buf = []

        self.fig, self.ax = plt.subplots(figsize=(10, 5))
        self.ax.set_facecolor("#1e1e1e"); self.ax.tick_params(colors="white")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.live_tab)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def build_daily_ui(self):
        cols = ("Stock", "Open", "Close", "Change %", "Profit")
        self.daily_tree = ttk.Treeview(self.daily_tab, columns=cols, show="headings", height=18)
        for h, w in zip(cols, (150, 130, 130, 130, 130)):
            self.daily_tree.heading(h, text=h); self.daily_tree.column(h, width=w, anchor="center")
        self.daily_tree.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Button(self.daily_tab, text="🔄 Refresh", command=self.load_daily_performance).pack(pady=6)

    def extract_price(self, obj):
        if isinstance(obj, dict):
            return float(obj.get("price", 0))
        return float(obj or 0)

    def load_predictions(self):
        self.tree.delete(*self.tree.get_children())
        rows = []
        for s in STOCKS:
            try:
                q = nsefetch(f"https://www.nseindia.com/api/quote-equity?symbol={s}")
                week_data = q.get("priceInfo", {}).get("weekHighLow", {})
                low_raw = week_data.get("weekLow") or week_data.get("min")
                high_raw = week_data.get("weekHigh") or week_data.get("max")
                low = self.extract_price(low_raw)
                high = self.extract_price(high_raw)

                if high > 0 and low > 0 and high > low:
                    pct = ((high - low) / low) * 100
                    if pct > 2:
                        sig = "✅ Buy"
                    elif pct > 0.5:
                        sig = "👀 Watch"
                    else:
                        sig = "❌ Avoid"
                    rows.append((s, f"{pct:+.2f}%", sig))
                else:
                    print(f"Invalid data for {s} → Low: {low}, High: {high}")
            except Exception as e:
                print(f"Prediction error for {s}: {e}")

        rows.sort(key=lambda x: float(x[1].replace("%", "")), reverse=True)
        for r in rows:
            self.tree.insert("", tk.END, values=r)
        best = ", ".join(r[0] for r in rows[:3]) if rows else "N/A"
        self.top_lbl.config(text=f"🏆 Top performers: {best}")

    def load_daily_performance(self):
        self.daily_tree.delete(*self.daily_tree.get_children())
        for s in STOCKS:
            try:
                q = nsefetch(f"https://www.nseindia.com/api/quote-equity?symbol={s}")
                price_info = q.get("priceInfo", {})
                open_price = float(price_info.get("open", 0))
                close_price = float(price_info.get("lastPrice", 0))
                if open_price > 0:
                    change_pct = ((close_price - open_price) / open_price) * 100
                    profit = close_price - open_price
                    emoji = "📈" if profit >= 0 else "📉"
                    result = f"{emoji} ₹{profit:.2f}"
                    self.daily_tree.insert("", tk.END, values=(s, f"₹{open_price:.2f}", f"₹{close_price:.2f}", f"{change_pct:+.2f}%", result))
            except Exception as e:
                print(f"Daily data error for {s}: {e}")

    def zoom(self, factor):
        self.zoom_factor *= factor

    def update_live_graph_loop(self):
        self.update_live_graph()
        self.root.after(REFRESH_MS, self.update_live_graph_loop)

    def update_live_graph(self):
        s = self.sel.get()
        try:
            q = nsefetch(f"https://www.nseindia.com/api/quote-equity?symbol={s}")
            price = float(q["priceInfo"]["lastPrice"])
            prev_close = float(q["priceInfo"]["previousClose"])
            now = datetime.now()
            self.price_buf.append((now, price))
            self.price_buf = self.price_buf[-300:]

            t, p = zip(*self.price_buf)
            up = p[-1] >= p[0]
            color = "#00ff5f" if up else "#ff4c4c"

            self.ax.clear()
            self.ax.set_facecolor("#1e1e1e")
            self.ax.grid(True, linestyle="--", alpha=0.2)

            self.ax.plot(t, p, color=color, lw=2)
            self.ax.fill_between(t, p, color=color, alpha=0.3)

            self.ax.plot(t[-1], p[-1], 'o', color='white', markersize=6)
            self.ax.text(t[-1], p[-1] + 0.5, f"₹{p[-1]:.2f}", color="white", fontsize=9,
                         ha='center', va='bottom',
                         bbox=dict(fc="#1e1e1e", ec="white", lw=0.5, boxstyle="round,pad=0.2"))

            self.ax.axhline(y=prev_close, color="white", linestyle="--", linewidth=1)
            self.ax.annotate(f"Prev ₹{prev_close:.2f}",
                             xy=(t[-1], prev_close),
                             xytext=(10, 0),
                             textcoords='offset points',
                             color='white',
                             fontsize=9,
                             va='center',
                             bbox=dict(boxstyle="round,pad=0.2", fc="#1e1e1e", ec="white", lw=0.5))

            rng = max(p) - min(p)
            if rng == 0: rng = p[-1] * 0.01
            pad = rng * 0.3 * self.zoom_factor
            self.ax.set_ylim(min(p) - pad, max(p) + pad)

            self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
            self.ax.tick_params(axis="x", colors="white")
            self.ax.tick_params(axis="y", colors="white")
            self.ax.set_xlabel("Time (IST)", color="white", labelpad=12)
            self.ax.set_ylabel("Price (₹)", color="white", labelpad=12)

            today = now.strftime("%d %b %Y")
            self.ax.set_title(f"{s} Live ₹{p[-1]:.2f}  •  {today}", color="white")

            self.canvas.draw()
        except Exception as e:
            print(f"Live graph error for {s}: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = StockApp(root)
    root.mainloop()
