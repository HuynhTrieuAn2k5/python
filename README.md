# ASCII Christmas Tree 2026

## Chạy trên web

Trang web nằm trong `index.html` và dùng nhạc từ `assets/Christmas.mp3`.

Để tạo link mở trực tiếp chương trình bằng GitHub Pages:

1. Đẩy `index.html`, thư mục `assets/` và các tệp dự án lên GitHub.
2. Mở **Settings → Pages** trong repository.
3. Ở **Build and deployment**, chọn **Deploy from a branch**, nhánh `main`, thư mục `/(root)`, rồi nhấn **Save**.
4. Sau khi GitHub Pages hoàn tất triển khai, link trang sẽ hiện ở phần **Pages**. Mở link đó để chạy chương trình.

> Trình duyệt chặn tự phát âm thanh. Nhấn **Bật nhạc** trên trang để bắt đầu phát.

## Điều khiển

- **Tạm dừng** hoặc `Space`: dừng/tiếp tục hoạt cảnh
- **Chạy lại** hoặc `R`: bắt đầu lại
- **↑ / ↓**: tăng/giảm tốc độ quay
- **− Tốc độ / + Tốc độ**: chỉnh tốc độ bằng nút cảm ứng trên điện thoại
- **Bật nhạc / Tắt nhạc** hoặc `M`: điều khiển nhạc
- **Âm lượng** hoặc `+ / -`: chỉnh âm lượng
- **Tắt tiếng** hoặc `0`: tắt tiếng/bật lại

## Chạy bản Python trên máy

Cài `pygame` rồi chạy:

```bash
python -m pip install pygame
python christmas_tree.py
```
