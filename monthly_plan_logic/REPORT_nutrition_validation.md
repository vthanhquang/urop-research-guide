# Báo Cáo Kiểm Tra Dinh Dưỡng Thực Đơn 85K

**Script:** `validate_nutrition.py`
**Ngày báo cáo:** 08/07/2026
**Nguồn dữ liệu:**
- `weekly_meal_plan_85k.json` — Thực đơn cơm tháng 5/2026 (11 nhóm bệnh, 7 ngày × 3 bữa)
- `VTN_FCT_2007_food_composition.csv` — Bảng thành phần dinh dưỡng thực phẩm Việt Nam 2007 (Bộ Y tế, 2077 entries)
- `sp_thuong_mai.csv` — Thành phần dinh dưỡng thực phẩm thương mại Việt Nam (bổ sung)

---

## Tóm Tắt Kết Quả (Sau FCT Mapping Cleanup)

| Nhóm | Code | Rec kcal | Calc kcal | Δ kcal | P% | L% | G% | Status |
|---|---|---|---|---|---|---|---|---|
| Cơm chuẩn | BT01-CƠM | 1771 | 2050 | +279 | 21.2% | 19.5% | 59.3% | REVIEW |
| Phẫu thuật | PT01-CƠM, PT02-CƠM... | 1771 | 2050 | +279 | 21.2% | 19.5% | 59.3% | REVIEW |
| Sản khoa | SẢN | 2072 | 1971 | **-101** | 19.3% | 16.7% | 63.9% | REVIEW |
| Bệnh thận | TN01-CƠM, TN02-CƠM | 1781 | 2038 | +257 | 21.3% | 19.6% | 59.1% | REVIEW |
| Tim mạch | TM01-CƠM, TH01-CƠM | 1771 | 2050 | +279 | 21.2% | 19.5% | 59.3% | REVIEW |
| Đái tháo đường | ĐĐ01-CƠM, ĐĐ02-CƠM | 1515 | 1729 | +214 | 24.0% | 22.6% | 53.4% | REVIEW |
| Gan mật | GM01-CƠM | 1782 | 2102 | +320 | 20.9% | 21.4% | 57.8% | REVIEW |
| Ung thư | UT01-CƠM | 1782 | 2102 | +320 | 20.9% | 21.4% | 57.8% | REVIEW |
| Gút | GU01-CƠM, GU03-CƠM | 1782 | 2102 | +320 | 20.9% | 21.4% | 57.8% | REVIEW |
| Kiêng i-ốt | IOD | 1726 | 2132 | +406 | 20.2% | 19.5% | 60.2% | REVIEW |
| Người nhà | NGƯỜI NHÀ | 1771 | 2050 | +279 | 21.2% | 19.5% | 59.3% | REVIEW |

**Tất cả 11 nhóm đều ⚠️ REVIEW** — không có nhóm nào đạt đầy đủ ngưỡng quy định. Chi tiết rules violations ở Mục 3.

---

## Mục 1: Lịch Sử Xử Lý — FCT Mapping Cleanup (08/07/2026)

### 1.1. FCT Name Fixes (map-to-self → correct FCT entry)

Trước đây một số key trong `FCT_NAMES{}` được set map-to-self (`"cà rốt": "cà rốt"`) nhưng FCT gốc không có entry tên đó, dẫn đến direct lookup fail → fuzzy fallback nhảy sai entry.

| Key | Before (broken) | After (fixed) | kcal/100g before | kcal/100g after |
|---|---|---|---|---|
| `cà rốt` | fuzzy → `cà rốt khô` (NOT direct match) | `cà rốt (củ đỏ, vàng)` | 292 | **39** |
| `bí đỏ` | fuzzy → `hạt bí đỏ rang` | `bí ngô` | 519 | **27** |
| `ớt` | fuzzy → `tương ớt` | `ớt đỏ to` | 37 | **23** |

### 1.2. FCT Name Redirects (regional names / typos → correct entry)

| Key | FCT target | kcal/100g | Reason |
|---|---|---|---|
| `thịt lợn vai` | `thịt lợn nửa nạc, nửa mỡ` | 260 | Thịt vai thực tế có cả nạc và mỡ |
| `thịt vai quay` | `thịt lợn nửa nạc, nửa mỡ` | 260 | Same |
| `thịt lợn vai quay` | `thịt lợn nửa nạc, nửa mỡ` | 260 | Same |
| `cải ngọt` | `dưa cải bẹ` | 17 | Là dưa muối, không phải cải xanh tươi |
| `thịt bò` | `thịt bò loại i` | 118 | Direct match; FCT không có thịt bò nạc |

### 1.3. Compound Dish Parsing — 12 patterns

Hàm `parse_compound_dish()` trong `validate_nutrition.py` xử lý các món ăn có nhiều nguyên liệu với trọng lượng riêng, tách thành các thành phần để lookup FCT chính xác hơn.

| # | Dish (raw) | Parsed as | kcal/100g (composite) |
|---|---|---|---|
| 1 | `Thịt lợn băm xào cà rốt, hành lá: 50g, 10g, 5g` | thịt lợn nạc + cà rốt + hành lá | ~139 |
| 2 | `Tôm rang thịt lợn, hành lá: 60g, 70g, 5g` | tôm đồng + thịt lợn nạc + hành lá | ~90 |
| 3 | `Thịt lợn xào hành tây, cà rốt: 70g, 10g, 10g` | thịt lợn nạc + cà rốt + hành tây | ~139 |
| 4 | `Thịt bò xào cần tỏi tây, hành tây: 60g, 20g, 10g` | thịt bò loại i + hành tây + hành tây | ~118 |
| 5 | `Ức gà xào hành tây, cà rốt: 60g, 10g, 10g` | thịt gà ta + cà rốt + hành tây | ~199 |
| 6 | `Thịt lợn nạc vai xào cần tỏi tây, hành tây: 100g, 10g, 5g` | thịt lợn nửa nạc nửa mỡ + hành tây + hành tây | ~260 |
| 7 | `Thịt lợn nạc vai xào ớt đà lạt: 100g, 20g` | thịt lợn nửa nạc nửa mỡ + ớt đỏ to | ~260 |
| 8 | `Thịt lợn băm xào hành lá: 50g, 5g` | thịt lợn nạc + hành lá | ~139 |
| 9 | `Thịt bê xào sả ớt: 50g, 10g, 5g` | thịt bê nạc + hành tây + ớt đỏ to | ~85 |
| 10 | `Thịt lợn, trứng gà kho tàu: 90g, 1 quả` | thịt lợn nạc + trứng gà (50g) | ~166 |
| 11 | `Trứng đúc thịt: 01 quả, 10g` | trứng gà (50g) + thịt lợn nạc (10g) | ~166 |
| 12 | `Tôm rang thịt lợn: 60g, 70g` | tôm đồng + thịt lợn nạc | ~90 |

> Định dạng pattern: `(dish_name_substring, [(fct_name, weight_index), ...])`
> weight_index cho biết trọng lượng nào trong chuỗi gốc tương ứng với nguyên liệu đó (0 = trọng lượng đầu tiên).

### 1.4. Known FCT gaps (chưa xử lý)

| FCT target | Vấn đề | Tác động |
|---|---|---|
| `thịt bò loại i` | FCT không có thịt bò nạc → dùng có mỡ (118 vs ~100 kcal/100g nạc) | Protein % hơi cao hơn thực tế |
| `thịt bê mỡ` (fuzzy fallback) | Không có thịt bê nạc | Tương tự |
| `thịt lợn mỡ` (fuzzy fallback) | Fuzzy fallback cho `thịt lợn` → mỡ thay vì nạc | kcal hơi cao nếu dùng bare "thịt lợn" |
| `Cá trắm rán xốt cà chua` | Vẫn dùng yield factor 0.85 (không parse thành nguyên liệu) | Cà chua bị bỏ qua, ảnh hưởng nhỏ |
| `Thịt lợn xào ớt đà lạt` | Vẫn dùng yield factor 0.85 (không parse thành nguyên liệu) | Ớt bị bỏ qua, ảnh hưởng nhỏ |

Xem `special_case.md` đầy đủ.

---

## Mục 2: Đối Chiếu Quy Tắc (QĐ 2879/QĐ-BYT)

### 2.1. Cơm Thông Thường — BT01 (Chuẩn)

| Chỉ số | Ngưỡng QĐ 2879 | Ghi nhận | Tính từ FCT | Đạt? |
|---|---|---|---|---|
| Kcal | 1800–1900 | 1771 | 2050 | ⚠️ Tính cao hơn 50–250 kcal |
| P% | 12–15% | 21% | 21.2% | ❌ Cao hơn ngưỡng |
| L% | 15–25% | 21% | 19.5% | ✅ Sát ngưỡng giữa |
| G(g) | 330–450g | 230g | 304g | ⚠️ Thấp hơn sàn 330g |

**Chi tiết per-day:**

| Ngày | Kcal | P(g) | L(g) | G(g) | P% | L% | G% |
|---|---|---|---|---|---|---|---|
| Thứ 2 | 1922 | 115.0 | 29.7 | 299.6 | 23.9% | 13.9% | 62.2% |
| Thứ 3 | **2370** | 105.3 | **81.3** | 304.1 | 17.8% | **30.9%** | 51.3% |
| Thứ 4 | 1763 | 92.1 | 23.5 | 295.9 | 20.9% | 12.0% | 67.1% |
| Thứ 5 | 2100 | 113.7 | 47.8 | 304.2 | 21.6% | 20.5% | 57.9% |
| Thứ 6 | 2102 | **120.2** | 36.1 | 324.4 | **22.9%** | 15.4% | 61.7% |
| Thứ 7 | 1934 | 99.5 | 39.7 | 295.0 | 20.6% | 18.5% | 61.0% |
| Chủ nhật | **2154** | 114.5 | 53.1 | 304.9 | 21.2% | 22.2% | 56.6% |
| **TB** | **2050** | **109** | **44** | **304** | **21.2%** | **19.5%** | **59.3%** |

> **Quan sát:** Thứ 3 có kcal cao nhất (2370) do có món nhiều lipid. P% dao động 17.8–23.9%, L% dao động 12.0–30.9% — biến động lớn giữa các ngày.

---

### 2.2. Phẫu Thuật / Bệnh Lý Chung — PT

Dùng chung thực đơn với BT01 → kết quả y hệt BT01.

| Chỉ số | Ngưỡng QĐ 2879 | Tính từ FCT | Đạt? |
|---|---|---|---|
| Kcal | 1800–1900 | 2050 | ⚠️ Cao hơn ngưỡng |
| P% | 12–14% | 21.2% | ❌ Cao hơn ngưỡng |

---

### 2.3. Sản Khoa — SK

| Chỉ số | Ngưỡng QĐ 2879 | Ghi nhận | Tính từ FCT | Đạt? |
|---|---|---|---|---|
| Kcal | 2450–2800 | 2072 | 1971 | ❌ Cả hai đều dưới ngưỡng |
| P% | 12–15% | 17% | 19.3% | ❌ Cao hơn ngưỡng |
| L% | 20–25% | 25% | 16.7% | ❌ Thấp hơn sàn |
| G(g) | 350–450g | 299g | 315g | ❌ Thấp hơn sàn |

**Chi tiết per-day:**

| Ngày | Kcal | P% | L% | G% |
|---|---|---|---|---|
| Thứ 2 | 1849 | 21.0% | 12.8% | 66.2% |
| Thứ 3 | 2068 | 18.9% | 21.5% | 59.6% |
| Thứ 4 | 1825 | 20.1% | 11.8% | 68.1% |
| Thứ 5 | **2258** | 18.1% | 26.0% | 55.9% |
| Thứ 6 | 1920 | 18.6% | 8.8% | 72.6% |
| Thứ 7 | **2129** | 19.2% | 20.4% | 60.4% |
| Chủ nhật | 1749 | 19.7% | 12.8% | 67.6% |

→ **Kết luận:** Cả kcal ghi nhận (2072) lẫn tính từ FCT (1971) đều không đạt ngưỡng SK03 cho phụ nữ cho con bú (2600–2700 kcal/ngày). Thực đơn SK thực tế thiếu khoảng **500–700 kcal/ngày** so với yêu cầu.

---

### 2.4. Bệnh Thận — TN

| Chỉ số | Ngưỡng QĐ 2879 | Ghi nhận | Tính từ FCT | Đạt? |
|---|---|---|---|---|
| Kcal | 1800–1900 | 1781 | 2038 | ⚠️ Tính cao hơn ngưỡng |
| P% | 12–14% | 21% | 21.3% | ❌ Cao hơn ngưỡng |

Dùng chung thực đơn với BT01, chỉ thay 4 loại rau có kali cao.

> **Lưu ý:** FCT 2007 không chứa cột Kali/Natri → không kiểm tra được đầy đủ quy tắc cho bệnh thận.

---

### 2.5. Tim Mạch — TM

| Chỉ số | Ngưỡng QĐ 2879 | Tính từ FCT | Đạt? |
|---|---|---|---|
| Kcal | 1800–1900 | 2050 | ⚠️ Cao hơn ngưỡng |
| P% | 12–14% | 21.2% | ❌ Cao hơn ngưỡng |
| L% | 20–30% | 19.5% | ⚠️ Gần sàn 20% |

→ Dùng chung thực đơn với BT01.

---

### 2.6. Đái Tháo Đường — ĐĐ

| Chỉ số | Ngưỡng QĐ 2879 | Ghi nhận | Tính từ FCT | Đạt? |
|---|---|---|---|---|
| Kcal | 1500–1700 | 1515 | 1729 | ⚠️ Ghi sát, tính cao |
| P% | 15–20% | 25% | 24.0% | ❌ Cao hơn ngưỡng |
| L% | 20–30% | 21% | 22.6% | ✅ Sát ngưỡng giữa |

**Chi tiết per-day:**

| Ngày | Kcal | P% | L% | G% |
|---|---|---|---|---|
| Thứ 2 | 1580 | 24.7% | 15.2% | 60.1% |
| Thứ 3 | 2038 | 20.6% | **35.8%** | 43.7% |
| Thứ 4 | 1462 | 23.4% | 13.8% | 62.9% |
| Thứ 5 | 1909 | **24.4%** | 22.0% | 53.5% |
| Thứ 6 | 1644 | **27.5%** | 19.2% | 53.3% |
| Thứ 7 | 1614 | 23.9% | 22.0% | 54.1% |
| Chủ nhật | 1852 | 24.2% | 25.6% | 50.2% |

→ **Thứ 3 có L% = 35.8%** — cao hơn ngưỡng 30%. Thứ 2, 4, 6, 7 có P% > 20%.

---

### 2.7. Gan Mật — GM

| Chỉ số | Ngưỡng QĐ 2879 | Ghi nhận | Tính từ FCT | Đạt? |
|---|---|---|---|---|
| Kcal | 1500–1800 | 1782 | 2102 | ❌ Cao hơn ngưỡng |
| P% | 12–16% | 21% | 20.9% | ❌ Cao hơn ngưỡng |
| L% | 10–18% | 21% | 21.4% | ❌ Cao hơn ngưỡng |

→ Thực đơn GM tính ra kcal cao hơn cả ghi nhận. L% = 21.4% vượt ngưỡng 18%.

---

### 2.8. Ung Thư — UT

Kết quả y hệt GM (dùng chung thực đơn).

| Chỉ số | Ngưỡng QĐ 2879 | Tính từ FCT | Đạt? |
|---|---|---|---|
| Kcal | 1800–2000 | 2102 | ❌ Cao hơn ngưỡng |
| P% | 12–15% | 20.9% | ❌ Cao hơn ngưỡng |
| L% | 20–25% | 21.4% | ✅ Sát ngưỡng trên |
| G(g) | 300–370g | 304g | ✅ |

---

### 2.9. Gút — GU

Kết quả y hệt GM/UT.

---

### 2.10. Kiêng I-ốt (Tuyến Giáp) — IOD

| Chỉ số | Ngưỡng QĐ 2879 | Ghi nhận | Tính từ FCT | Đạt? |
|---|---|---|---|---|
| Kcal | 1800–2000 | 1726 | 2132 | ❌ Tính cao hơn ngưỡng |
| P% | 12–18% | 18% | 20.2% | ❌ Cao hơn ngưỡng |

→ Thực đơn IOD kiêng trứng, đậu phụ → thiếu nguồn lipid và protein chính. kcal tính ra 2132 cao hơn ghi nhận 1726 → có thể phần sữa không được tính đủ.

---

### 2.11. Người Nhà Người Bệnh

Dùng chung thực đơn với BT01 → kết quả y hệt.

---

## Mục 3: Tổng Hợp Rules Violations

| Nhóm | kcal | P% | L% | G(g) |
|---|---|---|---|---|
| BT01 (DEFAULT) | ⚠️ HIGH | ❌ HIGH | ✅ OK | ⚠️ LOW |
| PT | ⚠️ HIGH | ❌ HIGH | ✅ OK | — |
| SK | ❌ LOW | ❌ HIGH | ❌ LOW | ❌ LOW |
| TN | ⚠️ HIGH | ❌ HIGH | ✅ OK | — |
| TM | ⚠️ HIGH | ❌ HIGH | ⚠️ LOW | — |
| ĐĐ | ⚠️ HIGH | ❌ HIGH | ✅ OK | — |
| GM | ❌ HIGH | ❌ HIGH | ❌ HIGH | — |
| UT | ❌ HIGH | ❌ HIGH | ✅ OK | — |
| GU | ❌ HIGH | ❌ HIGH | ✅ OK | — |
| IOD | ❌ HIGH | ❌ HIGH | ✅ OK | — |
| Người nhà | ⚠️ HIGH | ❌ HIGH | ✅ OK | — |

> **Mẫu số chung:** `P%` tính được luôn cao hơn ngưỡng quy định → nguyên nhân gốc: FCT gốc là thực phẩm sống (raw), không chứa giá trị lipid của thực phẩm đã nấu chín và dầu ăn hấp thụ khi xào/rán. Khi lipid thiếu, tổng năng lượng giảm → P% tăng tương đối.

---

## Mục 4: Vấn Đề Hệ Thống

### 4.1. FCT 2007 Là Dữ Liệu Thực Phẩm Sống (Raw)

Đây là nguyên nhân gốc của hầu hết sai số:

| Thiếu trong FCT | Tác động |
|---|---|
| Thịt bò/thịt lợn/thịt ngan đã nấu chín | Không tính được protein/lipid chính |
| Dầu ăn hấp thụ khi xào/rán | **Nguyên nhân chính P% và L% lệch** |
| Các loại cá (trắm, basa, rô, thu, lóc) | Thiếu protein từ cá |
| Tôm, mực, chả cá | Thiếu nguồn protein đã chế biến |

### 4.2. Known FCT Gaps (không xử lý)

- `thịt bò loại i` — không có thịt bò nạc → dùng có mỡ
- `thịt bê mỡ` — không có thịt bê nạc
- `Cá trắm rán xốt cà chua` — cà chua bị bỏ qua
- `Thịt lợn xào ớt đà lạt` — ớt bị bỏ qua

---

## Mục 5: Kết Luận và Khuyến Nghị

### 5.1. Đánh Giá Tổng Thể

| Tiêu chí | Kết quả |
|---|---|
| Độ chính xác kcal | ⚠️ Chấp nhận được (±200–400 kcal) |
| Độ chính xác P/L/G% | ⚠️ Không đáng tin khi chưa điều chỉnh dầu ăn |
| Đối chiếu quy tắc | ❌ 11/11 nhóm có ít nhất 1 chỉ số lệch ngưỡng |
| FCT coverage | ⚠️ FCT gốc là thực phẩm sống — thiếu dầu ăn và món đã nấu |

### 5.2. Nhóm Cần Xem Xét Đặc Biệt

**① Sản khoa (SK) — Ưu tiên cao nhất**
- Cả kcal ghi nhận (2072) lẫn tính từ FCT (1971) đều không đạt ngưỡng SK03 (2600–2700 kcal)
- Thực đơn thực tế thiếu khoảng 500–700 kcal/ngày

**② Đái tháo đường (ĐĐ) — Ưu tiên cao**
- P% ghi nhận 25% và tính được 24.0% — vượt ngưỡng 15–20%
- L% có ngày vượt 30% (Thứ 3: 35.8%)

**③ Gan mật (GM) — Ưu tiên cao**
- kcal tính ra 2102 cao hơn cả ghi nhận (1782)
- L% = 21.4% vượt ngưỡng 18%

### 5.3. Khuyến Nghị Chung

1. **Bổ sung CSDL FCT cho thực phẩm đã chế biến** (nấu chín, có hệ số cooking yield)
2. **Áp dụng hệ số dầu ăn**: thêm 10–15g lipid/ngày cho mỗi bữa có món xào/rán → sẽ giảm P% xuống và tăng L%
3. **Xác nhận lại số liệu** từ bộ phận dinh dưỡng bệnh viện
4. **Rà soát thực đơn Sản khoa** — kcal thực tế thấp hơn yêu cầu SK03

---

## Phụ Lục: Các File Liên Quan

```
monthly_plan_logic/
├── validate_nutrition.py              ← Script chính (parse + FCT lookup + validation)
├── special_case.md                    ← FCT mapping decisions & known gaps
├── data/
│   ├── weekly_meal_plan_85k.json      ← Thực đơn gốc
│   ├── VTN_FCT_2007_food_composition.csv  ← FCT gốc (2077 entries)
│   ├── sp_thuong_mai.csv              ← Bổ sung thực phẩm thương mại
│   ├── rules.txt                      ← Quy tắc QĐ 2879/QĐ-BYT
│   └── validation_summary.json       ← Kết quả structured
└── ANALYSIS_diet_group_differences.md ← So sánh các nhóm bệnh với baseline
```

---

*Báo cáo được tạo tự động bằng `validate_nutrition.py`.*
*Cần xác nhận lại với bộ phận dinh dưỡng bệnh viện trước khi sử dụng cho mục đích nghiên cứu.*
