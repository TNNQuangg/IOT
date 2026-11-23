# KỊCH BẢN MÔ PHỎNG V3 — TỐI ƯU LORA P2P TRƯỚC TRIỂN KHAI

Ngày chốt yêu cầu: 20/11/2026. Trạng thái: **đặc tả triển khai, chưa có kết quả V3**.

V3 là đặc tả chuẩn cho lần triển khai tiếp theo, thay thế các chỉ dẫn mâu thuẫn trong V2. Giữ V2, báo cáo Word và log cũ để đối chiếu; không sử dụng số liệu cũ làm kết quả nghiệm thu V3.

## 1. Mục tiêu và ranh giới

- Ứng dụng: quan trắc sạt lở tại miền núi phía Bắc Việt Nam; mô phỏng để lựa chọn cấu hình trước khi lắp đặt.
- Ưu tiên: đạt **ít nhất 90% sự kiện có cảnh báo tới Gateway trong 30 giây**, sau đó tối thiểu hóa năng lượng nút cảm biến chịu tải lớn nhất. Thời hạn tính từ khởi phát sự kiện, gồm chờ lấy mẫu và chuyển tiếp.
- Giữ mạng chuỗi 10 cảm biến S1–S10 và Gateway S11, không ACK/NACK, phát lặp mù và khử trùng lặp; chỉ vượt một nút hỏng. Không mở rộng mesh hay thêm giao thức ACK trong V3.
- Phần cứng chỉ nhắc các cảm biến đã có trong báo cáo: cảm biến độ ẩm đất điện dung, MPU-6050 và SW-420. Chưa chỉ định thêm bo mạch hay module LoRa. Đầu vào vẫn là trạng thái chuẩn hóa, không phải mô hình địa kỹ thuật dự báo sạt lở.
- Demo phần cứng sau này chỉ có hai node, minh họa phát/nhận, cờ sự kiện, phát lặp và lọc trùng. Demo đó không xác nhận được hiệu năng 10 chặng, nối vòng hoặc độ tin cậy cảnh báo của toàn mạng.
- Không ACK là ràng buộc thiết kế của nghiên cứu; không diễn giải thành kết luận LoRa nói chung không hỗ trợ hoặc luôn tốt hơn khi bỏ ACK.

## 2. Đồng hồ và ngân sách chạy

### 2.1. Một đơn vị thời gian thống nhất

Mọi thời điểm trong thuật toán, log và kết quả đều dùng **giây hoạt động thực được mô phỏng**. Các chu kỳ 5/15/30 s, jitter 100–400 ms, thời gian phát LoRa, va chạm và hạn cảnh báo 30 s không bị co riêng lẻ. Lấy thời gian từ đồng hồ sự kiện của bộ mô phỏng, không tự cộng thời gian delay để thay đồng hồ.

- Dừng sinh dữ liệu mới ở `T_GEN_END = 1000 s`.
- Tiếp tục relay, điều khiển tuyến và các bản sao của gói đã sinh đến `T_END = 1300 s`; không tạo dữ liệu cảm biến mới sau 1000 s.
- Hỏng nút có hiệu lực chính xác tại thời điểm sự kiện được lập lịch, kể cả khi nút đang ngủ; ghi riêng thời điểm cấu hình và thời điểm thực thi.
- 300 s cuối là cửa sổ theo dõi có giới hạn, không bảo đảm mọi hàng đợi đã rỗng. Gói chưa kết thúc tại 1300 s được ghi là chưa xác định, không tự coi đã mất.

### 2.2. Tăng tốc chạy trên máy

Mặc định hiểu ngân sách **5–10 phút cho một kịch bản, cấu hình chính, 30 seed**. Đối chứng, quét tham số và lượt xác nhận độc lập là các ngân sách bổ sung. Không cắt ngắn thời gian mô phỏng hay giảm số seed để ép vừa thời gian.

Chọn hệ số chạy khởi đầu `A = 90` giây mô phỏng / giây chạy máy: 30 × 1300 / 90 ≈ 433 s, tức 7,2 phút nếu đạt tốc độ này và chưa tính khởi động/phân tích. Đây là mục tiêu thông lượng, **không phải tốc độ đã đo** và không phải giá trị gán trực tiếp cho `simulationspeed` của CupCarbon.

Trước benchmark, chạy pilot KB-0, KB-4, KB-6, mỗi loại 3 seed, đo cả khởi động, mô phỏng, ghi log và phân tích. Dùng headless/event-driven và tốc độ tối đa khả dụng; nếu nhanh hơn 5 phút thì chấp nhận, không chèn chờ. Nếu quá 10 phút, giảm chi phí UI/log hoặc chạy song song số tiến trình phù hợp tài nguyên, mỗi tiến trình có thư mục riêng. Nếu vẫn quá ngân sách, báo thời gian đo được và giữ nguyên ngữ nghĩa. Không cam kết một tỷ lệ cố định sẽ cho cùng thời gian máy ở mọi kịch bản.

## 3. Mạng, đầu vào và thứ tự ưu tiên

### 3.1. Topology và cấu hình ban đầu

S11 ở vị trí 0 m, S1 ở 50 m, …, S10 ở 500 m; tuyến cơ sở `S_i → S_(i-1)` và `S1 → S11`. Dùng khoảng cách hình học dọc tuyến, không lấy chênh lệch ID để tính khoảng cách tới S11. Liên kết thường 50 m, bypass 100 m; không cho tuyến 150 m. Tọa độ trong bản cũ chỉ là bố trí minh họa, không đại diện số đo hiện trường.

Với adapter CupCarbon dùng bán kính bao hình 120 m để tạo các ứng viên liên kết. Bộ lọc topology chỉ cho liên kết thường hoặc bypass hợp lệ; chất lượng thu do mô hình kênh quyết định. Không diễn giải bán kính này thành vùng phủ LoRa đo được hay tự tăng công suất nếu chưa cấu hình.

| Tham số | Mặc định |
|---|---|
| Giá trị nền / nhiễu | 20 / nguyên đều từ −2 đến +2 |
| Tăng trạng thái do mưa | +22 tại S4–S7 |
| Trạng thái sạt lở | 88–92 tại S5 từ thời điểm sự kiện |
| Ngưỡng Delta / mưa / khẩn cấp | 5 / 40 / 85 |
| Chu kỳ lấy mẫu L0/L1/L2 | 5 / 15 / 30 s |
| Đếm ổn định để vào L1/L2 | 3 / 6 chu kỳ |
| Giữ leo thang | 60 s kể từ bản tin 255/150 mới hợp lệ gần nhất |
| Số bản sao theo cờ 0/100/255/150/200 | 1 / 2 / 3 / 3 / 3, áp dụng cả nguồn và relay |
| Jitter giữa bản sao | đều 0,1–0,4 s, tính từ khi bản trước phát xong |
| Ngưỡng im lặng | 90 s tại mọi relay và Gateway |
| Số lần gửi cụm REPAIR | tối đa 3, cách nhau 5 s |

Thứ tự thống nhất trong mô tả, giả mã và code:

1. Nút hỏng: dừng thu, phát và xử lý; hủy các sự kiện radio chưa thực hiện.
2. `FLAG=255` hoặc đang giữ leo thang hoặc `Delta>=5`: L0, reset bộ đếm ổn định.
3. Nếu không thuộc bước 2 và `FLAG=100`: L1, reset bộ đếm ổn định.
4. Còn lại tăng bộ đếm: dưới 3 là L0, từ 3 là L1, từ 6 là L2.

Đo rồi cập nhật level trước khi sinh gói. Sự kiện có thể xuất hiện giữa hai lần đo; không cho thuật toán biết giá trị mới trước lần lấy mẫu kế tiếp. Δ là trị tuyệt đối chênh lệch hai mẫu; gửi Δ trong trường dài cố định không được gọi là nén tiết kiệm airtime khi chưa có phép đo số byte.

### 3.2. Thu/phát và ngủ

Mặc định MCU chuyển tiếp được đánh thức bởi radio; **radio luôn RX khi không TX**, còn 5/15/30 s là chu kỳ lấy mẫu, không phải thời gian radio tắt. Gói hợp lệ hoàn tất thu được xử lý ngay theo hàng đợi, không chờ lần đo sau. Ghi rõ đây là lựa chọn tốn năng lượng RX để hướng tới hạn cảnh báo 30 s.

Radio half-duplex: đang TX không thu; không lưu gói đến khi radio OFF/ngủ hoặc nút chết. Không dùng cơ chế CupCarbon đệm gói khi ngủ như thu vô tuyến thành công. Cấu hình radio ngủ chỉ được xét khi có lịch thức rõ ràng, dùng làm nghiên cứu sau; không bật ngầm trong V3.

### 3.3. Gói và lọc trùng

Khung dữ liệu mô hình: SRC 1 byte, FLAG 1 byte, VAL 2 byte, SEQ 4 byte, PREV 1 byte: **9 byte payload**. Mỗi nguồn dùng chung bộ đếm SEQ cho cả dữ liệu và điều khiển, không quay vòng trong một lượt. TGEN, TTX, event_id, copy_id và run_id là metadata ngoài khung, không tự cộng vào airtime; triển khai phải có cơ chế truy vết metadata không đi trên sóng.

Nhận thành công theo radio → kiểm tra địa chỉ/topology → cập nhật bằng chứng láng giềng → lọc trùng chính xác bằng `(SRC,SEQ)` → xử lý điều khiển hoặc relay. Không dùng riêng `SEQ <= max` để loại gói vì gói cũ có thể đến muộn. Bản sao trùng không được relay lại, nhưng vẫn là bằng chứng nút kề còn liên lạc. Các gói 200 hợp lệ có thể đến từ nút cách hai chặng trước khi bypass được mở; phải có ngoại lệ lọc rõ ràng để tránh bế tắc sửa tuyến.

### 3.4. Nối vòng không biết trước sự cố

Chỉ bộ phát sinh sự cố biết FAIL_NODE/T_FAIL. Logic giao thức của nút sống không đọc được lịch này. Nút hạ lưu phát hiện thiếu liên lạc từ con sau 90 s, phát 150 về Gateway và gửi 200 tới cháu cách 100 m. Cháu nhận 200 hợp lệ thì đổi next hop qua nút hỏng. Không ACK; dữ liệu từ cháu là bằng chứng khôi phục. Khi nhận lại gói trực tiếp từ con cũ, hoàn tác và gửi 200/VAL=0. Phân biệt mất liên lạc với hỏng phần cứng: timeout không chứng minh nút đã chết.

Nếu không có dữ liệu cháu sau 3 cụm yêu cầu và 90 s theo dõi tiếp theo, ghi `UNREACHABLE`; không kết luận chắc chắn hai nút chết chỉ từ im lặng. S1 hỏng thì Gateway phát hiện và yêu cầu S2; S10 hỏng chỉ báo mất nút cuối. Hai nút liền nhau hỏng vượt phạm vi sửa tuyến.

Cấu hình biết trước sự cố chỉ tồn tại dưới tên `ORACLE_BYPASS`, dùng làm cận tham chiếu riêng và không tham gia chọn cấu hình triển khai. Hạn 30 s áp dụng cả KB-6; nếu phát hiện/sửa tuyến không kịp thì phải báo không đạt, không điều chỉnh mốc bắt đầu hạn sau khi sửa tuyến.

## 4. Mô hình vô tuyến, va chạm và năng lượng

### 4.1. Cấu hình radio giả định

Giữ 868 MHz và 14 dBm từ đặc tả cũ; đây là cấu hình nghiên cứu, chưa xác nhận phù hợp cấu hình triển khai tại địa điểm thực. Mặc định SF7, BW125 kHz, CR4/5, preamble 8 symbol, explicit header, CRC bật, payload 9 byte. Không chỉ định thêm tên module. Các giá trị phải xuất trong manifest.

Time-on-Air dùng công thức LoRa theo các tham số trên; kiểm tra độc lập với tài liệu/công cụ của hãng trước khi sử dụng. Với SF7, LDRO=0 và cấu hình này, giá trị kiểm tra là **41,216 ms**. Lập lịch TX_START/TX_END cho từng bản sao; hàng đợi TX FIFO, không phát chồng trên cùng radio. Jitter bắt đầu sau TX_END, không thay thế airtime.

### 4.2. Hai profile kênh

- `LEGACY_IID`: xác suất nền 0/12/25%, sạt lở chậm tăng lên 40–50% trong 60 s, nhanh 80–85%, bypass +10 điểm phần trăm trần 95%. Dùng hồi quy và đối chiếu giải tích trong chế độ tắt va chạm; không gọi đây là mô hình vật lý LoRa.
- `LORA_STRESS`: bật airtime, half-duplex, va chạm và kênh mất theo cụm. Đây là profile chính để tối ưu. Giữ mức mất biên của LEGACY để so sánh, nhưng dùng chuỗi Markov tốt/xấu theo từng liên kết thay vì rút độc lập từng bản sao.

Mô hình cụm mặc định: trạng thái tốt thu được, trạng thái xấu mất; với mức mất biên p, đặt tốc độ chuyển tốt→xấu là `p/tau`, xấu→tốt là `(1-p)/tau`, `tau=1 s`. Tại sự kiện thay đổi p, giữ trạng thái hiện tại và cập nhật tốc độ; p=0 đặt tốt. Quét tau=0,1/1/5 s; LEGACY_IID là đối chứng độc lập. Giữ p cố định trong mỗi pha nhanh với một giá trị rút theo liên kết/seed, không rút lại mức suy giảm cho mỗi bản sao. Mức p do thời tiết/địa chất là giả thuyết stress-test, chưa được đo ở miền núi phía Bắc.

Trong LORA_STRESS, dùng một kênh cùng SF cho cấu hình mặc định. Hai bản phát trùng thời gian ở cùng máy thu bị hủy nếu hai máy phát nằm trong bán kính nhiễu 120 m của máy thu; bỏ qua thời gian lan truyền ở cự ly này. Bán kính nhiễu áp dụng cả gói không gửi cho máy thu. Capture tắt, quét bán kính nhiễu 120/250/500 m để đánh giá độ nhạy. Đây là mô hình va chạm bảo thủ có giới hạn không gian, chưa mô phỏng capture, fading theo RSSI hoặc nhiễu liên-SF. Không bật thêm MAC/mất ngẫu nhiên nội bộ CupCarbon gây đếm hai lần; adapter phải xác minh và tắt lớp tương ứng hoặc ghi rõ không đủ khả năng.

Ở mỗi bản sao, kiểm tra cả trạng thái TX/RX và chồng lấn trong toàn khoảng thu; đánh giá kênh tại TX_START. Lưu tất cả nguyên nhân nếu cùng xảy ra, dùng thứ tự NODE_DEAD → RADIO_OFF → HALF_DUPLEX → COLLISION → CHANNEL để phân loại nguyên nhân chính, không suy diễn nguyên nhân vật lý từ bộ đếm.

Chỉ công bố mô hình path-loss/RSSI đã hiệu chỉnh khi có dữ liệu phù hợp. V3 hiện cải thiện mức mô phỏng thời gian và tranh chấp kênh, không tuyên bố tái tạo đầy đủ môi trường LoRa thực địa. Duty-cycle được xuất dưới dạng mức chiếm kênh theo nút; chưa gán một giới hạn pháp lý chung cho cấu hình địa điểm chưa xác định.

### 4.3. Năng lượng

Tính `E_radio = V × (I_TX*T_TX + I_RX*T_RX + I_SLEEP*T_SLEEP)` theo A, V, s; mỗi khoảng thời gian chỉ thuộc một trạng thái. Thêm năng lượng MCU/cảm biến chỉ khi có tham số, ghi riêng phần chưa tính. Không dùng số TX thay cho năng lượng.

Chưa chọn module nên mặc định chỉ xuất thời lượng trạng thái và **năng lượng chuẩn hóa**: `E_norm = T_TX + rho*T_RX`, `rho=0,4`; quét rho=0,2/0,4/0,8. Đây là giây TX tương đương, không phải joule hay tuổi thọ pin. Chỉ xuất joule khi cung cấp V và dòng từ datasheet/đo của phần cứng được chọn; không tự gán dòng điện vào tên cảm biến có trong báo cáo.

Đánh giá theo từng nút, cực đại trên S1–S10 và toàn mạng; Gateway luôn thu, nguồn ổn định và được báo riêng. So sánh tính ổn định của lựa chọn cấu hình qua các rho; nếu thứ hạng đổi thì chưa chốt được cấu hình tối ưu năng lượng cho phần cứng thật.

## 5. Ma trận kịch bản và đối chứng

| ID | Điều kiện, theo giây thực được mô phỏng |
|---|---|
| KB-0 | Không sự kiện, không mất kênh nền; va chạm vẫn có khi profile bật |
| KB-1 | Mất nền 12%, từ 26 đến 200 s, sau đó 0%; không sạt lở/hỏng |
| KB-2 | Mất nền 25%, từ 26 đến 200 s, sau đó 0%; không sạt lở/hỏng |
| KB-3 | Nền 12% từ 26 s; sạt lở chậm tại S5 từ 73 s, vùng S4–S7 |
| KB-4 | Như KB-3 nhưng suy giảm nhanh 80–85% |
| KB-5 | Nền 0%; S3 hỏng tại 90 s |
| KB-6 | Như KB-4; S5 hỏng tại 93 s; hạn cảnh báo kết thúc tại 103 s |

Mỗi seed có một sự kiện sạt lở ở KB-3/4/6. Tính thành công sự kiện cho cả ba kịch bản riêng; KB-0/1/2/5 không có sự kiện sạt lở nên không gán tỷ lệ thành công cảnh báo bằng 0 hoặc 100%. KB-6 chỉ có ít cơ hội phát trước khi nguồn chết là một phần của kịch bản, vẫn nằm trong mẫu số sự kiện.

### 5.1. Đối chứng tách cơ chế

| Cấu hình | Thay đổi duy nhất so với cấu hình đầy đủ | Kịch bản |
|---|---|---|
| FULL | Theo đặc tả | Tất cả |
| FIXED_5 | Chu kỳ lấy mẫu cố định 5 s, bỏ điều chỉnh và leo thang chu kỳ | Tất cả |
| FIXED_30 | Chu kỳ lấy mẫu cố định 30 s, bỏ điều chỉnh và leo thang chu kỳ | Tất cả |
| NO_REPEAT | Mọi cờ chỉ một bản sao | Tất cả |
| NO_ESCALATE | Bỏ ép level do nhận 255/150; giữ phản ứng cảm biến cục bộ | KB-3/4/6 |
| NO_BYPASS | Không chuyển tuyến/REPAIR; vẫn ghi phát hiện mất liên lạc | KB-5/6 |
| ORACLE_BYPASS | Biết trước sự cố, chỉ dùng làm tham chiếu | KB-5/6 |

FIXED_5/FIXED_30 đánh giá chính sách chu kỳ thay thế, không dùng để quy toàn bộ chênh lệch cho một cơ chế độc lập. Các đối chứng cùng seed chia sẻ đầu vào môi trường; dùng các luồng ngẫu nhiên tách biệt theo cảm biến, liên kết và jitter. Không đồng nhất seed với cùng chuỗi rút ngẫu nhiên nếu số bản sao khác nhau.

### 5.2. Quét tối ưu theo hai bước

1. Quét một biến mỗi lần trên KB-0/3/4/6, 10 seed sàng lọc: N cảnh báo=1/2/3/5; jitter=0,1–0,4 hoặc 0,4–1 s; L0=2/5 s; timeout=45/90 s. Bắt đầu từ FULL, chỉ đổi một tham số ở mỗi thử nghiệm. Timeout 45 s có thể báo nhầm vì lấy mẫu 30 s, phải đo chi phí này.
2. Ghép hai giá trị tốt nhất của từng nhóm thành tối đa 16 tổ hợp, chạy 30 seed trên bảy kịch bản. Xác nhận cấu hình được chọn bằng 30 seed mới không dùng để chọn tham số.

Xếp hạng: trước hết phải đạt mục tiêu cảnh báo trên từng KB-3/4/6; sau đó chọn cấu hình có cực đại năng lượng chuẩn hóa theo nút thấp nhất, lấy cực đại qua bảy kịch bản. Nếu bằng nhau chọn P95 thời gian cảnh báo nhỏ hơn, rồi tổng airtime nhỏ hơn. Nếu không cấu hình nào đạt, báo **chưa đạt mục tiêu trong kiến trúc/ràng buộc đã chọn**, xuất đường đánh đổi; không thay mô hình mất gói để làm đẹp kết quả.

## 6. Seed, số liệu và khoảng tin cậy

- Đánh giá chính/đối chứng: seed 1–30; xác nhận độc lập: 1001–1030. Manifest ghi seed gốc, cách tạo seed thành phần, phiên bản bộ sinh và cấu hình; mỗi run có thư mục riêng, không ghi đè log cũ.
- Nếu estimate cảnh báo ≥90% nhưng cận dưới Wilson 95% <90%, tăng lượt xác nhận theo các mốc 60/100/200 seed, dùng cả kết quả trước đó; ở 200 vẫn chưa đủ thì ghi chưa đủ bằng chứng. Không loại lượt thất bại giao thức. Lỗi chương trình là run lỗi, phải sửa và chạy lại cấu hình nhất quán.
- Tỷ lệ đúng hạn tính theo **số sự kiện/seed**, CI Wilson 95% hai phía. Phân biệt “ước lượng đạt 90%” và “có bằng chứng cận dưới CI đạt 90%”; dùng tiêu chí thứ hai để khẳng định đạt mục tiêu. Báo CI tại mốc số mẫu cuối, không dùng dừng tuần tự này để tuyên bố mức bảo đảm kiểm định tuần tự.
- Với PDR, năng lượng và độ trễ: tính theo run trước, báo trung bình, SD và CI bootstrap 95% với 2000 lần lấy lại mẫu run. Chênh lệch đối chứng dùng bootstrap cặp seed. Không coi mỗi gói trong cùng run là mẫu độc lập.

| Chỉ số | Quy tắc |
|---|---|
| PDR dữ liệu theo nguồn và cờ | Gói `(SRC,SEQ)` tới GW trước 1300 s / gói sinh trước 1000 s; tách dữ liệu và điều khiển |
| Hiệu ứng cuối phiên | Báo PDR nhận trước 1000 s và trước 1300 s; số gói còn chờ tại 1300 s, không loại tùy ý 30 s cuối |
| PDR chặng | Bản sao hợp lệ nhận tại đích / bản sao thực sự bắt đầu TX tới đích đó; RX lân cận ngoài đích không tính |
| PDR cảnh báo | Gói 255 nhận / gói 255 sinh; không đồng nhất với tỷ lệ phát hiện sự kiện |
| Cảnh báo đúng hạn | Có ít nhất một 255 của sự kiện tới GW trong 30 s từ T_LS; mọi sự kiện đều trong mẫu số |
| Độ trễ | T_GW đầu tiên − T_GEN bất biến; trung bình/P50/P95 theo nguồn/cờ, kèm PDR và số mẫu |
| Phân rã thời gian cảnh báo | Chờ lấy mẫu + thời gian từ GEN đến GW; không bỏ thời gian phát hiện |
| Không nhận cảnh báo | Ghi thất bại đúng hạn; độ trễ không nhận là NA, không gán 0 và không loại khỏi mẫu số sự kiện |
| Sửa tuyến | FAIL→DETECT, DETECT→nhận dữ liệu qua bypass đầu tiên; tỷ lệ sửa thành công; báo nhầm và số REVERT |
| Chi phí | TX/RX airtime, mức chiếm kênh, thời gian trạng thái, năng lượng chuẩn hóa và joule khi đủ đầu vào |

Không bắt buộc PDR S10 < S1 ở mọi seed; chỉ kiểm tra xu hướng tổng hợp. Công thức tích `(1-p^N)` chỉ đối chiếu LEGACY_IID, không va chạm, không hết hạn, đủ thời gian theo dõi và tham số đồng nhất tương ứng; không dùng sai số ±5 điểm phần trăm làm nghiệm thu mọi trường hợp.

## 7. Log, triển khai và kiểm tra

### 7.1. Đầu ra bắt buộc

- Manifest: scenario, profile, cấu hình, seed, phiên bản code, đồng hồ, thời gian máy, hệ số tăng tốc đo được và mọi giả định.
- Log sự kiện: RUN_START/END, GEN, TX_START/END, RX_OK, DROP, DUP, LEVEL, FAIL, DETECT, REPAIR_TX, BYPASS_ON, REVERT, UNREACHABLE, GW, RADIO_STATE.
- Mỗi bản ghi có `run_id,t,node`; gói có `src,seq,flag,event_id,copy_id,from,to,tgen,ttx`; DROP có nguyên nhân chính và tập nguyên nhân. RX/GW phải khớp TX tương ứng, tgen không đổi qua relay.
- Bảng CSV/JSON theo run và tổng hợp CI; đồ thị PDR từng nút, cảnh báo đúng hạn/CI, phân bố thời gian cảnh báo và đường đánh đổi năng lượng–độ tin cậy. Báo rõ số run hợp lệ/lỗi.

### 7.2. Trình tự triển khai

1. Kiểm tra adapter CupCarbon: đồng hồ, headless, seed, TX/RX thật, đệm khi ngủ và MAC nội bộ. Hiện runner gọi TestSimulation.class và chưa có tham số seed; phải tìm/khôi phục nguồn harness hoặc viết harness có nguồn kiểm tra được trước benchmark.
2. Tạo harness sự kiện với một lớp radio duy nhất chịu trách nhiệm airtime/va chạm/trạng thái; SenScript giữ logic giao thức. Nếu CupCarbon không cung cấp đủ hook thì bổ sung adapter/harness Java có mã nguồn và kiểm thử; không giả lập va chạm chỉ bằng thêm xác suất DROP trong script.
3. Hoàn thiện pilot và hồi quy LEGACY; sau đó LORA_STRESS, đối chứng, quét cấu hình và xác nhận độc lập.
4. Chỉ sau khi có log V3 mới cập nhật bảng, hình và kết luận báo cáo. Giữ các kết quả không đạt và hạn chế của mô hình; chưa có kiểm chứng thực địa thì không gọi là xác nhận triển khai an toàn.

### 7.3. Ca nghiệm thu hành vi

- Hai node không lỗi: airtime khớp 41,216 ms; tăng tốc máy không thay timestamp mô phỏng hoặc kết quả cùng seed.
- Hai TX chồng lấn cùng máy thu: va chạm; không chồng lấn thì không va chạm; máy đang TX/OFF hoặc chết không RX.
- Thay đổi chu kỳ lấy mẫu không tự tắt radio; kiểm tra năng lượng RX liên tục và half-duplex.
- Mưa + Delta lớn cùng lúc: L0; leo thang có hiệu lực đủ 60 s và gia hạn đúng quy tắc.
- Bản sao cùng khóa chỉ tới GW/relay một lần; gói khác đến đảo thứ tự không bị bỏ nhầm; kiểm tra cả điều khiển.
- Không biết lịch hỏng: bypass không kích hoạt vì so sánh T_FAIL; thử S1/S3/S10 hỏng và hai nút liên tiếp; timeout sai khi kênh xấu phải xuất được.
- Bộ đếm cảnh báo: nhận ở 29,999/30,000 s là đúng hạn; sau 30 s là trễ; không nhận là thất bại; không có sự kiện là NA.
- Gói cuối phiên có thể tới trong theo dõi; gói còn chờ cuối cùng có trạng thái riêng; độ trễ không âm, tgen không đổi.
- LEGACY_IID khớp xác suất theo khoảng tin cậy thống kê trong thử nghiệm cô lập; LORA_STRESS cho thấy tác động tương quan/va chạm thay vì ép khớp IID.
- Tích phân trạng thái radio cộng đủ thời gian sống và năng lượng tính tay của ví dụ nhỏ; lặp cùng seed/cấu hình cho cùng kết quả.

## 8. Cách trình bày đóng góp và giới hạn

Đóng góp cần chứng minh là cách phối hợp cơ chế nhẹ và lựa chọn tham số dưới ràng buộc cảnh báo/năng lượng trên chuỗi tuyến tính. Lập bảng đối chiếu với [1] LoRa đa chặng và [2] quan trắc sạt lở thích ứng trong báo cáo theo cơ chế, giả định và bằng chứng; không mặc định từng cơ chế đơn lẻ là mới. Gom mô tả phát lặp/nối vòng/kênh vào một nơi, phần kết quả chỉ phân tích ảnh hưởng đo được.

Các mức mất do thời tiết, bán kính nhiễu và tỷ lệ dòng chuẩn hóa chưa được hiệu chỉnh thực địa. Demo hai node sau này chỉ xác nhận thao tác và trao đổi gói ở quy mô nhỏ. Thí nghiệm nhiều seed và mô hình tốt hơn tăng chất lượng bằng chứng mô phỏng, không tự bảo đảm hệ thống an toàn ngoài đời hay đủ điều kiện xuất bản.
