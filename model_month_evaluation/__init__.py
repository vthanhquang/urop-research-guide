# -*- coding: utf-8 -*-
"""
model_month_evaluation/
========================
Đánh giá chất lượng thực đơn tháng sinh ra bởi model_generation/.

Mô-đun:
  rules_checker.py   — Kiểm tra từng nhóm theo ngưỡng QĐ 2879/QĐ-BYT
  statistics.py       — Thống kê mô tả: trung bình, min/max, CV, phân bố
  compliance.py       — Tính tỷ lệ tuân thủ: ngày đạt / tổng ngày
  report.py          — Báo cáo tổng hợp + CLI
  run.py             — Chạy đánh giá đầy đủ

Kết quả lưu tại output/
"""
from __future__ import annotations
