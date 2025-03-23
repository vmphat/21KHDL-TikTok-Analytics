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
st.set_page_config(page_title="Write Scripts", page_icon="📝")

# Define the legacy prompt to be sent (default prompt)
legacy_prompt = f"""
Topic: %s

Instructions: You are a powerful AI designed to create engaging and high-quality video scripts that can attract millions of views. I need a complete script for a video on the topic provided above. The script should include a catchy hook, an engaging introduction, informative and entertaining content, and a compelling call to action. Follow these detailed steps to create the script:

### Hook:

- Start with an attention-grabbing hook that introduces the topic in an exciting way.
- Use a surprising fact, a question, or a bold statement to draw viewers in.
- Keep the hook under 30 seconds to ensure it's concise and impactful.

### Introduction:

- Briefly introduce yourself and establish credibility.
- Provide a quick overview of what the video will cover.
- Highlight the value the viewer will get from watching the entire video.

### Main Content:

- Break down the topic into clear, easy-to-follow sections.
- Use a mix of informative content, personal anecdotes, and engaging storytelling.
- Include at least three main points or subtopics to keep the content organized.
- Use examples, statistics, and visuals (if applicable) to enhance the explanation.
- Keep the tone conversational and relatable to maintain viewer interest.

### Engagement:

- Ask rhetorical questions to keep viewers thinking and engaged.
- Encourage viewers to leave comments, like the video, and subscribe to the channel.
- Use phrases like “Let me know in the comments” or “What do you think about this?”

### Call to Action:

- End with a strong call to action that tells viewers what to do next.
- Suggest watching another related video, downloading a resource, or following on social media.
- Thank the viewers for watching and remind them to subscribe for more content.

Please give the answer in Vietnamese.

Give the answer in format (add newline character after each section):

### Hook  
- [a paragraph]
### Introduction
- [a paragraph]
### Main Content
- [List of main content]
### Engagement
- [List of engagement]
### Call to Action
- [a paragraph]
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
st.title('📝🔗 Write Scripts')
st.markdown("Generate engaging video scripts with AI assistance")


# Set start session time
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
# Prompt customization section
if 'prompt' not in st.session_state:
    st.session_state.write_script_prompt = legacy_prompt


with st.expander("View/Edit Research Prompt", expanded=False):
    st.markdown("**You can customize the research prompt below:**")
    st.markdown(
        "_This is the instruction sent to the AI model. You can modify it to better suit your needs._")

    # Text area for editing the prompt
    custom_prompt = st.text_area(
        "Customize Prompt Template:",
        # Use the same key as the session state variable
        key=f"2_write_scripts_custom_prompt_{st.session_state.start_time}",
        value=st.session_state.write_script_prompt,
        height=300
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Update Prompt"):
            st.session_state.write_script_prompt = custom_prompt
            st.success("Prompt updated successfully!")

    with col2:
        if st.button("Reset to Default"):
            st.success("Prompt reset to default!")
            st.session_state.write_script_prompt = legacy_prompt
            st.session_state.start_time = time.time()
            st.rerun()

prompt = st.session_state.write_script_prompt
print("Prompt:", prompt)


# Main content
topic = st.text_area('Enter your video topic:', height=100,
                     placeholder="For example: 'Street food for students'")
print(f"Topic: {topic}")

# Generate content when button is pressed
if st.button('Generate Script') and topic:
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
    st.info("For example: Enter 'Street food for students' and click on the 'Generate Script' button.")
