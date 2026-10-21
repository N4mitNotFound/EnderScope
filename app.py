import json
import re
import pandas as pd
import streamlit as st

from enderscope_core import SAMPLE, format_duration, parse_stats

st.set_page_config(
    page_title="ENDERSCOPE // Minecraft Analytics",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded",
)

CYBER_CSS = """
<style>
:root { --cyan:#00f5ff; --pink:#ff2bd6; --bg:#070b12; --panel:#0c1420; --muted:#8ca0b8; }
.stApp { background: radial-gradient(ellipse at 15% 0%, #102332 0%, #070b12 42%, #080811 100%); color:#e8f6ff; }
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
h1,h2,h3 { font-family:'Consolas','Courier New',monospace !important; letter-spacing:.04em; }
p, label, div, span { font-family:'Segoe UI',Arial,sans-serif; }
.block-container { padding-top: 1.6rem; max-width: 1500px; }
[data-testid="stMetric"] { background:linear-gradient(145deg,rgba(12,27,42,.96),rgba(10,12,24,.96)); border:1px solid rgba(0,245,255,.28); padding:18px 20px; border-radius:12px; box-shadow:0 0 18px rgba(0,245,255,.045); }
[data-testid="stMetricLabel"] { color:#9bb6ca !important; font-size:1rem !important; }
[data-testid="stMetricValue"] { color:#00f5ff !important; font-family:'Consolas','Courier New',monospace !important; }
div[data-testid="stVerticalBlockBorderWrapper"] { border-color:rgba(0,245,255,.20) !important; }
.stButton>button, .stDownloadButton>button { border:1px solid #00f5ff; background:#07131d; color:#00f5ff; border-radius:7px; font-weight:700; }
.stButton>button:hover, .stDownloadButton>button:hover { border-color:#ff2bd6; color:#ff2bd6; }
[data-testid="stSidebar"] { background:#080d16; border-right:1px solid rgba(0,245,255,.20); }
[data-testid="stFileUploader"] { border:1px dashed rgba(0,245,255,.45); border-radius:10px; padding:8px; }
.small-muted { color:#8ca0b8; font-size:.95rem; }
.status-line { color:#00f5ff; letter-spacing:.15em; font-family:'Consolas','Courier New',monospace; font-size:.75rem; }
hr { border-color:rgba(0,245,255,.18); }
</style>
"""
st.markdown(CYBER_CSS, unsafe_allow_html=True)

st.markdown('<div class="status-line">● SYSTEM ONLINE &nbsp; // &nbsp; PLAYER TELEMETRY CONSOLE</div>', unsafe_allow_html=True)
st.title("ENDERSCOPE")
st.markdown('<p class="small-muted">MINECRAFT PLAYER ANALYTICS // LOCAL-FIRST DATA TERMINAL</p>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ◈ DATA INPUT")
    mode = st.radio("Source mode", ["Demo data", "Upload JSON"], index=0)
    uploaded = None
    if mode == "Upload JSON":
        uploaded = st.file_uploader(
            "Player statistics JSON",
            type=["json"],
            help="Upload a stats/<player-uuid>.json file from a Minecraft Java Edition world.",
        )
    st.divider()
    st.markdown("### ◈ MODULES")
    st.caption("MINING // COMBAT // MOVEMENT // INVENTORY")
    st.divider()
    st.markdown("### ◈ PRIVACY")
    st.caption("Files are processed in this local app session. No paid API or account connection is used.")
    st.caption("For public demos, use the included fictional sample data.")

if mode == "Demo data":
    raw_data = SAMPLE
    st.info("DEMO MODE ACTIVE — these numbers are fictional sample data, not your actual Minecraft history.")
elif uploaded is None:
    st.warning("Upload a Minecraft statistics JSON file from the sidebar to load your player data.")
    st.stop()
else:
    try:
        uploaded.seek(0)
        raw_data = json.load(uploaded)
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
        st.error("The file could not be parsed as valid JSON.")
        st.stop()

try:
    result = parse_stats(raw_data)
except (ValueError, TypeError, AttributeError) as exc:
    st.error(f"Statistics file format problem: {exc}")
    st.stop()

mined = result["mined"]
killed = result["killed"]
total_blocks = int(mined["Count"].sum()) if not mined.empty else 0
total_mobs = int(killed["Count"].sum()) if not killed.empty else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("BLOCKS MINED", f"{total_blocks:,}", help="Sum of entries in minecraft:mined.")
m2.metric("TIME PLAYED", format_duration(result["play_hours"]), help="Minecraft records play time in ticks.")
m3.metric("WALK DISTANCE", f"{result['walk_km']:,.2f} km")
m4.metric("DEATHS", f"{result['deaths']:,}")

st.divider()
left, right = st.columns(2, gap="large")
with left:
    st.subheader("01 // MINING OUTPUT")
    if not mined.empty:
        st.bar_chart(mined.head(10).set_index("Block")["Count"], horizontal=True, color="#00f5ff")
        st.caption(f"{len(mined):,} block types recorded")
    else:
        st.info("No mining statistics found in this file.")
with right:
    st.subheader("02 // COMBAT LOG")
    if not killed.empty:
        st.bar_chart(killed.head(10).set_index("Mob")["Count"], horizontal=True, color="#ff2bd6")
        st.caption(f"{total_mobs:,} total recorded mob kills")
    else:
        st.info("No per-mob kill statistics found in this file.")

st.divider()
st.subheader("03 // PLAYER TELEMETRY")
a, b, c, d = st.columns(4)
a.metric("JUMPS", f"{result['jumps']:,}")
b.metric("SPRINT DISTANCE", f"{result['sprint_km']:,.2f} km")
c.metric("DAMAGE DEALT", f"{result['damage_dealt']:,.1f}")
d.metric("ANIMALS BRED", f"{result['animals_bred']:,}")

with st.expander("INVENTORY & ITEM ACTIVITY"):
    tabs = st.tabs(["Broken", "Crafted", "Used", "Picked up", "Dropped"])
    for tab, key in zip(tabs, ["broken", "crafted", "used", "picked_up", "dropped"]):
        with tab:
            frame = result[key]
            if frame.empty:
                st.caption("No data recorded in this category.")
            else:
                st.dataframe(frame, use_container_width=True, hide_index=True)

with st.expander("FULL MINING DATA"):
    if not mined.empty:
        search = st.text_input("Filter block names", placeholder="e.g. diamond, stone, deepslate")
        view = mined[mined["Block"].str.contains(re.escape(search), case=False, na=False)] if search else mined
        st.dataframe(view, use_container_width=True, hide_index=True)
        st.download_button(
            "DOWNLOAD MINING CSV",
            data=view.to_csv(index=False).encode("utf-8"),
            file_name="enderscope_mining.csv",
            mime="text/csv",
        )
    else:
        st.caption("No mining data available to export.")

with st.expander("RAW STATISTICS METADATA"):
    st.write("Data version:", result["data_version"])
    st.write("Statistic groups found:", ", ".join(sorted(raw_data.get("stats", {}).keys())) or "None")
    st.caption("Minecraft statistics differ by version, world settings, and player activity. Missing keys are displayed as zero or an empty table; this does not prove the activity never happened.")

st.markdown("---")
st.markdown(
    '<div class="small-muted">ENDERSCOPE // V1.0.0 &nbsp; · &nbsp; BUILT WITH PYTHON + STREAMLIT &nbsp; · &nbsp; NO PAID APIS</div>',
    unsafe_allow_html=True,
)
