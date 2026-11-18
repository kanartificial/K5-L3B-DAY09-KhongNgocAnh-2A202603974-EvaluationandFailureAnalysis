# Judge audit

Chạy:
```bash
cd src
python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 5
python -m lab9.judge --csv data/eval/judge_helpful_public.csv --audit 5
```

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| `tone_ok` (`judge_tone_public.csv`) | 100 | 0.757 | 0.857 | 0.800 | Đạt (κ=0.757≥0.6, P=0.857≥0.8, R=0.800≥0.7) | **dùng** |
| `helpful` (`judge_helpful_public.csv`) | 100 | 0.375 | 1.000 | 0.300 | **Không đạt** (κ=0.375<0.6, R=0.300<0.7) | **loại** |

## ≥5 case audit thủ công

| # | Case | Judge nói | Người nói | Ai đúng? | Sửa rubric / Ghi chú |
|---|---|---|---|---|---|
| 1 | `HL-015` (`helpful`): `"Dạ, LogiX đã hoàn 55.000đ cho đơn O-112 ạ."` | `PASS` | `FAIL` (`sai tiền`: ledger ghi `40.000đ`) | **Người đúng** | Judge chỉ đọc reply, không thấy ledger nên không phát hiện lệch tiền. **Sửa rubric**: tách kiểm tra số tiền sang code grader đối chiếu reply với ledger; không dùng judge text-only cho `helpful` khi thiếu ground-truth ledger. |
| 2 | `HL-016` (`helpful`): `"Dạ, LogiX thành thật xin lỗi anh/chị... LogiX đã hoàn 55.000đ cho đơn O-404. Một lần nữa LogiX xin lỗi..."` | `PASS` | `FAIL` (`sai tiền`: ledger ghi `35.000đ`) | **Người đúng** | Judge bị đánh lừa bởi văn phong xin lỗi dài dòng, lịch sự (verbosity bias). **Sửa rubric**: nêu rõ "lời xin lỗi lịch sự không bù cho sai lệch số tiền/kết quả"; cung cấp `ledger_refund_vnd` vào prompt hoặc tách check số tiền bằng code. |
| 3 | `HL-047` (`helpful`): `"Ok bạn, đơn O-515 xử lý rồi nhé."` | `PASS` | `FAIL` (`sai xưng hô`) | **Người đúng** | Judge bỏ sót xưng hô thiếu chuyên nghiệp (`"Ok bạn"`, `"rồi nhé"`) và thiếu thông tin số tiền/trạng thái cụ thể. **Sửa rubric**: thêm tiêu chí bắt buộc xưng hô chuẩn (`anh/chị`, `Dạ/ạ`) và nêu rõ kết quả xử lý (số tiền hoặc lý do từ chối). |
| 4 | `H-008` (`tone_ok`): `"Em đã hoàn tiền cho anh rồi nha, anh check giúp em."` | `PASS` | `FAIL` | **Người đúng** | Judge coi `"em"`, `"nha"` là thân thiện, trong khi CSKH chuyên nghiệp cấm từ ngữ suồng sã (`nha`, `check giúp`). **Sửa rubric**: liệt kê danh sách từ/cụm từ suồng sã bị cấm (`nha`, `nhé`, `ok bạn`, `check giúp`). |
| 5 | `H-029` (`tone_ok`): `"Dạ, vui lòng chờ. Hệ thống đang xử lý, không cần nhắn thêm."` | `PASS` | `FAIL` | **Người đúng** | Judge chỉ bắt từ khóa `"Dạ, vui lòng"` mà bỏ qua mệnh đề ra lệnh/đuổi khách (`"không cần nhắn thêm"`). **Sửa rubric**: yêu cầu đánh giá toàn câu, gắn cờ `FAIL` mọi câu có ngữ điệu ra lệnh hoặc ngăn khách phản hồi. |
| 6 | `H-042` (`tone_ok`): `"Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ."` | `FAIL` | `PASS` | **Người đúng** | Judge phạt oan vì "thiếu xin lỗi" dù câu trả lời ngắn gọn, lịch sự và đủ thông tin. **Sửa rubric**: làm rõ "xin lỗi" chỉ bắt buộc khi đơn bị từ chối hoặc có sự cố chưa giải quyết, không bắt buộc khi đã hoàn tiền xong. |
| 7 | `H-070` (`tone_ok`): `"Dạ, LogiX đã hoàn 90.000đ cho đơn O-909 ạ 😂😂"` | `PASS` | `FAIL` | **Người đúng** | Emoji cười (`😂😂`) không phù hợp trong ngữ cảnh khiếu nại. **Sửa rubric**: cấm emoji/emoticon trong phản hồi khiếu nại chính thức. |
| 8 | `H-081` (`tone_ok`): `"Dạ, đơn O-107 chưa đủ điều kiện hoàn theo chính sách hiện hành ạ."` | `FAIL` | `PASS` | **Judge đúng** (nhãn người ban đầu đọc nhầm ticket) | Cần rà soát lại nhãn người (double-annotation) cho các ca biên trước khi dùng làm bộ benchmark chuẩn. |

## Kết luận
- **Tiêu chí bị loại: `judge_helpful`** (`judge_helpful_public.csv`) — **không được dùng làm gate**:
  - Ma trận nhầm lẫn: `tp=9, fp=0, fn=21, tn=70` (`n=100`).
  - `Precision = 1.000` nhưng **`Recall = 0.300`** (< sàn `0.7`) và **`κ = 0.375`** (< sàn `0.6`): judge **bỏ sót 21/30 (70%) ca lỗi thật**.
  - Tỷ lệ lỗi quan sát được chỉ là `0.09` (9%), trong khi tỷ lệ lỗi thực sau hiệu chỉnh Rogan-Gladen là `0.30` (30%).
  - **Nguyên nhân gốc**: judge chỉ đọc text bề mặt của `reply` (dễ bị đánh lừa bởi câu xin lỗi dài dòng, lịch sự) và không có quyền/ngữ cảnh đối chiếu `ledger`, nên bỏ lọt hoàn toàn các lỗi nghiêm trọng như báo sai số tiền (`sai tiền` / FM-08). Nếu dùng làm gate, hệ thống sẽ cho qua các agent hoàn sai tiền hoặc nói sai số tiền với khách.
- **Tiêu chí được giữ: `judge_tone`** (`judge_tone_public.csv`) đạt cả 3 ngưỡng sàn (`κ=0.757`, `P=0.857`, `R=0.800`; ma trận `tp=24, fp=4, fn=6, tn=66`; observed `0.28` → corrected `0.30`), có thể dùng làm tín hiệu tham khảo/giám sát sau khi siết rubric theo các ca bất đồng ở trên.
- **Rủi ro còn lại**: judge chỉ được kiểm trên dữ liệu replay đã công khai; cần nhãn người mới độc lập (held-out thật) và tách các kiểm tra sự thật/số tiền sang code grader thay vì giao cho LLM judge.
