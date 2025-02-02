# 21KHDL-TikTok-Analytics

## TODO: Trước buổi họp tiếp theo (15h, T3 ngày 04/02)

- Setup môi trường
- Thu thập dữ liệu

## Các công cụ cần cài đặt

- Hadoop:
- Spark:
- Airflow: https://www.youtube.com/watch?v=K9AnJ9_ZAXE&list=PLwFJcsJ61oujAqYpMp1kdUBcPG0sE0QMT&index=1

## Công cụ được sử dụng cho các bước chính trong quá trình phân tích

- Thu thập dữ liệu:
  - Python + TikTok API (unofficial)
- Xử lý dữ liệu:
  - PySpark
- Trực quan hóa dữ liệu và rút trích insights (kết hợp LLMs để hỗ trợ):
  1. Tự code: Plotly + Streamlit (Ưu tiên cao hơn)
  2. Tools: Tableau, PowerBI,
- (Optional) Giải quyết 1 bài toán học máy:
  - Dùng LLMs để hỗ trợ:
    - Viết mô tả (Description) cho video,
    - Đề xuất các hashtag phổ biến dựa trên wordcloud
    - Đề xuất nhạc nền (audio) cho video

## Vai trò của các thành viên trong nhóm

- Thu thập dữ liệu: Hãn, Hiếu, Tín
- Xử lý dữ liệu: Phát, Hãn, Tín, Lực, Mỹ
- Trực quan hóa dữ liệu và rút trích insights (kết hợp LLMs để hỗ trợ): Phát, Tín, Lực, Mỹ
- (Optional) Giải quyết 1 bài toán học máy: Phát, Hãn, Hiếu, Tín

# Meeting 25/01/2025

## Chủ đề phân tích dữ liệu

- Phân tích dữ liệu TikTok
- Mình là 1 công ty quản lý nhiều TikTok-er
- End-user:
  - **Doanh nghiệp**: Giúp doanh nghiệp lựa chọn KOL phù hợp nhất (trong số các TikTok-er mà mình đang quản lý) cho chiến lược quảng cáo của mình

## Câu hỏi cần giải quyết

- Câu hỏi 1: Phân tích video đang trending trên TikTok
- Câu hỏi 2: Phân tích đặc điểm của các TikTok-er có nhiều followers nhất

## Công nghệ được sử dụng

- Spark xử lý dữ liệu và Lưu local
  - Đẩy kết quả cuối cùng lên cloud để các thành viên lấy dữ liệu
