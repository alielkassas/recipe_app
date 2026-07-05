import streamlit as st
import pandas as pd


df = pd.read_csv('salaryy.csv')
st.write(df)