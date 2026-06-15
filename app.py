import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import io

st.set_page_config(
    page_title="Data Visualization Dashboard",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #111827);
    color: white;
}
.main-title {
    font-size: 42px;
    font-weight: 800;
    text-align: center;
    color: #38bdf8;
}
.sub-title {
    text-align: center;
    color: #cbd5e1;
    font-size: 18px;
    margin-bottom: 30px;
}
.card {
    background: rgba(255,255,255,0.08);
    padding: 25px;
    border-radius: 18px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.15);
    margin-bottom: 15px;
}
.card h3 {
    color: #94a3b8;
    font-size: 16px;
}
.card h2 {
    color: #38bdf8;
    font-size: 34px;
}
.footer {
    text-align: center;
    color: #94a3b8;
    margin-top: 40px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>📊 Data Visualization Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>CSV / Excel upload karke dynamic charts aur AI insights generate karo</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload CSV or Excel File",
    type=["csv", "xlsx"]
)

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
else:
    df = pd.read_csv("sample_data.csv")

st.sidebar.title("⚙ Dashboard Controls")

st.sidebar.subheader("🧹 Data Cleaning")
remove_nulls = st.sidebar.checkbox("Remove Null Values")
remove_duplicates = st.sidebar.checkbox("Remove Duplicate Rows")

cleaned_df = df.copy()

if remove_nulls:
    cleaned_df = cleaned_df.dropna()

if remove_duplicates:
    cleaned_df = cleaned_df.drop_duplicates()

filter_column = st.sidebar.selectbox("Select Filter Column", cleaned_df.columns)
filter_value = st.sidebar.selectbox("Select Filter Value", cleaned_df[filter_column].unique())

filtered_df = cleaned_df[cleaned_df[filter_column] == filter_value]

st.subheader("🔎 Search Data")
search_text = st.text_input("Search anything in dataset")

if search_text:
    searched_df = filtered_df[
        filtered_df.astype(str)
        .apply(lambda row: row.str.contains(search_text, case=False).any(), axis=1)
    ]
else:
    searched_df = filtered_df

numeric_columns = cleaned_df.select_dtypes(include=["int64", "float64"]).columns.tolist()
all_columns = cleaned_df.columns.tolist()

col1, col2, col3, col4 = st.columns(4)

col1.markdown(f"<div class='card'><h3>Total Rows</h3><h2>{cleaned_df.shape[0]}</h2></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='card'><h3>Total Columns</h3><h2>{cleaned_df.shape[1]}</h2></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='card'><h3>Missing Values</h3><h2>{cleaned_df.isnull().sum().sum()}</h2></div>", unsafe_allow_html=True)
col4.markdown(f"<div class='card'><h3>Duplicate Rows</h3><h2>{cleaned_df.duplicated().sum()}</h2></div>", unsafe_allow_html=True)

st.markdown("---")

st.subheader("🤖 AI Insights Section")

if len(numeric_columns) > 0:
    selected_metric = st.selectbox("Select Metric Column for Insights", numeric_columns)

    max_value = cleaned_df[selected_metric].max()
    min_value = cleaned_df[selected_metric].min()
    avg_value = cleaned_df[selected_metric].mean()

    insight_col1, insight_col2, insight_col3 = st.columns(3)

    insight_col1.metric("Highest Value", round(max_value, 2))
    insight_col2.metric("Lowest Value", round(min_value, 2))
    insight_col3.metric("Average Value", round(avg_value, 2))

    if len(all_columns) > 1:
        category_column = st.selectbox("Select Category Column", all_columns)

        best_category = cleaned_df.groupby(category_column)[selected_metric].sum().idxmax()
        best_value = cleaned_df.groupby(category_column)[selected_metric].sum().max()

        st.success(f"🏆 Best Performing {category_column}: {best_category} with total {selected_metric} = {best_value}")

    st.info(
        f"📌 Summary: Dataset me total {cleaned_df.shape[0]} rows aur {cleaned_df.shape[1]} columns hain. "
        f"{selected_metric} ka highest value {round(max_value, 2)}, lowest value {round(min_value, 2)} "
        f"aur average value {round(avg_value, 2)} hai."
    )
else:
    st.warning("AI insights ke liye numeric column required hai.")

st.markdown("---")

st.subheader("📌 Dataset Preview")
st.dataframe(cleaned_df, use_container_width=True)

st.subheader("🎯 Filtered + Searched Data")
st.dataframe(searched_df, use_container_width=True)

csv = searched_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇ Download Cleaned CSV",
    data=csv,
    file_name="cleaned_filtered_data.csv",
    mime="text/csv"
)

def create_pdf_report(rows, cols, missing, duplicates):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 10, "Data Visualization Dashboard Report", ln=True, align="C")

    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Total Rows: {rows}", ln=True)
    pdf.cell(0, 10, f"Total Columns: {cols}", ln=True)
    pdf.cell(0, 10, f"Missing Values: {missing}", ln=True)
    pdf.cell(0, 10, f"Duplicate Rows: {duplicates}", ln=True)

    pdf.ln(10)
    pdf.multi_cell(0, 10, "This report was generated from the uploaded dataset using Python, Streamlit, Pandas and Plotly.")

    return pdf.output(dest="S").encode("latin-1")

pdf_data = create_pdf_report(
    cleaned_df.shape[0],
    cleaned_df.shape[1],
    cleaned_df.isnull().sum().sum(),
    cleaned_df.duplicated().sum()
)

st.download_button(
    label="📄 Download PDF Report",
    data=pdf_data,
    file_name="dashboard_report.pdf",
    mime="application/pdf"
)

st.markdown("---")
st.subheader("📊 Basic Charts")

if len(numeric_columns) > 0 and not searched_df.empty:
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        x_axis = st.selectbox("Select X Axis", all_columns)
        y_axis = st.selectbox("Select Y Axis", numeric_columns)

        bar_chart = px.bar(
            searched_df,
            x=x_axis,
            y=y_axis,
            title=f"{y_axis} by {x_axis}",
            template="plotly_dark"
        )
        st.plotly_chart(bar_chart, use_container_width=True)

    with chart_col2:
        pie_column = st.selectbox("Select Column for Pie Chart", all_columns)

        pie_chart = px.pie(
            searched_df,
            names=pie_column,
            title=f"{pie_column} Distribution",
            template="plotly_dark"
        )
        st.plotly_chart(pie_chart, use_container_width=True)

    line_chart = px.line(
        searched_df,
        x=x_axis,
        y=y_axis,
        markers=True,
        title=f"{y_axis} Trend by {x_axis}",
        template="plotly_dark"
    )
    st.plotly_chart(line_chart, use_container_width=True)

    st.markdown("---")
    st.subheader("📈 Advanced Charts")

    adv_col1, adv_col2 = st.columns(2)

    with adv_col1:
        scatter_x = st.selectbox("Scatter X Axis", numeric_columns)
        scatter_y = st.selectbox("Scatter Y Axis", numeric_columns)

        scatter_chart = px.scatter(
            searched_df,
            x=scatter_x,
            y=scatter_y,
            title=f"{scatter_y} vs {scatter_x}",
            template="plotly_dark"
        )
        st.plotly_chart(scatter_chart, use_container_width=True)

    with adv_col2:
        hist_column = st.selectbox("Histogram Column", numeric_columns)

        hist_chart = px.histogram(
            searched_df,
            x=hist_column,
            title=f"{hist_column} Distribution",
            template="plotly_dark"
        )
        st.plotly_chart(hist_chart, use_container_width=True)

    if len(numeric_columns) >= 2:
        corr = searched_df[numeric_columns].corr()

        heatmap = px.imshow(
            corr,
            text_auto=True,
            title="Correlation Heatmap",
            template="plotly_dark"
        )
        st.plotly_chart(heatmap, use_container_width=True)

    missing_data = cleaned_df.isnull().sum().reset_index()
    missing_data.columns = ["Column", "Missing Values"]

    null_chart = px.bar(
        missing_data,
        x="Column",
        y="Missing Values",
        title="Missing Values by Column",
        template="plotly_dark"
    )
    st.plotly_chart(null_chart, use_container_width=True)

elif searched_df.empty:
    st.warning("Search/filter ke baad koi data nahi mila.")
else:
    st.warning("CSV / Excel file me numeric column nahi hai.")

st.markdown("<p class='footer'>Made by Mohd Kashif | Python + Streamlit + Pandas + Plotly</p>", unsafe_allow_html=True)