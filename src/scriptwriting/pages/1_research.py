import os
import sys
try:
    import streamlit as st
    from google import genai
    import time
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


# App configuration
st.set_page_config(page_title="Research on topics",
                   page_icon="✨")


# Define the legacy prompt to be sent (default prompt)
legacy_prompt = f"""
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
""".strip()


# Available AI Models
available_models = [
    # Input token limit: 1,048,576
    # Output token limit: 8,192
    "gemini-2.0-flash",

    # Input token limit 2,048,576
    # Output token limit 8,192
    "gemini-2.0-pro-exp",

    "gemini-2.0-flash-thinking-exp",

    # Input token limit 1,048,576
    # Output token limit 8,192
    "gemini-2.0-flash-lite",

    # Input token limit 1,048,576
    # Output token limit 8,192
    "gemini-1.5-flash",

    # Input token limit 1,048,576
    # Output token limit 8,192
    "gemini-1.5-flash-8b",

    # Input token limit 2,097,152
    # Output token limit 8,192
    "gemini-1.5-pro",

    "learnlm-1.5-pro-experimental",

    "gemma-3-27b-it",
]


def get_model():
    # Function to get the selected model
    return st.sidebar.selectbox(
        "Select AI Model:",
        available_models,
        index=available_models.index("gemini-2.0-flash")
    )


# Get selected model
model = get_model()
print(f"Selected Model: {model}")

# Title and description
st.title('Research on topics')
st.markdown("Generate detailed explanations on various topics with AI assistance")


# Set start session time
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
# Prompt customization section
if 'prompt' not in st.session_state:
    st.session_state.prompt = legacy_prompt


with st.expander("View/Edit Research Prompt", expanded=False):
    st.markdown("**You can customize the research prompt below:**")
    st.markdown(
        "_This is the instruction sent to the AI model. You can modify it to better suit your needs._")

    # Text area for editing the prompt
    custom_prompt = st.text_area(
        "Customize Prompt Template:",
        # Use the same key as the session state variable
        key=f"custom_prompt_{st.session_state.start_time}",
        value=st.session_state.prompt,
        height=300
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Update Prompt"):
            st.session_state.prompt = custom_prompt
            st.success("Prompt updated successfully!")

    with col2:
        if st.button("Reset to Default"):
            st.success("Prompt reset to default!")
            st.session_state.prompt = legacy_prompt
            st.session_state.start_time = time.time()
            st.rerun()

prompt = st.session_state.prompt
print("Prompt:", prompt)


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
                model=model,
                contents=(prompt % topic).strip(),
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
