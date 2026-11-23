# -*- coding: utf-8 -*-
"""
Script: update_paper_scopus.py
Nang cap va chuan hoa toan dien bai bao khoa hoc:
'Bao_Cao_Khoa_Hoc_LoRa_Landslide.docx'
Dat tieu chuan hoc thuat quoc te (Scopus/ISI):
- Bo sung va kiem chung toan bo tai lieu tham khao [1]-[12] (doi chieu chuan DOI).
- Nhieu bang bieu thong so chuan, tieu de dat tren bang.
- Chen 5 hinh ve khoa hoc chat luong cao (Topology, Sleep FSM, PDR/node, Latency/node, TX/node).
- Chuan hoa cong thuc toan hoc RI (tong trong so toi da dung 100).
- Khach quan hoa cac nhan dinh khoa hoc, phan tich trung thuc co che chuyen tuyen va gioi han mo phong.
"""

import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def generate_paper():
    doc = Document()
    
    # Can le 1 inch (2.54 cm) chuan A4
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        
    def set_cell_background(cell, fill_hex):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        tcPr.append(shd)

    def set_cell_margins(cell, top=120, bottom=120, left=140, right=140):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
        tcPr.append(tcMar)

    def set_table_borders(table, color="B0C4DE", sz="4", val="single"):
        tblPr = table._tbl.tblPr
        borders = parse_xml(f'<w:tblBorders {nsdecls("w")}><w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/><w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/><w:left w:val="none"/><w:right w:val="none"/><w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/><w:insideV w:val="none"/></w:tblBorders>')
        tblPr.append(borders)

    def add_title(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(14)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(15.5)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 32, 96)
        return p

    def add_heading_1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12.5)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 51, 102)
        return p

    def add_heading_2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11.5)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 70, 140)
        return p

    def add_heading_3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.italic = True
        run.font.color.rgb = RGBColor(40, 40, 40)
        return p

    def add_body_p(text, bold_prefix="", italic_prefix=""):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.line_spacing = 1.25
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = 'Times New Roman'
            r_pre.font.size = Pt(11)
            r_pre.font.bold = True
        if italic_prefix:
            r_it = p.add_run(italic_prefix)
            r_it.font.name = 'Times New Roman'
            r_it.font.size = Pt(11)
            r_it.font.italic = True
            
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)
        return p

    def add_caption(text, is_table=False):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(6) if not is_table else Pt(10)
        p.paragraph_format.space_after = Pt(4) if not is_table else Pt(4)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next = True if is_table else False
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0, 51, 102) if is_table else RGBColor(50, 50, 50)
        return p

    def add_equation_box(eq_text, eq_num=""):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(5)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        r = p.add_run(eq_text)
        r.font.name = 'Cambria Math'
        r.font.size = Pt(11)
        r.font.bold = True
        
        if eq_num:
            r_num = p.add_run(f"    ({eq_num})")
            r_num.font.name = 'Times New Roman'
            r_num.font.size = Pt(10.5)
            r_num.font.italic = True
            r_num.font.bold = False
        return p

    def add_figure_img(path, width_in, caption_text):
        if os.path.exists(path):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.keep_with_next = True
            run = p.add_run()
            run.add_picture(path, width=Inches(width_in))
            add_caption(caption_text, is_table=False)
        else:
            print(f"[CANH BAO] Khong tim thay anh: {path}")

    # ==================== PHẦN ĐẦU BÁO CÁO ====================
    add_title("THIẾT KẾ VÀ ĐÁNH GIÁ GIAO THỨC TRUYỀN THÔNG THÍCH ỨNG ĐA CHẶNG TRÊN NỀN TẢNG LORA P2P CHO HỆ THỐNG CẢNH BÁO SỚM SẠT LỞ ĐẤT")

    # Abstract EN
    add_body_p(
        "Landslides on steep slopes in Northern Vietnam represent severe natural hazards, often causing devastating human and infrastructural losses. Deploying low-cost Internet of Things (IoT) monitoring systems in these rugged areas is hindered by scarce telecommunication coverage, battery constraints, and harsh wireless propagation. This study presents the design, software-level protocol optimization, and performance evaluation of an event-driven, multi-hop LoRa Peer-to-Peer (P2P) communication protocol for landslide early warning. Rather than focusing on proprietary hardware manufacturing, the system abstracts commercial sensory inputs (capacitive soil moisture, MPU-6050 angular kinematics, and SW-420 mechanical shock interrupts) to synthesize a non-linear multi-variable Landslide Risk Index (RI). To balance node lifespan and alert latency, an adaptive three-level sleep scheduling mechanism combined with Delta compression is implemented. Crucially, addressing the severe channel constraints of LoRa, the protocol operates without acknowledgments (ACK/NACK), relying on prioritized blind replication with randomized jitter, sequence deduplication, and downstream alarm escalation. Furthermore, a decentralized fault-tolerant self-healing mechanism is evaluated to maintain connectivity under node hard failure. The system is benchmarked on the CupCarbon simulator across a 500 m linear topology comprising 10 sensor nodes and one gateway under seven benchmark scenarios (KB-0 to KB-6) incorporating independent probabilistic channel attenuation models. Results show a baseline Packet Delivery Ratio (PDR) of 97.8% (99.4% excluding boundary buffer packets) with an average latency of 16.10 s, while maintaining 93.9% PDR under single-node hard failure. Under severe environmental stress and compound disasters, prioritized critical alerts maintain robust delivery channels, demonstrating the feasibility of the proposed software-driven protocol for sustainable disaster risk reduction.",
        bold_prefix="Abstract—"
    )
    add_body_p(
        "Landslide Early Warning Systems (LEWS), Wireless Sensor Networks (WSNs), Multi-Hop LoRa P2P, Event-Driven Adaptive Sleep, Delta Compression, Self-Healing Routing, CupCarbon Simulator.",
        bold_prefix="Keywords: "
    )

    # Tóm tắt VI
    add_body_p(
        "Sạt lở đất tại các sườn dốc đồi núi phía Bắc Việt Nam là hiểm họa địa chất nghiêm trọng, thường xuyên gây thiệt hại nặng nề về người và hạ tầng giao thông. Việc triển khai các hệ thống quan trắc Internet vạn vật (IoT) chi phí thấp tại các vùng địa hình hiểm trở gặp rào cản lớn do thiếu hụt hạ tầng viễn thông công cộng, giới hạn năng lượng pin và điều kiện truyền sóng vô tuyến bất lợi. Nghiên cứu này tập trung vào thiết kế, tối ưu hóa giao thức phần mềm và đánh giá hiệu năng mạng LoRa ngang hàng (P2P) đa chặng hướng sự kiện phục vụ cảnh báo sớm sạt lở đất. Hệ thống khai thác dữ liệu từ các cảm biến thương mại sẵn có (cảm biến độ ẩm đất điện dung chống ăn mòn, cảm biến vi cơ điện tử MPU-6050 đo góc nghiêng/vận tốc góc và cảm biến rung chấn SW-420 kích hoạt ngắt cứng) để xây dựng mô hình tính toán chỉ số nguy cơ sạt lở đất đa biến phi tuyến (RI). Nhằm giải quyết sự đánh đổi giữa tuổi thọ nguồn pin và độ trễ cảnh báo khẩn cấp, một thuật toán điều khiển chu kỳ ngủ sâu thích ứng ba cấp kết hợp nén dữ liệu Delta và cơ chế leo thang báo động xuôi dòng được thiết lập. Để phù hợp với đặc thù băng thông hẹp của LoRa, giao thức vận hành hoàn toàn không dùng bản tin xác nhận (ACK/NACK), đảm bảo độ tin cậy thông qua cơ chế phát lặp mù có độ trễ ngẫu nhiên, khử trùng lặp theo số thứ tự và giải thuật chuyển tuyến tự phục hồi phân tán khi có nút trung gian bị hỏng cứng. Toàn bộ hệ thống được kiểm chứng mô phỏng trên nền tảng sự kiện rời rạc CupCarbon với chuỗi tuyến tính 10 nút cảm biến và một trạm cổng dọc tuyến 500 m qua bảy kịch bản chuẩn mực (KB-0 đến KB-6) dưới tác động của mô hình suy hao kênh truyền xác suất độc lập do mưa, sạt lở và sự cố phá hủy nút. Kết quả cho thấy mạng đạt tỷ lệ chuyển phát gói tin (PDR) 97,8% ở điều kiện cơ sở (đạt 99,4% khi loại trừ các gói đệm biên cuối phiên) với độ trễ trung bình 16,10 s, duy trì PDR 93,9% khi một nút trung gian bị hỏng cứng. Trong các tình huống sạt lở nghiêm trọng và thảm họa phức hợp, cơ chế phân cấp ưu tiên giúp chuyển tiếp hiệu quả các bản tin cảnh báo khẩn cấp về trạm cổng, khẳng định tính khả thi của giải pháp tối ưu hóa phần mềm trong quan trắc thiên tai cộng đồng.",
        bold_prefix="Tóm tắt—"
    )
    add_body_p(
        "Cảnh báo sớm sạt lở đất, Mạng cảm biến không dây (WSN), LoRa đa chặng không ACK, Chu kỳ ngủ sâu thích ứng, Nén dữ liệu Delta, Tự phục hồi mạng, Mô phỏng CupCarbon.",
        bold_prefix="Từ khóa: "
    )

    # ==================== 1. GIỚI THIỆU ====================
    add_heading_1("1. GIỚI THIỆU")
    add_body_p(
        "Sạt lở đất là một trong những hiểm họa địa chất nguy hiểm và khó dự đoán nhất tại các khu vực đồi núi dốc, đặc biệt là miền núi phía Bắc Việt Nam. Địa hình phân cắt mạnh, tầng vỏ phong hóa tàn tích dày và các đợt mưa lớn kéo dài trong mùa mưa bão là những yếu tố kích hoạt chính dẫn đến mất ổn định mái dốc. Cơ chế trượt lở mái dốc thường bắt nguồn từ quá trình nước mưa thẩm thấu vào tầng đất, làm tăng áp lực nước lỗ rỗng và suy giảm sức chống cắt của khối đất đá theo nguyên lý cơ học đất Mohr-Coulomb [8]. Khi khối đất đạt trạng thái bão hòa kết hợp với biến dạng chuyển vị vi mô ban đầu, hiện tượng đứt gãy cung trượt có thể xảy ra nhanh chóng, đe dọa trực tiếp đến tính mạng người dân và cô lập các tuyến giao thông huyết mạch."
    )
    add_body_p(
        "Trước đây, công tác quan trắc mái dốc thường dựa vào các thiết bị địa kỹ thuật chuyên dụng như máy đo nghiêng sâu (inclinometer), máy đo áp lực nước lỗ rỗng (piezometer) hoặc trạm định vị vi sai D-GNSS [8]. Mặc dù có độ chính xác cao, các hệ thống này đòi hỏi chi phí đầu tư và bảo dưỡng rất lớn, quy trình lắp đặt phức tạp và khó phủ kín mật độ tại nhiều điểm dân sinh xung yếu. Mạng cảm biến không dây (WSN) và Internet vạn vật (IoT) mang lại hướng tiếp cận kinh tế và linh hoạt hơn cho các hệ thống cảnh báo sớm (Early Warning Systems – EWS) [1], [4]. Tuy nhiên, việc triển khai tại các vùng núi hiểm trở phía Bắc gặp phải hai rào cản hạ tầng cốt tử: sóng viễn thông di động (3G/4G) kém ổn định hoặc tê liệt khi mưa lũ; và nguồn điện lưới không khả dụng, đòi hỏi các nút mạng phải tự cung cấp năng lượng từ pin độc lập."
    )
    add_body_p(
        "Công nghệ truyền thông vô tuyến công suất thấp tầm xa LoRa (Long Range) nổi lên như giải pháp tối ưu nhờ độ nhạy thu cao (lên tới -148 dBm), khả năng xuyên thấu vật cản tốt và tiêu hao năng lượng thấp [2], [10]. Tại Việt Nam, thiết bị vô tuyến cự ly ngắn băng hẹp công suất thấp hoạt động theo Quy chuẩn kỹ thuật quốc gia QCVN 122:2020/BTTTT và Thông tư 08/2021/TT-BTTTT của Bộ Thông tin và Truyền thông, trong đó quy định dải tần cho phép là 920–923 MHz (kế hoạch tần số khu vực AS923) với giới hạn chu kỳ chiếm sóng (duty cycle) không quá 1% đối với nút cảm biến đầu cuối và không quá 10% đối với trạm cổng [12]. Khi ứng dụng LoRa vào hệ thống giám sát sạt lở dọc tuyến sườn dốc dài, các thách thức kỹ thuật chính về mặt phần mềm và giao thức bao gồm:"
    )
    add_body_p(
        "Sự đánh đổi năng lượng - độ trễ cảnh báo (Energy-Latency Trade-off): Các giao thức truyền thống áp dụng chu kỳ lấy mẫu và gửi tin định kỳ cố định. Nếu giãn cách chu kỳ gửi để tiết kiệm pin, độ trễ cảnh báo sẽ lớn và dễ bỏ lỡ thời điểm dịch chuyển tức thời; ngược lại, nếu duy trì tần suất gửi dày đặc, nguồn pin tại hiện trường sẽ nhanh chóng cạn kiệt.",
        italic_prefix="• "
    )
    add_body_p(
        "Giới hạn truyền thông đa chặng trên kênh LoRa băng hẹp: Do sườn dốc kéo dài hàng trăm mét bị che khuất bởi địa hình và tán rừng (Non-Line-of-Sight – NLoS), truyền thông trực tiếp một chặng từ đỉnh dốc về trạm cổng đòi hỏi hệ số trải phổ (SF) lớn hoặc công suất cao, làm tăng thời gian chiếm sóng (Time-on-Air) và vi phạm quy định tần số [9], [12]. Cấu trúc đa chặng tuyến tính là giải pháp tất yếu, nhưng việc áp dụng cơ chế xác nhận hai chiều (ACK/NACK) trên kênh LoRa sẽ làm tăng gấp đôi lưu lượng, gây xung đột và suy giảm tuổi thọ pin [10].",
        italic_prefix="• "
    )
    add_body_p(
        "Nguy cơ đứt gãy mạng do lệch pha ngủ khi nút trung gian gặp sự cố: Khi một nút trung gian bị đất đá phá hủy, luồng dữ liệu từ các nút thượng lưu sẽ bị gián đoạn. Các thuật toán định tuyến tự phục hồi truyền thống dựa vào trao đổi bản tin điều khiển hai chiều, vốn khó hoạt động ổn định khi các nút vận hành ở chế độ ngủ sâu không đồng bộ.",
        italic_prefix="• "
    )
    add_body_p(
        "Khác với các nghiên cứu tập trung vào chế tạo phần cứng, bài báo này tập trung vào thiết kế thuật toán phần mềm và tối ưu hóa giao thức mạng. Hệ thống chỉ khai báo sử dụng các tham số đầu vào từ cụm cảm biến chi phí thấp sẵn có gồm: cảm biến độ ẩm đất điện dung (chống ăn mòn khi chôn ngầm), cảm biến gia tốc và góc nghiêng vi cơ điện tử MPU-6050 (đo chuyển vị động học), và cảm biến rung chấn SW-420 (kích hoạt ngắt phần cứng). Trọng tâm nghiên cứu là xây dựng mô hình thuật toán xử lý dữ liệu và giao thức mạng LoRa đa chặng tự phục hồi, được đánh giá trên nền tảng mô phỏng sự kiện rời rạc CupCarbon [6], [7]."
    )
    add_body_p(
        "Các đóng góp chính của nghiên cứu bao gồm:",
        bold_prefix="Đóng góp của nghiên cứu: "
    )
    add_body_p(
        "Đề xuất mô hình tính toán Chỉ số nguy cơ sạt lở đất đa biến phi tuyến (RI), kết hợp biến thiên độ ẩm đất thể tích, vận tốc góc biến dạng sườn dốc và xung chấn động cơ học theo nguyên lý cơ - thủy văn sườn dốc.",
        bold_prefix="1) "
    )
    add_body_p(
        "Thiết kế thuật toán điều khiển chu kỳ ngủ sâu thích ứng ba cấp kết hợp nén dữ liệu Delta và cơ chế leo thang báo động xuôi dòng, bảo toàn tỷ lệ thời gian giữa mô hình thực địa và mô hình mô phỏng thu nhỏ, giúp giảm 83,3% tần suất thức dậy ở trạng thái ổn định.",
        bold_prefix="2) "
    )
    add_body_p(
        "Xây dựng giao thức mạng LoRa đa chặng vận hành hoàn toàn không dùng bản tin xác nhận (ACK/NACK), kết hợp kỹ thuật phát lặp mù có độ trễ ngẫu nhiên (Blind Replication with Jitter) và bộ lọc khử trùng lặp theo số thứ tự.",
        bold_prefix="3) "
    )
    add_body_p(
        "Phát triển và đánh giá giải thuật chuyển tuyến tự phục hồi phân tán kết hợp cơ chế chuyển tuyến nhanh chủ động từ phía phát và cơ chế chấp nhận gói cháu tại phía thu, duy trì kết nối mạng khi nút trung gian bị phá hủy mà không cần giao thức bắt tay.",
        bold_prefix="4) "
    )
    add_body_p(
        "Đánh giá định lượng toàn diện trên môi trường mô phỏng CupCarbon qua bảy kịch bản thực nghiệm chuẩn mực (KB-0 đến KB-6), tích hợp mô hình suy hao kênh truyền xác suất độc lập do mưa, sạt lở và sự cố nút, làm rõ sự đánh đổi giữa PDR, độ trễ và chi phí truyền thông.",
        bold_prefix="5) "
    )
    add_body_p(
        "Bố cục bài báo được tổ chức như sau: Phần 2 trình bày tổng quan nghiên cứu liên quan. Phần 3 mô tả thiết kế thuật toán phần mềm, mô hình chỉ số sạt lở và giao thức mạng đề xuất. Phần 4 phân tích kết quả mô phỏng bảy kịch bản trên CupCarbon. Phần 5 thảo luận sâu về hiệu năng và các hạn chế. Phần 6 tổng kết các kết quả chính và định hướng nghiên cứu tiếp theo."
    )

    # ==================== 2. TỔNG QUAN NGHIÊN CỨU ====================
    add_heading_1("2. TỔNG QUAN NGHIÊN CỨU LIÊN QUAN")
    add_body_p(
        "Nghiên cứu ứng dụng mạng cảm biến không dây trong quan trắc sạt lở đất đã được triển khai rộng rãi trên thế giới. Ramesh [3] đã phát triển và thử nghiệm thực địa hệ thống WSN cảnh báo sạt lở tại Munnar (Ấn Độ), chứng minh rằng việc kết hợp đo lượng mưa, độ ẩm đất và áp lực nước lỗ rỗng theo cấu trúc cảnh báo ba cấp (sớm, trung gian, khẩn cấp) mang lại khả năng cảnh báo hiệu quả cho cộng đồng. Intrieri và cộng sự [8] đã chuẩn hóa quy trình thiết lập ngưỡng động học cho hệ thống cảnh báo sớm trượt lở quy mô mái dốc tại Torgiovannetto (Ý), nhấn mạnh tầm quan trọng của việc kết hợp đo độ ẩm với vận tốc biến dạng chuyển vị. Chu và cộng sự [4] triển khai mạng SitkaNet tại Alaska, minh chứng tính khả thi của việc sử dụng các cảm biến vi cơ điện tử thương mại chi phí thấp để quan trắc biến động áp lực lỗ rỗng và độ ẩm tầng đất phong hóa."
    )
    add_body_p(
        "Về công nghệ truyền thông, LoRa và LoRaWAN đã trở thành công nghệ tiêu biểu cho các ứng dụng quan trắc môi trường đồi núi [2], [5]. Wang và cộng sự [2] thiết kế hệ thống quan trắc sạt lở dựa trên LoRa topo hình sao, chỉ ra rằng LoRa có khả năng xuyên thấu tán rừng và hoạt động tốt hơn ZigBee hay Bluetooth trong môi trường đồi dốc. Tuy nhiên, Bor và cộng sự [9] đã phân tích khả năng mở rộng của mạng LoRa và chỉ ra rằng khi số lượng nút tăng hoặc khoảng cách truyền lớn, hiện tượng suy hao và va chạm gói trên kênh vô tuyến tăng nhanh. Cattani, Boano và Römer [10] qua các đánh giá thực nghiệm đã khẳng định rằng độ tin cậy của liên kết LoRa phụ thuộc đáng kể vào các yếu tố môi trường (nhiệt độ, độ ẩm tán cây) và việc hạ tốc độ dữ liệu ở các liên kết rìa phủ sóng có thể phản tác dụng do thời gian chiếm sóng tăng cao."
    )
    add_body_p(
        "Để khắc phục giới hạn tầm nhìn thẳng (LoS) trên địa hình đồi dốc dài, kiến trúc LoRa đa chặng đã được nghiên cứu. Ranasinghe và cộng sự [1] đề xuất kiến trúc LoRa Leap đa chặng cho cảnh báo động đất phi tập trung, sử dụng cơ chế phát tán đa đường để giảm công suất nút và mở rộng tầm phủ sóng. Tuy nhiên, cơ chế phát tán nhiều đường kèm xác nhận ACK tạo ra phụ tải kênh lớn, chưa tối ưu cho các hệ thống giám sát pin dài hạn. Về phương pháp thu thập dữ liệu thích ứng, Joshi, Kanungo và Panigrahi [11] đề xuất thiết bị SMARTMODE ứng dụng mạng ZigBee có khả năng chuyển đổi chu kỳ lấy mẫu theo mức độ biến động của môi trường. Mặc dù vậy, công trình của Joshi chưa giải quyết bài toán phối hợp chu kỳ ngủ giữa các nút trên tuyến chuyển tiếp đa chặng."
    )
    add_body_p(
        "Về môi trường mô phỏng, CupCarbon là nền tảng mô phỏng mạng cảm biến dựa trên sự kiện rời rạc được sử dụng phổ biến [6]. López-Pavón và cộng sự [7] đã đánh giá CupCarbon và chỉ ra rằng các mô hình mặc định thường giả định môi trường truyền sóng lý tưởng, chưa tích hợp trực tiếp các biến động suy hao ngẫu nhiên của kênh truyền khi có mưa lớn hoặc biến dạng địa hình sạt lở. Từ các nghiên cứu trên, bài báo này tập trung giải quyết bài toán tối ưu hóa thuật toán phần mềm cho mạng LoRa đa chặng không ACK, có khả năng thích ứng chu kỳ ngủ và tự phục hồi khi nút trung gian bị phá hủy."
    )

    # ==================== 3. THIẾT KẾ HỆ THỐNG VÀ THUẬT TOÁN ====================
    add_heading_1("3. THIẾT KẾ HỆ THỐNG VÀ THUẬT TOÁN TỐI ƯU PHẦN MỀM")
    
    add_heading_2("3.1. Topology mạng và Khai báo thông số cảm biến đầu vào")
    add_body_p(
        "Hệ thống giám sát được thiết lập dọc theo một tuyến sườn dốc xung yếu dài 500 m, đại diện cho cung trượt taluy dương tại vùng núi phía Bắc. Mạng sử dụng cấu trúc chuỗi tuyến tính (Linear Daisy-Chain Topology) gồm 10 nút cảm biến (S1 đến S10) và một trạm cổng (Gateway, ký hiệu S11) đặt tại chân dốc an toàn (Hình 1). Tọa độ địa lý được đặt tại kinh độ 103,840000°E và vĩ độ từ 22,335000°N (S11 – 0 m) đến 22,339505°N (S10 – 500 m trên đỉnh dốc). Khoảng cách giữa hai nút liền kề cố định ở mức d = 50 m."
    )

    # FIGURE 1
    add_figure_img(
        "figures/fig1_topology.png", 6.2,
        "Hình 1. Sơ đồ cấu trúc mạng chuỗi tuyến tính gồm 10 nút cảm biến và một trạm cổng (S11) dọc tuyến khảo sát 500 m, minh họa vùng sạt lở giả định (S4–S7) và liên kết nối vòng vượt cấp 100 m."
    )

    add_body_p(
        "Hệ thống định hướng tối ưu hóa thuật toán phần mềm, không yêu cầu phần cứng chuyên dụng phức tạp mà khai báo sử dụng các tham số đầu vào từ cụm ba cảm biến thương mại (Bảng 1):"
    )

    # TABLE 1: SENSORS
    add_caption("Bảng 1. Khai báo các tham số cảm biến đầu vào và vai trò trong thuật toán.", is_table=True)
    t_sens = doc.add_table(rows=4, cols=4)
    t_sens.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_sens)
    
    headers_ts = ["Cảm biến", "Đại lượng đo", "Giao tiếp vi điều khiển", "Vai trò trong thuật toán phần mềm"]
    for j, h in enumerate(headers_ts):
        c = t_sens.cell(0, j); c.text = h
        set_cell_background(c, "003366"); set_cell_margins(c, 120, 120, 100, 100)
        p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs: r.font.name = 'Times New Roman'; r.font.size = Pt(9.5); r.font.bold = True; r.font.color.rgb = RGBColor(255, 255, 255)
        
    data_ts = [
        ["Độ ẩm đất điện dung v1.2", "Độ ẩm thể tích đất (H, %)", "Tín hiệu tương tự (ADC 10-bit)", "Đo độ bão hòa nước trong tầng đất, đóng vai trò kích hoạt điều kiện tiền đề sạt lở."],
        ["MPU-6050 (MEMS 6-DoF)", "Góc nghiêng (Pitch, Roll) và vận tốc góc (ω)", "Bus số I2C", "Xác định chuyển vị biến dạng động học của khối đất đá trên mái dốc."],
        ["SW-420 (Rung cơ học)", "Xung rung chấn cơ học (V_vib ∈ {0, 1})", "Ngắt ngoài phần cứng (EXTI)", "Đánh thức tức thời vi điều khiển khỏi chế độ Deep-Sleep khi xuất hiện nứt toác cơ học."]
    ]
    for i, row in enumerate(data_ts):
        bg = "F4F8FA" if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row):
            c = t_sens.cell(i+1, j); c.text = val
            set_cell_background(c, bg); set_cell_margins(c, 100, 100, 100, 100)
            p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j in [0, 3] else WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs: r.font.name = 'Times New Roman'; r.font.size = Pt(9.0); r.font.bold = True if j == 0 else False

    add_body_p(
        "Cơ chế ngắt cứng của SW-420: Ở trạng thái bình thường, vi điều khiển duy trì chế độ ngủ sâu (Deep-Sleep) với dòng tiêu thụ tĩnh chỉ khoảng 10–15 µA. Khi đất đá nứt toác cơ học, xung sườn xuống từ SW-420 kích hoạt bộ ngắt EXTI, đánh thức vi điều khiển trong thời gian dưới 1 ms mà không cần chờ hết chu kỳ ngủ hẹn giờ (RTC Timer). Sau khi thức dậy, vi điều khiển đọc kiểm tra chéo góc biến dạng từ MPU-6050 để loại bỏ rung chấn giả trước khi phát bản tin cảnh báo khẩn cấp. Trong môi trường CupCarbon, cơ chế ngắt cứng này được trừu tượng hóa thông qua lệnh kiểm tra sự kiện dreadsensor evt."
    )

    add_body_p(
        "Toàn bộ cấu hình mạng vô tuyến LoRa và các tham số mô phỏng được chuẩn hóa trong Bảng 2:"
    )

    # TABLE 2: SIMULATION PARAMS
    add_caption("Bảng 2. Bảng tham số mô phỏng và cấu hình giao thức mạng trên CupCarbon.", is_table=True)
    t_cfg = doc.add_table(rows=11, cols=3)
    t_cfg.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_cfg)
    
    headers_tc = ["Nhóm tham số", "Tham số cấu hình", "Giá trị thiết lập"]
    for j, h in enumerate(headers_tc):
        c = t_cfg.cell(0, j); c.text = h
        set_cell_background(c, "003366"); set_cell_margins(c, 120, 120, 120, 120)
        p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs: r.font.name = 'Times New Roman'; r.font.size = Pt(9.5); r.font.bold = True; r.font.color.rgb = RGBColor(255, 255, 255)
        
    data_tc = [
        ["Cấu hình vô tuyến LoRa", "Dải tần số hoạt động / Điều chế", "920–923 MHz (AS923) / LoRa Chirp Spread Spectrum"],
        ["", "Công suất phát / Hệ số trải phổ (SF)", "14 dBm (25 mW) / SF = 7, Băng thông BW = 125 kHz"],
        ["", "Bán kính truyền vật lý / Bán kính logic danh định", "110 m (cho phép nối vòng) / 70 m (giới hạn lọc logic)"],
        ["Thời gian và chu kỳ ngủ", "Thời lượng mô phỏng mỗi kịch bản (T_sim)", "1000 s (trên nền tảng CupCarbon)"],
        ["", "Chu kỳ ngủ thích ứng (Level 0 / 1 / 2)", "5 s (Khẩn cấp) / 15 s (Cảnh báo mưa) / 30 s (Ổn định)"],
        ["", "Ngưỡng số chu kỳ ổn định (stablecnt)", "stablecnt ≥ 3 (chuyển Level 1), stablecnt ≥ 6 (chuyển Level 2)"],
        ["Cơ chế phát lặp & Jitter", "Số bản sao phát lặp (N_REP)", "FLAG 0: 1 bản (không mưa) / 2 bản (mưa); FLAG 100: 2 bản; FLAG 255/150/200: 3 bản"],
        ["", "Giãn cách ngẫu nhiên giữa các bản sao (Jitter)", "100–400 ms (JIT_MIN đến JIT_MAX), nghỉ sau cụm: 150–250 ms"],
        ["Tự phục hồi & Giám sát", "Ngưỡng thời gian im lặng tối đa (T_sil)", "clamp(3 × T_sleep, 70 s, 90 s); cố định 100 s tại trạm cổng"],
        ["Khung gói tin", "Kích thước tải trọng hữu ích (Payload)", "Khoảng 6 byte: [SRC, FLAG, VAL, SEQ, PREV]"]
    ]
    for i, row in enumerate(data_tc):
        bg = "F4F8FA" if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row):
            c = t_cfg.cell(i+1, j); c.text = val
            set_cell_background(c, bg); set_cell_margins(c, 100, 100, 100, 100)
            p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j > 0 else WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs: r.font.name = 'Times New Roman'; r.font.size = Pt(9.0); r.font.bold = True if j == 0 else False

    add_heading_2("3.2. Thuật toán hợp nhất dữ liệu và Công thức chỉ số nguy cơ sạt lở đa biến (RI)")
    add_body_p(
        "Theo lý thuyết cơ học đất, sạt lở là quá trình tương tác cơ - thủy văn phức tạp [8]. Độ ẩm bão hòa làm giảm góc ma sát trong và lực dính hữu hiệu là điều kiện tiền đề; biến dạng góc và rung chấn cơ học là biểu hiện động học trực tiếp của sự đứt gãy cung trượt. Nếu chỉ có mưa lớn mà sườn dốc chưa biến dạng, nguy cơ dừng ở mức cảnh báo; nhưng nếu độ ẩm cao xảy ra đồng thời với biến dạng góc, nguy cơ sạt lở sẽ tăng vọt do hiện tượng mất ổn định trượt lở."
    )
    add_body_p(
        "Để phản ánh bản chất trên, nghiên cứu đề xuất công thức tính toán Chỉ số nguy cơ sạt lở đất đa biến phi tuyến RI(t) ∈ [0, 100] tại thời điểm t như sau:"
    )
    add_equation_box(
        "RI(t) = RI_base + w_H · f(H) + w_θ · g(Δθ, ω) + w_V · V_vib + w_coup · [f(H) × g(Δθ, ω)]",
        eq_num="1"
    )
    add_body_p(
        "Trong đó:"
    )
    add_body_p(
        "RI_base = 20 ± ε: Chỉ số nền ở trạng thái sườn dốc ổn định, trong đó ε ∈ [-2, +2] là thành phần nhiễu vi khí hậu ngẫu nhiên.",
        italic_prefix="• "
    )
    add_body_p(
        "f(H) ∈ [0, 1]: Hàm bão hòa độ ẩm đất phi tuyến dạng Sigmoid, chuẩn hóa từ độ ẩm thể tích H: f(H) = 1 / (1 + exp(-k_H · (H - H_th))), với H_th là ngưỡng bão hòa của tầng vỏ phong hóa và k_H là hệ số dốc. Khi mưa lớn kéo dài, f(H) → 1.",
        italic_prefix="• "
    )
    add_body_p(
        "g(Δθ, ω) ∈ [0, 1]: Hàm biến dạng động học thu được từ MPU-6050, kết hợp độ biến thiên góc nghiêng tổng hợp Δθ = √((ΔPitch)² + (ΔRoll)²) và vận tốc góc tức thời ω = dθ/dt: g(Δθ, ω) = min(1, c_1 · (Δθ / θ_max) + c_2 · (ω / ω_max)).",
        italic_prefix="• "
    )
    add_body_p(
        "V_vib ∈ {0, 1}: Trạng thái nhị phân từ cảm biến rung SW-420, nhận giá trị 1 khi có xung chấn động vượt ngưỡng kích hoạt ngắt và 0 khi ở trạng thái nghỉ.",
        italic_prefix="• "
    )
    add_body_p(
        "w_H, w_θ, w_V, w_coup: Các trọng số thành phần, được cân đối để tổng giá trị tối đa không vượt quá 100: w_base = 20, w_H = 22, w_θ = 20, w_V = 13, và trọng số tương tác ghép đôi w_coup = 25 (tổng cực đại: 20 + 22 + 20 + 13 + 25 = 100).",
        italic_prefix="• "
    )
    add_body_p(
        "Công thức (1) là mô hình khái niệm định lượng hóa nguy cơ; trong mô phỏng CupCarbon, để kiểm soát chính xác các kịch bản thực nghiệm, các mức giá trị RI được gán trực tiếp theo kịch bản: giá trị nền 20 ± 2, bước nhảy mưa +22 đơn vị (đạt 42–44) và sự kiện sạt lở đạt 88–92. Chỉ số tổng hợp RI(t) được ánh xạ trực tiếp sang ba mức trạng thái vận hành của mạng cảm biến:",
        bold_prefix="Lưu ý về mô hình hóa: "
    )
    add_body_p(
        "Trạng thái Bình thường (Normal, RI < 40): Môi trường ổn định, f(H) ≈ 0, g ≈ 0, V_vib = 0, RI dao động quanh mức 20 ± 2 (< 40). Nút gán cờ định kỳ (FLAG = 0), chỉ gửi độ lệch Delta và chuyển dần sang chế độ ngủ sâu.",
        bold_prefix="1) "
    )
    add_body_p(
        "Trạng thái Cảnh báo mưa lớn (Pre-warning, 40 ≤ RI < 85): Mưa lớn làm bão hòa đất (f(H) → 1) nhưng sườn dốc chưa biến dạng (g ≈ 0, V_vib = 0), chỉ số tăng thêm 22 đơn vị, đạt 42–44. Nút kích hoạt cờ cảnh báo (FLAG = 100), chuyển chu kỳ ngủ về cấp 1 (15 s) và tăng cường bản sao phát lặp.",
        bold_prefix="2) "
    )
    add_body_p(
        "Trạng thái Nguy cấp sạt lở (Imminent Landslide, RI ≥ 85): Đất bão hòa nước kết hợp chuyển vị góc dốc và kích hoạt rung chấn SW-420, thành phần ghép đôi bùng nổ, đưa RI lên ngưỡng 88–92 (≥ 85). Nút gán cờ khẩn cấp (FLAG = 255), chuyển về chu kỳ thức nhanh cấp 0 (5 s) và kích hoạt leo thang báo động toàn tuyến.",
        bold_prefix="3) "
    )

    add_heading_2("3.3. Cơ chế ngủ sâu thích ứng 3 cấp và Thuật toán nén dữ liệu Delta")
    add_body_p(
        "Hệ thống áp dụng cơ chế quản lý năng lượng thích ứng ba cấp (Level 0, Level 1, Level 2) kết hợp với thuật toán nén dữ liệu Delta hướng sự kiện (Hình 2)."
    )

    # FIGURE 2
    add_figure_img(
        "figures/fig2_sleep_fsm.png", 6.2,
        "Hình 2. Sơ đồ máy trạng thái chu kỳ ngủ thích ứng ba cấp (Level 0, Level 1, Level 2) và điều kiện chuyển trạng thái dựa trên cờ sự kiện, bộ lọc ngưỡng Delta và cơ chế leo thang báo động xuôi dòng."
    )

    add_body_p(
        "Biện luận hai tầng thời gian (Operational Profile vs. Scaled Simulation Profile): Trong triển khai thực địa thực tế, sạt lở là hiện tượng tích lũy theo thời gian. Ở điều kiện an toàn, chu kỳ lấy mẫu danh định được đặt ở mức 15–30 phút (Level 2) để dòng tiêu thụ tĩnh duy trì tuổi thọ pin từ 1–2 năm; khi có mưa lớn, chu kỳ rút ngắn về 3–5 phút (Level 1); và khi xuất hiện biến dạng, chu kỳ chuyển sang lấy mẫu dày đặc 5–10 giây (Level 0). Tuy nhiên, trong mô phỏng CupCarbon với thời lượng phiên chạy 1000 s (≈ 16,6 phút), việc áp dụng chu kỳ ngủ 15 phút sẽ khiến mỗi nút chỉ thức dậy một lần, không thể quan sát động học mạng đa chặng và độ trễ lan truyền. Do đó, nghiên cứu áp dụng mô hình thu nhỏ thời gian có chủ đích với các chu kỳ ngủ tương ứng là 5 s (Level 0), 15 s (Level 1) và 30 s (Level 2). Tỷ lệ tương đối giữa các cấp độ được bảo toàn ở mức 1 : 3 : 6 (giảm 83,3% tần suất thức dậy ở Level 2 so với Level 0), phản ánh đúng bản chất tiết kiệm năng lượng mà không làm mất tính tổng quát của thuật toán.",
        bold_prefix="Biện luận hai tầng thời gian: "
    )
    add_body_p(
        "Thuật toán nén Delta: Tại mỗi chu kỳ thức, nút tính độ lệch tuyệt đối Δ = |RI(t) - RI(t-1)|. Nếu Δ < θ = 5,0 và cờ hiện hành FLAG = 0, môi trường được xem là ổn định; nút chỉ gửi giá trị vi sai Δ và tăng bộ đếm ổn định stablecnt thêm 1. Khi stablecnt ≥ 3, nút chuyển từ Level 0 sang Level 1; khi stablecnt ≥ 6, nút chuyển xuống Level 2. Ngược lại, nếu Δ ≥ θ hoặc xuất hiện FLAG > 0, stablecnt lập tức bị đặt lại về 0 và nút chuyển ngay về Level 0.",
        bold_prefix="Thuật toán nén Delta: "
    )
    add_body_p(
        "Cơ chế leo thang báo động xuôi dòng (Downstream Alarm Escalation): Để tránh việc gói tin khẩn cấp bị ứ đọng do các nút trung gian hạ lưu đang ngủ ở Level 1 (15 s) hoặc Level 2 (30 s), bất kỳ nút trung gian nào khi nhận và chuyển tiếp thành công gói tin mang cờ khẩn cấp (FLAG = 255) hoặc cờ báo mất nút (FLAG = 150) sẽ lập tức chuyển trạng thái về Level 0 (chu kỳ 5 s) trong thời gian tối thiểu 60 s tiếp theo. Cơ chế này giúp thiết lập nhanh tuyến truyền thông thông suốt từ vị trí sự cố về trạm cổng.",
        bold_prefix="Leo thang báo động xuôi dòng: "
    )

    add_heading_2("3.4. Giao thức truyền thông LoRa đa chặng không ACK và Bộ lọc khử trùng lặp")
    add_body_p(
        "Kênh truyền LoRa có băng thông hẹp (125 kHz) và tốc độ truyền dữ liệu thấp. Nếu áp dụng cơ chế xác nhận bắt tay hai chiều (ACK/NACK) trên từng chặng, số lượng gói tin phát sóng trên mạng sẽ tăng gấp đôi, gây tắc nghẽn kênh và tăng xác suất xung đột. Do đó, giao thức được thiết kế vận hành hoàn toàn không ACK, duy trì độ tin cậy thông qua kỹ thuật phát lặp mù có độ trễ ngẫu nhiên (Blind Replication with Jitter) kết hợp bộ lọc khử trùng lặp tại nút thu."
    )
    add_body_p(
        "Cơ chế phát lặp mù có độ trễ ngẫu nhiên (TX_COPIES): Tại nút nguồn tạo gói, số bản sao phát lặp (N_REP) được phân cấp: Gói tin Delta định kỳ (FLAG = 0) phát 1 bản sao khi không mưa và 2 bản sao khi có mưa; gói tin cảnh báo độ ẩm cao (FLAG = 100) phát 2 bản sao; gói khẩn cấp sạt lở (FLAG = 255) và gói điều khiển mạng (FLAG = 150, 200) phát 3 bản sao. Đối với các nút trung gian chuyển tiếp, gói dữ liệu thông thường được chuyển tiếp với 1 bản sao, trong khi các gói cảnh báo ưu tiên (FLAG = 100, 255, 150) duy trì chuyển tiếp tương ứng 2 đến 3 bản sao. Giữa các bản sao liên tiếp của cùng một gói, nút chèn một khoảng trễ ngẫu nhiên (Jitter) từ 100 ms đến 400 ms (JIT_MIN đến JIT_MAX), đồng thời nghỉ thêm 150 ms đến 250 ms sau mỗi cụm phát nhằm phân tán thời điểm chiếm kênh và giảm xung đột."
    )
    add_body_p(
        "Bộ lọc khử trùng lặp theo số thứ tự: Tại phía thu của các nút chuyển tiếp và Gateway, hệ thống duy trì mảng trạng thái lưu số thứ tự lớn nhất đã tiếp nhận thành công từ từng nút nguồn: lastseq[1..10]. Khi nhận gói tin mang cặp (SRC, SEQ), nếu SEQ ≤ lastseq[SRC], gói tin bị hủy bỏ ngay lập tức (ghi log [DUP]). Chỉ bản sao hợp lệ đầu tiên vượt qua bộ lọc mới được cập nhật lastseq, xử lý nghiệp vụ và chuyển tiếp tới bước nhảy kế tiếp."
    )

    add_heading_2("3.5. Giải thuật chuyển tuyến tự phục hồi phân tán")
    add_body_p(
        "Trong cấu trúc mạng chuỗi tuyến tính, khi một nút trung gian Sk bị phá hủy hoàn toàn (hỏng cứng), luồng dữ liệu từ các nút thượng lưu Sk+1 đến S10 sẽ bị gián đoạn. Các giao thức định tuyến cổ điển giải quyết bài toán này bằng cách để nút cha Sk-1 phát hiện sự im lặng sau một khoảng thời gian, sau đó gửi gói yêu cầu sửa đường (REPAIR – FLAG 200) ngược lên cho nút con Sk+1. Tuy nhiên, cơ chế này gặp khó khăn do hiện tượng lệch pha chu kỳ ngủ: Nút Sk-1 mất từ 70–90 s mới phát hiện im lặng, trong khi nút con Sk+1 đang ở chu kỳ ngủ lệch pha sẽ không nhận được gói REPAIR và tiếp tục gửi dữ liệu vào nút đã hỏng, làm sụt giảm PDR."
    )
    add_body_p(
        "Để giải quyết vấn đề này mà vẫn tuân thủ nguyên tắc không dùng bắt tay hai chiều, nghiên cứu khảo sát sự kết hợp của hai cơ chế:",
        bold_prefix="Cơ chế tự phục hồi phân tán: "
    )
    add_body_p(
        "Cơ chế chuyển tuyến nhanh chủ động từ phía gửi (Sender Fast-Failover): Nút con Sk+1 chuyển bước nhảy nexthop vượt cấp trực tiếp sang Sk-1 ở cự ly 100 m và bật cờ nối vòng (bypass_next = 1). Trong kịch bản KB-5, cơ chế này được kích hoạt theo mốc thời gian cấu hình sự cố (t ≥ T_fail) nhằm xác lập cận trên hiệu năng lý tưởng của khả năng nối vòng khi nút gửi phát hiện sự cố sớm.",
        bold_prefix="1) "
    )
    add_body_p(
        "Cơ chế chấp nhận gói cháu tại phía thu (Receiver Grandchild Acceptance): Tại phía thu, bộ lọc láng giềng logic thông thường chỉ tiếp nhận gói tin có khoảng cách logic bằng 1 (|PREV - myid| = 1) để khống chế cự ly 70 m. Khi nút cha Sk-1 nhận được gói tin có khoảng cách logic bằng 2 xuất phát từ nút cháu Sk+1, bộ lọc logic tự động tiếp nhận gói tin hợp lệ, khóa trạng thái đón gói cháu (bypass_child = 1, bypass_child_id = Sk+1), cập nhật thời gian nghe thấy gần nhất lastheard = tnow và chuyển tiếp gói về Gateway mà không cần gói tin bắt tay.",
        bold_prefix="2) "
    )
    add_body_p(
        "Giám sát thời gian im lặng và hoàn tác (Silence Monitoring & REVERT): Song song với cơ chế trên, thuật toán giám sát im lặng thụ động được duy trì với ngưỡng T_sil = clamp(3 × T_sleep, 70 s, 90 s) (cố định 100 s tại Gateway đối với nút S1). Nếu quá T_sil mà không nghe thấy tín hiệu, nút Sk-1 phát gói báo mất nút (FLAG = 150) về Gateway và gửi 3 bản sao gói REPAIR (FLAG = 200) tới Sk+1 ở chế độ tăng công suất. Nếu sau đó kênh truyền hồi phục và Sk-1 lại nhận được gói trực tiếp từ Sk, nút Sk-1 lập tức hủy trạng thái nối vòng (ghi log [REVERT]) và gửi gói hoàn tác (FLAG = 200, VAL = 0) tới Sk+1 để khôi phục định tuyến ban đầu.",
        bold_prefix="3) "
    )

    add_heading_2("3.6. Mô hình suy hao kênh truyền xác suất độc lập")
    add_body_p(
        "Nhằm đánh giá sát thực tế hiệu năng giao thức, một mô hình suy hao kênh truyền theo xác suất (P_LINK) được tích hợp trực tiếp tại khâu tiếp nhận của mọi nút cảm biến và Gateway. Xác suất hủy một bản sao gói tin phát từ nút a đến nút b tại thời điểm t = TTX được xác định bởi:"
    )
    add_equation_box(
        "p_drop = max(p_rain(t), p_ls(a, b, t)) + p_bypass_extra",
        eq_num="2"
    )
    add_body_p(
        "Trong đó: p_rain(t) là suy hao kênh cơ sở do thời tiết mưa áp dụng cho mọi chặng truyền trong toàn mạng (0% khi thời tiết tốt, 12% khi mưa vừa và 25% khi mưa to) trong khoảng thời gian từ T_rain_start đến T_rain_end; p_ls(a, b, t) là suy hao kênh do sạt lở đất, chỉ áp dụng cho các chặng có ít nhất một đầu nằm trong vùng sạt lở (từ S4 đến S7) khi t ≥ T_ls = 73 s (với sạt lở chậm, p_ls tăng tuyến tính lên 40–50% sau thời gian T_ramp = 60 s; với sạt lở nhanh, p_ls nhảy bậc lên 80–85%); và p_bypass_extra là xác suất suy hao phạt bổ sung bằng +10% đối với các liên kết nối vòng cự ly 100 m do suy giảm cường độ tín hiệu theo khoảng cách. Tổng xác suất p_drop trên một chặng được khống chế ở mức trần 95%."
    )

    # ==================== 4. KẾT QUẢ MÔ PHỎNG ====================
    add_heading_1("4. KẾT QUẢ MÔ PHỎNG VÀ ĐÁNH GIÁ HIỆU NĂNG")
    
    add_heading_2("4.1. Thiết lập kịch bản mô phỏng trên nền tảng CupCarbon")
    add_body_p(
        "Hệ thống được đánh giá mô phỏng trên nền tảng CupCarbon Klaines 8.3 thông qua bảy kịch bản thực nghiệm độc lập (từ KB-0 đến KB-6), mỗi kịch bản vận hành liên tục trong thời gian tiêu chuẩn 1000 s: KB-0 (Đường cơ sở đối chứng trong điều kiện thời tiết tốt, không sạt lở, không lỗi phần cứng); KB-1 & KB-2 (Suy hao kênh do mưa vừa 12% và mưa to 25% từ t = 26 s đến 200 s); KB-3 & KB-4 (Mưa vừa kéo dài kết hợp sạt lở tại S5 từ t = 73 s theo chế độ chậm 40–50% và nhanh 80–85%); KB-5 (Nút trung gian S3 hỏng cứng lúc T_fail = 90 s trong điều kiện thời tiết tốt); và KB-6 (Thảm họa phức hợp: Mưa kéo dài, sạt lở nhanh tại S5 từ t = 73 s và nút S5 bị phá hủy hoàn toàn tại t = 93 s)."
    )

    add_heading_2("4.2. Bảng tổng hợp kết quả định lượng")
    add_body_p(
        "Kết quả tổng hợp hiệu năng mạng qua bảy kịch bản mô phỏng 1000 s được lượng hóa chi tiết trong Bảng 3. Hai chỉ số chính gồm: Tỷ lệ chuyển phát gói tin thành công đầu-cuối (PDR), tính bằng tỷ số giữa tổng số gói tin duy nhất nhận được tại Gateway trên tổng số gói tin gốc sinh ra tại các nút nguồn; và độ trễ truyền tin trung bình đầu-cuối từ lúc sinh gói tại nguồn (TGEN) đến khi bản sao hợp lệ đầu tiên tới Gateway. Để đánh giá chính xác độ tin cậy truyền thông loại trừ ảnh hưởng của các gói tin sinh ra ở cuối phiên chưa kịp đến Gateway, chỉ số PDR_excl30 (loại trừ các gói sinh trong 30 s cuối phiên) được tính toán bổ sung."
    )

    # TABLE 3: BENCHMARK
    add_caption("Bảng 3. Kết quả tổng hợp hiệu năng mạng qua bảy kịch bản mô phỏng (1000 s trên CupCarbon).", is_table=True)
    t_res = doc.add_table(rows=8, cols=8)
    t_res.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_res)
    
    headers_tr = ["Kịch bản", "Mô tả kịch bản", "Gói sinh", "Gói nhận", "PDR (%)", "PDR_excl30 (%)", "Độ trễ TB (s)", "Bản sao bị hủy"]
    for j, h in enumerate(headers_tr):
        c = t_res.cell(0, j); c.text = h
        set_cell_background(c, "003366"); set_cell_margins(c, 120, 120, 80, 80)
        p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs: r.font.name = 'Times New Roman'; r.font.size = Pt(9.0); r.font.bold = True; r.font.color.rgb = RGBColor(255, 255, 255)
        
    data_tr = [
        ["KB-0", "Thời tiết tốt, không lỗi", "358", "350", "97,8", "99,4", "16,10", "0 (Kênh lý tưởng)"],
        ["KB-1", "Mưa vừa (W = 12%)", "387", "355", "91,7", "93,7", "31,89", "73 (Mưa)"],
        ["KB-2", "Mưa to (W = 25%)", "389", "331", "85,1", "86,8", "30,56", "141 (Mưa)"],
        ["KB-3", "Sạt lở chậm (P_ls = 40–50%)", "949", "678", "71,4", "72,5", "6,91", "425 (M) + 869 (SL)"],
        ["KB-4", "Sạt lở nhanh (P_ls = 80–85%)", "1028", "464", "45,1", "45,5", "4,69", "240 (M) + 1367 (SL) + 112 (BP)"],
        ["KB-5", "Nút S3 hỏng (T_fail = 90 s)", "329", "309", "93,9", "95,6", "13,57", "12 (Bypass)"],
        ["KB-6", "Mưa + Sạt lở + Nút S5 hỏng", "471", "150", "31,8", "32,8", "6,83", "95 (M) + 381 (SL) + 224 (BP)"]
    ]
    for i, row in enumerate(data_tr):
        bg = "F4F8FA" if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row):
            c = t_res.cell(i+1, j); c.text = val
            set_cell_background(c, bg); set_cell_margins(c, 100, 100, 80, 80)
            p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 1 else WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.name = 'Times New Roman'; r.font.size = Pt(8.5)
                if j in [0, 4, 5]: r.font.bold = True

    add_body_p(
        "Ghi chú viết tắt trong Bảng 3: M = Mưa, SL = Sạt lở đất, BP = Nối vòng cự ly 100 m (Bypass). PDR_excl30 là tỷ lệ chuyển phát tính trên tập các gói tin sinh ra trước mốc t = 970 s nhằm loại trừ sai số do các gói còn nằm trong bộ đệm chuyển tiếp tại thời điểm kết thúc mô phỏng.",
        italic_prefix="* "
    )

    add_body_p(
        "Bên cạnh chỉ số PDR toàn mạng, khả năng chuyển phát tin cậy đối với các bản tin cảnh báo trọng yếu (bản tin cảnh báo mưa lớn FLAG 100 và báo động khẩn cấp sạt lở FLAG 255) được lượng hóa trong Bảng 4:"
    )

    # TABLE 4: ALERTS
    add_caption("Bảng 4. Tỷ lệ phân phát thành công các bản tin cảnh báo sự kiện theo mức cờ ưu tiên.", is_table=True)
    t_alt = doc.add_table(rows=6, cols=3)
    t_alt.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_alt)
    
    headers_ta = ["Kịch bản mô phỏng", "Cảnh báo mưa lớn (FLAG = 100)", "Báo động sạt lở nguy cấp (FLAG = 255)"]
    for j, h in enumerate(headers_ta):
        c = t_alt.cell(0, j); c.text = h
        set_cell_background(c, "003366"); set_cell_margins(c, 120, 120, 120, 120)
        p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs: r.font.name = 'Times New Roman'; r.font.size = Pt(9.5); r.font.bold = True; r.font.color.rgb = RGBColor(255, 255, 255)
        
    data_ta = [
        ["KB-1 (Mưa vừa)", "44 / 44 (100,0%)", "– (Không có sự kiện sạt lở)"],
        ["KB-2 (Mưa to)", "31 / 45 (68,9%)", "– (Không có sự kiện sạt lở)"],
        ["KB-3 (Sạt lở chậm)", "179 / 275 (65,1%)", "123 / 154 (79,9%)"],
        ["KB-4 (Sạt lở nhanh)", "64 / 342 (18,7%)", "35 / 159 (22,0%)"],
        ["KB-6 (Thảm họa phức hợp)", "38 / 235 (16,2%)", "0 / 3 (0,0% - Nút phát bị phá hủy sớm lúc t = 93 s)"]
    ]
    for i, row in enumerate(data_ta):
        bg = "F4F8FA" if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row):
            c = t_alt.cell(i+1, j); c.text = val
            set_cell_background(c, bg); set_cell_margins(c, 100, 100, 120, 120)
            p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.name = 'Times New Roman'; r.font.size = Pt(9.0)
                if j == 0 or (j > 0 and "%" in val): r.font.bold = True

    add_heading_2("4.3. Phân tích chi tiết hiệu năng theo từng nút và từng kịch bản")
    add_body_p(
        "Phân bố PDR theo vị trí từng nút nguồn (từ S1 gần trạm cổng đến S10 ở xa nhất) được thể hiện trực quan trên Hình 3. Xu hướng suy giảm PDR theo số chặng chuyển tiếp được ghi nhận rõ rệt trên tất cả các kịch bản có suy hao kênh."
    )

    # FIGURE 3
    add_figure_img(
        "figures/fig3_pdr_per_node.png", 6.2,
        "Hình 3. Tỷ lệ chuyển phát gói tin thành công (PDR) theo từng nút nguồn (S1 đến S10) trên bảy kịch bản mô phỏng 1000 s."
    )

    add_body_p(
        "Kịch bản KB-0 (Baseline): Ở điều kiện lý tưởng, mạng đạt PDR 97,8% (và đạt 99,4% khi tính theo PDR_excl30). Toàn bộ 4 nút gần trạm cổng (S1 đến S4) đạt PDR tuyệt đối 100%. Các nút ở xa (S5 đến S10) thiếu hụt từ 1–2 gói do phiên mô phỏng kết thúc khi các gói này đang được chuyển tiếp. Độ trễ trung bình tăng tuyến tính theo số chặng: Nút S1 chỉ mất 0,06 s, trong khi S10 mất 32,50 s (Hình 4), tương ứng mức tích lũy trung bình khoảng 3,6 s cho mỗi bước nhảy.",
        bold_prefix="Kịch bản KB-0 (Baseline): "
    )

    # FIGURE 4
    add_figure_img(
        "figures/fig4_latency_per_node.png", 6.2,
        "Hình 4. Độ trễ truyền tin đầu-cuối trung bình (s) theo từng nút nguồn trên các kịch bản đại diện (KB-0, KB-1, KB-2, KB-5)."
    )

    add_body_p(
        "Kịch bản KB-1 & KB-2 (Suy hao do mưa): Dưới tác động của mưa vừa (KB-1), PDR giảm còn 91,7% (93,7% PDR_excl30) với 73 bản sao bị hủy. Mức suy giảm thể hiện rõ theo khoảng cách: S1 duy trì 100%, trong khi S8, S9 và S10 giảm lần lượt còn 88,9%, 80,6% và 73,0% (Hình 3). Độ trễ trung bình tăng lên 31,89 s do các nút hạ lưu xử lý các bản sao đến sau qua nhiều chặng. Nhờ cơ chế phát lặp 2 bản sao cho cờ ưu tiên tại nút nguồn, toàn bộ 44/44 gói tin cảnh báo mưa lớn (FLAG = 100) đều tới trạm cổng thành công (đạt 100%). Khi cường độ mưa tăng lên mức bão (KB-2, suy hao 25%), PDR giảm xuống 85,1% với 141 bản sao bị hủy, và tỷ lệ chuyển giao gói FLAG 100 đạt 68,9% (31/45 gói).",
        bold_prefix="Kịch bản KB-1 & KB-2 (Suy hao do mưa): "
    )
    add_body_p(
        "Kịch bản KB-3 & KB-4 (Sạt lở đất): Khi sự kiện sạt lở kích hoạt, tổng số gói tin sinh ra tăng vọt lên 949 gói (KB-3) và 1028 gói (KB-4) – gấp gần 3 lần kịch bản cơ sở, xác nhận cơ chế lấy mẫu thích ứng hướng sự kiện đã vận hành chính xác. Với sạt lở chậm (KB-3), PDR đạt 71,4%; trong đó gói khẩn cấp (FLAG = 255) đạt tỷ lệ tới nơi 79,9% (123/154 gói) nhờ cơ chế phát lặp 3 bản sao. Bản tin cảnh báo khẩn cấp đầu tiên tới Gateway lúc t = 101,2 s (chỉ sau 28,2 s kể từ thời điểm sạt lở t = 73 s). Ngược lại, trong kịch bản sạt lở nhanh (KB-4), suy hao kênh tức thời 80–85% làm PDR giảm còn 45,1%. Hệ thống ghi nhận 20 lần phát hiện im lặng (DETECT), 18 lần phát yêu cầu sửa đường (REPAIR_TX) và hoàn tác tuyến (REVERT) khi kênh hồi phục.",
        bold_prefix="Kịch bản KB-3 & KB-4 (Sạt lở đất): "
    )
    add_body_p(
        "Kịch bản KB-5 (Khả năng chịu lỗi hỏng nút S3): Khi nút trung gian S3 bị ngắt hoạt động hoàn toàn lúc t = 90 s, cơ chế chuyển tuyến nhanh Sender Fast-Failover tại S4 kích hoạt lúc t = 93,3 s (chỉ sau 3,3 s kể từ thời điểm sự cố), chuyển tuyến trực tiếp sang S2 ở cự ly 100 m. Bộ lọc Receiver Grandchild Acceptance tại S2 tiếp nhận thông suốt luồng dữ liệu (ghi nhận 191 thông điệp CONFIRM). PDR toàn mạng duy trì ở mức 93,9% (95,6% PDR_excl30), chỉ giảm 3,9% so với điều kiện không có lỗi. Độ trễ trung bình toàn mạng giảm từ 16,10 s xuống 13,57 s (và S10 giảm từ 32,50 s xuống 27,45 s) do tuyến đường nối vòng đã bỏ qua một bước nhảy trung gian.",
        bold_prefix="Kịch bản KB-5 (Khả năng chịu lỗi hỏng nút S3): "
    )
    add_body_p(
        "Kịch bản KB-6 (Thảm họa phức hợp): KB-6 tái hiện tình huống khắc nghiệt nhất: Mưa kéo dài, sạt lở nhanh tại S5 (t = 73 s) và nút S5 bị đất đá vùi lấp hoàn toàn lúc t = 93 s. Sau sự cố, nút S6 thiết lập tuyến vòng sang S4 thành công lúc t = 107,8 s (chậm 14,8 s do suy hao kênh). Do liên kết nối vòng 100 m nằm trọn trong vùng sạt lở và chịu mức phạt suy hao lên tới 95%, PDR toàn mạng giảm xuống 31,8%. Ba nút gần trạm (S1–S3) vẫn đạt PDR 75–100%, trong khi các nút phía sau điểm sạt lở chịu tổn thất nặng nề. Cả 3 gói khẩn cấp phát ra trước khi S5 bị phá hủy đều không tới được Gateway do kênh truyền suy hao cực độ.",
        bold_prefix="Kịch bản KB-6 (Thảm họa phức hợp): "
    )

    add_heading_2("4.4. Đánh giá chi phí phát sóng và hiệu quả năng lượng")
    add_body_p(
        "Do việc đo lường dòng điện trực tiếp đòi hỏi mô hình phần cứng nhúng thực nghiệm, nghiên cứu sử dụng tổng số lần phát vật lý [TX] và số lần thức dậy của nút như một đại lượng đại diện (proxy) để đánh giá chi phí năng lượng truyền thông (Hình 5)."
    )

    # FIGURE 5
    add_figure_img(
        "figures/fig5_tx_per_node.png", 6.2,
        "Hình 5. Tổng số lần phát sóng vật lý [TX] theo từng nút trong kịch bản cơ sở (KB-0), sạt lở chậm (KB-3) và sạt lở nhanh (KB-4)."
    )

    add_body_p(
        "Kết quả trên Hình 5 phản ánh rõ đặc tính của cấu trúc mạng chuỗi tuyến tính: Nút S1 nằm sát trạm cổng phải gánh chịu tải chuyển tiếp lớn nhất (350 lần phát trong KB-0 và lên tới 1261 lần phát trong KB-3), trong khi nút đầu tuyến S10 chỉ phát 37 lần trong KB-0 và 70 lần trong KB-3. Cơ chế ngủ sâu ba cấp kết hợp nén Delta giúp giảm 83,3% số lần phát không cần thiết ở các nút thượng lưu trong trạng thái ổn định, bảo toàn năng lượng quý giá cho các giai đoạn xuất hiện biến động môi trường."
    )

    # ==================== 5. THẢO LUẬN ====================
    add_heading_1("5. THẢO LUẬN")
    add_body_p(
        "Kết quả thực nghiệm mô phỏng cung cấp những hiểu biết quan trọng về động học truyền thông của mạng cảm biến LoRa đa chặng trong điều kiện thiên tai, đồng thời làm rõ ba vấn đề kỹ thuật trọng tâm:"
    )
    add_body_p(
        "Thứ nhất, tính đánh đổi giữa cấu trúc chuỗi đa chặng và sự phân rã độ tin cậy theo khoảng cách. Do đặc thù topo tuyến tính, xác suất chuyển phát thành công của một gói tin tích lũy qua k chặng truyền độc lập tuân theo phân phối Bernoulli. Tuy nhiên, cần lưu ý rằng trong thuật toán đề xuất, cơ chế phát lặp mù 2 bản sao khi có mưa (KB-1) chỉ được thực hiện tại nút nguồn, trong khi các nút trung gian chuyển tiếp gói dữ liệu thông thường với 1 bản sao. Do đó, các chặng chuyển tiếp phía sau vẫn chịu xác suất mất gói cơ sở p = 12%. Điều này giải thích vì sao PDR thực nghiệm của nút xa nhất S10 đạt 73,0%, thấp hơn so với mức lý thuyết nếu tất cả các chặng đều phát lặp 2 bản sao (≈ 86,4%). Kết quả này cho thấy để duy trì PDR cao cho các nút ở xa trong điều kiện kênh xấu, cần xem xét mở rộng cơ chế phát lặp cho cả các chặng chuyển tiếp trung gian đối với các gói tin định kỳ quan trọng.",
        bold_prefix="Tính đánh đổi đa chặng: "
    )
    add_body_p(
        "Thứ hai, hiện tượng 'độ trễ trung bình giảm giả tạo' trong điều kiện suy hao nặng. Một quan sát thoạt nhìn nghịch lý trong Bảng 3 là độ trễ trung bình trong KB-3 (6,91 s) và KB-4 (4,69 s) lại thấp hơn đáng kể so với kịch bản cơ sở KB-0 (16,10 s). Tuy nhiên, phân tích sâu nhật ký sự kiện kết hợp biểu đồ Hình 4 khẳng định nguyên nhân: Không phải do mạng truyền nhanh hơn, mà do phần lớn các gói tin từ các nút xa (S6 đến S10 – vốn có độ trễ tích lũy từ 30–70 s) đã bị hủy trên kênh truyền do sạt lở. Tập gói tin chuyển giao thành công về Gateway chủ yếu xuất phát từ các nút gần trạm (S1 đến S4) với độ trễ chỉ dưới 5 s, kéo giá trị trung bình toàn mạng xuống thấp. Do đó, trong các báo cáo khoa học về mạng WSN thiên tai, độ trễ bắt buộc phải được phân tích đồng thời với PDR phân bố theo từng nút để tránh đưa ra những kết luận sai lệch.",
        bold_prefix="Độ trễ trung bình giảm giả tạo: "
    )
    add_body_p(
        "Thứ ba, hiệu quả và giới hạn của cơ chế tự phục hồi phân tán. Việc kết hợp chuyển tuyến nhanh và chấp nhận gói cháu trong KB-5 đã duy trì PDR toàn mạng ở mức cao 93,9% mà không cần bản tin bắt tay hai chiều. Tuy nhiên, cần nhìn nhận khách quan rằng trong kịch bản KB-5, nút S4 kích hoạt chuyển tuyến dựa trên mốc thời gian cấu hình sự cố, đóng vai trò là một kiểm thử cận trên lý tưởng (oracle benchmark). Trong thực tế phân tán không có thông tin báo trước, nút gửi chỉ có thể chuyển tuyến sau khi giám sát thấy sự im lặng từ nút kế tiếp (mất từ 70–90 s theo ngưỡng T_sil). Hơn nữa, giới hạn cố hữu của cấu trúc chuỗi tuyến tính là chỉ có khả năng nối vòng qua một nút hỏng đơn lẻ (khoảng cách 100 m). Nếu hai nút liền kề cùng bị phá hủy (khoảng cách 150 m), vượt quá bán kính phủ sóng hiệu dụng của LoRa, mạng sẽ rơi vào trạng thái chia cắt hoàn toàn ([PARTITION]).",
        bold_prefix="Khả năng tự phục hồi và giới hạn topo: "
    )
    add_body_p(
        "Các giả định và hạn chế của nghiên cứu cần được ghi nhận rõ ràng: (1) Kênh truyền trong CupCarbon áp dụng mô hình mất gói xác suất độc lập theo bản sao, chưa xét đến hiện tượng suy hao do fading tương quan thời gian và phản xạ đa đường thực tế; (2) Giả định các nút chuyển tiếp có cơ chế thức dậy đủ để xử lý gói tin trong bộ đệm chuyển tiếp; và (3) Nghiên cứu mới dừng ở quy mô mô phỏng sự kiện rời rạc, cần các bước thực nghiệm thực địa trên phần cứng nhúng để kiểm chứng ảnh hưởng của thời tiết thực và tán cây rừng rậm.",
        bold_prefix="Hạn chế của nghiên cứu: "
    )

    # ==================== 6. KẾT LUẬN ====================
    add_heading_1("6. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN")
    add_body_p(
        "Nghiên cứu đã thiết kế, tối ưu hóa thuật toán phần mềm và đánh giá toàn diện một giao thức truyền thông LoRa P2P đa chặng thích ứng hướng sự kiện phục vụ hệ thống cảnh báo sớm sạt lở đất. Bằng cách tập trung vào lớp phần mềm, hệ thống đã khai thác hiệu quả các dữ liệu đầu vào từ cụm cảm biến chi phí thấp (độ ẩm đất điện dung, MPU-6050 và ngắt cứng SW-420) để xây dựng mô hình tính toán chỉ số nguy cơ sạt lở đất đa biến phi tuyến (RI). Giao thức tích hợp thành công cơ chế ngủ sâu thích ứng ba cấp, nén dữ liệu Delta, phát lặp mù khử trùng lặp không ACK và giải thuật chuyển tuyến tự phục hồi phân tán."
    )
    add_body_p(
        "Kết quả thực nghiệm trên nền tảng CupCarbon qua bảy kịch bản chuẩn mực chứng minh mạng vận hành tin cậy trong điều kiện bình thường (PDR 97,8%, trễ 16,10 s), chống chịu tốt trước suy hao do mưa (PDR 85,1–91,7%), duy trì tỷ lệ chuyển giao bản tin cảnh báo trọng yếu đạt 100% trong mưa vừa và phục hồi kết nối hiệu quả khi có nút trung gian bị hỏng cứng (PDR 93,9%). Nghiên cứu cung cấp cơ sở lý thuyết và dữ liệu thực nghiệm quan trọng cho việc phát triển các giải pháp quan trắc thiên tai chi phí thấp tại các vùng miền núi khó khăn."
    )
    add_body_p(
        "Hướng phát triển tiếp theo của đề tài tập trung vào ba nhiệm vụ: (1) Thiết kế cơ chế định tuyến đa đường thích ứng (Mesh/Multi-path) nhằm khắc phục nguy cơ chia cắt mạng khi nhiều nút liền kề bị phá hủy; (2) Tích hợp thuật toán học máy phân tán tại biên (TinyML) trên vi điều khiển nút để tự động nhận dạng sớm các pha biến dạng trượt lở phức tạp; và (3) Chế tạo mô hình phần cứng thực nghiệm, tiến hành thử nghiệm thực địa tại một sườn dốc xung yếu ở miền núi phía Bắc Việt Nam nhằm kiểm chứng và hiệu chuẩn mô hình mô phỏng trong điều kiện môi trường thực tế."
    )

    # ==================== TÀI LIỆU THAM KHẢO ====================
    add_heading_1("TÀI LIỆU THAM KHẢO")
    
    refs = [
        "[1] V. Ranasinghe, N. Udara, M. Mathotaarachchi, T. Thenuwara, D. Dias, R. Prasanna, S. Edirisinghe, S. Gayan, C. Holden, A. Punchihewa, M. Stephens, and P. Drummond, \"Rapid and Resilient LoRa Leap: A Novel Multi-Hop Architecture for Decentralised Earthquake Early Warning Systems,\" Sensors, vol. 24, no. 18, Art. no. 5960, Sep. 2024. https://doi.org/10.3390/s24185960",
        "[2] C. Wang, W. Guo, K. Yang, X. Wang, and Q. Meng, \"Real-Time Monitoring System of Landslide Based on LoRa Architecture,\" Frontiers in Earth Science, vol. 10, Art. no. 899509, Jun. 2022. https://doi.org/10.3389/feart.2022.899509",
        "[3] M. V. Ramesh, \"Design, development, and deployment of a wireless sensor network for detection of landslides,\" Ad Hoc Networks, vol. 13, pp. 2–18, Feb. 2014. https://doi.org/10.1016/j.adhoc.2012.09.002",
        "[4] M. Chu, A. Patton, J. Roering, C. Siebert, J. Selker, C. Walter, and C. Udell, \"SitkaNet: A low-cost, distributed sensor network for landslide monitoring and study,\" HardwareX, vol. 9, Art. no. e00191, Apr. 2021. https://doi.org/10.1016/j.ohx.2021.e00191",
        "[5] M. Ragnoli, M. Scarsella, A. Leoni, G. Ferri, and V. Stornelli, \"Wireless Sensor Network-Based Rockfall and Landslide Monitoring Systems: A Review,\" Sensors, vol. 23, no. 16, Art. no. 7278, Aug. 2023. https://doi.org/10.3390/s23167278",
        "[6] K. Mehdi, M. Lounis, A. Bounceur, and T. Kechadi, \"CupCarbon: A Multi-Agent and Discrete Event Wireless Sensor Network Design and Simulation Tool,\" in Proc. 7th International Conference on Simulation Tools and Techniques (SIMUTOOLS), Lisbon, Portugal, 2014, pp. 1–6. https://doi.org/10.4108/icst.simutools.2014.254811",
        "[7] C. López-Pavón, S. Sendra, and J. F. Valenzuela-Valdés, \"Evaluation of CupCarbon Network Simulator for Wireless Sensor Networks,\" Network Protocols and Algorithms, vol. 10, no. 2, pp. 1–27, 2018. https://doi.org/10.5296/npa.v10i2.13201",
        "[8] E. Intrieri, G. Gigli, F. Mugnai, R. Fanti, and N. Casagli, \"Design and implementation of a landslide early warning system,\" Engineering Geology, vol. 147–148, pp. 124–136, Oct. 2012. https://doi.org/10.1016/j.enggeo.2012.07.017",
        "[9] M. Bor, U. Roedig, T. Voigt, and J. M. Alonso, \"Do LoRa Low-Power Wide-Area Networks Scale?\" in Proc. 19th ACM International Conference on Modeling, Analysis and Simulation of Wireless and Mobile Systems (MSWiM '16), Malta, Nov. 2016, pp. 59–67. https://doi.org/10.1145/2988287.2989163",
        "[10] M. Cattani, C. A. Boano, and K. Römer, \"An Experimental Evaluation of the Reliability of LoRa Long-Range Low-Power Wireless Communication,\" Journal of Sensor and Actuator Networks, vol. 6, no. 2, Art. no. 7, Jun. 2017. https://doi.org/10.3390/jsan6020007",
        "[11] A. Joshi, D. P. Kanungo, and R. K. Panigrahi, \"WSN-Based Smart Landslide Monitoring Device,\" IEEE Transactions on Instrumentation and Measurement, vol. 72, Art. no. 5501912, pp. 1–12, 2023. https://doi.org/10.1109/TIM.2023.3269746",
        "[12] Bộ Thông tin và Truyền thông, \"Quy chuẩn kỹ thuật quốc gia về thiết bị vô tuyến cự ly ngắn dải tần từ 9 kHz đến 40 GHz - Thiết bị truy nhập vô tuyến băng hẹp (LPWAN),\" Quy chuẩn kỹ thuật quốc gia QCVN 122:2020/BTTTT, ban hành kèm theo Thông tư số 26/2020/TT-BTTTT và Thông tư số 08/2021/TT-BTTTT, Hà Nội, 2021."
    ]
    
    for r in refs:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.first_line_indent = Inches(-0.3)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        run = p.add_run(r)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)

    filename = "Bao_Cao_Khoa_Hoc_LoRa_Landslide.docx"
    doc.save(filename)
    print(f"[HOAN TAT] Da tao xong file bai bao chuan hoa: {filename}")

if __name__ == "__main__":
    generate_paper()
