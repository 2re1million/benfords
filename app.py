import streamlit as st
import PyPDF2
import re
from collections import defaultdict
import math
import pandas as pd
import altair as alt
from scipy.stats import chisquare

def extract_numbers_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return [int(match[0]) for match in re.findall(r'(\d+)', text)]

def benford_analysis(numbers):
    leading_digits = defaultdict(int)
    for num in numbers:
        leading_digit = int(str(num)[0])
        leading_digits[leading_digit] += 1

    total_numbers = len(numbers)
    benford_distribution = {i: math.log10(1 + 1/i) for i in range(1, 10)}

    observed = [leading_digits[i] for i in range(1, 10)]
    expected = [benford_distribution[i] * total_numbers for i in range(1, 10)]
    return observed, expected, leading_digits

def benford_comment(observed_counts, expected_counts):
    chi2_stat, p_val = chisquare(observed_counts, expected_counts)
    if p_val < 0.05:
        return "Red Flag: The distribution deviates significantly from Benford's Law."
    else:
        return "The distribution is consistent with Benford's Law."

st.title("Benford's Law Analysis")
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file:
    st.write("Analyzing the document ...")
    numbers = extract_numbers_from_pdf(uploaded_file)
    
    if numbers:
        observed, expected, leading_digits_count = benford_analysis(numbers)

        # Preparing data for Streamlit's bar chart with trendline
        df_chart = pd.DataFrame({
            'Digit': list(range(1, 10)),
            'Observed': observed,
            'Expected (red)': expected
        })

        bars = alt.Chart(df_chart).mark_bar(color='blue').encode(
            x='Digit:N',
            y='Observed:Q'
        )
        
        line = alt.Chart(df_chart).mark_line(color='red').encode(
            x='Digit:N',
            y='Expected (red):Q'
        )
        
        st.altair_chart((bars + line).properties(width=600), use_container_width=True)

        # Displaying the count of leading digits
        df_count = pd.DataFrame({
            'Digit': list(range(1, 10)),
            'Count': [leading_digits_count[i] for i in range(1, 10)]
        })
        
        st.write("Count of leading digits:")
        st.dataframe(df_count.set_index('Digit'))
        
        # Providing a comment based on chi-squared test result
        comment = benford_comment(observed, expected)
        st.write(comment)
        
    else:
        st.write("No numbers found in the document.")
else:
    st.write("Please upload a PDF file.")
