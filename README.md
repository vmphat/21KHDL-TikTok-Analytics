# Đồ án cuối kỳ - Khoa học dữ liệu ứng dụng - 21KHDL

## Sinh viên thực hiện: Nhóm 05

| STT | MSSV     | Họ và tên        |
| :-: | -------- | ---------------- |
|  1  | 21127038 | Võ Phú Hãn       |
|  2  | 21127739 | Vũ Minh Phát     |
|  3  | 21127742 | Nguyễn Minh Hiếu |

## Link đến playlist chứa video demo của đồ án

- Link đến playlist chứa video demo của đồ án: https://www.youtube.com/playlist?list=PL3SfxVDJ_Zc6DvBKVd6xUc-exmt0AyA7x
- Trong playlist sẽ có video trình bày đầy đủ cả 3 công cụ hỗ trợ mà nhóm đã xây dựng, xoay quanh chủ đề trọng tâm của đồ án lần này là: "Xây dựng công cụ hỗ trợ viết kịch bản dành cho các video trên TikTok".

## Link đến trang web chứa sản phẩm của đồ án

- Link đến trang web chứa sản phẩm của đồ án: https://21khdl-tiktok-analytics.streamlit.app/

## Cách tổ chức thư mục của đồ án

Dự án này được tổ chức với các thư mục và tệp chính như sau:

1. **Tệp chính:**

   - `README.md`: Tài liệu giới thiệu và hướng dẫn sử dụng dự án.
   - `Team-Plan-and-Work-Distribution.md`: Kế hoạch thực hiện và phân công công việc của nhóm.
   - `requirements.txt`: Danh sách các thư viện cần thiết để chạy dự án.
   - `packages.txt`: Có thể chứa thông tin về các gói hoặc môi trường.

2. **Thư mục chính:**

   - `data`: Chứa dữ liệu thô, dữ liệu đã xử lý, và các tệp liên quan đến phân tích dữ liệu.
   - `demo`: Có thể chứa các tệp demo hoặc video minh họa.
   - `development`: Chứa mã nguồn phát triển, các tệp thử nghiệm, và tài liệu liên quan.
   - `docs`: Tài liệu chi tiết về dự án, API, và các hướng dẫn khác.
   - `models`: Có thể chứa các mô hình đã huấn luyện hoặc các tệp liên quan đến mô hình.
   - `notebooks`: Các notebook Jupyter phục vụ cho việc phân tích và thử nghiệm.
   - `src`: Mã nguồn chính của ứng dụng, bao gồm các tệp Streamlit hoặc các module khác.

## Kế hoạch thực hiện đồ án và phân công công việc

- Tài liệu về kế hoạch thực hiện đồ án của nhóm 05 và bảng phân công công việc chi tiết cho mỗi thành viên đã được đính kèm trong file "**`Team-Plan-and-Work-Distribution.md`**" của bài nộp.

## Hướng dẫn chạy webapp trên máy cá nhân

- Di chuyển môi trường lập trình đến thư mục gốc của dự án (root folder), hay còn gọi là thư mục chứa file "**`requirements.txt`**".
- Chạy các lệnh sau trong terminal để cài đặt các thư viện cần thiết và chạy ứng dụng Streamlit:

```bash
pip install -r requirements.txt
streamlit run src/app/streamlit_app.py
```
