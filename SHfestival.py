import streamlit as st
import random

a = random.randint(1,5)
st.title("소수인가?")
st.latex(a)

st.button("another", type="primary")
if st.button("another"):
  a = random.randint(1,5)
  st.latex(a)
