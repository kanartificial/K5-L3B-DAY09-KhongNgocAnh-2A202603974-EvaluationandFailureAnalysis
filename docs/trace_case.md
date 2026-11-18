# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Case đã điều tra: `seeded_regression C-002@11`

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11` (report `E-seeded_regression-20261118-dae8`, item `E-002`) |
| Triệu chứng | Grader Lab 8 `FAIL (status resolved != denied)`. Reply nói `"Dạ, LogiX đã hoàn 20.000đ cho đơn O-202."`, ledger ghi `refund_vnd=20000`, `refund_count=1` trong khi nhãn đúng là `refund_vnd=0`, `refund_count=0`, `status=denied`. |
| Bước sai đầu tiên | Event `#3` `model_override`: `{"delay_days": 5}` |
| Vì sao là bước *đầu tiên* | Event `#1` `handoff` đúng phạm vi (`principal_scope="owner_order_only"`, `claim_id="C-002"`); event `#2` `investigator` đọc DB đúng (`order_id="O-202"`, `delay_days=2`, `status="delivered"`). Chỉ tới event `#3`, model mới ghi đè `delay_days=5` từ ticket thay cho giá trị DB. |
| Failure mode | `FM-03` (`ticket_trust` — tin ticket hơn DB) trong `docs/failure_taxonomy.md` |
| Đối chứng | `fixed C-002@11`: không có event `model_override`; event `#3` là `quote` trả `amount_vnd=0, reason="no_entitlement"`, event `#4` là `reply` từ chối (`status=denied`), ledger `refund_vnd=0, refund_count=0`, `lab8_pass=True`. |
| Regression test | `src/tests/test_trace_case_c002.py` (`test_c002_fixed_passes_and_does_not_override_db`, `test_c002_seeded_regression_is_caught_by_db_fact_and_refund`) dùng grader `DbFactKept` và `RefundAmountCorrect`: fail trên `seeded_regression`, pass trên `fixed`. |
| Chưa chắc chắn | MockLLM mô phỏng lỗi `ticket_trust` có chủ đích; trên LLM thật cần kiểm tra thêm các cách diễn đạt ticket tinh vi hơn (không chỉ `delay_days`). |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
