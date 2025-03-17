import os
import sys
try:
    import streamlit as st
    from google import genai
except ImportError as e:
    import traceback
    print(f"Error importing required packages: {e}")
    print(traceback.format_exc())
    try:
        # If streamlit is successfully imported, show error in UI
        if 'st' in globals():
            st.error(
                f"Failed to import required packages. Please install them using: pip install -r requirements.txt\n\nError: {e}")
            st.stop()
    except:
        # If we can't even use streamlit, exit the program
        sys.exit(1)


# Define the prompt to be sent
prompt = f"""
I need a detailed explanation on %s. Please include:

- Overview: Define and explain the significance of the topic.  
- Key Points: List and explain essential factors or components of the topic.  
- Examples: Provide examples or case studies related to the topic  
- Challenges: Discuss common challenges or misconceptions.  
- Best Practices: Outline effective strategies or tips.  
- Trends: Identify current trends or future directions.  
- Resources: Suggest additional resources for further learning.  

Ensure the information is clear and concise. Please give the answer in Vietnamese.

Give the answer in format (add newline character after each section):

### Overview  
- [a paragraph]
### Key Points
- [List of key points]
### Examples
- [List of examples]
### Challenges
- [List of challenges]
### Best Practices
- [List of best practices]
### Trends
- [List of trends]
### Resources
- [List of resources]
"""

# App configuration
st.set_page_config(page_title="Research on topics", page_icon="✨")

# Title and description
st.title('Research on topics')
st.markdown("Generate detailed explanations on various topics with AI assistance")


# Main content
topic = st.text_area('Enter your video topic:', height=100,
                     placeholder="For example: 'Food review'")
print(f"Topic: {topic}")

# Generate content when button is pressed
if st.button('Research') and topic:
    try:
        # Research on the topic
        with st.spinner('Researching content...'):
            print(prompt % topic)

            client = genai.Client(
                api_key="AIzaSyBYqr4g63GOBTslf5xP0-AbIcSSlAuvMnM")
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt % topic,
            )

        # Display results
        st.subheader("Generated Content:")
        st.write(response.text)

        # # Expandable sections for additional info
        # with st.expander('Title History'):
        #     st.info(title_memory.buffer)

        # with st.expander('Script History'):
        #     st.info(script_memory.buffer)

        # with st.expander('Wikipedia Research'):
        #     st.info(wiki_research)

        # # Download options
        # st.download_button(
        #     label="Download Script",
        #     data=f"TITLE: {title}\n\n{script}",
        #     file_name="youtube_script.txt",
        #     mime="text/plain"
        # )

    except Exception as e:
        st.error(f"An error occurred: {e}")

elif topic == "":
    st.info("Please enter a topic to research.")
    st.info("For example: Enter 'Food review' and click on the 'Research' button.")
