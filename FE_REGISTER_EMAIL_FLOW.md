# Hướng dẫn luồng đăng ký và xác thực email cho FE

## 1. Luồng đăng ký tài khoản

1. **FE hiển thị form đăng ký** (username, email, password, ...)
2. **FE gửi request đăng ký tới backend:**
   - Endpoint:
     - `POST /api/v1/auth/register`
   - Body ví dụ:
     ```json
     {
       "username": "your_username",
       "email": "your_email@example.com",
       "password": "your_password",
       "full_name": "Your Name"
     }
     ```
3. **Backend tạo tài khoản với trạng thái inactive và gửi email xác thực cho user.**
4. **FE hiển thị thông báo:**
   - "Đăng ký thành công! Vui lòng kiểm tra email để xác thực tài khoản."

## 2. Luồng xác thực email

1. **User click vào link xác thực trong email:**
   - Link dạng: `https://swd.nhducminhqt.name.vn/verify-email?token=<token>`
2. **FE tại route `/verify-email` lấy token từ URL, gọi API xác thực email:**
   - **Endpoint CHUẨN:**
     - `GET /api/v1/accounts/confirm-email?token=<token>`
     - hoặc `POST /api/v1/accounts/confirm-email?token=<token>`
   - **Lưu ý:** Nếu gọi sai endpoint (ví dụ `/api/v1/auth/confirm-email`), backend sẽ trả về 404.
   - Xử lý response như hướng dẫn ở file FE_EMAIL_VERIFICATION_FLOW.md
3. **Nếu xác thực thành công:**
   - Hiển thị thông báo "Xác thực email thành công! Bạn có thể đăng nhập."
   - Redirect về trang login.

## 3. Response mẫu từ backend khi đăng ký

```json
{
  "username": "your_username",
  "email": "your_email@example.com",
  "status": "inactive",
  ...
}
```

## 4. Lưu ý & debug nhanh

- Sau khi đăng ký, tài khoản sẽ ở trạng thái **inactive** cho đến khi xác thực email.
- FE cần hướng dẫn user kiểm tra email và xác thực trước khi đăng nhập.
- Nếu user chưa xác thực email, khi đăng nhập sẽ nhận được thông báo "Account is not active. Please confirm your email first."
- Nếu cần gửi lại email xác thực, FE có thể gọi endpoint `/api/v1/accounts/resend-confirmation`.
- **Nếu tài khoản vẫn inactive hoặc gặp lỗi 404 khi xác thực:**
  - Kiểm tra lại endpoint FE gọi phải là `/api/v1/accounts/confirm-email`.
  - Kiểm tra network tab: request gửi lên đúng chưa, response trả về gì?
  - Gửi log request/response cho backend để hỗ trợ debug.

---

**Nếu cần hướng dẫn chi tiết về code hoặc flow, hãy liên hệ backend!**
