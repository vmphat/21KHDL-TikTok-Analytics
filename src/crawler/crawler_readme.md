1. Thư viện cần thiết:
```bash
pip install TikTokApi
python -m playwright install
pip install yt_dlp
pip install asyncio
```
2. Cách chạy
```bash
python crawler.py <hashtag> <number_of_videos>

VD: python crawler.py khoahoc 20
```
3. Cây thư mục chứa data
```bash
videos
    hashtag1
        video1.mp4
        video2.mp4
        ...
        videos_info.json
    hastag2
    ...
```
***Lưu ý:*** Thư mục `TikTokApi` có sự thay đổi so với api cài bằng `pip`. Cứ để chung với file `crawler.py` chạy bình thường.