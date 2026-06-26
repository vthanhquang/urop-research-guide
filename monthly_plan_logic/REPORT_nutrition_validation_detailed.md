# BÁO CÁO KIỂM TRA DINH DƯỠNG
## Thực Đơn Cơm Bệnh Viện Mức Ăn 85.680đ — Tháng 5/2026

---

**Ngày báo cáo:** 26/06/2026
**Nguồn dữ liệu:**
- `weekly_meal_plan_85k.json` — Thực đơn cơm tháng 5/2026 (11 nhóm bệnh, 7 ngày × 3 bữa)
- `VTN_FCT_2007_food_composition.csv` — Bảng thành phần dinh dưỡng thực phẩm Việt Nam 2007 (Bộ Y tế)
- `rules.pdf` — Hướng dẫn chế độ ăn bệnh viện (QĐ 2879/QĐ-BYT ngày 10/8/2006)

---

## 1. TỔNG QUAN KẾT QUẢ

Kiểm tra bao gồm:
1. **Tính lại kcal, P, L, G** từ FCT cho mỗi ngày trong thực đơn
2. **So sánh** kết quả tính được với giá trị ghi nhận trong thực đơn
3. **Đối chiếu** với ngưỡng dinh dưỡng theo quy tắc bệnh viện (QĐ 2879/QĐ-BYT)

| Nhóm bệnh | Mã | Kcal ghi | Kcal tính | Δ Kcal | P% ghi | P% tính | L% ghi | L% tính | G% ghi | G% tính | Ghi chú |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Cơm thông thường | BT01 | 1771 | 1720 | -51 | 21% | 13.8% | 21% | 12.7% | 58% | 73.4% | Kcal sát, L% thấp |
| Phẫu thuật | PT | 1771 | 1720 | -51 | 21% | 13.8% | 21% | 12.7% | 58% | 73.4% | Như BT01 |
| Sản khoa | SK | 2072 | 1472 | **-600** | 17% | 14.2% | 25% | 8.0% | 58% | 77.9% | **Chênh lệch lớn** |
| Bệnh thận | TN | 1781 | 1677 | -104 | 21% | 13.8% | 21% | 13.0% | 58% | 73.2% | Kcal sát |
| Tim mạch | TM | 1771 | 1720 | -51 | 21% | 13.8% | 21% | 12.7% | 58% | 73.4% | Như BT01 |
| Đái tháo đường | ĐĐ | 1515 | 1393 | -122 | 25% | 15.2% | 21% | 16.6% | 54% | 68.2% | Kcal sát |
| Gan mật | GM | 1782 | 1757 | -25 | 21% | 14.6% | 21% | 13.3% | 58% | 72.1% | ✅ Kcal rất sát |
| Ung thư | UT | 1782 | 1757 | -25 | 21% | 14.6% | 21% | 13.3% | 58% | 72.1% | ✅ Như GM |
| Gút | GU | 1782 | 1757 | -25 | 21% | 14.6% | 21% | 13.3% | 58% | 72.1% | ✅ Như GM |
| Kiêng i-ốt | IOD | 1726 | 1539 | -187 | 18% | 12.3% | 25% | 5.7% | 57% | 82.0% | Kcal thấp, L% rất thấp |
| Người nhà | — | 1771 | 1720 | -51 | 21% | 13.8% | 21% | 12.7% | 58% | 73.4% | Như BT01 |

> **Ghi chú:** Nhóm PT, TM, BT01, TN, GU, UT, Người nhà dùng chung thực đơn nên cho kết quả gần như y hệt.

---

## 2. PHƯƠNG PHÁP KIỂM TRA

### 2.1. Công thức tính

Với mỗi nguyên liệu trong thực đơn:

```
Năng lượng (kcal) = Giá trị FCT (kcal/100g) × Khối lượng (g) / 100
Protein (g)        = Giá trị FCT (protein g/100g) × Khối lượng (g) / 100
Lipid (g)          = Giá trị FCT (fat g/100g) × Khối lượng (g) / 100
Glucid (g)         = Giá trị FCT (carb g/100g) × Khối lượng (g) / 100
```

Tỷ lệ phần trăm năng lượng:

```
P% = Protein(g) × 4 kcal / (P×4 + L×9 + G×4) × 100
L% = Lipid(g) × 9 kcal / (P×4 + L×9 + G×4) × 100
G% = Glucid(g) × 4 kcal / (P×4 + L×9 + G×4) × 100
```

### 2.2. Hạn chế của phương pháp

**FCT VTN 2007 là cơ sở dữ liệu thực phẩm thô (raw), chưa chế biến:**
- Không có giá trị dinh dưỡng cho thịt/cá đã nấu chín, đã xào, đã rán
- Không có giá trị cho dầu/mỡ hấp thụ trong quá trình chế biến
- Một số thực phẩm phổ biến trong bữa ăn Việt Nam hoàn toàn không có trong FCT

→ **Kết quả kcal có độ chính xác khá tốt**, nhưng **kết quả lipid (L%) luôn thiếu** vì thiếu dầu ăn.

---

## 3. KẾT QUẢ CHI TIẾT THEO NHÓM

---

### 3.1. Cơm Thông Thường — BT01 (Chuẩn)

| Chỉ số | Ghi nhận | Tính từ FCT | Chênh lệch |
|---|---|---|---|
| Năng lượng | 1771 kcal | 1720 kcal | **-51 kcal** |
| Protein | 83 g | 60 g | -23 g |
| Lipid | 58 g | 24 g | -34 g |
| Glucid | 230 g | 316 g | +86 g |
| P% | 21% | 13.8% | -7.2 điểm % |
| L% | 21% | 12.7% | **-8.3 điểm %** |
| G% | 58% | 73.4% | +15.4 điểm % |

**Đánh giá:**
- ✅ kcal: **chênh chỉ -51 kcal** (≈ 3%) → đáng tin cậy
- ⚠️ L% tính được **12.7%** thấp hơn ngưỡng sàn 15% → thiếu dầu ăn
- ⚠️ G% tính được **73.4%** cao hơn vì tỷ lệ bị đẩy lên khi thiếu lipid

**Nguyên nhân L% thấp:** Mỗi bữa trưa và tối có 1-2 món xào/rán. Dầu ăn hấp thụ thêm khoảng **10-15g lipid/ngày** (tương đương 90-135 kcal) nhưng không có trong FCT raw. Nếu bổ sung 15g dầu:
- Kcal: 1720 + 135 = **1855 kcal** (sát mốc giữa)
- L% tăng lên ≈ **21%** → nằm trong ngưỡng 15-28%

**Chi tiết per-day:**

| Ngày | Kcal | P(g) | L(g) | G(g) | P% | L% | G% | SL món ? |
|---|---|---|---|---|---|---|---|---|
| Thứ 2 | 1925 | 58 | 17 | 386 | 12.1% | 7.8% | 80.1% | 11 |
| Thứ 3 | 1463 | 58 | 15 | 275 | 15.7% | 9.1% | 75.2% | 12 |
| Thứ 4 | 1982 | 72 | 48 | 317 | 14.5% | 21.6% | 63.9% | 11 |
| Thứ 5 | 1703 | 60 | 17 | 329 | 14.0% | 8.7% | 77.3% | 11 |
| Thứ 6 | 1594 | 44 | 14 | 323 | 10.9% | 8.1% | 81.0% | 12 |
| Thứ 7 | 1455 | 49 | 9 | 294 | 13.6% | 5.8% | 80.6% | 12 |
| Chủ nhật | 1920 | 77 | 51 | 289 | 15.9% | 23.9% | 60.1% | 12 |
| **TB** | **1720** | **60** | **24** | **316** | **13.8%** | **12.7%** | **73.4%** | — |

> **Quan sát:** Thứ 4 và Chủ nhật có L% ≈ 22-24% → những ngày có cá trắm rán hoặc thịt gà rang (món có fat cao từ FCT thịt gà ta). Các ngày khác L% rất thấp (5-10%) vì thiếu dầu ăn.

**Đối chiếu quy tắc (BT01):**

| Chỉ số | Ngưỡng QĐ 2879 | Tính từ FCT | Đạt? |
|---|---|---|---|
| Kcal | 1800-1900 | 1720 | ⚠️ Thấp hơn 80 kcal |
| P% | 12-14% | 13.8% | ✅ |
| L% | 15-25% | 12.7% | ⚠️ Thấp hơn sàn 15% |
| G(g) | 340-440g | 316g | ⚠️ Thấp hơn sàn 330g |

---

### 3.2. Phẫu Thuật — PT

| Chỉ số | Ghi nhận | Tính từ FCT | Chênh lệch |
|---|---|---|---|
| Năng lượng | 1771 kcal | 1720 kcal | **-51 kcal** |
| P% | 21% | 13.8% | -7.2 điểm % |
| L% | 21% | 12.7% | **-8.3 điểm %** |

→ Kết quả y hệt BT01 vì dùng chung thực đơn.

**Đối chiếu quy tắc (PT04 - giai đoạn hồi phục):**

| Chỉ số | Ngưỡng QĐ 2879 | Tính từ FCT | Đạt? |
|---|---|---|---|
| Kcal | 1800-1900 | 1720 | ⚠️ Thấp hơn 80 kcal |
| P% | 12-14% | 13.8% | ✅ |
| L% | 15-25% | 12.7% | ⚠️ Thấp hơn sàn 15% |

---

### 3.3. Sản Khoa — SK ⚠️

| Chỉ số | Ghi nhận | Tính từ FCT | Chênh lệch |
|---|---|---|---|
| Năng lượng | **2072 kcal** | **1472 kcal** | **-600 kcal** |
| Protein | 87 g | 52 g | -35 g |
| Lipid | 59 g | 13 g | -46 g |
| Glucid | 299 g | 287 g | -12 g |
| P% | 17% | 14.2% | -2.8 điểm % |
| L% | 25% | 8.0% | **-17.0 điểm %** |

**⚠️ Đây là nhóm có chênh lệch lớn nhất.**

**Nguyên nhân chênh lệch -600 kcal:**

Thực đơn SK khác chuẩn ở hai điểm chính:

1. **Bữa sáng** thay từ Phở/Bún (~450-550 kcal) → **Cháo thịt nạc + Sữa Grandcare Gold** (~300-350 kcal)
   - Món cháo+sữa có nhiều nguyên liệu không có trong FCT
   - Trường hợp cụ thể: "thịt lợn + Gia vị vừa đủ + Sữa Grandcare Gold 180ml: 01 hộp" → phần sữa Grandcare Gold không có trong FCT → thiếu ~130-180 kcal/ngày × 7 = 910-1260 kcal/tuần

2. **Rau cải** (cải bắp, cải chíp, cải ngọt) → thay bằng **bí xanh, đậu cove** (không thay đổi kcal đáng kể)

**Chi tiết per-day:**

| Ngày | Kcal | P(g) | L(g) | G(g) | P% | L% | G% | SL món ? |
|---|---|---|---|---|---|---|---|---|
| Thứ 2 | 1482 | 44 | 9 | 307 | 11.8% | 5.4% | 82.8% | 11 |
| Thứ 3 | 1491 | 57 | 16 | 280 | 15.4% | 9.5% | 75.1% | 12 |
| Thứ 4 | 1390 | 48 | 11 | 275 | 13.6% | 7.4% | 79.0% | 10 |
| Thứ 5 | 1491 | 57 | 16 | 280 | 15.4% | 9.5% | 75.1% | 11 |
| Thứ 6 | 1506 | 42 | 8 | 316 | 11.1% | 4.8% | 84.0% | 8 |
| Thứ 7 | 1529 | 67 | 18 | 275 | 17.4% | 10.8% | 71.8% | 8 |
| Chủ nhật | 1418 | 51 | 13 | 275 | 14.5% | 8.1% | 77.4% | 9 |
| **TB** | **1472** | **52** | **13** | **287** | **14.2%** | **8.0%** | **77.9%** | — |

**Đối chiếu quy tắc (SK03 - Phụ nữ cho con bú 6 tháng đầu):**

| Chỉ số | Ngưỡng QĐ 2879 | Ghi nhận | Tính từ FCT | Đạt? |
|---|---|---|---|---|
| Kcal | **2600-2700** | **2072** | **1472** | ❌ Không đạt |
| P% | 12-14% | 17% | 14.2% | ⚠️ Ghi cao hơn ngưỡng |
| L% | 20-25% | 25% | 8.0% | ❌ Thấp hơn ngưỡng |
| G(g) | 390-470g | 299g | 287g | ❌ Thấp hơn ngưỡng |

**→ Kết luận:** Cả giá trị ghi nhận lẫn tính từ FCT đều **không đạt** ngưỡng quy định cho chế độ ăn phụ nữ cho con bú. Thực đơn SK thực tế chỉ đạt khoảng **1472-2072 kcal/ngày**, trong khi SK03 yêu cầu **2600-2700 kcal/ngày**. Cần xem xét lại.

---

### 3.4. Bệnh Thận — TN

| Chỉ số | Ghi nhận | Tính từ FCT | Chênh lệch |
|---|---|---|---|
| Năng lượng | 1781 kcal | 1677 kcal | **-104 kcal** |
| P% | 21% | 13.8% | -7.2 điểm % |
| L% | 21% | 13.0% | -8.0 điểm % |

→ Dùng chung thực đơn với BT01, chỉ thay 4 loại rau có kali cao.

**Đối chiếu quy tắc (TN - Viêm cầu thận cấp):**

| Chỉ số | Ngưỡng QĐ 2879 | Tính từ FCT | Đạt? |
|---|---|---|---|
| Kcal | 1800-1900 | 1677 | ⚠️ Thấp hơn 123 kcal |
| P% | 12-14% | 13.8% | ✅ |
| L% | 20-25% | 13.0% | ❌ Thấp hơn sàn 20% |

**Về Kali và Natri** — không thể kiểm tra từ FCT 2007 vì FCT không chứa cột Kali/Natri. Cần CSDL riêng cho điện giải.

---

### 3.5. Tim Mạch — TM

| Chỉ số | Ghi nhận | Tính từ FCT | Chênh lệch |
|---|---|---|---|
| Năng lượng | 1771 kcal | 1720 kcal | **-51 kcal** |
| P% | 21% | 13.8% | -7.2 điểm % |
| L% | 21% | 12.7% | **-8.3 điểm %** |

→ Kết quả y hệt BT01 (dùng chung thực đơn).

**Đối chiếu quy tắc (TM01 - Suy tim độ 1-2):**

| Chỉ số | Ngưỡng QĐ 2879 | Tính từ FCT | Đạt? |
|---|---|---|---|
| Kcal | 1800-1900 | 1720 | ⚠️ Thấp hơn 80 kcal |
| P% | 12-14% | 13.8% | ✅ |
| L% | 20-30% | 12.7% | ❌ Thấp hơn sàn 20% |

---

### 3.6. Đái Tháo Đường — ĐĐ

| Chỉ số | Ghi nhận | Tính từ FCT | Chênh lệch |
|---|---|---|---|
| Năng lượng | 1515 kcal | 1393 kcal | **-122 kcal** |
| Protein | 79 g | 53 g | -26 g |
| Lipid | 57 g | 26 g | -31 g |
| Glucid | 171 g | 238 g | +67 g |
| P% | 25% | 15.2% | -9.8 điểm % |
| L% | 21% | 16.6% | -4.4 điểm % |
| G% | 54% | 68.2% | +14.2 điểm % |

**Nhận xét:** Thực đơn ĐĐ giảm gạo 150→100g ở trưa và tối → lẽ ra giảm ~143g gạo/ngày = ~492 kcal. Từ 1771 - 492 = **1279 kcal** lý thuyết. Ghi nhận 1515 kcal → có thể tăng thêm khẩu phần protein để bù. Tính được 1393 kcal → chênh -122 kcal so với ghi nhận.

**Chi tiết per-day:**

| Ngày | Kcal | P(g) | L(g) | G(g) | P% | L% | G% | SL món ? |
|---|---|---|---|---|---|---|---|---|
| Thứ 2 | 1750 | 48 | 31 | 321 | 10.9% | 15.7% | 73.4% | 12 |
| Thứ 3 | 1176 | 57 | 15 | 204 | 19.4% | 11.2% | 69.4% | 11 |
| Thứ 4 | 1638 | 64 | 47 | 241 | 15.7% | 25.6% | 58.8% | 12 |
| Thứ 5 | 1367 | 52 | 16 | 255 | 15.3% | 10.2% | 74.5% | 11 |
| Thứ 6 | 1064 | 32 | 13 | 205 | 11.9% | 11.1% | 77.0% | 13 |
| Thứ 7 | 1178 | 49 | 9 | 224 | 16.8% | 7.1% | 76.1% | 11 |
| Chủ nhật | 1576 | 69 | 50 | 213 | 17.4% | 28.6% | 54.0% | 12 |
| **TB** | **1393** | **53** | **26** | **238** | **15.2%** | **16.6%** | **68.2%** | — |

**Biến động rất lớn:** Thứ 6 chỉ 1064 kcal, Thứ 2 là 1750 kcal → chênh 686 kcal/ngày. Cần xác nhận lại dữ liệu cho Thứ 6.

**Đối chiếu quy tắc (DD01 - Đái tháo đường đơn thuần):**

| Chỉ số | Ngưỡng QĐ 2879 | Ghi nhận | Tính từ FCT | Đạt? |
|---|---|---|---|---|
| Kcal | 1500-1700 | 1515 | 1393 | ✅ Ghi đạt, tính thấp |
| P% | 15-20% | 25% | 15.2% | ⚠️ Ghi cao hơn ngưỡng |
| L% | 20-30% | 21% | 16.6% | ⚠️ Tính thấp hơn sàn 20% |
| G(g) | 200-280g | 171g | 238g | ⚠️ Ghi thấp hơn sàn |
| Chất xơ | ≥20g | — | — | ❓ Không kiểm tra được |

---

### 3.7. Gan Mật — GM ✅

| Chỉ số | Ghi nhận | Tính từ FCT | Chênh lệch |
|---|---|---|---|
| Năng lượng | 1782 kcal | 1757 kcal | **-25 kcal** |
| P% | 21% | 14.6% | -6.4 điểm % |
| L% | 21% | 13.3% | -7.7 điểm % |

→ Đây là nhóm có **kcal gần nhất với ghi nhận** (chỉ -25 kcal).

**Đối chiếu quy tắc (GM04 - Xơ gan):**

| Chỉ số | Ngưỡng QĐ 2879 | Tính từ FCT | Đạt? |
|---|---|---|---|
| Kcal | 1500-1700 | 1757 | ⚠️ Cao hơn 57 kcal |
| P% | 12-16% | 14.6% | ✅ |
| L% | 10-15% | 13.3% | ✅ |
| Natri | ≤2000 mg | — | ❓ Không kiểm tra |

---

### 3.8. Ung Thư — UT

Kết quả y hệt GM (dùng chung thực đơn). Δ kcal = **-25 kcal**.

---

### 3.9. Gút — GU

Kết quả y hệt GM (dùng chung thực đơn). Δ kcal = **-25 kcal**.

---

### 3.10. Kiêng I-ốt — IOD ⚠️

| Chỉ số | Ghi nhận | Tính từ FCT | Chênh lệch |
|---|---|---|---|
| Năng lượng | 1726 kcal | 1539 kcal | **-187 kcal** |
| Protein | 78 g | 47 g | -31 g |
| Lipid | 49 g | 10 g | -39 g |
| Glucid | 244 g | 316 g | +72 g |
| P% | 18% | 12.3% | -5.7 điểm % |
| L% | 25% | 5.7% | **-19.3 điểm %** |

**⚠️ L% tính được chỉ 5.7% — thấp nhất trong tất cả các nhóm.**

**Nguyên nhân:**
- Thực đơn IOD kiêng trứng, đậu phụ → thiếu 2 nguồn lipid quan trọng
- Phần lớn các món còn lại là gạo + rau → carb cao, lipid rất thấp
- Không có dầu ăn trong FCT → L% tính được quá thấp

**Chi tiết per-day:**

| Ngày | Kcal | P(g) | L(g) | G(g) | P% | L% | G% | SL món ? |
|---|---|---|---|---|---|---|---|---|
| Thứ 2 | 1678 | 43 | 7 | 361 | 10.3% | 3.6% | 86.1% | 13 |
| Thứ 3 | 1426 | 49 | 10 | 284 | 13.8% | 6.5% | 79.6% | 13 |
| Thứ 4 | 1587 | 52 | 8 | 326 | 13.2% | 4.7% | 82.1% | 11 |
| Thứ 5 | 1584 | 47 | 12 | 322 | 11.9% | 6.8% | 81.3% | 13 |
| Thứ 6 | 1637 | 44 | 14 | 332 | 10.9% | 7.9% | 81.2% | 12 |
| Thứ 7 | 1413 | 46 | 9 | 287 | 13.0% | 5.8% | 81.2% | 14 |
| Chủ nhật | 1449 | 48 | 8 | 297 | 13.2% | 4.7% | 82.0% | 12 |
| **TB** | **1539** | **47** | **10** | **316** | **12.3%** | **5.7%** | **82.0%** | — |

→ **Mỗi ngày đều có G% > 79%** — thực đơn gần như hoàn toàn carb. L% trung bình chỉ 5.7% (bao gồm cả lipid có sẵn trong gạo và rau). Nếu bổ sung dầu ăn ~10g/ngày: L% tăng lên ~11%, kcal tăng ~90 → 1629 kcal → vẫn thiếu so với ghi nhận.

---

### 3.11. Người Nhà

Kết quả y hệt BT01 (dùng chung thực đơn). Δ kcal = **-51 kcal**.

---

## 4. VẤN ĐỀ HỆ THỐNG

### 4.1. FCT 2007 Là Dữ Liệu Thực Phẩm Sống (Raw)

Đây là nguyên nhân gốc của hầu hết sai số:

| Thiếu trong FCT | Tác động |
|---|---|
| Thịt bò/thịt lợn/thịt ngan đã nấu chín | Không tính được protein/lipid chính |
| Các loại cá (trắm, basa, rô, thu, lóc) | Thiếu protein từ cá |
| Tôm, mực, chả cá, lạc rim, đậu phụ rán | Thiếu nguồn protein đã chế biến |
| Dầu ăn hấp thụ khi xào/rán | **Nguyên nhân chính L% thấp** |

**Ảnh hưởng:**
- **kcal**: sai số nhỏ (-25 đến -122 kcal) vì carb chiếm tỷ trọng lớn trong bữa ăn Việt và FCT có đủ dữ liệu carb
- **L%**: luôn thiếu 8-20 điểm phần trăm vì thiếu dầu/mỡ chế biến
- **P%**: luôn thấp hơn 5-10 điểm phần trăm vì thiếu thịt/cá nấu chín

### 4.2. Thực Phẩm Không Tìm Thấy Trong FCT

Danh sách món ăn trong thực đơn không khớp với FCT:

| Món ăn | Tình trạng FCT | Ghi chú |
|---|---|---|
| Gạo tám Lào | ✅ Có (→ gạo tẻ máy) | Khớp tốt |
| Bún, bánh phở | ✅ Có | Khớp tốt |
| Rau củ (củ cải, cải bắp, bí xanh...) | ✅ Có | Khớp tốt |
| Thịt gà ta | ✅ Có | Khớp tốt |
| Trứng gà | ✅ Có | Khớp tốt |
| Thịt bò, thịt lợn, thịt ngan | ❌ Không có | Chỉ có FCT gốc |
| Cá các loại (trắm, basa, rô, thu, lóc) | ❌ Không có | Hoàn toàn thiếu |
| Tôm, mực | ❌ Không có | Hoàn toàn thiếu |
| Chả cá, chả lá lốt, lạc rim | ❌ Không có | Hoàn toàn thiếu |
| Đậu phụ rán | ❌ Không có | Hoàn toàn thiếu |
| Thịt gà (cả xương) rang | ❌ Không có | Chỉ có thịt gà ta sống |
| Sữa Grandcare Gold | ❌ Không có | Thiếu hoàn toàn |
| Dầu ăn (dầu lạc có trong FCT) | ⚠️ Có nhưng chưa áp dụng | Chưa được cộng vào |

### 4.3. Sự Không Nhất Quán Nội Tại Trong Dữ Liệu

**Vấn đề Thứ 6 Đái tháo đường:** Chỉ 1064 kcal — thấp hơn rất nhiều so với các ngày khác (1176-1750 kcal). Cần kiểm tra lại dữ liệu gốc.

**Vấn đề Sản khoa:** kcal ghi nhận 2072 nhưng ngưỡng SK03 yêu cầu 2600-2700 → không đạt quy tắc. Tính từ FCT ra 1472 → càng xa hơn.

---

## 5. KẾT LUẬN VÀ KHUYẾN NGHỊ

### 5.1. Đánh Giá Tổng Thể

| Tiêu chí | Kết quả |
|---|---|
| Độ chính xác kcal | ⚠️ Khá (8/11 nhóm ≤ ±200 kcal) |
| Độ chính xác P/L/G% | ⚠️ Chỉ đáng tin khi đã điều chỉnh dầu ăn |
| Đối chiếu quy tắc | ⚠️ 10/11 nhóm có ít nhất 1 chỉ số lệch ngưỡng |
| Tính nhất quán nội tại | ⚠️ Một số ngày có kcal bất thường |

### 5.2. Nhóm Cần Xem Xét Đặc Biệt

**① Sản khoa (SK) — Ưu tiên cao nhất**
- kcal ghi nhận 2072 nhưng tính được chỉ 1472 — chênh -600
- Thực đơn thực tế không đạt ngưỡng SK03 (2600-2700 kcal)
- Khuyến nghị: bộ phận dinh dưỡng bệnh viện cần rà soát lại thực đơn SK

**② Đái tháo đường (ĐĐ) — Ưu tiên cao**
- P% ghi nhận 25% vượt ngưỡng 15-20%
- Thứ 6 chỉ 1064 kcal — bất thường cần kiểm tra
- Khuyến nghị: xác nhận lại số liệu từng ngày

**③ Kiêng i-ốt (IOD) — Ưu tiên trung bình**
- L% rất thấp (5.7%) do kiêng trứng và đậu phụ
- Khuyến nghị: kiểm tra xem thực đơn có đảm bảo đủ lipid từ các nguồn khác không

### 5.3. Khuyến Nghị Chung

1. **Bổ sung CSDL FCT cho thực phẩm chế biến** (đã nấu chín, có hệ số cooking yield)
2. **Áp dụng hệ số dầu ăn** khi xào/rán: thêm 10-15g lipid/ngày cho mỗi bữa có món xào
3. **Xác nhận lại** số liệu từng ngày của nhóm Đái tháo đường (Thứ 6)
4. **Rà soát thực đơn Sản khoa** với bộ phận dinh dưỡng bệnh viện
5. **Bổ sung CSDL điện giải** (Kali, Natri, Phosphat) để kiểm tra đầy đủ quy tắc cho bệnh thận, tim mạch

---

## 6. PHỤ LỤC

### 6.1. Cấu Trúc Thực Đơn Mỗi Ngày

```
Bữa sáng (6h):   1 món chính (phở/bún/cháo...) + 1 loại sữa
Bữa trưa (11h): Gạo + Rau + 2 món protein + 1 món canh
Bữa tối (17h):  Gạo + Rau + 2 món protein + 1 món canh
```

### 6.2. Giá Trị FCT Đã Sử Dụng (Mẫu)

| Thực phẩm | FCT tương ứng | Kcal/100g | P/100g | L/100g | G/100g |
|---|---|---|---|---|---|
| Gạo tám Lào | Gạo tẻ máy | 344 | 7.9 | 1.0 | 75.9 |
| Bánh phở (Phở) | Bánh phở | 143 | 3.2 | 0.4 | 31.7 |
| Bún | Bún | 110 | 1.7 | — | 25.7 |
| Củ cải trắng | Củ cải trắng | 18 | 0.7 | 0.1 | 3.6 |
| Cải bắp | Cải bắp | 22 | 1.3 | 0.2 | 3.4 |
| Cải xanh | Cải xanh | 20 | 2.1 | 0.2 | 2.0 |
| Bí xanh | Bí xanh | 12 | 0.6 | 0.1 | 2.2 |
| Khoai tây | Khoai tây | 93 | 2.0 | 0.1 | 20.9 |
| Thịt gà ta | Thịt gà ta | 199 | 20.3 | 13.1 | 0 |
| Trứng gà | Trứng gà | 166 | 14.8 | 11.6 | 0.5 |
| Dầu lạc | Dầu lạc | 900 | 0 | 100 | 0 |

### 6.3. Script và Dữ Liệu Liên Quan

```
validate_nutrition.py          — Script kiểm tra dinh dưỡng (tính kcal từ FCT)
validation_summary.json         — Kết quả structured cho 11 nhóm × 7 ngày
VTN_FCT_2007_food_composition.csv — Bảng FCT gốc (526 dòng)
```

---

*Báo cáo được tạo tự động bằng script `validate_nutrition.py`.*
*Cần xác nhận lại với bộ phận dinh dưỡng bệnh viện trước khi sử dụng cho mục đích nghiên cứu.*
