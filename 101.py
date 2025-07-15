import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from nsepython import nsefetch

plt.style.use('dark_background')

STOCKS = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN",
          "HINDUNILVR", "BHARTIARTL", "AXISBANK", "KOTAKBANK", "WIPRO",
          "LT", "ASIANPAINT", "ITC", "MARUTI"]

# Price buffer to simulate live graph per session
if "price_buf" not in st.session_state:
    st.session_state.price_buf = {}

# Title
st.set_page_config(page_title="📈 Modern Stock Analyzer", layout="wide")
st.title("📈 Modern Stock Analyzer - NSE")

tabs = st.tabs(["📊 Predictions", "📡 Live Graph", "📅 Daily Performance"])

# ------------------ TAB 1: Predictions ------------------ #
with tabs[0]:
    st.subheader("Weekly Prediction (High vs Low Range)")
    data = []
    for s in STOCKS:
        try:
            q = nsefetch(f"https://www.nseindia.com/api/quote-equity?symbol={s}")
            week = q["priceInfo"]["weekHighLow"]
            low, high = float(week["weekLow"]), float(week["weekHigh"])
            pct = ((high - low) / low) * 100 if low else 0
            sig = "✅ Buy" if pct > 2 else ("👀 Watch" if pct > 0 else "❌ Avoid")
            data.append({"Stock": s, "Weekly %": f"{pct:+.2f}%", "Suggestion": sig})
        except Exception as e:
            data.append({"Stock": s, "Weekly %": "Error", "Suggestion": "N/A"})
    df = pd.DataFrame(data)
    df = df.sort_values(by="Weekly %", ascending=False)
    st.dataframe(df, use_container_width=True)
    top = ", ".join(df.head(3)["Stock"].tolist())
    st.markdown(f"🏆 **Top performers**: {top}")

# ------------------ TAB 2: Live Graph ------------------ #
with tabs[1]:
    st.subheader("📡 Live Stock Graph")
    selected = st.selectbox("Select Stock", STOCKS)

    # Fetch data
    try:
        q = nsefetch(f"https://www.nseindia.com/api/quote-equity?symbol={selected}")
        price = float(q["priceInfo"]["lastPrice"])
        prev_close = float(q["priceInfo"]["previousClose"])
        now = datetime.now()

        if selected not in st.session_state.price_buf:
            st.session_state.price_buf[selected] = []
        st.session_state.price_buf[selected].append((now, price))
        st.session_state.price_buf[selected] = st.session_state.price_buf[selected][-300:]

        # Graph
        buf = st.session_state.price_buf[selected]
        t, p = zip(*buf)
        up = p[-1] >= p[0]
        color = "#00ff5f" if up else "#ff4c4c"

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.set_facecolor("#1e1e1e")
        ax.grid(True, linestyle="--", alpha=0.3)
        ax.plot(t, p, color=color, lw=2)
        ax.fill_between(t, p, color=color, alpha=0.3)

        # Dot and price label
        ax.plot(t[-1], p[-1], 'o', color='white')
        ax.text(t[-1], p[-1]+0.5, f"₹{p[-1]:.2f}", color='white', fontsize=9,
                ha='center', bbox=dict(fc="#1e1e1e", ec="white", boxstyle="round,pad=0.2"))

        # Previous close line
        ax.axhline(y=prev_close, color="white", linestyle="--")
        ax.annotate(f"Prev ₹{prev_close:.2f}", xy=(t[-1], prev_close), xytext=(10, 0),
                    textcoords='offset points', color='white', fontsize=9,
                    bbox=dict(boxstyle="round,pad=0.2", fc="#1e1e1e", ec="white"))

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        ax.set_xlabel("Time (IST)", color="white")
        ax.set_ylabel("Price (₹)", color="white")
        ax.set_title(f"{selected} Live ₹{p[-1]:.2f} - {now.strftime('%d %b %Y')}", color="white")
        ax.tick_params(colors="white")
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Graph Error: {e}")

# ------------------ TAB 3: Daily Performance ------------------ #
with tabs[2]:
    st.subheader("📅 Daily Performance")
    rows = []
    for s in STOCKS:
        try:
            q = nsefetch(f"https://www.nseindia.com/api/quote-equity?symbol={s}")
            info = q["priceInfo"]
            open_price = float(info["open"])
            close_price = float(info["lastPrice"])
            net = close_price - open_price
            emoji = "📈" if net > 0 else "📉"
            rows.append({
                "Stock": s,
                "Open": f"₹{open_price:.2f}",
                "Close": f"₹{close_price:.2f}",
                "Net P/L": f"{emoji} ₹{net:+.2f}"
            })
        except:
            rows.append({"Stock": s, "Open": "-", "Close": "-", "Net P/L": "N/A"})
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

st.caption("success")
