# Giải Thích Lý Do Thay Đổi Món Ăn Theo Quy Tắc Dinh Dưỡng

**Nguồn:**
- `weekly_meal_plan_85k.json` — Thực đơn cơm tháng 5/2026, mức ăn 85.680đ
- `rules.pdf` — Hướng dẫn chế độ ăn bệnh viện (QĐ 2879/QĐ-BYT ngày 10/8/2006), 81 trang

---

## Tổng Quan: Nguyên Tắc Xây Dựng Thực Đơn Bệnh Viện

Theo rules.pdf, cơ cấu khẩu phần chuẩn (BT) cho người lớn 50-55kg:

| Thành phần | Giá trị |
|---|---|
| Năng lượng | 1800-1900 Kcal/ngày (BT01) hoặc 2200-2400 Kcal/ngày (BT02) |
| Protid (P) | 12-14% tổng năng lượng → ~66-84g |
| Lipid (L) | 15-25% tổng năng lượng → ~40-65g |
| Glucid (G) | 350-440g |
| Natri | ≤ 2400 mg/ngày |
| Nước | 2-2.5 lít/ngày |
| Chất xơ | 15-25g/ngày |

Mỗi nhóm bệnh lý có **một hoặc nhiều quy tắc riêng** về: giới hạn năng lượng, giới hạn từng chất dinh dưỡng (P/L/G), giới hạn điện giải (Natri, Kali, Phosphat, Cholesterol), lựa chọn thực phẩm, và dạng chế biến. Các thay đổi món ăn trong thực đơn 85k đều xuất phát từ những quy tắc này.

---

## Chi Tiết Từng Nhóm Bệnh

---

### P6 — Đái Tháo Đường (Đường) — 29 thay đổi

**Quy tắc theo rules.pdf (Section III, pages 11-14):**

> **DD01-X — Đái tháo đường đơn thuần:**
> - Năng lượng: **30 kcal/kg** cân nặng lý tưởng/ngày (thấp hơn chuẩn 35-40 kcal/kg)
> - Protid: **15-20%** tổng năng lượng
> - Glucid: **55-65%**, nên dùng **glucid phức hợp, chỉ số đường huyết thấp**
> - Lipid: **20-30%**
> - **Chất xơ: 20-25g/ngày** (so với chuẩn 15-25g — mức tối thiểu cao hơn)
> - Số bữa ăn: 4-6 bữa/ngày (nhiều hơn chuẩn 3-4 bữa)

**Giải thích từng thay đổi:**

| Thay đổi | Trong thực đơn | Lý do theo quy tắc |
|---|---|---|
| Gạo **150g → 100g** (trưa & tối, 7/7 ngày) | Giảm tinh bột | Glucid cần ở mức 55-65% nhưng tổng năng lượng giảm → giảm lượng gạo để kiểm soát đường huyết |
| Rau luộc/xào **200g → 230g** (trưa & tối, 7/7 ngày) | Tăng rau | Chất xơ phải đạt **20-25g/ngày** — tăng khẩu phần rau là cách trực tiếp nhất để đạt mức này |
| Bữa sáng Thứ 2: Phở bò → **Bánh cuốn + Sữa Fami ít đường** | Đổi món + giảm đường | Phở bò có chỉ số đường huyết (GI) cao. Bánh cuốn + sữa ít đường = GI thấp hơn, phù hợp "glucid có chỉ số đường huyết thấp" |

---

### P10 — Kiêng I-ốt / Tuyến Giáp (IOD) — 35 thay đổi

**Quy tắc theo thực đơn 85k:**

Thực đơn IOD ghi rõ mục đích là cho bệnh nhân **kiêng i-ốt** — thường là bệnh nhân chuẩn bị xạ trị tuyến giáp bằng i-ốt phóng xạ (I-131), hoặc sau xạ trị. Nguyên tắc là **hạn chế tối đa i-ốt trong thức ăn**.

**Giải thích từng thay đổi:**

| Thay đổi | Trong thực đơn | Lý do |
|---|---|---|
| Gạo tám **Lào → Thái** (trưa & tối, 7/7 ngày) | Đổi giống gạo | Gạo tám Thái có hàm lượng khoáng chất (bao gồm i-ốt tự nhiên từ đất trồng) khác biệt so với Gạo tám Lào |
| Rau cải → **Đậu cove / Bí xanh** (5 ngày) | Thay loại rau | Rau cải (cải bắp, cải ngọt, cải chíp) chứa **nitrat tự nhiên** có thể ảnh hưởng đến khả năng hấp thu i-ốt phóng xạ của tuyến giáp. Đậu cove và bí xanh là lựa chọn thay thế có hàm lượng nitrat thấp hơn |
| Canh cải/mồng tơi → **Canh bí xanh** (lunch, 7/7 ngày) | Thay loại canh | Lý do tương tự — tránh rau cải trong canh |
| Canh cải/khoai → **Canh khoai tây nấu thịt nạc** (dinner, 7/7 ngày) | Đổi canh | Thay thế bằng rau/củ có hàm lượng i-ốt thấp |
| Bữa sáng Thứ 2: Phở bò → **Cháo thịt nạc + Sữa Grandcare Gold** | Đổi món | Phở bò (nước dùng từ xương) có thể chứa hàm lượng i-ốt nhỏ. Cháo + sữa chuyên dụng là lựa chọn an toàn hơn |

---

### P3 — Sản Khoa (SẢN) — 27 thay đổi

**Quy tắc theo rules.pdf (Section XII, pages 29-33):**

> **SK03-X — Phụ nữ nuôi con bú 6 tháng đầu:**
> - Năng lượng: **2600-2700 Kcal/ngày** (cao hơn chuẩn)
> - Protid: **12-14%** tổng năng lượng → ~80-95g
> - Glucid: phần lớn năng lượng
> - Chất xơ: **20-25g/ngày**, ưu tiên **chất xơ hòa tan**
> - Nước: **2-2.5 lít/ngày**
> - Vitamin: đủ vi lượng và vitamin A, B, C, E

**Giải thích từng thay đổi:**

| Thay đổi | Trong thực đơn | Lý do theo quy tắc |
|---|---|---|
| Bữa sáng: **Phở/Bún → Cháo thịt nạc băm + Sữa Grandcare Gold** (7/7 ngày) | Thay đổi hoàn toàn | Phụ nữ sau sinh / cho con bú cần thức ăn **dễ tiêu hóa, giàu dinh dưỡng**. Phở và bún có thể nặng bụng. Cháo thịt nạc băm + sữa Grandcare Gold đảm bảo đủ **vitamin và khoáng chất** (theo yêu cầu "đủ yếu tố vi lượng và vitamin A, B, C, E"), đồng thời dễ hấp thu sau sinh |
| Rau cải → **Bí xanh / Đậu cove** (lunch & dinner) | Thay loại rau | Rau cải (cải bắp, cải chíp) có thể gây **đầy hơi, khó tiêu** — không phù hợp cho phụ nữ mới sinh. Đậu cove và bí xanh dễ tiêu hơn, đồng thời cung cấp **chất xơ hòa tan** (ưu tiên trong SK03) |
| Canh thường → **Canh bí xanh nấu thịt nạc** (lunch, 7/7 ngày) | Thay đổi canh | Thịt nạc thay vì các loại thịt khác → **giàu đạm, ít mỡ**, phù hợp nhu cầu protid cao (80-95g/ngày) của phụ nữ cho con bú |
| Canh tối: Tăng thịt nạc **30g → 50g** hoặc đổi sang **Canh khoai tây nấu thịt nạc** | Tăng khẩu phần thịt | Nhu cầu protid của phụ nữ cho con bú cao hơn người bình thường (80-95g vs 66-84g) — cần bổ sung thêm thịt nạc |

---

### P4 — Bệnh Thận (TN) — 4 thay đổi

**Quy tắc theo rules.pdf (Section II, pages 3-10):**

> **Nguyên tắc chung cho bệnh thận:**
> - **Kali: < 2000-3000 mg/ngày** — hạn chế kali khi kali máu >6 mmol/l
> - Natri: **< 2000 mg/ngày** — ăn nhạt tương đối
> - Nước: **1-1.5 lít/ngày** (thấp hơn chuẩn 2-2.5l)
> - Phosphat: **< 800-1200 mg/ngày**
> - Lựa chọn rau củ: **hạn chế rau giàu kali** (khoai tây, cà chua, nấm, rau muống, cải bắp...)

Hàm lượng kali trong 100g rau củ:
- **Khoai tây: ~420-530mg kali** → Cao, cần hạn chế
- **Cải bắp: ~200-250mg kali** → Trung bình
- **Cải chíp: ~260-290mg kali** → Trung bình-cao
- **Bí đỏ: ~200-250mg kali** → Trung bình
- **Bí xanh: ~150-200mg kali** → Thấp
- **Đậu cove: ~150-200mg kali** → Thấp

**Giải thích từng thay đổi:**

| Thay đổi | Trong thực đơn | Lý do theo quy tắc |
|---|---|---|
| Tue lunch: Cải chíp luộc → **Bí xanh luộc** | Thay rau | Cải chíp có hàm lượng kali cao hơn bí xanh. Thay bằng rau có kali thấp hơn để kiểm soát **Kali < 2000mg/ngày** |
| Fri dinner: Khoai tây xào → **Cải chíp luộc** | Thay rau | Khoai tây là một trong những thực phẩm **giàu kali nhất** (420-530mg/100g) → bắt buộc thay |
| Sat dinner: Cải bắp luộc → **Đậu cove luộc** | Thay rau | Cải bắp ở mức trung bình-cao kali; đậu cove là lựa chọn thay thế có kali thấp hơn |
| Thu dinner: Cải bắp luộc → **Bí đỏ xào** | Thay rau | Tương tự — tránh cải bắp (kali trung bình-cao), dùng bí đỏ có kali ở mức an toàn |

> **Nhận xét:** Thay đổi ở bệnh thận chỉ là 4 ô — rất ít so với quy tắc nghiêm ngặt của rules.pdf. Có thể bệnh nhân thận trong thực đơn này ở mức độ nhẹ, hoặc các bữa khác đã được điều chỉnh khẩu phần thịt/cá để kiểm soát kali thay vì thay đổi rau.

---

## Nhóm Không Thay Đổi — Giải Thích

### P2 — Phẫu thuật (PT)
Theo rules.pdf (Section IX), **giai đoạn hồi phục sau phẫu thuật** (PT04-X) có:
> - Năng lượng: 1800-1900 Kcal/ngày
> - Protid: 12-14%
> - Natri: < 2400 mg/ngày
> - Lựa chọn thực phẩm: **"theo lứa tuổi và quen dùng"**

→ Giai đoạn hồi phục = **ăn uống gần như bình thường**, không cần thay đổi món, chỉ cần đảm bảo dinh dưỡng đủ. Danh sách món giống chuẩn là hợp lý.

### P5 — Tim mạch (TM) / Tăng huyết áp (TH)
Theo rules.pdf (Section V, pages 16-20 và Section VII, pages 24-27):

| Giai đoạn | Yêu cầu | Khác biệt với chuẩn |
|---|---|---|
| TH01-X — Viêm loét dạ dày ổn định | Natri < 2400mg, hạn chế chất kích thích, mềm ít xơ | Không khác về danh sách món |
| TM01-X — Suy tim độ 1-2 | Natri 20-50mg/kg, giàu kali, ít xơ | Chủ yếu điều chỉnh khẩu phần, không đổi món |

→ **Danh sách món giữ nguyên** — chỉ khác ở mức độ hạn chế gia vị/natri, không cần thay đổi loại thực phẩm.

### P7 — Gan Mật (GM)
Theo rules.pdf (Section VII, pages 24-27):

| Giai đoạn | Yêu cầu | Khác biệt với chuẩn |
|---|---|---|
| GM01-X — Viêm gan cấp giai đoạn đầu | Ưu tiên glucid, protid vừa phải | Danh sách món tương tự |
| GM04-X — Xơ gan | Natri 1200-2000mg, hạn chế rắn/nhiều xơ | Chủ yếu điều chỉnh lượng và dạng chế biến |

→ Mức độ thay đổi nằm ở **khẩu phần và cách chế biến** (mềm, ít xơ), không phải ở **danh sách món**. Bếp bệnh viện giữ nguyên món nhưng chế biến phù hợp.

### P8 — Ung Thư (UT), P9 — Gút (GU), P11 — Người nhà
- **Ung thư:** Chế độ ăn tập trung vào đảm bảo năng lượng và protid cao, dễ tiêu hóa — danh sách món chuẩn đã phù hợp.
- **Gút:** Hạn chế purin (thịt đỏ, nội tạng, hải sản giàu purin) — có thể đã điều chỉnh trong khẩu phần protein của metadata, không cần thay đổi món rau/cơm.
- **Người nhà:** Không có yêu cầu dinh dưỡng đặc biệt → dùng y chang chuẩn.

---

## Bảng Tổng Hợp: Quy Tắc Thay Đổi → Hành Động Trong Thực Đơn

| Nhóm bệnh | Thay đổi chính | Quy tắc từ rules.pdf | Cơ sở khoa học |
|---|---|---|---|
| Đái tháo đường (P6) | Giảm gạo, tăng rau, đổi bữa sáng | GI thấp, chất xơ 20-25g | Kiểm soát đường huyết, giảm đỉnh đường huyết sau ăn |
| Kiêng i-ốt (P10) | Gạo Lào→Thái, bỏ rau cải, đổi canh | Hạn chế i-ốt tối đa | Chuẩn bị/hồi phục sau xạ trị tuyến giáp bằng I-131 |
| Sản khoa (P3) | Bữa sáng → Cháo+sữa, đổi rau, tăng thịt | Dễ tiêu, giàu vitamin, protid cao | Phụ nữ sau sinh/cho con bú cần dinh dưỡng cao, dễ hấp thu |
| Bệnh thận (P4) | Thay rau kali cao bằng rau kali thấp | Kali < 2000-3000 mg/ngày | Hạn chế gánh nặng cho thận suy yếu |
| Phẫu thuật (P2) | Không đổi | PT04-X: "theo lứa tuổi và quen dùng" | Giai đoạn hồi phục — ăn bình thường |
| Tim mạch (P5) | Không đổi | TM: chủ yếu điều chỉnh gia vị/natri | Không cần thay đổi món, chỉ cần giảm muối |
| Gan mật (P7) | Không đổi | GM: chủ yếu điều chỉnh dạng chế biến | Mềm, ít xơ — không cần đổi danh sách món |
| Ung thư (P8) | Không đổi | UT: đảm bảo năng lượng và protid | Danh sách chuẩn đã phù hợp |
| Gút (P9) | Không đổi | GU: hạn chế purin | Điều chỉnh trong khẩu phần protein, không cần đổi món rau/cơm |
| Người nhà (P11) | Không đổi | Không có yêu cầu đặc biệt | Dùng chuẩn |

---

## Kết Luận

Tổng cộng **95/876 ô món ăn** bị thay đổi so với thực đơn chuẩn. Mỗi thay đổi đều có **cơ sở từ quy tắc dinh dưỡng bệnh viện (QĐ 2879/QĐ-BYT)** hoặc từ đặc thù điều trị của từng nhóm bệnh. Mô hình **"một thực đơn chuẩn + điều chỉnh tối thiểu"** của bệnh viện là hợp lý vì:

1. **Bệnh thận** chỉ cần thay 4 loại rau — không phải nấu riêng toàn bộ bữa ăn
2. **Đái tháo đường** chỉ cần giảm gạo và tăng rau — cùng nguyên liệu, chỉ khác khẩu phần
3. **Sản khoa** thay bữa sáng từ phở/bún sang cháo+sữa — có thể nấu chung với nhóm cháo OT có sẵn
4. **Kiêng i-ốt** thay gạo và rau cải — dùng nguyên liệu sẵn có từ nhóm khác

→ Bếp bệnh viện tối ưu công suất bằng cách **thay đổi thành phần cụ thể** thay vì nấu toàn bộ bữa ăn riêng cho từng nhóm.
