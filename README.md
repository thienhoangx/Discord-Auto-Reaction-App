# Discord-Auto-Reaction-App
Bước 1: Mở Discord Web
        Vào: https://discord.com/login
        Đăng nhập tài khoản của bạn.
Bước 2: Mở _DevTools_
        Nhấn _Ctrl + Shift + I_ (hoặc chuột phải → "Kiểm tra")
        Chuyển sang tab _Network_
Bước 3: Tải lại trang (F5) và lọc tìm token
        Nhấn F5 để reload lại Discord
        Ở thanh lọc (_filter_), chọn _XHR_
        Tìm dòng có URL chứa /api/v9/users/@me
        Nhấn vào dòng đó → tab Headers
        Ở phần Request Headers, tìm dòng có chữ:
        authorization: YOUR_TOKEN_HERE
