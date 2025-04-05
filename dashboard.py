
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from fpdf import FPDF
import math
import os

# Load data and logo
df = pd.read_csv("sa3_map_ready_data_cleaned.csv")
logo_path = "PropWealth logo final-05 (4).png"

st.set_page_config(layout="wide")
st.title("🏡 PropwealthNext: Pro Investment Dashboard")

score_cols = [
    "10 Year % Price Change (PA)", "RENT CHANGE", "YIELD",
    "Rent Trend", "Fully Owned", "Buy Afford", "Rent Afford"
]

tab1, tab2, tab3, tab4 = st.tabs(["📍 Map View", "📊 Radar Chart", "📋 Score Filter", "📄 Reports"])

# --- MAP TAB ---
with tab1:
    st.subheader("📍 Interactive SA3 Map")
    map_df = df.dropna(subset=["Latitude", "Longitude"])
    fig = px.scatter_mapbox(
        map_df,
        lat="Latitude",
        lon="Longitude",
        hover_name="SA3",
        hover_data={"Sa4": True, "Median": True, "YIELD": True, "RENT CHANGE": True},
        zoom=4,
        height=600
    )
    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig, use_container_width=True)

# --- RADAR TAB ---
with tab2:
    st.subheader("📊 Radar Comparison")
    selected = st.selectbox("Select SA3", df["SA3"].dropna().unique(), key="radar")
    row = df[df["SA3"] == selected].iloc[0]
    values = [row[col] for col in score_cols]
    values += values[:1]
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=values,
        theta=score_cols + [score_cols[0]],
        fill='toself',
        name=row["SA3"]
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[1, 5])),
        showlegend=False,
        height=600
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# --- FILTER TAB ---
with tab3:
    st.subheader("🎯 Filter by Scores (1–5)")
    filtered_df = df.copy()
    for col in score_cols:
        selected = st.multiselect(f"{col}", [1, 2, 3, 4, 5], default=[1, 2, 3, 4, 5], key=col)
        filtered_df = filtered_df[filtered_df[col].isin(selected)]
    st.dataframe(filtered_df[["SA3", "Sa4"] + score_cols + ["Median", "YIELD", "RENT CHANGE"]])
    st.download_button("📥 Download Filtered CSV", filtered_df.to_csv(index=False), "filtered_propwealth_data.csv", "text/csv")

# --- REPORT TAB ---
with tab4:
    st.subheader("📄 Generate Branded Investment Report")
    selected_sa3 = st.selectbox("Choose SA3 for PDF Report", df["SA3"].unique(), key="pdf")
    row = df[df["SA3"] == selected_sa3].iloc[0]

    values = [row[col] for col in score_cols]
    values += values[:1]
    angles = [n / float(len(score_cols)) * 2 * math.pi for n in range(len(score_cols))]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.plot(angles, values, linewidth=2, linestyle='solid', color='navy')
    ax.fill(angles, values, 'skyblue', alpha=0.4)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(score_cols, fontsize=8)
    ax.set_yticklabels([])
    plt.title(f"Investment Radar: {selected_sa3}", fontsize=12)
    radar_path = f"radar_{selected_sa3}.png"
    plt.savefig(radar_path, bbox_inches='tight')
    plt.close()

    # Generate PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.image(logo_path, x=10, y=8, w=50)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_xy(70, 15)
    pdf.cell(0, 10, f"PropwealthNext Report - {selected_sa3}", ln=True)
    pdf.image(radar_path, x=40, y=40, w=130)
    pdf.set_font("Arial", size=11)
    pdf.ln(110)
    pdf.cell(0, 10, f"SA4 Region: {row['Sa4']}", ln=True)
    pdf.cell(0, 10, f"Median Price: ${row['Median']:,}", ln=True)
    pdf.cell(0, 10, f"Yield: {row['YIELD']}%", ln=True)
    pdf.cell(0, 10, f"Rent Change: {row['RENT CHANGE']}%", ln=True)
    pdf.cell(0, 10, f"Buy Affordability: {row['Buy Afford']}", ln=True)
    pdf.cell(0, 10, f"Rent Affordability: {row['Rent Afford']}", ln=True)

    pdf_output_path = f"{selected_sa3}_Propwealth_Report.pdf"
    pdf.output(pdf_output_path)

    with open(pdf_output_path, "rb") as f:
        st.download_button("📥 Download SA3 PDF Report", f, file_name=pdf_output_path, mime="application/pdf")
