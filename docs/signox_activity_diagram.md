# Signox - So Do Hoat Dong

```mermaid
flowchart TD
    START([BAT DAU]) --> VISIT[Truy cap website]

    VISIT --> CHECK{Nguoi dung moi?}

    CHECK -->|Co| REGISTER[Dang ky tai khoan]
    CHECK -->|Khong| LOGIN[Dang nhap]

    REGISTER --> DASHBOARD
    LOGIN --> DASHBOARD

    DASHBOARD[Trang chu]

    DASHBOARD --> LESSONS[Hoc bai]
    DASHBOARD --> VIDEOS[Xem video]
    DASHBOARD --> QUIZ[Lam bai kiem tra]
    DASHBOARD --> FORUM[Dien dan]

    LESSONS --> VIEW_LESSON[Xem noi dung bai hoc]
    VIEW_LESSON --> FLASHCARD[Luyen tu vung]

    VIDEOS --> WATCH[Xem video]

    QUIZ --> DO_QUIZ[Tra loi cau hoi]
    DO_QUIZ --> RESULTS[Xem ket qua]

    FORUM --> POST[Dang bai / Binh luan]

    FLASHCARD --> POINTS
    WATCH --> POINTS
    RESULTS --> POINTS
    POST --> POINTS

    POINTS[Nhan diem XP]

    POINTS --> STREAK[Cap nhat chuoi ngay hoc]
    POINTS --> BADGE[Kiem tra huy hieu]

    STREAK --> NOTIFY
    BADGE --> NOTIFY

    NOTIFY[Thong bao]

    NOTIFY --> CONTINUE{Tiep tuc?}

    CONTINUE -->|Co| DASHBOARD
    CONTINUE -->|Khong| LOGOUT[Dang xuat]

    LOGOUT --> END([KET THUC])
```

## So Do Co So Du Lieu

```mermaid
erDiagram
    NguoiDung ||--o| HoSo : co
    NguoiDung ||--o| Diem : co
    NguoiDung ||--o| ChuoiNgay : co
    NguoiDung ||--o{ HuyHieu : nhan
    NguoiDung ||--o{ TienDo : theo_doi
    NguoiDung ||--o{ BaiDaLuu : luu
    NguoiDung ||--o{ LamBaiKT : lam
    NguoiDung ||--o{ BaiDang : tao
    NguoiDung ||--o{ BinhLuan : viet
    NguoiDung ||--o{ ThongBao : nhan

    DanhMuc ||--o{ BaiHoc : chua
    BaiHoc ||--o{ TuVung : gom
    BaiHoc ||--o{ BaiKiemTra : co

    BaiKiemTra ||--o{ CauHoi : chua
    CauHoi ||--o{ CauTraLoi : co

    DanhMucVideo ||--o{ Video : chua

    BaiDang ||--o{ BinhLuan : co
    BaiDang ||--o{ LuotThich : nhan

    NguoiDung {
        int id PK
        string ten_dang_nhap
        string email
        string mat_khau
        boolean la_admin
        boolean la_giao_vien
    }

    BaiHoc {
        int id PK
        int danh_muc_id FK
        string tieu_de
        string noi_dung
        string do_kho
    }

    TuVung {
        int id PK
        int bai_hoc_id FK
        string tu
        string nghia
        string hinh_anh
        string video
    }

    BaiKiemTra {
        int id PK
        int bai_hoc_id FK
        string tieu_de
        int diem_dat
    }

    CauHoi {
        int id PK
        int bai_kt_id FK
        string noi_dung
        string loai
        int diem
    }

    Video {
        int id PK
        int danh_muc_id FK
        string tieu_de
        string duong_dan
        int luot_xem
    }

    BaiDang {
        int id PK
        int tac_gia_id FK
        string tieu_de
        string noi_dung
    }
```

## Vai Tro Nguoi Dung

| Vai Tro | Quyen Truy Cap |
|---------|----------------|
| **Admin** | `/admin/` + `/manage/` |
| **Giao vien** | `/manage/` |
| **Nguoi dung** | Hoc tap |
