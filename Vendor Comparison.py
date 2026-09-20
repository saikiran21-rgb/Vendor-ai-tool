import streamlit as st
import pandas as pd

def detect_final_cost_column(df):
    final_keywords = ["final", "total", "grand", "net", "amount", "payable", "due", "cost"]

    columns = [col.lower() for col in df.columns]

    # Detect Qty column
    qty_column = None
    for col in df.columns:
        if col.lower() in ["qty", "quantity"]:
            qty_column = col
            break

    # Find matching cost columns
    matches = [
        df.columns[i]
        for i, col in enumerate(columns)
        if any(keyword in col for keyword in final_keywords)
    ]

    if not matches:
        return None

    # Prefer cost columns that appear AFTER Qty
    if qty_column:
        qty_index = df.columns.get_loc(qty_column)
        matches_after_qty = [col for col in matches if df.columns.get_loc(col) > qty_index]

        if matches_after_qty:
            matches = matches_after_qty

    # Pick the most specific column name
    matches_sorted = sorted(matches, key=lambda x: len(x), reverse=True)
    return matches_sorted[0]


st.title("Vendor Comparison AI Tool")

uploaded_files = st.file_uploader("Upload Vendor Quote Files", accept_multiple_files=True)

if st.button("Compare Vendors"):
    vendor_costs = {}

    # 1. Read files and detect cost column
    for file in uploaded_files:
        df = pd.read_excel(file)
        vendor_name = file.name.replace(".xlsx", "")
        final_cost_column = detect_final_cost_column(df)

        if final_cost_column is None:
            st.error(f"No final cost column found in {file.name}")
            continue

        total_cost = df[final_cost_column].sum()
        vendor_costs[vendor_name] = total_cost

    # 2. Vendor summary
    st.subheader("Vendor Cost Summary")
    for vendor, cost in vendor_costs.items():
        st.write(f"{vendor}: {cost}")

    # 3. Cheapest vendor
    cheapest_vendor = min(vendor_costs, key=vendor_costs.get)
    cheapest_cost = vendor_costs[cheapest_vendor]
    st.success(f"Cheapest Vendor → {cheapest_vendor} ({cheapest_cost})")

    # 4. Savings percentage
    highest_cost = max(vendor_costs.values())
    lowest_cost = min(vendor_costs.values())
    savings_percentage = ((highest_cost - lowest_cost) / highest_cost) * 100

    st.subheader("Savings Analysis")
    st.write(f"Highest Vendor Cost: {highest_cost}")
    st.write(f"Lowest Vendor Cost: {lowest_cost}")
    st.write(f"Savings Percentage: {savings_percentage:.2f}%")

    # 5. Bar Chart
    st.subheader("Vendor Cost Bar Chart")
    chart_data = pd.DataFrame({
        "Vendor": list(vendor_costs.keys()),
        "Cost": list(vendor_costs.values())
    })
    st.bar_chart(chart_data.set_index("Vendor"))

    # 6. Color‑coded vendor table
    st.subheader("Color‑Coded Vendor Table")
    df_table = pd.DataFrame({
        "Vendor": list(vendor_costs.keys()),
        "Cost": list(vendor_costs.values())
    })

    min_cost = df_table["Cost"].min()
    max_cost = df_table["Cost"].max()

    def highlight_row(row):
        if row["Cost"] == min_cost:
            return ["background-color: #d4f7d4"] * len(row)
        elif row["Cost"] == max_cost:
            return ["background-color: #f7d4d4"] * len(row)
        else:
            return ["background-color: #fff7d4"] * len(row)

    st.dataframe(df_table.style.apply(highlight_row, axis=1))
import pdfkit

config = pdfkit.configuration(
    wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
)

def generate_pdf(html_content):
    return pdfkit.from_string(html_content, False, configuration=config)

html_report = """
<h2>Vendor Comparison Report</h2>
<p>This is your vendor comparison PDF.</p>
"""

pdf = generate_pdf(html_report)

st.download_button(
    label="Download PDF",
    data=pdf,
    file_name="vendor_comparison.pdf",
    mime="application/pdf"
)
import pandas as pd
import altair as alt

st.subheader("Vendor Cost Bar Chart")

df = pd.DataFrame({
    "Vendor": df_table["Vendor"],
    "Cost": df_table["Cost"]
})

chart = alt.Chart(df).mark_bar().encode(
    x="Vendor",
    y="Cost",
    color="Vendor"
)

st.altair_chart(chart, use_container_width=True)