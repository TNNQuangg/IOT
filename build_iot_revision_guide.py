from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


doc = Document()
section = doc.sections[0]
section.page_width, section.page_height = Cm(21), Cm(29.7)
section.top_margin, section.bottom_margin = Cm(1.9), Cm(1.8)
section.left_margin = section.right_margin = Cm(2.15)

for name, size in (("Normal", 11), ("Title", 23), ("Heading 1", 17), ("Heading 2", 12)):
    style = doc.styles[name]
    style.font.name = "Arial"
    style.font.size = Pt(size)
    style.font.color.rgb = RGBColor(0, 0, 0)
    style.element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Arial")
    style.paragraph_format.space_after = Pt(6)
doc.styles["Normal"].paragraph_format.line_spacing = 1.14
doc.styles["Heading 2"].paragraph_format.space_before = Pt(10)
doc.styles["Title"].paragraph_format.space_after = Pt(10)
title_props = doc.styles["Title"].element.get_or_add_pPr()
border = title_props.find(qn("w:pBdr"))
if border is not None:
    title_props.remove(border)


def heading(text):
    doc.add_heading(text, level=2)


def para(text):
    doc.add_paragraph(text)


def draft(text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.45)
    p.add_run("Đoạn đề xuất. ").bold = True
    p.add_run(text)


doc.add_paragraph("Hướng dẫn sửa báo cáo IoT", "Title")
para("Đối chiếu với IOT.docx hiện tại và đặc tả KỊCH BẢN MÔ PHỎNG V3. Các mục dưới đây nêu vị trí cần sửa, những thay đổi đã thực hiện và dữ liệu cần có trước khi viết lại kết quả.")

heading("Tóm tắt và mục 1")
para("Chuyển mục tiêu từ mô tả khả năng hoạt động sang lựa chọn cấu hình trước khi triển khai ở miền núi phía Bắc Việt Nam. Đưa hạn cảnh báo và thứ tự tối ưu vào tóm tắt. Sau khi có kết quả CupCarbon, cập nhật đồng thời tóm tắt, mục kết quả và kết luận.")
draft("Nghiên cứu sử dụng mô phỏng để đánh giá mạng LoRa P2P dạng chuỗi gồm 10 nút cảm biến và một Gateway, với giao thức phát lặp không ACK. Mục tiêu thiết kế là ít nhất 90% sự kiện sạt lở có cảnh báo tới Gateway trong 30 giây kể từ khi khởi phát. Trong các cấu hình đạt mục tiêu, ưu tiên cấu hình giảm tiêu thụ năng lượng tại nút chịu tải lớn nhất.")

heading("Mục 2 Tổng quan và đóng góp")
para("So sánh trực tiếp với [1] về LoRa đa chặng và [2] về quan trắc thích ứng. Nêu cụ thể điểm kế thừa và điều được lượng hóa trong nghiên cứu này. Dùng các đối chứng về chu kỳ lấy mẫu, phát lặp, leo thang và bypass để hỗ trợ phát biểu về đóng góp. Gom mô tả lặp về các cơ chế vào mục 3.")

heading("Mục 3.1 đến 3.4 Mô hình và thuật toán")
para("Giữ các cảm biến đã nêu gồm cảm biến độ ẩm đất điện dung, MPU-6050 và SW-420. Các dải 50 m và 100 m mô tả hình học tuyến. Nếu nêu bán kính 120 m, ghi rõ đây là tham số mô phỏng. Giải thích Delta là giá trị sai khác giữa hai mẫu. Chỉ gọi là nén khi có bằng chứng số byte giảm.")
para("Đồng bộ mục 3.3 và Thuật toán 1 ở mục 3.7 theo đúng thứ tự của mã dùng để lấy kết quả. V3 quy định FLAG 255, cửa sổ leo thang hoặc Δ ≥ 5 được đưa về mức 0 trước khi xét FLAG 100. Kiểm tra trường hợp vừa có mưa vừa vượt ngưỡng Delta trước khi áp dụng mô tả này cho log CupCarbon.")

heading("Mục 3.5 Chuyển tuyến khi mất liên lạc")
para("Nhánh sử dụng lịch hỏng để chuyển tuyến sớm thuộc đối chứng lý tưởng. Batch CupCarbon đã tắt nhánh đó trên bản sao script khi chạy chính. Mô tả phát hiện dựa trên im lặng và bản tin REPAIR. Đối chiếu thứ tự FAIL, DETECT, REPAIR_TX và CONFIRM trước khi kết luận đã phục hồi. Báo riêng phát hiện nhầm hoặc lần thử không khôi phục được.")
para("SenScript đã sửa ca S10 trở lại sau khi mất liên lạc để S9 không gửi gói hoàn tác tới nút chưa được gán. Các gói sửa tuyến mới dùng số thứ tự tăng dần. Các bản sao của cùng một gói giữ chung số thứ tự.")

doc.add_page_break()
doc.add_heading("Cập nhật thiết kế thực nghiệm", level=1)

heading("Mục 3.6 Suy hao vô tuyến và năng lượng")
para("Bộ mô phỏng Python V3 đã bổ sung thời gian phát LoRa, radio bán song công, va chạm, mất gói theo cụm và năng lượng chuẩn hóa. Các kết quả đó phù hợp cho sàng lọc và kiểm tra độ nhạy. Batch CupCarbon hiện dùng lớp mất gói của SenScript đã có và tắt ACK cùng MAC nội bộ. Chỉ ghi một cơ chế V3 vào phương pháp CupCarbon sau khi đã xác minh cơ chế đó trong engine hoặc mã được sử dụng.")
para("Nếu dùng số TX trong Hình 5, gọi đó là tải phát. Khi có dữ liệu thời lượng TX, RX và ngủ, dùng dòng điện tương ứng để tính năng lượng. Ghi rõ đơn vị, giả định dòng, phần năng lượng được tính và nguồn dữ liệu trước khi ước lượng tuổi thọ pin.")

heading("Mục 4.1 Đồng hồ và số lượt chạy")
draft("Mỗi kịch bản CupCarbon chạy trong cửa sổ 600 giây thời gian máy kể từ lúc engine bắt đầu mô phỏng. Thời điểm sự kiện, thời gian chuyển tiếp và hạn 30 giây xác định bằng đồng hồ mô phỏng. Báo cáo ghi cả thời gian máy và mốc dừng mô phỏng cho từng lượt.")
para("Lấy mốc dừng từng lượt từ log CupCarbon. Để so sánh công bằng giữa các lượt có mốc dừng khác nhau, dùng một cửa sổ sinh gói chung ngắn hơn thời gian mô phỏng thực tế nhỏ nhất và quy định thời gian theo dõi sau cửa sổ đó. Ghi rõ mẫu số, gói còn chờ và tiêu chí loại trừ.")
para("Batch 10 phút chạy một lượt mỗi kịch bản. Muốn ước lượng tỷ lệ sự kiện đúng hạn và khoảng tin cậy, cần các lượt độc lập có seed được kiểm soát. Dùng ít nhất 30 seed để khảo sát ban đầu và ghi số thành công, số lượt, khoảng tin cậy Wilson 95%. Với chỉ số PDR, tính theo lượt trước và lấy khoảng tin cậy trên các lượt.")

heading("Mục 4.2 đến 4.4 Cập nhật bảng và hình")
para("Bảng 3 dùng log CupCarbon, báo PDR theo cặp nguồn và số thứ tự. Bảng 4 phân biệt PDR gói cờ 255 với số sự kiện có ít nhất một cảnh báo tới Gateway trong 30 giây. Một lượt không nhận cảnh báo được tính là thất bại trong chỉ số sự kiện.")
para("Tính độ trễ từ GEN tới GW đầu tiên. Báo số mẫu, trung vị và P95 khi có đủ dữ liệu. Đặt Hình 4 cạnh PDR theo nút để giải thích thiên lệch khi chỉ các gói tới Gateway có độ trễ quan sát được. Dùng KB-4 và KB-6 để nêu giới hạn đúng hạn dưới suy hao nhanh và khi nguồn cảnh báo chết.")

doc.add_page_break()
doc.add_heading("Cập nhật thảo luận và kết luận", level=1)

heading("Mục 5 Đọc kết quả và giới hạn")
para("Phân tích từng đối chứng trên cùng điều kiện kênh, topology và tập seed. Thay đúng một cơ chế khi muốn quy chênh lệch cho nó. Ghi tỷ lệ cảnh báo đúng hạn, chi phí phát và các trường hợp nút sống bị báo mất liên lạc. Đối chứng biết trước sự cố chỉ dùng làm mốc tham chiếu.")
para("Giải thích vì sao độ trễ trung bình có thể giảm khi số gói từ các nút xa bị mất nhiều hơn. Nêu hạn chế của mức suy hao giả định, hành vi đệm gói của mô hình đang dùng và phạm vi kết luận về năng lượng. Demo hai node dự kiến chỉ minh họa trao đổi gói, cờ sự kiện và lọc trùng.")

heading("Mục 6 Kết luận và phạm vi bằng chứng")
para("Chốt mỗi kết luận bằng đúng bằng chứng từ CupCarbon. Nếu chưa đủ lượt độc lập để xác nhận tỷ lệ 90%, viết số sự kiện quan sát được và trạng thái mục tiêu. Nếu không đạt, nêu điều kiện gây thất bại và đánh đổi giữa cảnh báo, phát lặp và tải phát.")

heading("Các số liệu đã có để tham khảo nội bộ")
para("Đợt chạy Python V3 gồm 1.050 lượt, tính cả cấu hình chính và đối chứng. Với cấu hình chính và 30 seed, số sự kiện cảnh báo đúng hạn là 30/30 ở KB-3, 7/30 ở KB-4 và 5/30 ở KB-6. Ở KB-3, cận dưới Wilson 95% là 88,65%. Các số liệu này ghi rõ nguồn là bộ mô phỏng Python nếu được đưa vào phụ lục đối chiếu.")

heading("Thông tin cần lấy từ log CupCarbon mới")
for item in (
    "Thời gian chạy máy và thời gian mô phỏng của từng kịch bản.",
    "Tổng số gói sinh, số gói nhận và PDR toàn mạng, theo từng nút và theo cờ cảnh báo.",
    "Thời điểm sạt lở, thời điểm cảnh báo đầu tiên và trạng thái đúng hạn 30 giây ở KB-3, KB-4, KB-6.",
    "Mốc hỏng, phát hiện, yêu cầu sửa tuyến và nhận dữ liệu qua tuyến mới ở KB-5 và KB-6.",
    "Số seed, khoảng tin cậy và kết quả đối chứng khi có đợt chạy lặp độc lập.",
):
    doc.add_paragraph(item, "List Bullet")

doc.core_properties.title = "Hướng dẫn sửa báo cáo IoT"
doc.core_properties.subject = "Đối chiếu IOT.docx với thiết kế mô phỏng LoRa P2P V3"
doc.save(Path(__file__).resolve().parent / "Huong_dan_sua_bao_cao_IOT.docx")
