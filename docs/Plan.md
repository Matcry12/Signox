# BẢN ĐỀ XUẤT DỰ ÁN KHOA HỌC KỸ THUẬT

**Tên đề tài:** Hệ thống Web Hỗ trợ Học Ngôn ngữ Ký hiệu Cá nhân hóa & Kết nối Cộng đồng
**Lĩnh vực:** Phần mềm hệ thống / Giáo dục 4.0

## 1. MỤC TIÊU DỰ ÁN

Xây dựng một nền tảng website toàn diện giúp phổ cập Ngôn ngữ Ký hiệu (NNKH) cho cộng đồng, giải quyết hai vấn đề chính:

1. **Khả năng tự học:** Cung cấp lộ trình học tập bài bản, trực quan qua Video và Hình ảnh.
2. **Tính cá nhân hóa:** Hệ thống tự động gợi ý bài học dựa trên năng lực và sở thích của người dùng (Điểm nổi bật để đi thi).

## 2. PHẠM VI CHỨC NĂNG (SCOPE OF WORK)

Hệ thống sẽ bao gồm 8 nhóm chức năng chính, chia làm 2 phân hệ: **Người dùng (User)** và **Quản trị (Admin)**.

### A. Phân hệ Người dùng (Học viên)

1. **Trang chủ (Dashboard):**
    - Tổng quan các khóa học.
    - Hiển thị tiến độ học tập (Progress bar).
    - Danh sách bài học được đề xuất riêng cho từng cá nhân.
2. **Học tập (Lessons):**
    - Học từ vựng qua Flashcard (Hình ảnh/Video).
    - Học ngữ pháp & Mẫu câu giao tiếp.
    - Các công cụ hỗ trợ: Lưu bài, Báo lỗi nội dung.
3. **Thư viện Video (Video Situations):**
    - Kho video tình huống thực tế (đi chợ, hỏi đường, bệnh viện...).
    - Bộ lọc tìm kiếm thông minh theo chủ đề.
4. **Hệ thống Gợi ý (Recommendation Engine - Tính năng lõi):**
    - Tự động đề xuất bài học mới dựa trên: Lịch sử đã xem, Điểm số bài Quiz, và Chủ đề yêu thích.
5. **Diễn đàn cộng đồng (Forum):**
    - Nơi trao đổi, hỏi đáp giữa người học.
    - Tính năng tương tác: Đăng bài, Upload ảnh/video, Bình luận, Thả tim.
6. **Tài khoản & Hồ sơ:**
    - Đăng ký/Đăng nhập bảo mật.
    - Quản lý lịch sử học tập cá nhân.

### B. Phân hệ Quản trị (Admin Panel)

1. **Quản trị Nội dung (CMS):**
    - Công cụ soạn thảo bài học, upload video, quản lý từ vựng.
    - Quản lý danh mục/chủ đề học tập.
2. **Quản trị Hệ thống & Người dùng:**
    - Dashboard thống kê: Số lượng người học, bài viết, báo cáo vi phạm.
    - Công cụ kiểm duyệt diễn đàn: Xóa bài, khóa tài khoản vi phạm.

## 3. ĐIỂM NHẤN CÔNG NGHỆ (KEY SELLING POINTS)

*Đây là phần quan trọng để thuyết phục Ban Giám Khảo:*

1. **Thuật toán Gợi ý (Rule-based Recommendation):** Không hiển thị bài học ngẫu nhiên, hệ thống phân tích dữ liệu người dùng để đưa ra gợi ý chính xác (Ví dụ: Người dùng yếu phần ngữ pháp -> Hệ thống ưu tiên hiện bài tập ngữ pháp).
2. **Trải nghiệm người dùng (UX/UI):** Giao diện thiết kế hiện đại, dễ sử dụng, tập trung vào hình ảnh trực quan (Visual Learning).
3. **Hệ sinh thái khép kín:** Học lý thuyết -> Xem thực hành (Video) -> Trao đổi cộng đồng (Forum).