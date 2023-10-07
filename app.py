import streamlit as st
import PyPDF2
import re
from collections import defaultdict
import math
import matplotlib.pyplot as plt


def extract_numbers_from_pdf(file):
    reader = PyPDF2.PdfFileReader(file)
    text = ""
    for page in range(reader.numPages):
        text += reader.getPage(page).extractText()
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
    return observed, expected

st.title("Benfords Lov Analyse")

uploaded_file = st.file_uploader("Last opp en PDF-fil", type="pdf")

if uploaded_file:
    st.write("Analyserer dokumentet ...")
    numbers = extract_numbers_from_pdf(uploaded_file)
    
    if numbers:
        observed, expected = benford_analysis(numbers)
        
        # Plotting
        fig, ax = plt.subplots()
        index = list(range(1, 10))
        bar_width = 0.35

        bar1 = ax.bar(index, observed, bar_width, label='Observerte', color='b')
        bar2 = ax.bar([i + bar_width for i in index], expected, bar_width, label='Forventet (Benford)', color='r')
        
        ax.set_xlabel('Siffer')
        ax.set_ylabel('Frekvens')
        ax.set_title('Observerte vs Forventet Frekvens av Ledende Siffer')
        ax.set_xticks([i + bar_width/2 for i in index])
        ax.set_xticklabels(index)
        ax.legend()
        
        st.pyplot(fig)
    else:
        st.write("Ingen tall funnet i dokumentet.")
else:
    st.write("Vennligst last opp en PDF-fil.")

