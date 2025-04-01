# Khoa học dữ liệu ứng dụng - 21KHDL

# Báo cáo tiến độ đồ án cuối kỳ

## Sinh viên thực hiện: Nhóm 05

| STT |   MSSV   | Họ và tên        |
| :-: | :------: | ---------------- |
|  1  | 21127038 | Võ Phú Hãn       |
|  2  | 21127739 | Vũ Minh Phát     |
|  3  | 21127742 | Nguyễn Minh Hiếu |

## Danh sách các tài liệu liên quan đến đồ án cuối kỳ

- File "[TikTokApi_package](TikTokApi_package.url)": Chứa link đến website hướng dẫn sử dụng các module trong package `TikTokApi` để thu thập dữ liệu từ các video trên TikTok.

- File "[Video_to_audio](Video_to_audio.url)": Chứa link đến website hướng dẫn kết hợp 2 package `yt-dlp` và `FFmpeg` để trích xuất âm thanh từ video. Thay vì phải tải file video (thường có dung lượng lớn) về máy, chúng ta có thể trích xuất âm thanh từ video và lưu trữ dưới dạng file audio (thường có dung lượng nhỏ hơn) để tiết kiệm dung lượng lưu trữ. Điều này cũng giúp giảm thời gian xử lý dữ liệu.

- File "[Gemini_API_docs](Gemini_API_docs.url)": Chứa link đến website hướng dẫn sử dụng API của Gemini để thực hiện nhiều tác vụ khác nhau. Trong phạm vi đồ án lần này, nhóm đã sử dụng API của Gemini để:

  - Trích xuất transcript từ video.
  - Sử dụng transcript để trích xuất ra các đặc trưng giúp phân loại video.
  - Phân loại video dựa trên các đặc trưng đã trích xuất.
  - Tạo kịch bản cho video TikTok dựa trên chủ đề mà người dùng mong muốn.
  - v.v.

- File "[Streamlit_dashboard](Streamlit_dashboard.url)": Chứa link đến bài viết hướng dẫn cách tạo ra các dashboard cho phép người dùng _tương tác trực tiếp_ (dùng thư viện `Altair`, `Plotly`, v.v.) thông qua giao diện web (dùng thư viện `Streamlit`).

- File "[Deploy_Streamlit_app](Deploy_Streamlit_app.url)": Chứa link đến tài liệu hướng dẫn cách deploy 1 webapp sử dụng `Streamlit` lên nền tảng **Streamlit Community Cloud** (miễn phí). Thông qua đó, người dùng có thể truy cập đến webapp thông qua đường link mà không cần cài đặt thêm bất kỳ phần mềm nào khác.

- File "[Scriptwriting_prompts](Scriptwriting_prompts.url)": Chứa link đến website cung cấp các gợi ý về cách viết kịch bản cho video. Ta sẽ dựa vào khung kịch bản này để tạo ra các câu prompt phù hợp và gửi đến các AI agent (ví dụ như các model được cung cấp bởi `Gemini API`) để tạo ra kịch bản phù hợp với chủ đề mà người dùng mong muốn.

- File "[TikTok_data_fields](TikTok_data_fields.md)": Chứa các trường dữ liệu mà `TikTokAPI` cho phép lập trình viên truy cập. Các trường dữ liệu này sẽ được sử dụng để phân tích và trích xuất các đặc trưng của video TikTok. Các trường dữ liệu này được chia thành 2 nhóm chính: `VIDEO API` và `USER API`. Trong đó, `VIDEO API` chứa các trường dữ liệu liên quan đến video TikTok, còn `USER API` chứa các trường dữ liệu liên quan đến người dùng TikTok.

- File "[Questions_and_Hypotheses](Questions_and_Hypotheses.pdf)": Chứa các câu hỏi nghiên cứu và giả thuyết mà nhóm đã đưa ra để định hướng cho việc thu thập dữ liệu và phân tích dữ liệu sau này. Tuy nhiên, các câu hỏi này có thể sẽ thay đổi trong quá trình thực hiện đồ án. Các câu hỏi này sẽ được nhóm cập nhật thường xuyên trong quá trình thực hiện đồ án.

- File "[Group_05_Proposal](Group_05_Proposal.pdf)": Chứa đề cương chi tiết cho đồ án cuối kỳ. Trong đó, nhóm đã trình bày rõ ràng các nội dung mà nhóm sẽ thực hiện trong đồ án này. Đề cương này sẽ được nhóm cập nhật thường xuyên trong quá trình thực hiện đồ án.

- File "[GPT-Brainstorm](GPT-Brainstorm.pdf)": Chứa các ý tưởng để phân tích dữ liệu TikTok và rút ra insight từ đó. Nhóm đã sử dụng các công cụ chatbot AI (như ChatGPT) để gợi ý các insight tiềm năng có thể rút ra từ dữ liệu TikTok. Tuy nhiên, các ý tưởng này chủ yếu được sử dụng để tham khảo và không đảm bảo tất cả ý tưởng đều khả thi. Nhóm sẽ chọn lọc và thực hiện các ý tưởng phù hợp với khả năng của nhóm và thời gian thực hiện đồ án.

- File "[GPT-Deep-Research](GPT-Deep-Research.pdf)": Sau khi chọn lọc một số ý tưởng thú vị sau quá trình brainstorm, nhóm đã sử dụng các công cụ chatbot AI (như ChatGPT) để tìm hiểu và nghiên cứu sâu hơn về các ý tưởng này. Nhóm đã sử dụng các công cụ AI để tìm hiểu về các thuật toán phân tích dữ liệu, các mô hình học máy, v.v. để áp dụng vào đồ án này. Tuy nhiên, nhóm sẽ không sử dụng hoàn toàn các ý tưởng này mà sẽ chọn lọc và điều chỉnh cho phù hợp với khả năng của nhóm và thời gian thực hiện đồ án.

- File "[Script-Generation-Pipeline](Script-Generation-Pipeline.pdf)": Chứa mô tả chi tiết về quy trình tạo kịch bản cho video TikTok. Trong quy trình này sẽ bao gồm nhiều bước như:

  - Phân tích yêu cầu của người dùng để xác định "thể loại" video mà người dùng mong muốn. Quá trình này sẽ được AI thực hiện hoàn toàn tự động dựa vào một số gợi ý mà chúng ta cung cấp cho nó.
  - Tùy theo loại video mà người dùng mong muốn, ta sẽ truy xuất cơ sở dữ liệu để chọn ra các video "trending" trên TikTok mà có nội dung tương tự với yêu cầu của người dùng.
  - Đặc trưng nổi bật của các video "trending" sẽ được trích xuất và bổ sung vào prompt để gửi đến các AI agent (như Gemini API) nhằm tạo ra kịch bản cho video TikTok. Quá trình này giúp bổ sung một lượng thông tin quan trọng để các mô hình AI có thể tạo ra kịch bản phù hợp với thị hiếu của phần lớn người dùng TikTok tại thị trường Việt Nam.
