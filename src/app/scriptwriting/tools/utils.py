import json
# from google import genai
from google.genai import types
import time
import pandas as pd

CONFIG_DIR = "src/app/scriptwriting/tools/config"


def filter_by_multiple_labels_unified(df, conditions, soft_fields=None, min_count=10):
    """
    Filter a dataframe based on initial conditions with a "relaxation" process:
    - Start with full conditions
    - Process fields in priority order: soft fields first, then strict fields
    - For each field (except 'categories'), gradually reduce labels until we have enough videos (>= min_count)
    - If still not enough, remove the field completely (except 'categories')

    Parameters:
    - df: pandas DataFrame to filter
    - conditions: dict of field -> list of labels to filter on
    - soft_fields: list of field names that can be relaxed first (default priority order)
    - min_count: minimum number of rows required in result

    Returns:
    - Filtered DataFrame with relaxed conditions if necessary
    """
    print(conditions)
    # Input validation
    if df is None or df.empty:
        print("DataFrame is empty or None")
        return df

    if conditions is None or not conditions:
        return df

    # Default soft fields if none provided
    if soft_fields is None:
        soft_fields = ["pacing", "audience_target",
                       "content_style", "tone_of_voice", "cta_type"]

    # Ensure all condition values are lists
    fixed_conditions = {k: v if isinstance(
        v, list) else [v] for k, v in conditions.items()}

    # Determine strict fields (those not in soft_fields)
    strict_fields = [f for f in fixed_conditions.keys()
                     if f not in soft_fields]

    # Processing order: soft fields first in their priority order, then strict fields
    field_order = [
        f for f in soft_fields if f in fixed_conditions] + strict_fields

    def apply_filters(dataframe, filter_conditions):
        """Apply all filter conditions to the dataframe"""
        result = dataframe.copy()
        for field, target_labels in filter_conditions.items():
            if field in result.columns and target_labels:  # Check if field exists and labels are not empty
                result = result[result[field].apply(
                    lambda labels: all(lbl in labels for lbl in target_labels))]
        return result

    # First try with all conditions
    test_conditions = fixed_conditions.copy()
    filtered_df = apply_filters(df, test_conditions)

    if len(filtered_df) >= min_count:
        print("Final condition (full):", test_conditions)
        print(filtered_df.shape)
        return filtered_df

    best_df = filtered_df  # Track the best result so far

    # Process fields in priority order
    for field in field_order:
        # Never relax 'categories' field
        if field == "categories" or field not in test_conditions:
            continue

        original_labels = test_conditions[field].copy()
        if not original_labels:  # Skip if empty list
            continue

        # Try removing labels one by one from the end
        for i in range(1, len(original_labels) + 1):
            candidate_labels = original_labels[:-i]

            # Skip if we'd end up with empty list (will be handled in the field removal step)
            if not candidate_labels:
                continue

            test_conditions[field] = candidate_labels
            filtered_df = apply_filters(df, test_conditions)

            print(
                f"Trying {field} with labels {candidate_labels}: {len(filtered_df)} results")

            if len(filtered_df) >= min_count:
                print("Final condition:", test_conditions)
                print(filtered_df.shape)
                return filtered_df

            # Keep track of best result
            if len(filtered_df) > len(best_df):
                best_df = filtered_df

        # If relaxing labels didn't help enough, try removing the field completely
        if field != "categories":
            del test_conditions[field]
            filtered_df = apply_filters(df, test_conditions)
            print(f"Removed field {field}: {len(filtered_df)} results")

            if len(filtered_df) >= min_count:
                print("Final condition:", test_conditions)
                print(filtered_df.shape)
                return filtered_df

            # Keep track of best result
            if len(filtered_df) > len(best_df):
                best_df = filtered_df

    print("Couldn't meet minimum count requirement. Returning best result with", len(
        best_df), "rows")
    print(best_df.shape)
    return best_df


def load_prompt(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def load_schema(path: str) -> dict:
    """Load JSON schema from given file path."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_labels_from_description(user_description, client, model):

    label_schema = load_schema(CONFIG_DIR+'/label_schema.json')

    annotate_user_desc_function = {
        "name": "filter_by_multiple_labels",
        # "description": "Dựa trên miêu tả của người dùng về video họ muốn thực hiện, tiến hành gán nhãn cho các trường được định trước.",
        "description": "Dựa trên miêu tả của người dùng về video họ muốn thực hiện, tiến hành lọc ra các video phù hợp với mô tả của người dùng.",
        "parameters": label_schema
    }

    system_instruction = load_prompt(CONFIG_DIR+'/label_instruction.md')

    prompt = "Dựa trên miêu tả của người dùng về video họ muốn thực hiện, tiến hành gán nhãn cho các trường được định trước.\n\n" + \
        f"Miêu tả: {user_description}"

    # Configure the client and tools

    tools = types.Tool(function_declarations=[annotate_user_desc_function])
    config = types.GenerateContentConfig(
        tools=[tools],
        # system_instruction=system_instruction,
        temperature=0.1,
        top_k=15,
        top_p=0.9
    )
    # Send request with function declarations
    response_filter = client.models.generate_content(
        model="gemini-2.0-flash",
        # model=model,
        contents=[system_instruction, prompt],
        config=config,
    )

    tool_call = response_filter.candidates[0].content.parts[0].function_call

    return tool_call.args if tool_call else None


def format_transcript_desc_examples(user_desc_filter_df, min_count=20):
    today = pd.Timestamp.now(tz='Asia/Ho_Chi_Minh')

    # Tính số ngày kể từ khi tạo video
    user_desc_filter_df['days_since'] = (
        today - user_desc_filter_df['createTime']).dt.days
    alpha = 0.7
    user_desc_filter_df['score'] = user_desc_filter_df['statsV2.playCount'] / \
        ((user_desc_filter_df['days_since'] + 1) ** alpha)
    sorted_df = user_desc_filter_df.sort_values(by='score', ascending=False)
    example_df = sorted_df.head(min_count)

    def create_examples(df, col):
        return "\n\n".join(
            [f"{i}. {t}" for i, t in enumerate(df[col], 1)]
        )

    transcript_sample_text = create_examples(example_df, 'transcript')
    desc_sample_text = create_examples(example_df, 'desc')
    return transcript_sample_text, desc_sample_text


def generate_plain_script(
        user_input, transcript_sample_text, word_count, client, model, max_output_tokens=2000000):

    prompt_input = {'user_input': user_input,
                    'transcript_sample_text': transcript_sample_text,
                    'word_count': word_count}

    prompt_plain_script = load_prompt(
        CONFIG_DIR+'/plain_script_prompt.md').format(**prompt_input)

    config = {
        'maxOutputTokens': max_output_tokens} if not model in (["gemini-2.0-flash-thinking-exp-1219", "gemini-2.5-pro-exp-03-25"]) else None
    response_plain_script = client.models.generate_content(
        # model="gemini-2.0-flash-thinking-exp-1219",
        # model="gemini-2.0-flash",
        model=model,
        contents=[prompt_plain_script],
        config=config,
    )

    print(response_plain_script.usage_metadata)
    return response_plain_script.text


def format_script_with_gemini(plain_script, desc_sample_text, mean_desc_word_count, mean_word_per_second, mean_hashtag_count, top_10_cat_hashtags_text, client, model):
    script_seconds = len(plain_script.split()) / (mean_word_per_second)
    print("output script words:",  len(plain_script.split()))
    print("output script seconds:",  script_seconds)

    raw_schema = load_schema(
        CONFIG_DIR+'/structured_script_schema.json')
    schema_str = json.dumps(raw_schema)
    schema_str = schema_str.replace(
        "{mean_hashtag_count}", str(mean_hashtag_count)).replace(
        "{mean_desc_word_count}", str(mean_desc_word_count))
    response_structured_script_schema = json.loads(schema_str)

    duration_text = f"{int(script_seconds // 60)} phút {int(script_seconds % 60)} giây"
    prompt_input = {'duration_text': duration_text,
                    'top_10_cat_hashtags_text': top_10_cat_hashtags_text,
                    'desc_sample_text': desc_sample_text,
                    'plain_script': plain_script}

    prompt_structured_script = load_prompt(
        CONFIG_DIR+'/structured_script_prompt.md').format(**prompt_input)

    response_structured_script = client.models.generate_content(
        model="gemini-2.0-flash",
        # model=model,
        contents=[prompt_structured_script],
        config={
            'response_mime_type': "application/json",
            'response_schema': response_structured_script_schema,
            # 'system_instruction': system_instruction,
            # 'temperature': 0.1

        }
    )

    try:
        response_dict = json.loads(response_structured_script.text)
    except json.decoder.JSONDecodeError as e:
        print("JSON decode error:", e)
        return None

    # script_seconds = len(response_plain_script.text.split()) / int(mean_word_per_second)
    # response_dict['duration'] = f"{int(script_seconds // 60)} phút {int(script_seconds % 60)} giây"
    # === Tính lại time_range cho từng đoạn main_content ===

    def seconds_to_mmss(sec):
        minutes = int(sec // 60)
        seconds = int(sec % 60)
        return f"{minutes}:{seconds:02d}"

    current_time = 0.0
    for step in response_dict.get("main_content", []):
        dialogue = step.get("dialogue", "")
        word_count = len(dialogue.split())
        duration = duration = round(word_count / mean_word_per_second, 2)

        start = seconds_to_mmss(current_time)
        end = seconds_to_mmss(current_time + duration)
        step["time_range"] = f"{start}-{end}"

        current_time += duration
    return response_dict
