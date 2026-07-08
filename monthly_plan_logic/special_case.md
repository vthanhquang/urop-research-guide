# FCT Special Cases & Mapping Notes

> Ghi chép các trường hợp đặc biệt khi ánh xạ tên món ăn trong thực đơn sang FCT (Vietnamese Food Composition Table 2007).

> **File chính:** `validate_nutrition.py` — tất cả mappings nằm trong `FCT_NAMES{}` và `parse_compound_dish()`.
> **Script xác nhận:** chạy `python validate_nutrition.py` — output "0 unfound, 0 not in FCT" nghĩa là mọi món đều được resolve.

---

## Processing History

### 2026-07-08 — FCT Mapping Cleanup

**FCT name fixes (map-to-self → correct FCT entry):**

| Key | Before (broken) | After (fixed) | kcal/100g before | kcal/100g after |
|---|---|---|---|---|
| `cà rốt` | fuzzy → `cà rốt khô` (NOT direct match) | `cà rốt (củ đỏ, vàng)` | 292 | **39** |
| `bí đỏ` | fuzzy → `hạt bí đỏ rang` | `bí ngô` | 519 | **27** |
| `ớt` | fuzzy → `tương ớt` | `ớt đỏ to` | 37 | **23** |

**FCT name redirects (regional names / typos → correct entry):**

| Key | FCT target | kcal/100g | Reason |
|---|---|---|---|
| `thịt lợn vai` | `thịt lợn nửa nạc, nửa mỡ` | 260 | Thịt vai thực tế có cả nạc và mỡ |
| `thịt vai quay` | `thịt lợn nửa nạc, nửa mỡ` | 260 | Same |
| `thịt lợn vai quay` | `thịt lợn nửa nạc, nửa mỡ` | 260 | Same |
| `cải ngọt` | `dưa cải bẹ` | 17 | Là dưa muối, không phải cải xanh tươi |
| `thịt bò` | `thịt bò loại i` | 118 | Direct match; FCT không có thịt bò nạc |

**Compound dish parsing (parse_compound_dish) — added 9 new patterns:**

12 of 15 multi-weight protein entries now split into individual ingredients with correct weights.

---

## 1. Tên gọi khác miền — cùng một thực phẩm

| Tên trong thực đơn | FCT target | Lý do | kcal/100g |
|---|---|---|---|
| `bí đỏ` | `bí ngô` | Cùng loại quả, gọi theo miền Nam / miền Bắc | 27 |
| `cải ngọt` | `dưa cải bẹ` | "Cải ngọt" trong thực đơn = dưa cải bẹ (muối), không phải cải xanh tươi | 17 |
| `hành` | `hành lá` | Hành (không chỉ rõ) → mặc định là hành lá | 22 |
| `thịt ngan` | `thịt ngỗng` | Lỗi đánh máy — FCT không có entry ngan riêng | 167 |

---

## 2. Tên không tồn tại trong FCT — fuzzy fallback

> **Quy tắc:** Nếu key không có trong FCT gốc, `lookup()` tìm entry gần nhất bằng substring match.

| Key | Fuzzy match | kcal/100g | Ghi chú |
|---|---|---|---|
| `bí xanh` | `bí đao (bí xanh)` | 12 | ✅ Chính xác |
| `mồng tơi` | `rau mồng tơi` | 14 | ✅ Chính xác |
| `hành lá` | `hành lá (hành hoa)` | 22 | ✅ Chính xác |
| `cà rốt` | `cà rốt (củ đỏ, vàng)` | 39 | ✅ Đã fix — trước đó nhảy nhầm sang `cà rốt khô` (292 kcal) |
| `thịt bò` | `thịt bò loại i` | 118 | ⚠️ FCT không có thịt bò nạc — `loại i` là có mỡ (mỡ ~20%) |
| `thịt bê` | `thịt bê mỡ` | 144 | ⚠️ Tương tự — không có thịt bê nạc trong FCT |
| `thịt lợn` | `thịt lợn mỡ` | 394 | ⚠️ FCT chỉ có `thịt lợn mỡ`, không có nạc |
| `ớt` | `ớt đỏ to` | 23 | ✅ Đã fix — trước đó nhảy nhầm sang `tương ớt` (37 kcal) |

---

## 3. Món không có trong FCT — dùng sp_thuong_mai.csv

| Key | FCT target | kcal/100g | Nguồn |
|---|---|---|---|
| `cá lóc` | `cá basa (bạc)` | 96 | sp_thuong_mai.csv |
| `cá basa` | `cá basa (bạc)` | 96 | sp_thuong_mai.csv |

---

## 4. Thịt lợn vai — cần thay đổi FCT target

> **Vấn đề:** FCT không có entry `thịt lợn vai`. "Thịt vai" trong thực tế bao gồm cả nạc và mỡ.

| Key trong thực đơn | FCT cũ (sai) | FCT mới (đúng) | kcal/100g |
|---|---|---|---|
| `thịt lợn vai` | `thịt lợn vai` (NOT IN FCT) | `thịt lợn nửa nạc, nửa mỡ` | 260 |
| `thịt vai quay` | `thịt lợn vai` (NOT IN FCT) | `thịt lợn nửa nạc, nửa mỡ` | 260 |
| `thịt lợn vai quay` | `thịt lợn vai quay` (NOT IN FCT) | `thịt lợn nửa nạc, nửa mỡ` | 260 |

---

## 5. Món compound — tách thành nguyên liệu riêng

> **Quy tắc:** Nếu một món ăn có nhiều nguyên liệu với nhiều trọng lượng riêng (ví dụ: `Thịt lợn băm xào cà rốt, hành lá: 50g, 10g, 5g`), parser sẽ tách thành các mục riêng dựa trên `parse_compound_dish()`.

### Định dạng nguyên liệu (key, weight index)

Mỗi pattern trong `COMPOUND_PATTERNS` là tuple:
```
(dish_name_substring, [(fct_name, weight_index), ...])
```

`weight_index` cho biết trọng lượng nào trong chuỗi gốc tương ứng với nguyên liệu đó (0 = trọng lượng đầu tiên, 1 = thứ hai, v.v.)

### Danh sách compound dishes đã xử lý

| Dish name (raw) | Parsed as | kcal/100g (composite) |
|---|---|---|
| `Thịt lợn băm xào cà rốt, hành lá: 50g, 10g, 5g` | thịt lợn nạc 50g + cà rốt 10g + hành lá 5g | ~139 |
| `Tôm rang thịt lợn, hành lá: 60g, 70g, 5g` | tôm đồng 60g + thịt lợn nạc 70g + hành lá 5g | ~90 |
| `Thịt lợn xào hành tây, cà rốt: 70g, 10g, 10g` | thịt lợn nạc 70g + cà rốt 10g + hành tây 10g | ~139 |
| `Thịt bò xào cần tỏi tây, hành tây: 60g, 20g, 10g` | thịt bò loại i 60g + hành tây 20g + hành tây 10g | ~118 |
| `Ức gà xào hành tây, cà rốt: 60g, 10g, 10g` | thịt gà ta 60g + cà rốt 10g + hành tây 10g | ~199 |
| `Thịt lợn nạc vai xào cần tỏi tây, hành tây: 100g, 10g, 5g` | thịt lợn nửa nạc nửa mỡ 100g + hành tây 10g + hành tây 5g | ~260 |
| `Thịt lợn nạc vai xào ớt đà lạt: 100g, 20g` | thịt lợn nửa nạc nửa mỡ 100g + ớt đỏ to 20g | ~260 |
| `Thịt lợn băm xào hành lá: 50g, 5g` | thịt lợn nạc 50g + hành lá 5g | ~139 |
| `Thịt bê xào sả ớt: 50g, 10g, 5g` | thịt bê nạc 50g + hành tây 10g + ớt đỏ to 5g | ~85 |
| `Thịt lợn, trứng gà kho tàu: 90g, 1 quả` | thịt lợn nạc 90g + trứng gà 50g | ~166 |
| `Trứng đúc thịt: 01 quả, 10g` | trứng gà 50g + thịt lợn nạc 10g | ~166 |
| `Tôm rang thịt lợn: 60g, 70g` | tôm đồng 60g + thịt lợn nạc 70g | ~90 |

### Các món vẫn dùng yield factor (không parse thành nguyên liệu)

| Dish | Xử lý qua | kcal/100g | Ghi chú |
|---|---|---|---|
| `Cá trắm rán xốt cà chua` | `FCT_NAMES → ("cá trắm cỏ", 0.85)` | ~77 | Cà chua bị bỏ qua, có thể thêm compound pattern nếu cần |
| `Thịt lợn xào ớt đà lạt` | `FCT_NAMES → ("thịt lợn nạc", 0.85)` | ~118 | Ớt bị bỏ qua; sai nhưng ảnh hưởng nhỏ |

---

## 6. Món bị loại khỏi tính dinh dưỡng (kcal = 0)

> Những món này có trong thực đơn nhưng không đóng góp kcal đáng kể hoặc không tìm thấy trong FCT.

| Key | Lý do |
|---|---|
| `xương ống` | Gia vị nấu nước, không ăn phần thịt |
| `gia vị` | Gia vị tổng hợp, lượng rất nhỏ |
| `hẹ` | Không có trong FCT, lượng dùng nhỏ |
| `tiêu` | Không có trong FCT, lượng dùng nhỏ |
| `mắm` | Không xác định được loại / lượng |
| `dầu ăn` | Không theo dõi riêng — giả định đã tính trong món |
| `bột ngọt` | Không có trong FCT |

> **Lưu ý:** `hành lá` và `rau mùi` không bị loại — chúng được tính kcal rất nhỏ (22 kcal và 17 kcal/100g) và xuất hiện thường xuyên.

---

## 7. Đơn vị đặc biệt

| Định dạng | Xử lý | Quy đổi |
|---|---|---|
| `01 quả`, `1 quả` | Đọc số + đơn vị `quả` | → 50g mặc định |
| `5g`, `10g` (sau dấu `:`) | Bare numeric token | Bị skip trong phần protein; dùng làm garnish weight mặc định |
| `khẩu phần` | Đọc số | Dùng trực tiếp làm trọng lượng |

---

## 8. Known FCT gaps (không xử lý)

| FCT target | Vấn đề | Tác động |
|---|---|---|
| `thịt bò loại i` | Không có thịt bò nạc → dùng có mỡ (118 vs ~100 kcal/100g nạc) | Protein % hơi cao hơn thực tế |
| `thịt bê mỡ` | Không có thịt bê nạc | Tương tự |
| `thịt lợn mỡ` (fuzzy fallback) | Fuzzy fallback cho `thịt lợn` → mỡ thay vì nạc | kcal hơi cao nếu dùng bare "thịt lợn" |
| `bông cải` | Không tồn tại trong FCT | Không xuất hiện trong thực đơn hiện tại |
| `thịt lợn vai quay` | FCT không có | Đã map sang `thịt lợn nửa nạc, nửa mỡ` |
