# 21KHDL-TikTok-Analytics

- Lịch họp cố định: 15h T3 hàng tuần

# TODO: Đến 15h CN, ngày 09/02/2025

- Tìm template để làm slide cho bài thuyết trình (Canva)
  - Yêu cầu: sáng màu
  - Lực
- Trình bày 3 đề tài
  - Hãn
- Soạn nội dung và làm slide cho phần "Thu thập dữ liệu TikTok" (dùng unofficial API)
  - Tín
- Soạn nội dung và làm slide cho phần "Các công nghệ được sử dụng" (Spark, Airflow, ...)
  - Phát
- Viết code để convert từ JSON sang CSV, code phải có khả năng duyệt qua tất cả folder con và file JSON bên trong
  - Lực (Deadline T3)
- Viết code để trích xuất các thông tin cần thiết từ các video, lưu kết quả vào file CSV, code phải có khả năng duyệt qua tất cả folder con để lấy toàn bộ file .mp4 bên trong
  - Cả nhóm

# TODO: Buổi họp tiếp theo 15h T5, 06/02/2025

## Thu thập dữ liệu

- [Link](https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/vi)
- Quy trình:
  - 1 người làm 2 ngành => 12 ngành (6 người, 1 người - 2 ngành)
  - 1 ngành lấy 5 hashtag hay nhất => 60 hashtag (mỗi người 10 hashtag)
  - 1 hashtag lấy 50 video => 3000 video (mỗi người 500 hàng)
- Danh sách các ngành (max 18):
  1. Trang phục và phụ kiện
  2. Làm đẹp và chăm sóc cá nhân
  3. Giáo dục
  4. Thực phẩm và đồ uống
  5. Trò chơi
  6. Sản phẩm cải tạo nhà
  7. Sản phẩm gia dụng
  8. Dịch vụ đời sống
  9. Tin tức và giải trí
  10. Du lịch
  11. Thể thao và hoạt động ngoài trời
  12. Công nghệ và đồ điện tử

### Phân công

- Hãn: 1 + 2
- Lực: 3 + 4
- Hiếu: 5 + 6
- Mỹ: 7 + 8
- Tín: 9 + 10
- Phát: 11 + 12

## Setup môi trường

### Các công cụ cần cài đặt

- Hadoop:
- Spark:
- Airflow: https://www.youtube.com/watch?v=K9AnJ9_ZAXE&list=PLwFJcsJ61oujAqYpMp1kdUBcPG0sE0QMT&index=1

# Công cụ được sử dụng cho các bước chính trong quá trình phân tích

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

# Vai trò của các thành viên trong nhóm

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
