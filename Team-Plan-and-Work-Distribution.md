# 21KHDL-TikTok-Analytics

- Lịch họp cố định:
  - 14h T3 hàng tuần
  - 14h T6 hàng tuần

# TODO: 14h T6, 18/04/2025

- Viết báo cáo cuối kỳ trên Overleaf
  - Link: https://www.overleaf.com/project/68078b37211771149621ef34

```
Danh sách thành viên và Bảng mức độ đóng góp

Chương 1: Giới thiệu chung
- Giới thiệu chung về đồ án
- Tóm tắt về công nghệ được sử dụng trong đồ án
  - TikTok-API (unofficial), Gemini API, Plotly, Streamlit, Streamlit Community Cloud, v.v.
  - AI để phân tích dữ liệu
  - st.Page để merge các page
  - st.cache để cache dữ liệu
  - File parquet để keep datatype
  - Dùng Gemini API để tạo báo cáo
  - v.v.


[Hãn]
Chương 2: Thu thập dữ liệu
- Nhấn mạnh rằng dùng TikTok-API (unofficial) để thu thập dữ liệu
- Có 2 tập dữ liệu chính: video-data + user-data


[Phát]
Chương 3: Tiền xử lý dữ liệu
- Trình bày giống trong file notebook
- Rút trích transcript
- Rút trích món ăn và địa điểm


[Hãn]
Chương 4: Webapp tạo kịch bản (dashboard + tools)
- Rút trích ... của Hãn
- Trình bày webapp


[Lực]
Chương 5: Dashboard phân tích user
- Filter + Loại biểu đồ + Nhận xét + v.v.


[C.Mỹ]
Chương 6: Dashboard phân tích video
- Câu hỏi: Vào thời điểm nào trong tuần/tháng/năm thì video được đăng tải nhiều? Có lượt tương tác nhiều không?
- Filter + Loại biểu đồ + Nhận xét + v.v.


[Tín]
Chương 7: Dashboard phân tích xu hướng
- Filter + Loại biểu đồ + Nhận xét + v.v.


[Phát]
Chương 8: Một vài công cụ bổ sung
- Một vài webapp hỗ trợ nghiên cứu


[Phát]
Chương 9: Hướng phát triển trong tương lai
- Dùng airflow để tự động hóa pipeline (ưu điểm: vì chỉ dùng API nên đảm bảo thời gian xử lý nhanh hơn)
- Tập trung vào các chart để trả lời các câu hỏi người dùng muốn nghe

```

## Tiền xử lý dữ liệu

- Viết mô tả cho các bước tiền xử lý dữ liệu
- Có thể chèn code nếu cần
- Trình bày kết quả sau bước tiền xử lý dữ liệu

## Trực quan hóa và phân tích dữ liệu

- Có thể viết mô tả ngắn gọn cho các bước code để trực quan hóa dữ liệu
- Giới thiệu các tính năng mà người dùng có thể thực hiện trên dashboard
- Chụp hình chart, dashboard và chèn vào báo cáo
- Viết nhận xét cho các chart, dashboard

# Insights phân tích dashboard

## Lực

- Số lượt `follower` tương quan thuận với lượt `heart`

## Tín

- Tập dữ liệu có 70 tuần, mỗi tuần nhóm sẽ trích ra top 20% video có điểm số cao nhất để tiến hành phân tích các món ăn và địa điểm được để cập trong video.

# TODO: Lịch họp giai đoạn cuối

- Tối CN (06/04): 21h => Cố gắng hoàn tất toàn bộ dashboard và webapp + Tập dợt trình bày báo cáo cuối kỳ lần 1
- Chiều T2 (07/04): 14h => Tập dợt trình bày báo cáo cuối kỳ lần 2
- Chiều T3 (08/04): 14h => Tập dợt trình bày báo cáo cuối kỳ lần 3
- Tối T3 (08/04): 20h => Tập dợt trình bày báo cáo cuối kỳ lần 4
- Sáng T4 (09/04) => Chính thức báo cáo cuối kỳ

## Note

- Toàn bộ Dashboard và Webapp sẽ sử dụng ngôn ngữ tiếng Việt để tạo ra sự thống nhất trong việc trình bày và sử dụng
- Tại vì có 2 nhóm cùng báo cáo nên nhóm mình sẽ có khoảng 45 phút để trình bày kết quả đạt được sau đồ án lần này
- Mỗi người sẽ có khoảng 6 phút để trình bày phần của mình, mọi người cố gắng tận dụng thời gian này để trình bày càng chi tiết càng tốt
- Trình bày dashboard: Đi từ tổng quan đến chi tiết
  - Tổng quan: Không dùng filter gì cả mà nhận xét trực tiếp trên dashboard
  - Chi tiết: Sẽ dùng các filter để phân tích chi tiết hơn về một khía cạnh nào đó của dashboard (như: tập trung hơn về 1 user, 1 hashtag, 1 món ăn, 1 vùng/miền, v.v. nào đó)
- Trong phần trình bày, khuyến khích mọi người đưa ra những nhận xét của cá nhân xung quanh kết quả phân tích dữ liệu vì đây là phần ăn điểm. Nhận xét cá nhân này có thể theo hình thức formal là thông tin từ báo đài hoặc informal theo cách mọi người yapping về các vấn đề của xã hội hiện tại
  - Ví dụ: Quận 10 Thành phố Hồ Chí Minh là nơi được đề cập nhiều nhất trong các video về món ăn, vì quận 10 nổi tiếng với các con đường ẩm thực "Hồ Thị Kỷ", "Nguyễn Tri Phương", v.v.. Đồng thời quận 10 cũng là nơi tọa lạc của nhiều trường học nên các hàng quán mọc lên rất nhiều để phục vụ cho các bạn học sinh, sinh viên. Do đó, quận 10 là nơi có nhiều video về món ăn nhất trong các video TikTok hiện tại.

# TODO: 14h T3, 24/04/2025

- Bổ sung công nghệ:
  - Lưu dữ liệu thành file parquet để giữ nguyên kiểu dữ liệu của cột

# TODO: 21h CN, 23/03/2025

- Phát:
  - Viết file Preprocessing.ipynb để xử lý dữ liệu
  - Viết web tạo kịch bản
  - Hỏi thầy xem có nên gộp các web app lại với nhau hay không?
    - Có: deploy 1 web app duy nhất
    - Không: 4 web app riêng biệt
  - Trình bày công nghệ: Xử lý dữ liệu + Deploy web app
  - Trình bày cấu trúc prompt cho viết kịch bản
- Hãn:
  - Rút thêm đặc trưng trong dữ liệu
  - Phân tích dashboard
- Tín:
  - Cấu trúc prompt cho: tên món ăn, giá cả, giờ mở cửa, v.v.
- Làm slide: Hãn + Phát + Tín
- 3 dashboards chính:
  1. Thống kê từ user (Lực)
  2. Thống kê từ video (Mỹ)  
     => Trả lời: Tần suất đăng video như thế nào? Thời lượng video tối ưu? Số lượng hashtag tối ưu?
  3. Insights cho việc viết kịch bản (Hãn)
- Công nghệ nổi bật trong dự án:
  - Thu thập dữ liệu: TikTok API (unofficial)
  - Tiền xử lý dữ liệu: Dùng Gemini (multimodal) API để tách transcript và các cột khác
  - Dashboard: Plotly + Streamlit + Deploy lên Cloud Community
    - Dùng AI để phân tích dữ liệu
  - Web hỗ trợ tạo kịch bản: Prompting

# TODO: 14h T6, 14/03/2025

- Team tiền xử lý dữ liệu: Phát, Hãn, Tín
- Team phân tích dữ liệu và rút insights: Lực, Mỹ, Tín, Phát

  - Dùng thư viện trực quan hóa dữ liệu có thể tương tác được (ví dụ: Plotly, v.v.)
  - **Phân tích theo video** (trọng tâm): Mỹ
    - Phân tích tương quan:
      - số vs số => scatter Plot
      - số vs phân loại => bar chart, heatmap
  - Phân tích theo user (sẽ group by userId trong tập dữ liệu video): Lực

  `*.save_fig() => .png/.jpg => gemini => rút insights`

- Team làm web app để tạo kịch bản: Hiếu, Hãn

# TODO: Đến 15h T3, ngày 11/03/2025

- Lọc dữ liệu từ transcription, lọc lại các cột dữ liệu trong video_info
- Trình bày thu thập + xử lý dữ liệu + công nghệ bên dưới:
  - Tên mô hình + Tên tác vụ + Số lượng tham số

# TODO: Đến 15h T3, ngày 04/03/2025

- Thu thập dữ liệu: Hãn
- Trích xuất nội dung thêm từ video:
  - Phát: Tìm hiểu cách xử lý video mà không cần tải xuống

# TODO: Đến 15h T6, ngày 28/02/2025

- Tập trung tìm hiểu về danh sách các TikToker trong lĩnh vực ẩm thực

# TODO: Đến 15h T3, ngày 25/02/2025

1. Phát: Trình bày data pipeline, kết quả thu thập dữ liệu (mẫu), khai thác được gì từ video
2. Hãn: Trình bày hiện tại có bao nhiêu mẫu dữ liệu rồi (100 noxscore, 1 tháng trở lại) => 1000 mẫu, 100 trường
3. Tín, Lực, Hiếu: Trình bày phân tích dữ liệu, cleaning trên text, cắt frame để xem hoạt ảnh của video có ảnh hưởng lượt view không
4. Tiếp tục tìm hiểu về cách trích xuất nội dung từ video

# TODO: Đến 15h T6, ngày 21/02/2025

- Trình bày data pipeline (code chạy được), kết quả thu thập dữ liệu, khai thác được gì từ video
  - Data pipeline: Phát (Lấy dữ liệu, trích xuất audio, audio2text, flatten JSON)
  - Thu thập dữ liệu: Hãn
- Trực quan hóa dữ liệu (trình bày một mẫu dashboard đơn giản), phân tích dữ liệu, và rút ra insights
  - Dữ liệu mẫu: https://github.com/vphuhan/21KHDL-TikTok-Analytics/blob/vmphat/data/interim/video_info.csv
  - Dữ liệu chính thức: Phát upload sau
  - Dùng Plotly + Streamlit
  - Lực, Tín và Hiếu
- Tìm thêm TikToker trong các lĩnh vực: Lấy ~20 người TikToker, nên chọn người Việt, nên chọn người nổi tiếng
  - Công nghệ: Tín
  - Ẩm thực (Food reviewer): Hiếu
  - Thể dục thể thảo, gym, đời sống, thời trang, trang điểm, làm đẹp: Hãn
  - Việc làm, viết CV, hướng dẫn học (ngành giáo dục): Lực
  - Du lịch, khám phá: Phát  
    => Lấy: username (ví dụ erikkkofficial, không lấy ký tự @) rồi bỏ vào code để lấy video sau.

# TODO: Đến 15h T3, ngày 18/02/2025

- Tín: Tạo thành file CSV, viết bảng mô tả cho các cột trong 1 file notebook riêng
- Phát: Tách audio từ video, chuyển audio thành text
- Lực: tui làm data image caption cho các frame trong folder video

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
