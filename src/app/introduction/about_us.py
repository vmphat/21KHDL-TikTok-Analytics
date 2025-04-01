import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="About Us",
    # page_icon="",
    layout="wide",
)

st.title("About Us")

# Organization overview
st.header("Who We Are")
st.write("""
We are a team of dedicated professionals committed to excellence and innovation. 
Our mission is to provide cutting-edge solutions that address real-world challenges.
""")

# Our story section
st.header("Our Story")
st.write("""
Founded in 2023, our journey began with a simple vision: to create technology that makes a difference.
Since then, we've grown into a dynamic team working at the intersection of technology and human needs.
""")

# Our values in columns
st.header("Our Values")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Innovation")
    st.write("We push boundaries and explore new possibilities.")

with col2:
    st.subheader("Integrity")
    st.write("We operate with transparency and ethical responsibility.")

with col3:
    st.subheader("Impact")
    st.write("We measure success by the positive change we create.")

# Team section
st.header("Our Team")
team_cols = st.columns(3)

with team_cols[0]:
    st.subheader("Sarah Chen")
    st.write("Chief Executive Officer")
    # st.image("path/to/image.jpg")

with team_cols[1]:
    st.subheader("Alex Rivera")
    st.write("Chief Technology Officer")
    # st.image("path/to/image.jpg")

with team_cols[2]:
    st.subheader("Jamie Taylor")
    st.write("Head of Research")
    # st.image("path/to/image.jpg")

# Contact information
st.header("Get in Touch")
st.write("Email: contact@organization.com")
st.write("Phone: (123) 456-7890")
st.write("Address: 123 Innovation Drive, Tech City, TC 10101")

# Social links
st.write("---")
st.markdown(
    "Connect with us: [LinkedIn](https://linkedin.com) | [Twitter](https://twitter.com) | [GitHub](https://github.com)")
