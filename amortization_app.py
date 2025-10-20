import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# -------------------- STYLING --------------------
st.markdown(
    """
    <style>
    .main-heading {
        text-align: center;
        color: #2E86C1;
        font-size: 36px;
        font-weight: bold;
    }
    .sub-heading {
        color: #C0392B;
        font-size: 24px;
        font-weight: bold;
    }
    .center-button {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .stTextInput>label, .stNumberInput>label, .stSelectbox>label, .stDateInput>label {
        color: #8E44AD;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------- HEADING --------------------
st.markdown('<div class="main-heading">💰 Amortization Calculator</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#1F618D;">Upload data sources on the left and fill/view Payee ID info on the right.</p>', unsafe_allow_html=True)

today = datetime.today()
col_left, col_right = st.columns([1, 2])

# -------------------- LEFT COLUMN --------------------
with col_left:
    st.markdown('<div class="sub-heading">Data Sources Upload</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Upload Excel files", type=["xlsx"], accept_multiple_files=True)
    st.write("")

# -------------------- RIGHT COLUMN --------------------
with col_right:
    st.markdown('<div class="sub-heading">Payee ID Information</div>', unsafe_allow_html=True)

    # Default values
    selected_payee = "Provide Payee ID"
    total_incentive = 0.0
    cap = 0.0
    term = 0
    frequency = "Monthly"
    start_date = today

    all_dfs = []
    all_payee_ids = []

    if uploaded_files:
        for file in uploaded_files:
            df = pd.read_excel(file)
            df.columns = df.columns.str.strip().str.lower()
            df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

            if "payee id" in df.columns:
                all_dfs.append(df)
                all_payee_ids.extend(df["payee id"].dropna().unique().tolist())

        all_payee_ids = list(set(all_payee_ids))  # Unique Payee IDs

        if all_payee_ids:
            selected_payee = st.selectbox("Payee ID", all_payee_ids)

            # Find the row corresponding to the selected Payee ID
            selected_row = None
            for df in all_dfs:
                payee_data = df[df["payee id"] == selected_payee]
                if not payee_data.empty:
                    if len(payee_data) > 1:
                        st.info(f"Multiple entries found for {selected_payee}. Select one row below:")
                        payee_row = st.selectbox(
                            "Select Payee Record",
                            payee_data.index.tolist(),
                            format_func=lambda i: f"Term: {payee_data.loc[i, 'term']}, "
                                                  f"Frequency: {payee_data.loc[i, 'payment frequency']}, "
                                                  f"Start Date: {payee_data.loc[i, 'payment start date']}"
                        )
                        selected_row = payee_data.loc[payee_row]
                    else:
                        selected_row = payee_data.iloc[0]
                    break

            if selected_row is not None:
                total_incentive = float(selected_row["total incentive"])
                cap = float(selected_row["cap %"])
                term = int(selected_row["term"])
                frequency = "Monthly" if str(selected_row["payment frequency"]).lower().startswith("m") else "Quarterly"
                start_date = pd.to_datetime(selected_row["payment start date"])

    # Input fields
    selected_payee = st.text_input("Payee ID", selected_payee)
    total_incentive = st.number_input("Total Incentive", min_value=0.0, value=total_incentive)
    cap = st.number_input("Cap (%)", min_value=0.0, value=cap)
    term = st.number_input("Term", min_value=0, value=term)
    frequency = st.selectbox("Payment Frequency", ["Monthly", "Quarterly"], index=0 if frequency=="Monthly" else 1)
    start_date = st.date_input("Payment Start Date", start_date)

    df_selected = pd.DataFrame([{
        "Payee ID": selected_payee,
        "Total Incentive": total_incentive,
        "Cap %": cap,
        "Term": term,
        "Payment Frequency": frequency,
        "Payment Start Date": start_date.strftime("%Y-%m-%d")
    }])

# -------------------- CENTERED BUTTON --------------------
if st.button("Calculate Amortization"):
    results = []
    for _, row in df_selected.iterrows():
        total = row["Total Incentive"]
        cap_ratio = row["Cap %"] / 100
        term_count = int(row["Term"])
        freq = row["Payment Frequency"].lower()
        start = datetime.strptime(str(row["Payment Start Date"]), "%Y-%m-%d")

        if term_count == 0:
            st.warning("⚠️ Term is 0. Cannot calculate amortization.")
            continue

        step = 30 if freq == "monthly" else 90
        payment_amount = (total * cap_ratio) / term_count
        cumulative = 0

        for i in range(1, term_count + 1):
            pay_date = start + timedelta(days=step * (i - 1))
            cumulative += payment_amount
            results.append({
                "Payee ID": row["Payee ID"],
                "Payment No": i,
                "Payment Date": pay_date.strftime("%Y-%m-%d"),
                "Payment Amount": round(payment_amount, 2),
                "Cumulative Amount": round(cumulative, 2),
                "End Date": (start + timedelta(days=step * term_count)).strftime("%Y-%m-%d")
            })

    if results:
        result_df = pd.DataFrame(results)
        st.success("✅ Amortization calculated successfully!")
        st.dataframe(result_df)
        st.download_button(
            "Download Results as CSV",
            data=result_df.to_csv(index=False).encode('utf-8'),
            file_name="amortization_schedule.csv",
            mime="text/csv"
        )

# -------------------- CENTER BUTTON CSS --------------------
st.markdown(
    """
    <style>
    div.stButton > button:first-child {
        display: block;
        margin: 0 auto;
        background-color: #27AE60;
        color: white;
        font-size: 18px;
        padding: 10px 30px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
