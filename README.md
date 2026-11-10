# User Registry

Ứng dụng Flutter quản lý người dùng trên Web và Android, sử dụng Firebase
Authentication và Firebase Realtime Database.

- Web demo: https://midtern-users-2026-htt1325.web.app
- Android APK: https://github.com/htt1325abc/MidTernProject-Nov2026/releases/latest/download/user-registry.apk
- GitHub: https://github.com/htt1325abc/MidTernProject-Nov2026
- Tài khoản quản trị demo: `admin@userhub.local`
- Mật khẩu demo: `Admin@123`

## Chức năng

- Đăng nhập quản trị bằng Email/Password
- Hiển thị danh sách người dùng theo thời gian thực
- Thêm, sửa và xóa hồ sơ
- Chọn ảnh trên Web/Android, nén ảnh trước khi lưu
- Tìm kiếm theo họ tên hoặc email
- Sắp xếp theo họ tên hoặc email
- Ẩn/hiện mật khẩu
- Giao diện responsive: bảng quản trị trên màn hình rộng và thẻ hồ sơ trên di động

## Cấu trúc dữ liệu

Mỗi node trong `/users` chỉ chứa đúng bốn trường theo yêu cầu đề bài:

```json
{
  "email": "lan.nguyen@example.com",
  "matkhau": "Lan@12345",
  "hoten": "Nguyễn Thị Lan",
  "hinhanh": "data:image/jpeg;base64,..."
}
```

Firebase node key chỉ được dùng ở runtime, không được ghi thành trường dữ liệu.
Rule tại `database.rules.json` từ chối hồ sơ thiếu trường hoặc có trường khác.

> `matkhau` là trường dữ liệu bắt buộc của đề bài. Tài khoản đăng nhập quản trị
> vẫn do Firebase Authentication quản lý riêng.

## Chạy project

Yêu cầu Flutter 3.47 trở lên và một trình duyệt hoặc Android SDK.

```bash
flutter pub get
flutter run -d chrome
```

Chạy với Firebase Emulator:

```bash
firebase emulators:start --only auth,database
flutter run -d chrome --dart-define=USE_FIREBASE_EMULATOR=true
```

## Kiểm tra và build

```bash
flutter analyze
flutter test
flutter build web --release
flutter build apk --debug
firebase deploy --only database,hosting
```

File cơ sở dữ liệu nộp kèm nằm tại `submission/database.json`.
