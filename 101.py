# modern_stock_gui.py
# ----------------------------------------------------------
# Modern Stock Analyzer – NSE (Streamlit desktop version)
# Tabs:
#   1. Weekly Predictions with Buy/Watch/Avoid
#   2. Manual‑refresh Live Graph (zoom, shaded area, crash detect)
#   3. Daily Performance snapshot
# ----------------------------------------------------------

import streamlit as st
import pandas as pd
from datetime import datetime
from nsepython import nsefetch
import plotly.graph_objects as go

# ─────────────────────────
#  USER CONFIGURABLE LIST
# ─────────────────────────
STOCKS = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN",
    "HINDUNILVR", "BHARTIARTL", "AXISBANK", "KOTAKBANK", "WIPRO",
    "LT", "ASIANPAINT", "ITC", "MARUTI"
]

# Session‑level storage for live‑price buffers
if "price_buf" not in st.session_state:
    st.session_state.price_buf = {}   # {symbol: [(timestamp, price), ...]}

# ─────────────────────────
#  PAGE SETUP
# ─────────────────────────
st.set_page_config(page_title="📈 Modern Stock Analyzer", layout="wide")
st.title("📈 Modern Stock Analyzer – NSE")

tabs = st.tabs(["📊 Predictions", "📡 Live Graph", "📅 Daily Performance"])

# ==========================================================
# TAB 1 : WEEKLY PREDICTIONS
# ==========================================================
with tabs[0]:
    st.subheader("Weekly Prediction (High vs Low Range)")

    rows = []
    for s in STOCKS:
        try:
            q = nsefetch(f"https://www.nseindia.com/api/quote-equity?symbol={s}")
            week = q["priceInfo"]["weekHighLow"]

            # NSE API now returns min/max
            low  = float(str(week["min"]).replace(",", ""))
            high = float(str(week["max"]).replace(",", ""))

            pct = ((high - low) / low) * 100 if low else 0.0
            sig = "✅ Buy" if pct > 2 else ("👀 Watch" if pct > 0 else "❌ Avoid")

            rows.append({"Stock": s, "Weekly %": f"{pct:+.2f}%", "Suggestion": sig})
        except Exception:
            rows.append({"Stock": s, "Weekly %": "Error", "Suggestion": "N/A"})

    df = pd.DataFrame(rows)
    df = df[df["Weekly %"].str.contains("%")]
    df = df.sort_values(
        by="Weekly %",
        ascending=False,
        key=lambda c: c.str.replace("%", "").astype(float),
        ignore_index=True
    )

    st.dataframe(df, use_container_width=True)
    top3 = ", ".join(df.head(3)["Stock"].tolist())
    st.markdown(f"🏆 **Top performers**: {top3}")

# ==========================================================
# TAB 2 : LIVE GRAPH (manual refresh, no blinking)
# ==========================================================
with tabs[1]:
    st.subheader("📡 Live Stock Graph")

    selected = st.selectbox("Select Stock", STOCKS, key="live_stock_select")

    # manual refresh button
    refresh_clicked = st.button("🔄 Refresh Price", key="refresh_btn")

    # Only plot when user presses refresh or first time load
    if refresh_clicked or selected not in st.session_state.price_buf:
        try:
            q = nsefetch(f"https://www.nseindia.com/api/quote-equity?symbol={selected}")
            price      = float(q["priceInfo"]["lastPrice"])
            prev_close = float(q["priceInfo"]["previousClose"])
            now        = datetime.now()

            # update buffer
            buf = st.session_state.price_buf.setdefault(selected, [])
            buf.append((now, price))
            buf[:] = buf[-300:]          # keep last 300 points (~15 min @ 3 s)

            times, prices = zip(*buf)
            uptrend = prices[-1] >= prices[0]
            line_color  = "lime" if uptrend else "red"
            area_color  = "rgba(0,255,0,0.20)" if uptrend else "rgba(255,0,0,0.20)"
            # crash detection: >3 % drop from max in buffer
            crash = prices[-1] < max(prices) * 0.97
            if crash:
                line_color = "red"
                area_color = "rgba(255,0,0,0.35)"

            # Build figure
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=times,
                y=prices,
                mode="lines",
                line=dict(color=line_color, width=2),
                fill="tozeroy",
                fillcolor=area_color,
                name=selected
            ))

            # Dot + price label
            fig.add_trace(go.Scatter(
                x=[times[-1]],
                y=[prices[-1]],
                mode="markers+text",
                marker=dict(size=8, color="white"),
                text=[f"₹{prices[-1]:.2f}"],
                textposition="top center",
                showlegend=False
            ))

            # Previous close dashed
            fig.add_hline(
                y=prev_close,
                line_dash="dash",
                line_color="white",
                annotation_text=f"Prev ₹{prev_close:.2f}",
                annotation_position="bottom right"
            )

            fig.update_layout(
                title=f"{selected} Live ₹{prices[-1]:.2f} – {now.strftime('%d %b %Y')}",
                plot_bgcolor="#1e1e1e",
                paper_bgcolor="#1e1e1e",
                font=dict(color="white"),
                hovermode="x unified",
                dragmode="zoom",
                xaxis_title="Time (IST)",
                yaxis_title="Price (₹)"
            )

            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Graph Error: {e}")

    else:
        st.info("Hit the 🔄 **Refresh Price** button to load data.")

# ==========================================================
# TAB 3 : DAILY PERFORMANCE
# ==========================================================
with tabs[2]:
    st.subheader("📅 Daily Performance")

    perf_rows = []
    for s in STOCKS:
        try:
            q = nsefetch(f"https://www.nseindia.com/api/quote-equity?symbol={s}")
            info = q["priceInfo"]
            open_price  = float(info["open"])
            close_price = float(info["lastPrice"])
            net         = close_price - open_price
            emoji       = "📈" if net > 0 else "📉"
            perf_rows.append({
                "Stock": s,
                "Open":  f"₹{open_price:.2f}",
                "Close": f"₹{close_price:.2f}",
                "Net P/L": f"{emoji} ₹{net:+.2f}"
            })
        except Exception:
            perf_rows.append({"Stock": s, "Open": "-", "Close": "-", "Net P/L": "N/A"})

    st.dataframe(pd.DataFrame(perf_rows), use_container_width=True)

st.caption("success")



