# Báo cáo đợt đánh giá 50 seed

Đã hoàn thành 2450 lượt chính, 49 cặp cấu hình–kịch bản, mỗi cặp đủ seed 1–50. Pilot 42 lượt đạt các kiểm tra baseline. Tất cả 1225 kết quả cũ được tái lập chính xác, bỏ qua thời gian thực thi.

Code thử nghiệm nằm riêng trong IOT/experiment_50_20261124, không sửa mô hình V3 gốc. Công tắc detect mặc định bật; BASE_5/BASE_30 tắt detect, bypass, escalate và repeat, lấy mẫu cố định. Tần số 920 MHz ở manifest mới chỉ là metadata: simulator không dùng tần số sóng mang để tính truyền sóng hoặc airtime. Metadata cũ 868 MHz giữ nguyên.

## Kết quả chính

SC-3: FULL 50/50, BASE_5 39/50, BASE_30 12/50, NO_REPEAT 31/50 và NO_ESCALATE 50/50. Cận dưới Wilson 95% danh nghĩa cho 50/50 là 92.87%. FULL tăng tỷ lệ đạt hạn 22 điểm phần trăm so với BASE_5 (bootstrap ghép cặp 95%: 12–34) và 76 điểm so với BASE_30 (64–88).

SC-4: FULL 11/50. SC-6: FULL 8/50. Các kết quả này chưa đạt mục tiêu 90% quan sát.

SC-3: tải đỉnh trung bình FULL 540.55, NO_ESCALATE 537.76 giây phát tương đương, giảm 0.52%. FULL cao hơn BASE_5 (536.91) và BASE_30 (522.88). Không gọi tải này là năng lượng joule.

SC-5: PDR FULL 68.10%, NO_BYPASS 34.16%; chênh lệch ghép cặp 33.94 điểm phần trăm, t CI95% 31.02–36.86. BASE_5/BASE_30 lần lượt 26.56%/26.54%.

PDR FULL không luôn cao hơn đối chứng: ở SC-0 là 68.13% so với 70.20%/70.80%; SC-4 là 21.73% so với 24.88%/25.10%. SC-3 cải thiện thời hạn nhưng chênh lệch PDR với baseline có khoảng tin cậy chứa 0.

## Kiểm chứng và giới hạn

Các kiểm tra sự kiện đã đạt: nhận/chuyển tiếp giữa hai lần lấy mẫu, half-duplex, trạng thái kênh ghép cặp tại cùng thời điểm, loại trùng khi gói đến không đúng thứ tự, và gói thực sự đi qua chặng S4→S2 tới gateway. V3 loại trùng bằng tập định danh; SenScript dùng ngưỡng số thứ tự. V3 không dùng khoảng nghỉ sau cụm 150–250 ms của SenScript. Các khác biệt được nêu trong phương pháp.

Thiết kế mở rộng sau khi xem kết quả ban đầu; mốc 35 chỉ nêu tại phương pháp, kết quả và hình/bảng V3 dùng 50 seed. Khoảng tin cậy là danh nghĩa, từng phép so sánh, chưa hiệu chỉnh nhiều phép so sánh. Không gọi đây là kiểm định xác nhận độc lập. Các cặp NR giữ nguyên.

## Tái lập

run_experiment.py: chạy pilot và toàn bộ bộ chính; từ chối ghi đè bộ đã hoàn tất. Khi cần tái lập dùng bản sao thư mục với thư mục results mới; không xóa dữ liệu gốc.
analyze.py: tạo CSV/JSON và biểu đồ từ metrics.
verify_events.py: kiểm tra hành vi sự kiện.
update_paper.py: tạo LaTeX từ số liệu tổng hợp.

results/design.json, completion.json, pilot_checks.json và event_checks.json lưu thiết kế và bằng chứng kiểm tra. results/paired_results.csv có 2450 dòng dữ liệu; paper_tables.json lưu thống kê và khoảng tin cậy; per_node.csv lưu số liệu theo nguồn.

PDF cuối đã biên dịch 10 trang với Times New Roman Unicode; đã xem ảnh tổng thể tất cả các trang và trang giả mã. Log không có missing character, overfull box hoặc undefined references; còn cảnh báo underfull và fallback kiểu chữ nhỏ không ảnh hưởng nội dung.
