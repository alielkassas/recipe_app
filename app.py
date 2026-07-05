import streamlit as st
import pandas as pd


df = pd.read_csv('data/salaryy.csv')
print(df.head())
print("Done")
st.write(df)