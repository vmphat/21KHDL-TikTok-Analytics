import pandas as pd
import ast
from video_analysis.config import COLUMN_LABELS


def parse_list_column(value):
    try:
        parsed = ast.literal_eval(value) if isinstance(
            value, str) and value.startswith('[') else value
        return parsed if isinstance(parsed, list) else [parsed]
    except:
        return [value]


def load_data(path):
    df = pd.read_csv(path)
    list_columns = list(COLUMN_LABELS.keys())  # từ config
    for col in list_columns:
        if col in df.columns:
            df[col] = df[col].apply(parse_list_column)
    # loại "Audio không liên quan ẩm thực"
    df = df[~df['category'].apply(lambda x: isinstance(
        x, list) and "Audio không liên quan ẩm thực" in x)]
    # df[['has_personal_story', 'has_cta']] = df[[
    #     'has_personal_story', 'has_cta']].astype('bool')
    # print(df.info())
    return df
