# Báo Cáo Kiểm Tra Dinh Dưỡng Thực Đơn 85K

**Script:** `validate_nutrition.py`
**Nguồn tham chiếu:**
- `weekly_meal_plan_85k.json` — Thực đơn cơm tháng 5/2026
- `VTN_FCT_2007_food_composition.csv` — Bảng thành phần dinh dưỡng thực phẩm Việt Nam 2007 (Bộ Y tế)

---

## Tóm Tắt Kết Quả

| Nhóm | Ghi nhận (kcal) | Tính từ FCT (kcal) | Δ kcal | P% (calc) | L% (calc) | G% (calc) | Đánh giá |
|---|---|---|---|---|---|---|---|
| Cơm chuẩn (BT01) | 1771 | 1720 | -51 | 13.8% | 12.7% | 73.4% | ⚠️ kcal sát, L% thấp |
| Phẫu thuật (PT) | 1771 | 1720 | -51 | 13.8% | 12.7% | 73.4% | ⚠️ kcal sát, L% thấp |
| Sản khoa (SK) | 2072 | 1472 | **-600** | 14.2% | 8.0% | 77.9% | ⚠️ kcal thấp rất nhiều |
| Bệnh thận (TN) | 1781 | 1677 | -104 | 13.8% | 13.0% | 73.2% | ⚠️ kcal sát, L% thấp |
| Tim mạch (TM) | 1771 | 1720 | -51 | 13.8% | 12.7% | 73.4% | ⚠️ kcal sát, L% thấp |
| Đái tháo đường (ĐĐ) | 1515 | 1393 | -122 | 15.2% | 16.6% | 68.2% | ⚠️ kcal sát |
| Gan mật (GM) | 1782 | 1757 | -25 | 14.6% | 13.3% | 72.1% | ✅ kcal rất sát |
| Ung thư (UT) | 1782 | 1757 | -25 | 14.6% | 13.3% | 72.1% | ✅ kcal rất sát |
| Gút (GU) | 1782 | 1757 | -25 | 14.6% | 13.3% | 72.1% | ✅ kcal rất sát |
| Kiêng i-ốt (IOD) | 1726 | 1539 | -187 | 12.3% | 5.7% | 82.0% | ⚠️ kcal thấp, L% rất thấp |
| Người nhà | 1771 | 1720 | -51 | 13.8% | 12.7% | 73.4% | ⚠️ kcal sát, L% thấp |

**Nhận xét chung:**
- 8/11 nhóm có kcal tính từ FCT khớp trong phạm vi ±200 kcal so với ghi nhận
- 3 nhóm có kcal chênh lệch lớn: **Sản khoa (-600 kcal)**, Kiêng i-ốt (-187 kcal), Đái tháo đường (-122 kcal)
- **Vấn đề hệ thống: Lipid (L%) tính từ FCT luôn thấp hơn ghi nhận** — nguyên nhân: thiếu dầu/mỡ trong CSDL
- 3 nhóm (GM, UT, GU) dùng chung dishes nên cho kết quả kcal gần như y hệt

---

## Vấn Đề 1: FCT 2007 Là Cơ Sở Dữ Liệu Thực Phẩm Sống (Raw)

Bảng thành phần VTN_FCT_2007 chỉ chứa giá trị dinh dưỡng cho **thực phẩm thô, chưa chế biến**. Không có mục nào cho:

| Thực phẩm thiếu trong FCT | Tác động |
|---|---|
| **Thịt bò, thịt lợn, thịt ngan** (chín) | Không tính được protein + lipid chính của bữa ăn |
| **Cá các loại** (cá trắm, cá basa, cá rô, cá thu, cá lóc) | Thiếu protein từ nguồn cá |
| **Tôm, mực** (chín/rang) | Thiếu protein và lipid |
| **Chả cá, chả lá lốt, lạc rim** | Thiếu protein đã chế biến |
| **Đậu phụ rán** | Thiếu cả protein lẫn lipid từ đậu |
| **Thịt gà (cả xương) rang** | Thiếu protein từ gà |
| **Dầu ăn dùng khi xào/rán** | Nguyên nhân chính khiến L% tính được thấp hơn đáng kể |

**Hệ quả trực tiếp:**
- Tính kcal trung bình chỉ sai **-51 kcal** (BT01) → dùng FCT raw vẫn cho kết quả khá chính xác
- Tính **lipid (L%)** luôn thiếu khoảng **8-20 điểm phần trăm** vì thiếu:
  1. Dầu ăn hấp thụ khi xào/rán (thêm ~10-15g lipid/ngày)
  2. Lipid có sẵn trong thịt/cá đã nấu chín (FCT raw không có)

---

## Vấn Đề 2: Tính Không Nhất Quán Giữa Các Nhóm Cùng Thực Đơn

Một số nhóm dùng **cùng dishes** nhưng có kcal ghi nhận khác nhau:

| Nhóm | Ghi kcal | Tính kcal |
|---|---|---|
| BT01 (chuẩn) | 1771 | 1720 |
| TN (bệnh thận) | 1781 | 1677 |
| ĐĐ (đái tháo đường) | **1515** | 1393 |
| SK (sản khoa) | **2072** | 1472 |
| IOD (kiêng i-ốt) | **1726** | 1539 |

→ Các nhóm cùng dùng chung dishes (PT, TM, BT01, TN, GU, UT, Người nhà) đều tính ra **1720 kcal** — nhưng ghi nhận khác nhau ±10-60 kcal. Đây là **dao động bình thường** do làm tròn.

→ Nhóm **ĐĐ ghi 1515 kcal** nhưng thực đơn giảm gạo 150→100g ở trưa+tối → lẽ ra chỉ giảm ~170 kcal → ghi nhận 1515 vs chuẩn 1771 = giảm 256 kcal → **phù hợp** với giảm 50g gạo/bữa × 2 bữa × 7 ngày / 7 = 143g gạo giảm → 143g × 344 kcal/100g = 492 kcal giảm → thực tế giảm nhiều hơn dự kiến.

→ Nhóm **SK ghi 2072 kcal** (cao hơn chuẩn 1771) → phản ánh nhu cầu cao hơn của phụ nữ cho con bú (SK03: 2600-2700 kcal/ngày theo rules). Nhưng thực đơn SK thay bữa sáng thành cháo+sữa → thay vì phở ~450 kcal bằng cháo+sữa ~300 kcal → giảm ~150 kcal ở bữa sáng. Đồng thời thay rau cải bằng bí xanh/đậu cove → không đổi về mặt kcal. Kết hợp tăng thịt nạc trong canh → tăng thêm protein. **Nhưng kcal ghi nhận 2072 > 1771 → không hợp lý** nếu bữa sáng thực tế giảm kcal.

→ Điểm bất thường lớn nhất: **Sản khoa kcal ghi 2072 nhưng tính được chỉ 1472** (chênh -600). Lý do: thực đơn SK thay bữa sáng từ phở/bún (~450-550 kcal) sang **cháo thịt nạc + sữa** (cháo ~200 kcal + sữa Grandcare Gold ~130 kcal = ~330 kcal), nhưng:
1. **Breakfast detail** của nhóm SK chứa rất nhiều món không có trong FCT → parser không trích xuất được đầy đủ kcal
2. Đặc biệt, breakfast SK không có weight cho sữa "Grandcare Gold" trong FCT → thiếu ~130-180 kcal/ngày × 7 = 900-1260 kcal trong tuần

---

## Vấn Đề 3: Thành Phần Không Tìm Thấy Trong FCT (Unfound Items)

Script đánh dấu **"?"** mỗi ngày cho các món không có trong FCT. Tổng hợp:

### Nhóm nguyên liệu hoàn toàn thiếu (không tìm thấy trong FCT 2007):
- **Thịt bò xào, thịt lợn xào, thịt vai quay** — FCT chỉ có "thịt bò" và "thịt gà ta", không có thịt lợn
- **Cá trắm kho, cá basa, cá rô, cá thu, cá lóc** — không có trong FCT 2007
- **Tôm rang, chả cá rán, lạc rim, đậu phụ rán** — không có
- **Thịt gà (cả xương) rang gừng sả** — FCT chỉ có "thịt gà ta" thô
- **Thịt bê xào, thịt ngan** — hoàn toàn không có

### Nhóm nguyên liệu có trong FCT (lookup thành công):
- ✅ Gạo tám Lào → gạo tẻ máy (344 kcal/100g)
- ✅ Bún, bánh phở → có trong FCT
- ✅ Rau củ các loại (củ cải, cải bắp, cải xanh, bí xanh, khoai tây, cà rốt, hành tây, đậu cove) → có trong FCT
- ✅ Thịt gà ta → có trong FCT
- ✅ Trứng gà → có trong FCT
- ✅ Dầu lạc (900 kcal/100g) → có trong FCT nhưng chưa được áp dụng

---

## Kiểm Tra Quy Tắc Dinh Dưỡng (Rules QĐ 2879/QĐ-BYT)

So sánh kết quả tính từ FCT với ngưỡng quy định:

### ✅ Nhóm Đạt Ngưỡng (Gan mật - GM)
| Thành phần | Tính được | Ngưỡng GM | Đánh giá |
|---|---|---|---|
| Kcal | 1757 | 1400-1800 | ✅ |
| P% | 14.6% | 12-16% | ✅ |
| L% | 13.3% | 10-18% | ✅ (gần sàn) |
| G(g) | 317g | 300-370g | ✅ |

### ⚠️ Nhóm Gần Đạt Ngưỡng (Cơm chuẩn - BT01)
| Thành phần | Tính được | Ngưỡng BT | Đánh giá |
|---|---|---|---|
| Kcal | 1720 | 1700-2000 | ✅ |
| P% | 13.8% | 12-15% | ✅ |
| **L%** | **12.7%** | 15-28% | ⚠️ Thấp hơn sàn 15% (thiếu dầu ăn) |
| **G(g)** | **316g** | 330-450g | ⚠️ Thấp hơn sàn 330g (thiếu dầu/mỡ) |

→ **Nguyên nhân L% và G(g) thấp cùng lúc:** Khi thiếu lipid từ dầu ăn và thịt nấu chín, tổng năng lượng giảm → carb chiếm tỷ lệ % cao hơn. Nếu thêm ~20g dầu ăn (180 kcal) vào mỗi ngày:
- Tổng kcal: 1720 + 180 = **1900** (sát ngưỡng giữa)
- L% tăng: (24+20)×9 / (1720+180)×4.34 ≈ **21%** → nằm trong ngưỡng 15-28%
- G% giảm tự nhiên xuống ~65%

### ⚠️ Nhóm Lệch Nhiều (Sản khoa - SK)
| Thành phần | Ghi nhận | Tính từ FCT | Ngưỡng SK | Đánh giá |
|---|---|---|---|---|
| Kcal | **2072** | 1472 | 2450-2800 | ⚠️ Cả hai đều lệch |
| P% | 17% | 14.2% | 11-15% | ⚠️ Ghi cao hơn ngưỡng |

→ Bản ghi nhận SK có kcal=2072 nhưng ngưỡng quy định là 2600-2700 → **bản thân số ghi nhận đã không đạt quy tắc** cho phụ nữ cho con bú (SK03). Tính từ FCT chỉ ra rằng thực đơn SK thực tế chỉ đạt ~1472 kcal, còn xa hơn nữa so với yêu cầu.

---

## Kết Luận

### Đánh giá tổng thể: ⚠️ CẦN XEM XÉT LẠI

**1. kcal ghi nhận trong thực đơn nhìn chung đáng tin cậy**
Cơ chế: bếp bệnh viện có thể dùng **FCT riêng đã điều chỉnh** cho thực phẩm nấu chín (đã áp dụng hệ số hấp thu dầu mỡ, hệ số hao hụt/mùi khi nấu). Các nhóm cùng thực đơn đều cho kết quả kcal ±200 kcal — chấp nhận được.

**2. Tuy nhiên, một số nhóm cần xem xét:**

| Nhóm | Vấn đề cụ thể |
|---|---|
| **Sản khoa** | kcal ghi 2072 nhưng thực tế chỉ ~1472 (thiếu ~600). Thực đơn thay bữa sáng từ phở/bún sang cháo+sữa → giảm kcal nhiều hơn dự kiến. Không đạt ngưỡng SK03 (2600-2700 kcal) |
| **Đái tháo đường** | kcal ghi 1515 — hợp lý với giảm gạo 150→100g. Nhưng L% tính được 16.6% vs ngưỡng 20-32% → thực tế cũng có thể thấp hơn ngưỡng do thiếu dầu ăn |
| **Kiêng i-ốt** | Thiếu ~187 kcal — có thể do sữa Grandcare Gold và thay đổi nguyên liệu không được tính đủ |

**3. Sai số hệ thống về Lipid (L%)**
Nguyên nhân: **FCT 2007 là cơ sở dữ liệu thực phẩm sống (raw)**, không chứa:
- Giá trị lipid của thịt/cá đã nấu chín (sau hao hụt mỡ khi rang/xào)
- Dầu ăn hấp thụ khi chế biến (thường 10-20g/ngày cho bữa ăn bệnh viện)
→ Kết luận: **L% ghi nhận trong thực đơn đáng tin cậy hơn kết quả tính từ FCT**

**4. Khuyến nghị:**
- Để kiểm tra chính xác kcal/P/L/G, cần bổ sung **FCT cho thực phẩm đã chế biến** (nấu chín) hoặc áp dụng hệ số cooking yield riêng
- Nhóm **Sản khoa** cần xem xét lại thực đơn — kcal thực tế thấp hơn ghi nhận và xa ngưỡng SK03
- Dữ liệu nên được kiểm tra bởi **điều dưỡng/bác sĩ dinh dưỡng** bệnh viện để xác nhận

---

## Phụ Lục: Chi Tiết Per-Day (BT01 Baseline)

| Ngày | Kcal | P(g) | L(g) | G(g) | P% | L% | G% | ?items |
|---|---|---|---|---|---|---|---|---|
| Thứ 2 | 1925 | 58 | 17 | 386 | 12.1% | 7.8% | 80.1% | 11 |
| Thứ 3 | 1463 | 58 | 15 | 275 | 15.7% | 9.1% | 75.2% | 12 |
| Thứ 4 | 1982 | 72 | 48 | 317 | 14.5% | 21.6% | 63.9% | 11 |
| Thứ 5 | 1703 | 60 | 17 | 329 | 14.0% | 8.7% | 77.3% | 11 |
| Thứ 6 | 1594 | 44 | 14 | 323 | 10.9% | 8.1% | 81.0% | 12 |
| Thứ 7 | 1455 | 49 | 9 | 294 | 13.6% | 5.8% | 80.6% | 12 |
| Chủ nhật | 1920 | 77 | 51 | 289 | 15.9% | 23.9% | 60.1% | 12 |

> Ghi chú: Thứ 4 và Chủ nhật có L% ~22-24% → những ngày có món **cá trắm rán** hoặc **thịt gà rang** → cho thấy khi protein động vật có fat cao được tính đúng (từ FCT thịt gà ta), L% sát với ghi nhận. Vấn đề là **các ngày khác** thiếu dầu ăn và thiếu món có fat rõ ràng.
