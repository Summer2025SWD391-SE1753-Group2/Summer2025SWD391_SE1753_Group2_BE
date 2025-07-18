# Hướng dẫn luồng xác thực email cho FE

## 1. Luồng xác thực email

- Khi người dùng đăng ký, backend sẽ gửi email xác thực với link dạng:
  ```
  https://swd.nhducminhqt.name.vn/verify-email?token=<token>
  ```
- Khi user click vào link này, FE sẽ nhận được token trên URL.

## 2. FE cần làm gì ở route `/verify-email`

1. **Lấy token từ URL**
2. **Gọi API xác thực email tới backend:**
   - Endpoint:
     - `GET /api/v1/accounts/confirm-email?token=<token>`
     - hoặc `POST /api/v1/accounts/confirm-email?token=<token>`
   - Ví dụ với axios:
     ```js
     axios
       .get("/api/v1/accounts/confirm-email", { params: { token } })
       .then((res) => {
         // Hiển thị thông báo thành công, redirect về login
       })
       .catch((err) => {
         // Hiển thị lỗi xác thực
       });
     ```
3. **Xử lý response:**
   - Nếu thành công, tài khoản sẽ được active, FE có thể hiển thị thông báo và redirect về trang login.
   - Nếu lỗi (token hết hạn, không hợp lệ), hiển thị thông báo lỗi.

## 3. Response mẫu từ backend

```json
{
  "message": "Email confirmed successfully",
  "account": {
    "username": "...",
    "email": "...",
    "status": "active"
  }
}
```

## 4. Lưu ý

- FE **bắt buộc phải gọi API xác thực email** khi user truy cập `/verify-email?token=...`, nếu không tài khoản sẽ không được active.
- Nếu tài khoản vẫn inactive, kiểm tra lại request FE gửi lên backend và response trả về.
- Nếu cần kiểm tra thêm, gửi log request/response cho backend để hỗ trợ.

---

**Nếu cần hướng dẫn chi tiết về code hoặc flow, hãy liên hệ backend!**
