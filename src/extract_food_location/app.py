import streamlit as st
import pandas as pd
import json
import google.generativeai as genai
from tqdm import tqdm
import time
import os
import logging
import plotly.express as px
from collections import Counter
import anthropic  # For Claude
import requests  # For DeepSeek API
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Food Video Transcript Analyzer",
    page_icon="🍜",
    layout="wide",
    initial_sidebar_state="expanded"
)

def setup_gemini_api(api_key=None, model_name=None):
    """Setup Gemini API with provided key or from environment"""
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")
    
    if not model_name:
        model_name = 'models/gemini-2.0-flash-thinking-exp-1219'
        
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)

def setup_claude_api(api_key, model_name):
    """Setup Claude API with user provided key"""
    client = anthropic.Anthropic(api_key=api_key)
    return client, model_name

def setup_deepseek_api(api_key, model_name):
    """Setup DeepSeek API with user provided key"""
    return api_key, model_name

def create_prompt(transcript):
    """Creates a well-structured prompt for the model based on the provided transcript."""
    prompt = f"""
    Phân tích transcript video sau và trích xuất thông tin:
    {transcript}

    Yêu cầu: Phân tích transcript video ẩm thực và trích xuất thông tin cấu trúc cho CSV:

    1. PHÂN LOẠI VIDEO (dựa trên từ khóa trong transcript):
    - "Review đồ ăn": Từ khóa: review, đánh giá, thử món, quán này, vị, ngon/dở, giá
    - "Nấu ăn": Từ khóa: công thức, nguyên liệu, cách làm, bước, chế biến, đun, cắt
    - "Mukbang": Từ khóa: ăn cùng, ăn thật nhiều, ăn nguyên/hết, no quá
    - "Khác": Không thuộc các nhóm trên

    2. THÔNG TIN TRÍCH XUẤT THEO LOẠI:
    REVIEW ĐỒ ĂN:
    - món_chính: [tên các món chính]
    - địa_điểm: [thành phố, quận, đường]
    - đánh_giá: [tích cực/tiêu cực/trung lập]

    NẤU ĂN:
    - món_chính: [tên món]
    - món_phụ: [nếu có]
    - nguyên_liệu: [danh sách chính]
    - đánh_giá: [tích cực/tiêu cực/trung lập]

    MUKBANG:
    - món_chính: [tên các món]
    - số_người: [nếu đề cập]
    - đánh_giá: [tích cực/tiêu cực/trung lập]

    KHÁC:
    - chủ_đề: [chủ đề chính]
    - từ_khóa: [3-5 từ khóa]
    - tóm_tắt: [1-2 câu]

    3. THÔNG TIN CHUNG (nếu được đề cập):
    - giá_cả: [giá từng món/tổng]
    - tên_quán: [tên nhà hàng/quán]
    - giờ_hoạt_động: [giờ mở/đóng cửa]
    - số_người: [số người tham gia]
    
    Trả lời dưới dạng JSON để dễ xử lý.
    """
    return prompt

def extract_json_from_response(response_text):
    """Extract and parse JSON from API response text."""
    try:
        if "```json" in response_text and "```" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.rfind("```")
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.rfind("```")
            response_text = response_text[json_start:json_end].strip()
        
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        # Return a basic structure if parsing fails
        return {
            "loại_video": "Không xác định",
            "món_chính": [],
            "địa_điểm": [],
            "giá_cả": ""
        }

def process_transcript(model_provider, model, transcript, idx, retry_count=3):
    """Process a single transcript using the selected model with retries"""
    for attempt in range(retry_count):
        try:
            # Format the prompt with the transcript
            prompt = create_prompt(transcript)
            
            if model_provider == "Gemini":
                # Generate response from Gemini model
                response = model.generate_content(prompt)
                response_text = response.text
            
            elif model_provider == "Claude":
                client, model_name = model
                # Generate response from Claude model
                response = client.messages.create(
                    model=model_name,
                    max_tokens=4096,
                    messages=[{"role": "user", "content": prompt}]
                )
                response_text = response.content[0].text
            
            elif model_provider == "DeepSeek":
                api_key, model_name = model
                # Generate response from DeepSeek model
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": model_name,
                    "messages": [{"role": "user", "content": prompt}]
                }
                response = requests.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers=headers,
                    json=payload
                )
                response_text = response.json()["choices"][0]["message"]["content"]
            
            # Parse the response as JSON
            result = extract_json_from_response(response_text)
            if result:
                result["row_index"] = idx
                return result
                
            logger.warning(f"Failed to parse response for transcript {idx}, attempt {attempt+1}/{retry_count}")
            if attempt < retry_count - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                
        except Exception as e:
            logger.error(f"Error processing transcript {idx}, attempt {attempt+1}/{retry_count}: {str(e)}")
            if attempt < retry_count - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
    
    logger.error(f"Failed to process transcript {idx} after {retry_count} attempts")
    return {
        "row_index": idx,
        "loại_video": "Lỗi xử lý",
        "món_chính": [],
        "địa_điểm": [],
        "giá_cả": ""
    }

def analyze_results(results):
    """Analyze the extracted information"""
    # Convert results list to DataFrame
    df = pd.DataFrame(results)
    
    # Initialize analysis dict
    analysis = {}
    
    # Count video types
    video_types = df['loại_video'].value_counts() if 'loại_video' in df.columns else None
    
    # Extract and count foods mentioned
    foods = []
    locations = []
    prices = []
    
    for result in results:
        if isinstance(result, dict):
            if 'món_chính' in result:
                if isinstance(result['món_chính'], list):
                    foods.extend(result['món_chính'])
                elif isinstance(result['món_chính'], str):
                    foods.append(result['món_chính'])
            
            if 'địa_điểm' in result and result['địa_điểm']:
                if isinstance(result['địa_điểm'], list):
                    locations.extend(result['địa_điểm'])
                elif isinstance(result['địa_điểm'], str):
                    locations.append(result['địa_điểm'])
            
            if 'giá_cả' in result and result['giá_cả']:
                prices.append(result['giá_cả'])

    analysis['food_counts'] = Counter(foods)
    analysis['location_counts'] = Counter(locations)
    analysis['video_types'] = video_types
    
    return analysis

def save_results(results, output_dir="analyzed_results"):
    """Save analysis results to JSON and CSV files."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    json_output = os.path.join(output_dir, f"transcript_analysis_{timestamp}.json")
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    results_df = pd.DataFrame(results)
    csv_output = os.path.join(output_dir, f"transcript_analysis_{timestamp}.csv")
    results_df.to_csv(csv_output, index=False)
    
    return results_df

def get_api_signup_link(provider):
    """Return the appropriate API signup/documentation link"""
    if provider == "Gemini":
        return "https://aistudio.google.com/app/apikey"
    elif provider == "Claude":
        return "https://www.anthropic.com/api"
    else:  # DeepSeek
        return "https://platform.deepseek.com/"

def main():
    st.title("🍜 Food Video Transcript Analyzer")
    st.markdown("---")
    
    with st.expander("ℹ️ About this tool", expanded=False):
        st.markdown("""
        This tool analyzes food-related video transcripts to extract structured information about:
        - Video type (food review, cooking tutorial, mukbang, etc.)
        - Main dishes mentioned
        - Locations
        - Prices and other metadata
        
        Upload a CSV or Excel file containing transcripts to begin.
        """)
    
    # Sidebar for configurations
    st.sidebar.header("⚙️ Configuration")
    
    # Model provider selection
    model_provider = st.sidebar.selectbox(
        "Select Model Provider",
        ["Gemini", "Claude", "DeepSeek"]
    )
    
    # Add API signup/documentation link
    api_link = get_api_signup_link(model_provider)
    st.sidebar.markdown(f"[Get {model_provider} API key]({api_link})")
    
    # Model selection based on provider
    if model_provider == "Gemini":
        model_options = [
            "models/gemini-2.0-flash-thinking-exp-1219",
            "models/gemini-pro",
            "models/gemini-1.5-pro",
            "models/gemini-1.0-pro"
        ]
        selected_model = st.sidebar.selectbox("Select Gemini Model", model_options)
        api_key = st.sidebar.text_input("Enter Gemini API Key", value=os.getenv("GEMINI_API_KEY", ""), type="password")
        
    elif model_provider == "Claude":
        model_options = [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
        selected_model = st.sidebar.selectbox("Select Claude Model", model_options)
        api_key = st.sidebar.text_input("Enter Claude API Key", value=os.getenv("ANTHROPIC_API_KEY", ""), type="password")
        
    else:  # DeepSeek
        model_options = [
            "deepseek-chat",
            "deepseek-coder",
            "deepseek-llm-67b-chat"
        ]
        selected_model = st.sidebar.selectbox("Select DeepSeek Model", model_options)
        api_key = st.sidebar.text_input("Enter DeepSeek API Key", value=os.getenv("DEEPSEEK_API_KEY", ""), type="password")
    
    # API validation notification
    if api_key:
        st.sidebar.success(f"✅ {model_provider} API key configured!")
    
    # Advanced settings in expander
    with st.sidebar.expander("Advanced Settings"):
        retry_count = st.slider("API Retry Count", min_value=1, max_value=5, value=3)
        chart_height = st.slider("Chart Height", min_value=300, max_value=700, value=400)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Analysis Options")
    show_data_preview = st.sidebar.checkbox("Show Data Preview", value=True)
    show_detailed_results = st.sidebar.checkbox("Show Detailed Results", value=True)
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    with col1:
        uploaded_file = st.file_uploader("📂 Upload CSV/Excel file with transcripts", type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file:
        try:
            # Load data with spinner for better UX
            with st.spinner("Loading data..."):
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ File '{uploaded_file.name}' uploaded successfully!")
            
            # Determine transcript column
            transcript_column = 'transcript' if 'transcript' in df.columns else df.columns[0]
            st.info(f"Using column '{transcript_column}' for analysis")
            
            # Show data preview if selected
            if show_data_preview:
                st.subheader("Data Preview")
                st.dataframe(df.head(3), use_container_width=True)
            
            # Check if API key is provided
            if not api_key:
                st.warning("⚠️ Please provide an API key in the sidebar to proceed.")
            else:
                start_analysis = st.button("🚀 Start Analysis", type="primary")
                
                if start_analysis:
                    results = []
                    
                    # Set up the selected model with status indicator
                    with st.spinner(f"Setting up {model_provider} model..."):
                        if model_provider == "Gemini":
                            model = setup_gemini_api(api_key, selected_model)
                        elif model_provider == "Claude":
                            model = setup_claude_api(api_key, selected_model)
                        else:  # DeepSeek
                            model = setup_deepseek_api(api_key, selected_model)
                    
                    # Process transcripts with improved progress information
                    st.subheader("Processing Transcripts")
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    time_estimate = st.empty()
                    
                    start_time = time.time()
                    skipped_count = 0
                    
                    for idx, row in enumerate(df.iterrows()):
                        # More detailed status with ETA calculation
                        elapsed = time.time() - start_time
                        if idx > 0:
                            estimated_total = elapsed * len(df) / idx
                            remaining = estimated_total - elapsed
                            time_estimate.text(f"⏱️ Estimated time remaining: {remaining:.1f} seconds")
                        
                        status_text.text(f"🔄 Processing transcript {idx+1}/{len(df)}")
                        
                        if pd.isna(row[1][transcript_column]) or row[1][transcript_column] == "":
                            logger.warning(f"Skipping row {idx}: empty transcript")
                            skipped_count += 1
                            continue
                            
                        result = process_transcript(model_provider, model, row[1][transcript_column], idx, retry_count)
                        results.append(result)
                        progress_bar.progress((idx + 1) / len(df))
                        time.sleep(0.5)  # Rate limiting
                    
                    if skipped_count > 0:
                        st.warning(f"⚠️ Skipped {skipped_count} empty transcripts.")
                    
                    # Save results
                    with st.spinner("Saving and analyzing results..."):
                        results_df = save_results(results)
                    st.success("✅ Analysis completed and results saved!")
                    
                    # Analyze results
                    analysis = analyze_results(results)
                    
                    # Display analysis results in tabs for better organization
                    st.subheader("📊 Analysis Results")
                    tabs = st.tabs(["Video Types", "Food Mentions", "Locations"])
                    
                    with tabs[0]:
                        # Video Types Distribution
                        if analysis.get('video_types') is not None:
                            st.write("#### Video Types Distribution")
                            fig = px.pie(values=analysis['video_types'].values, 
                                       names=analysis['video_types'].index,
                                       title="Video Categories",
                                       height=chart_height)
                            fig.update_traces(textposition='inside', textinfo='percent+label')
                            st.plotly_chart(fig, use_container_width=True)
                    
                    with tabs[1]:
                        # Most Mentioned Foods with improved labels and sorting
                        st.write("#### Most Mentioned Foods")
                        food_df = pd.DataFrame.from_dict(analysis['food_counts'], 
                                                       orient='index', 
                                                       columns=['count']).reset_index()
                        food_df.columns = ['Food', 'Count']
                        food_df = food_df.sort_values('Count', ascending=False).head(15)
                        
                        fig = px.bar(food_df, x='Food', y='Count',
                                    title="Top Food Mentions",
                                    labels={'Count': 'Number of Mentions', 'Food': 'Food Name'},
                                    height=chart_height)
                        fig.update_xaxes(tickangle=45)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with tabs[2]:
                        # Location Distribution with improved labels
                        st.write("#### Location Distribution")
                        location_df = pd.DataFrame.from_dict(analysis['location_counts'], 
                                                           orient='index', 
                                                           columns=['count']).reset_index()
                        location_df.columns = ['Location', 'Count']
                        location_df = location_df.sort_values('Count', ascending=False).head(15)
                        
                        fig = px.bar(location_df, x='Location', y='Count',
                                    title="Top Locations Mentioned",
                                    labels={'Count': 'Number of Mentions', 'Location': 'Location Name'},
                                    height=chart_height)
                        fig.update_xaxes(tickangle=45)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Show detailed results in expandable section if selected
                    if show_detailed_results:
                        with st.expander("Detailed Results"):
                            st.dataframe(results_df, use_container_width=True)
                    
                    # Download options in a cleaner format
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="📥 Download CSV Results",
                            data=results_df.to_csv(index=False).encode('utf-8'),
                            file_name=f'analysis_results_{time.strftime("%Y%m%d-%H%M%S")}.csv',
                            mime='text/csv'
                        )
                    with col2:
                        # Add JSON download option
                        json_data = json.dumps(results, ensure_ascii=False, indent=2)
                        st.download_button(
                            label="📥 Download JSON Results",
                            data=json_data.encode('utf-8'),
                            file_name=f'analysis_results_{time.strftime("%Y%m%d-%H%M%S")}.json',
                            mime='application/json'
                        )
                    
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            logger.error(f"Error in main application: {e}", exc_info=True)
    
    else:
        st.info("Please upload a file and configure an API key to begin analysis.")
        st.markdown("""
        ### Getting Started:
        1. Select a model provider in the sidebar
        2. Enter your API key
        3. Upload a CSV or Excel file with transcripts
        4. Click "Start Analysis"
        """)

if __name__ == "__main__":
    main()