import streamlit as st
import PyPDF2
import re
from collections import defaultdict
import math
import pandas as pd

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

    observed = [leading_digits[i] / total_numbers for i in range(1, 10)]
    expected = [benford_distribution[i] for i in range(1, 10)]
    return observed, expected, leading_digits

st.title("Benfords Lov Analyse")

uploaded_file = st.file_uploader("Last opp en PDF-fil", type="pdf")

if uploaded_file:
    st.write("Analyserer dokumentet ...")
    numbers = extract_numbers_from_pdf(uploaded_file)
    
    if numbers:
        observed, expected, leading_digits_count = benford_analysis(numbers)
        
        # Preparing data for Streamlit's bar chart
        df_chart = pd.DataFrame({
            'Siffer': list(range(1, 10)),
            'Observerte': observed,
            'Forventet (Benford)': expected
        })
        
        st.bar_chart(df_chart.set_index('Siffer'))
        
        # Displaying the count of leading digits
        df_count = pd.DataFrame({
            'Siffer': list(range(1, 10)),
            'Antall': [leading_digits_count[i] for i in range(1, 10)]
        })
        
        st.write("Antall av ledende siffer:")
        st.dataframe(df_count.set_index('Siffer'))
        
    else:
        st.write("Ingen tall funnet i dokumentet.")
else:
    st.write("Vennligst last opp en PDF-fil.")
