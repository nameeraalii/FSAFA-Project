import streamlit as st
import pandas as pd
import sys
import os

# -------------------------------------------------
# Make path robust (Windows-safe)
# -------------------------------------------------
sys.path.append(os.path.dirname(__file__))

# =================================================
# IMPORTS
# =================================================
from utils.forensic_scores import (
    beneish_m_score_series,
    sloan_accrual_series,
    piotroski_f_score_series,
    altman_z_score_series
)

from utils.forensic_engine import (
    compute_frs,
    position_engine,
    execution_engine
)

from utils.ai_explainer import (
    ai_explain_forensic_scores,
    ai_explain_positioning,
    ai_final_recommendation
)

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="Forensic Alpha Scanner",
    layout="wide"
)

st.title("🔍 Forensic Alpha Scanner")
st.caption(
    "Forensic accounting–driven portfolio positioning engine "
    "with local AI explanations (Ollama)"
)

# =================================================
# SESSION STATE
# =================================================
for key in ["raw_df", "pivot", "confirmed"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "confirmed" else False

# =================================================
# TABS
# =================================================
tabs = st.tabs([
    "📥 Data Input & Validation",
    "🧪 Forensic Scores",
    "⚙️ Risk → Position Engine",
    "📤 Final Execution Output"
])

# =================================================
# TAB 1 — DATA INPUT & VALIDATION
# =================================================
with tabs[0]:
    st.header("📥 Upload & Validate Financial Data")

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel (multi-year format)",
        type=["csv", "xlsx"]
    )

    if uploaded_file:
        df = (
            pd.read_csv(uploaded_file)
            if uploaded_file.name.endswith(".csv")
            else pd.read_excel(uploaded_file)
        )

        if not {"Statement", "Item"}.issubset(df.columns):
            st.error("File must contain 'Statement' and 'Item' columns.")
            st.stop()

        st.session_state.raw_df = df
        st.success("File uploaded successfully")

    if st.session_state.raw_df is not None:
        st.subheader("🧾 Review & Edit Financial Statements")

        df = st.session_state.raw_df.copy()
        year_cols = [c for c in df.columns if c not in ["Statement", "Item"]]

        long_df = df.melt(
            id_vars=["Statement", "Item"],
            value_vars=year_cols,
            var_name="year",
            value_name="value"
        )

        long_df["canonical_item"] = (
            long_df["Item"]
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("-", "_")
        )

        edited = st.data_editor(
            long_df,
            use_container_width=True,
            num_rows="fixed"
        )

        if st.button("✅ Confirm & Structure Data"):
            edited = edited.drop_duplicates(
                subset=["year", "canonical_item"],
                keep="first"
            )

            edited["value"] = pd.to_numeric(
                edited["value"], errors="coerce"
            )

            pivot = (
                edited
                .pivot_table(
                    index="year",
                    columns="canonical_item",
                    values="value",
                    aggfunc="first"
                )
                .sort_index()
            )

            try:
                pivot.index = pivot.index.astype(int)
            except Exception:
                pass

            st.session_state.pivot = pivot
            st.session_state.confirmed = True

            st.success("✅ Financial data validated and structured")

# =================================================
# TAB 2 — FORENSIC SCORES + AI EXPLANATION
# =================================================
with tabs[1]:
    st.header("🧪 Forensic Accounting Scores")

    if not st.session_state.confirmed:
        st.info("Confirm financial data to compute forensic scores.")
    else:
        pivot = st.session_state.pivot
        latest_year = pivot.index.max()

        m = beneish_m_score_series(pivot)
        s = sloan_accrual_series(pivot)
        f = piotroski_f_score_series(pivot)
        z = altman_z_score_series(pivot)

        frs_df = compute_frs(m, s, f, z)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Beneish M-Score", round(m.loc[latest_year], 2))
        c2.metric("Sloan Accruals", round(s.loc[latest_year], 3))
        c3.metric("Piotroski F-Score", int(f.loc[latest_year]))
        c4.metric("Altman Z-Score", round(z.loc[latest_year], 2))

        st.metric(
            "Composite Forensic Risk Score (FRS)",
            round(frs_df.loc[latest_year, "FRS"], 3)
        )

        st.divider()
        st.subheader("🤖 AI Explanation (Local – Ollama)")

        if st.button("Explain Forensic Scores"):
            with st.spinner("Ollama is interpreting forensic diagnostics..."):
                ai_text = ai_explain_forensic_scores(
                    m.loc[latest_year],
                    s.loc[latest_year],
                    f.loc[latest_year],
                    z.loc[latest_year],
                    frs_df.loc[latest_year, "FRS"]
                )
            st.markdown(ai_text)

# =================================================
# TAB 3 — POSITION SIZING + AI EXPLANATION
# =================================================
with tabs[2]:
    st.header("⚙️ Forensic Risk → Position Sizing Engine")

    if not st.session_state.confirmed:
        st.info("Confirm financial data to activate the engine.")
    else:
        pivot = st.session_state.pivot

        st.subheader("💼 Portfolio Inputs")

        c1, c2, c3 = st.columns(3)
        with c1:
            portfolio_value = st.number_input(
                "Total Portfolio Value (₹)",
                min_value=10_000.0,
                value=1_000_000.0,
                step=50_000.0
            )
        with c2:
            stock_price = st.number_input(
                "Current Stock Price (₹)",
                min_value=1.0,
                value=100.0,
                step=1.0
            )
        with c3:
            current_weight = st.number_input(
                "Current Portfolio Weight",
                min_value=-0.10,
                max_value=0.20,
                value=0.05,
                step=0.005,
                format="%.3f"
            )

        if stock_price <= 0:
            st.error("Stock price must be greater than zero.")
            st.stop()

        m = beneish_m_score_series(pivot)
        s = sloan_accrual_series(pivot)
        f = piotroski_f_score_series(pivot)
        z = altman_z_score_series(pivot)

        frs_df = compute_frs(m, s, f, z)
        pos_df = position_engine(
            frs_df,
            current_weight=current_weight,
            aggressiveness=0.10
        )

        latest = pos_df.iloc[-1]

        c1, c2, c3 = st.columns(3)
        c1.metric("Forensic Risk Score (FRS)", latest["FRS"])
        c2.metric("Signal", latest["Signal"])
        c3.metric("Target Weight", f"{latest['Target_weight']:.2%}")

        st.divider()
        st.subheader("🤖 AI Explanation: Position Sizing")

        if st.button("Explain Position Sizing"):
            with st.spinner("Ollama is explaining sizing logic..."):
                ai_text = ai_explain_positioning(
                    latest["FRS"],
                    latest["Signal"],
                    current_weight,
                    latest["Target_weight"]
                )
            st.markdown(ai_text)

# =================================================
# TAB 4 — EXECUTION OUTPUT + FINAL AI RECOMMENDATION
# =================================================
with tabs[3]:
    st.header("📤 Execution-Ready Output")

    if not st.session_state.confirmed:
        st.info("Run the engine to view execution output.")
    else:
        exec_df = execution_engine(
            pos_df,
            portfolio_value,
            stock_price,
            current_weight
        )

        latest = exec_df.iloc[-1]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Target Exposure (₹)", f"{latest['Target_value']:,.0f}")
        c2.metric("Target Shares", int(latest["Target_shares"]))
        c3.metric("Shares to Trade", int(latest["Shares_to_trade"]))
        c4.metric("Action", latest["Signal"])

        st.divider()
        st.subheader("🤖 AI-Assisted Final Recommendation")

        if st.button("Generate Final Recommendation"):
            with st.spinner("Ollama is drafting recommendation..."):
                ai_text = ai_final_recommendation(
                    latest["Signal"],
                    latest["Shares_to_trade"]
                )
            st.markdown(ai_text)

        st.subheader("📋 Full Engine Output (All Years)")
        st.dataframe(exec_df, use_container_width=True)
