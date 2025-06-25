# Hướng dẫn debug lỗi 403 khi gọi API `/api/v1/accounts/is-google-user` từ Frontend

## 1. Kiểm tra Access Token

- Đảm bảo frontend đã lấy đúng access token sau khi đăng nhập.
- Token phải là token mới nhất, không bị expired.
- Có thể test bằng cách copy token này và dùng Postman/cURL gọi thử API backend.

## 2. Kiểm tra Header Authorization

- Khi gọi API, header phải đúng định dạng:
  ```http
  Authorization: Bearer <access_token>
  ```
- Nếu thiếu "Bearer " hoặc token sai, backend sẽ trả về 401 hoặc 403.

### Ví dụ code (fetch):

```js
fetch("http://localhost:8000/api/v1/accounts/is-google-user", {
  method: "GET",
  headers: {
    Authorization: "Bearer " + accessToken,
    "Content-Type": "application/json",
  },
})
  .then((res) => res.json())
  .then(console.log)
  .catch(console.error);
```

## 3. Kiểm tra CORS

- Đảm bảo backend đã cấu hình CORS cho domain frontend (ví dụ: `http://localhost:5173`).
- Nếu bị lỗi CORS, browser sẽ chặn request trước khi gửi đến backend.
- Kiểm tra trong network tab của DevTools xem có lỗi CORS không.

## 4. Kiểm tra lại token ở backend

- Nếu token lấy từ frontend bị 403, thử lấy token đó gọi bằng Postman/cURL hoặc script Python:
  ```bash
  curl -X GET "http://localhost:8000/api/v1/accounts/is-google-user" -H "Authorization: Bearer <access_token>"
  ```
- Nếu backend trả về 200, nghĩa là lỗi ở frontend gửi request.
- Nếu backend cũng trả về 403, kiểm tra lại token hoặc trạng thái tài khoản.

## 5. Kiểm tra trạng thái tài khoản

- Tài khoản phải ở trạng thái active, không bị khóa hoặc chưa xác thực email.

## 6. Kiểm tra route backend

- Đảm bảo route `/api/v1/accounts/is-google-user` được định nghĩa trước route `/{account_id}` trong backend.

---

## Checklist nhanh

- [ ] Token đúng, chưa hết hạn
- [ ] Header Authorization đúng định dạng
- [ ] Không bị lỗi CORS
- [ ] Tài khoản active
- [ ] Route backend đúng thứ tự

Nếu vẫn lỗi, gửi access token và log lỗi chi tiết để backend hỗ trợ debug!
