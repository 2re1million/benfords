import streamlit as st
import PyPDF2
import re
from collections import defaultdict
import math
import pandas as pd
import numpy as np
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

    total_numbers = sum(leading_digits.values())
    benford_distribution = {i: math.log10(1 + 1/i) for i in range(1, 10)}

    benford_distribution = {i: math.log10(1 + 1/i) for i in range(1, 10)}
    observed = [leading_digits[i] for i in range(1, 10)]
    expected = [benford_distribution[i] * len(numbers) for i in range(1, 10)]
    return observed, expected, leading_digits

def benford_comment(observed_counts, expected_proportions):
    # Ensure observed counts only include counts for digits 1 through 9
    observed_counts = observed_counts[1:10] if len(observed_counts) == 10 else observed_counts

    # Convert expected proportions to expected counts
    total_numbers = sum(observed_counts)
    expected_counts = [e * total_numbers for e in expected_proportions]

    # Perform chi-squared test
    chi2_stat, p_val = chisquare(observed_counts, expected_counts)
    
    # Comment based on p-value (assuming significance level of 0.05)
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
        
        # Compute total counts for observed and expected for chi-squared test
        total_observed_counts = [count for count in leading_digits_count.values()]
        total_expected_counts = [e * sum(total_observed_counts) for e in expected]
        
        # Preparing data for Streamlit's bar chart with trendline
        df_chart = pd.DataFrame({
            'Digit': list(range(1, 10)),
            'Observed': observed,
            'Expected': expected
        })
        
        bars = alt.Chart(df_chart).mark_bar().encode(
            x='Digit:N',
            y='Observed:Q',
            color=alt.value('blue')
        )
        
        line = alt.Chart(df_chart).mark_line(color='red').encode(
            x='Digit:N',
            y='Expected:Q'
        )
        
        st.altair_chart(bars + line, use_container_width=True)
        
        # Displaying the count of leading digits
        df_count = pd.DataFrame({
            'Digit': list(range(1, 10)),
            'Count': [leading_digits_count[i] for i in range(1, 10)]
        })
        
        st.write("Count of leading digits:")
        st.dataframe(df_count.set_index('Digit'))
        
        # Providing a comment based on chi-squared test result
        comment = benford_comment(total_observed_counts, total_expected_counts)
        st.write(comment)
        
    else:
        st.write("No numbers found in the document.")
else:
    st.write("Please upload a PDF file.")
