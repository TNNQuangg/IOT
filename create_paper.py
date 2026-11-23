# -*- coding: utf-8 -*-
"""
Full Generator for 'Bao_Cao_Khoa_Hoc_LoRa_Landslide.docx'
"""

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def build_paper():
    doc = Document()
    
    # Configure 1-inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
    def set_cell_background(cell, fill_hex):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        tcPr.append(shd)

    def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
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
        run.font.size = Pt(16)
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
        run.font.size = Pt(13)
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
        run.font.size = Pt(12)
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
        run.font.size = Pt(11.5)
        run.font.bold = True
        run.font.italic = True
        run.font.color.rgb = RGBColor(30, 30, 30)
        return p

    def add_body_p(text, bold_prefix="", italic_prefix=""):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.25
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = 'Times New Roman'
            r_pre.font.size = Pt(11.5)
            r_pre.font.bold = True
        if italic_prefix:
            r_it = p.add_run(italic_prefix)
            r_it.font.name = 'Times New Roman'
            r_it.font.size = Pt(11.5)
            r_it.font.italic = True
            
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11.5)
        return p

    def add_equation_box(eq_text, eq_num=""):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(5)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        r = p.add_run(eq_text)
        r.font.name = 'Cambria Math'
        r.font.size = Pt(11.5)
        r.font.bold = True
        
        if eq_num:
            r_num = p.add_run(f"    ({eq_num})")
            r_num.font.name = 'Times New Roman'
            r_num.font.size = Pt(11)
            r_num.font.italic = True
            r_num.font.bold = False
        return p

    # --- TITLE ---
    add_title("THIẾT KẾ VÀ ĐÁNH GIÁ GIAO THỨC TRUYỀN THÔNG THÍCH ỨNG ĐA CHẶNG TRÊN NỀN TẢNG LORA P2P CHO HỆ THỐNG CẢNH BÁO SỚM SẠT LỞ ĐẤT")

    # --- ABSTRACT (ENGLISH) ---
    add_body_p(
        "Landslides in steep and mountainous terrains pose devastating natural hazards, frequently causing catastrophic losses of human life and destroying vital infrastructure. While low-cost Internet of Things (IoT) and Wireless Sensor Networks (WSNs) have emerged as promising solutions for environmental surveillance, their field deployment on complex slopes in Northern Vietnam is severely constrained by scarce telecommunication signals, limited energy sources, and harsh radio propagation environments. This paper presents the design, algorithmic software optimization, and comprehensive performance evaluation of an event-driven, multi-hop LoRa Peer-to-Peer (P2P) communication protocol for landslide early warning systems. Rather than focusing on proprietary hardware manufacturing, the study emphasizes high-level algorithmic integration: utilizing low-cost commercial sensory inputs (capacitive soil moisture, MPU-6050 angular kinematics, and SW-420 mechanical shock interrupts) to synthesize a non-linear multi-variable Landslide Risk Index (RI). To optimize energy consumption while strictly guaranteeing warning timeliness, an event-driven adaptive three-level sleep scheduling mechanism combined with Delta data compression is established. Crucially, addressing the severe channel constraints of LoRa, the protocol operates entirely without bi-directional acknowledgments (ACK/NACK), relying on prioritized blind replication with randomized jitter, sequence-number deduplication, and a downstream alarm escalation scheme. Furthermore, a decentralized fault-tolerant self-healing mechanism—integrating proactive Sender Fast-Failover and Receiver Grandchild Acceptance—is proposed to resolve sleep desynchronization when intermediary nodes suffer hard failure. The system is rigorously evaluated on the CupCarbon discrete-event simulation platform across a 500 m linear topology comprising 10 sensor nodes and one gateway under seven benchmark scenarios (KB-0 to KB-6) with harsh probabilistic weather and disaster attenuation models. Simulation results demonstrate a baseline packet delivery ratio (PDR) of 97.8% with an average latency of 16.10 s, while achieving 93.9% PDR under single-node hard failure. Under severe environmental stress and compound disasters, prioritized critical alerts maintain robust delivery channels, demonstrating the feasibility of the proposed software-driven protocol for sustainable disaster risk reduction.",
        bold_prefix="Abstract—"
    )
    add_body_p(
        "Landslide Early Warning Systems (LEWS), Wireless Sensor Networks (WSNs), Multi-Hop LoRa P2P, Event-Driven Adaptive Sleep, Delta Compression, Self-Healing Routing, CupCarbon Simulator.",
        bold_prefix="Keywords: "
    )

    # --- TÓM TẮT (TIẾNG VIỆT) ---
    add_body_p(
        "Sạt lở đất tại các khu vực đồi dốc hiểm trở thuộc miền núi phía Bắc Việt Nam là hiểm họa thiên tai đặc biệt nghiêm trọng, gây thiệt hại nặng nề về người và hạ tầng giao thông. Mặc dù công nghệ mạng cảm biến không dây (WSN) và Internet vạn vật (IoT) mang lại tiềm năng to lớn trong việc thiết lập các hệ thống cảnh báo sớm chi phí thấp, việc triển khai thực địa gặp rào cản lớn do địa hình chia cắt làm suy hao tín hiệu vô tuyến, thiếu thốn nguồn năng lượng lưới và vùng phủ sóng viễn thông kém ổn định. Nghiên cứu này tập trung vào thiết kế, tối ưu hóa thuật toán phần mềm và đánh giá hiệu năng giao thức truyền thông LoRa ngang hàng (P2P) đa chặng hướng sự kiện phục vụ cảnh báo sớm sạt lở đất. Định hướng trọng tâm của nghiên cứu là thiết kế thuật toán tối ưu hóa phần mềm thay vì phát triển phần cứng chuyên dụng: hệ thống khai thác các biến trạng thái từ cụm cảm biến thương mại sẵn có (cảm biến độ ẩm đất điện dung chống ăn mòn, cảm biến góc nghiêng vi cơ điện tử MPU-6050 và cảm biến rung chấn SW-420 kích hoạt ngắt cứng) để xây dựng công thức tính toán chỉ số nguy cơ sạt lở đất đa biến phi tuyến (RI). Nhằm triệt tiêu sự đánh đổi giữa tuổi thọ pin và độ trễ cảnh báo khẩn cấp, một thuật toán điều khiển chu kỳ ngủ sâu thích ứng ba cấp kết hợp nén dữ liệu Delta được đề xuất, bảo toàn tỷ lệ thời gian giữa mô hình thực tế và mô hình mô phỏng. Do đặc thù băng hẹp của LoRa, giao thức được thiết kế vận hành hoàn toàn không sử dụng gói tin xác nhận (ACK/NACK), đảm bảo độ tin cậy thông qua cơ chế phát lặp mù có giãn cách ngẫu nhiên, khử trùng lặp theo số thứ tự và leo thang báo động xuôi dòng. Đồng thời, một giải thuật chuyển tuyến tự phục hồi phân tán kết hợp cơ chế chuyển tuyến nhanh chủ động từ nút gửi (Sender Fast-Failover) và cơ chế chấp nhận gói cháu tại nút nhận (Receiver Grandchild Acceptance) được phát triển nhằm khắc phục triệt để hiện tượng lệch pha chu kỳ ngủ khi có nút trung gian bị hỏng cứng. Toàn bộ hệ thống được kiểm chứng mô phỏng thực nghiệm toàn diện trên nền tảng CupCarbon với chuỗi tuyến tính 10 nút cảm biến và một trạm cổng dọc tuyến khảo sát 500 m qua bảy kịch bản chuẩn mực (từ KB-0 đến KB-6) dưới tác động của mô hình suy hao kênh truyền xác suất độc lập do mưa, sạt lở và sự cố phá hủy nút. Kết quả thực nghiệm cho thấy mạng đạt tỷ lệ chuyển phát gói tin (PDR) 97,8% ở điều kiện cơ sở với độ trễ trung bình 16,10 s, duy trì PDR 93,9% khi một nút trung gian hỏng cứng và khôi phục kết nối chỉ sau 3,3 s. Trong các tình huống sạt lở nghiêm trọng và thảm họa phức hợp, cơ chế phân cấp ưu tiên đảm bảo các gói tin cảnh báo nguy cấp được chuyển tiếp tin cậy về trạm cổng, khẳng định tính khả thi vượt trội của giải pháp thuật toán trong giám sát thiên tai cộng đồng.",
        bold_prefix="Tóm tắt—"
    )
    add_body_p(
        "Cảnh báo sớm sạt lở đất, Mạng cảm biến không dây (WSN), LoRa đa chặng không ACK, Chu kỳ ngủ sâu thích ứng, Nén dữ liệu Delta, Tự phục hồi mạng, Mô phỏng CupCarbon.",
        bold_prefix="Từ khóa: "
    )

    # --- 1. GIỚI THIỆU ---
    add_heading_1("1. GIỚI THIỆU")
    add_body_p(
        "Sạt lở đất là một trong những loại hình tai biến địa chất phổ biến và có sức tàn phá khốc liệt nhất tại các vùng đồi núi dốc, đặc biệt là khu vực miền núi phía Bắc Việt Nam. Đặc thù địa hình phân cắt mạnh, tầng vỏ phong hóa tàn tích dày và lượng mưa tích lũy cục bộ lớn trong mùa mưa bão tạo điều kiện thuận lợi cho sự hình thành các cung trượt nguy hiểm. Cơ chế trượt lở mái dốc thường bắt nguồn từ quá trình nước mưa thấm sâu vào tầng đất, làm gia tăng áp lực nước lỗ rỗng, triệt tiêu lực dính và làm suy giảm nghiêm trọng sức chống cắt của khối đất đá. Khi khối đất đạt trạng thái bão hòa kết hợp với các biến dạng vi mô ban đầu, quá trình trượt lở có thể diễn ra với tốc độ cực nhanh, gây thiệt hại nghiêm trọng về sinh mạng, chia cắt các tuyến giao thông huyết mạch và phá hủy công trình dân sinh."
    )
    add_body_p(
        "Trước đây, công tác quan trắc sạt lở mái dốc chủ yếu dựa vào các thiết bị địa kỹ thuật truyền thống như máy đo nghiêng sâu (inclinometer), cảm biến áp lực nước lỗ rỗng chuyên dụng (piezometer) hoặc hệ thống định vị vệ tinh vi sai (D-GNSS). Mặc dù có độ chính xác cao, các giải pháp này đòi hỏi chi phí đầu tư và vận hành rất đắt đỏ, kỹ thuật lắp đặt phức tạp và khó có thể triển khai diện rộng với mật độ dày đặc tại các sườn dốc dân sinh xung yếu. Trong thập kỷ gần đây, sự phát triển của mạng cảm biến không dây (Wireless Sensor Networks – WSNs) và Internet vạn vật (IoT) đã mở ra hướng tiếp cận kinh tế và linh hoạt hơn cho các hệ thống cảnh báo sớm thiên tai (Early Warning Systems – EWS). Tuy nhiên, việc ứng dụng IoT tại vùng núi sâu phía Bắc gặp phải hai rào cản hạ tầng mang tính cốt tử: hạ tầng viễn thông di động (3G/4G/5G) thường có chất lượng sóng rất kém hoặc bị tê liệt hoàn toàn khi xảy ra mưa lũ kéo dài; và nguồn điện lưới hoàn toàn không khả dụng, đòi hỏi các nút mạng phải tự cung cấp năng lượng từ pin hoặc tấm pin năng lượng mặt trời trong nhiều tháng hoặc nhiều năm liên tục."
    )
    add_body_p(
        "Công nghệ truyền thông vô tuyến công suất thấp tầm xa LoRa (Long Range) nổi lên như một giải pháp lý tưởng nhờ độ nhạy thu cao (lên tới -148 dBm), khả năng xuyên thấu vật cản tốt và tiêu thụ năng lượng thấp. Tuy nhiên, việc ứng dụng LoRa trong quan trắc sạt lở đất sườn dốc dài đặt ra các thách thức kỹ thuật lớn về mặt phần mềm và giao thức mạng:"
    )
    add_body_p(
        "Thứ nhất, sự đánh đổi cố hữu giữa năng lượng và độ trễ cảnh báo (Energy-Latency Trade-off): Các giao thức truyền thống thường áp dụng chu kỳ thu thập và gửi dữ liệu định kỳ cố định. Nếu chu kỳ gửi quá dài (hàng chục phút) để tiết kiệm pin, hệ thống sẽ bỏ lỡ thời điểm dịch chuyển tức thời của sườn dốc; ngược lại, nếu lấy mẫu liên tục ở tần số cao, nguồn pin độc lập tại hiện trường sẽ cạn kiệt trong vòng vài tuần.",
        italic_prefix="• "
    )
    add_body_p(
        "Thứ hai, thách thức truyền thông đa chặng (Multi-hop) không bắt tay trên kênh LoRa băng hẹp: Do sườn dốc kéo dài hàng trăm mét với vật cản địa hình phức tạp, truyền thông điểm - điểm trực tiếp từ đỉnh dốc về chân dốc đòi hỏi công suất phát lớn hoặc hệ số trải phổ (Spreading Factor – SF) cao, làm tăng thời gian chiếm kênh (Time-on-Air) và gây nghẽn sóng. Cấu trúc mạng đa chặng tuyến tính là giải pháp tất yếu, nhưng việc sử dụng các cơ chế xác nhận hai chiều (ACK/NACK) trên kênh LoRa sẽ làm tăng gấp đôi lưu lượng, gây xung đột gói nghiêm trọng và làm cạn kiệt pin.",
        italic_prefix="• "
    )
    add_body_p(
        "Thứ ba, sự cố đứt gãy mạng do lệch pha ngủ khi nút trung gian bị phá hủy: Khi sạt lở hoặc đá rơi làm hỏng một nút cảm biến trung gian, luồng dữ liệu từ toàn bộ các nút thượng lưu phía sau sẽ bị ngắt quãng. Các thuật toán định tuyến tự phục hồi truyền thống thường dựa vào trao đổi bản tin điều khiển hai chiều, vốn hoàn toàn không khả thi khi các nút vận hành ở chế độ ngủ sâu không đồng bộ.",
        italic_prefix="• "
    )
    add_body_p(
        "Khác với các nghiên cứu tập trung vào chế tạo phần cứng phức tạp, bài báo này tập trung giải quyết bài toán sạt lở đất từ góc độ tối ưu hóa thuật toán phần mềm và thiết kế giao thức mạng thích ứng. Hệ thống chỉ khai báo sử dụng các thông số đầu vào từ cụm cảm biến chi phí thấp sẵn có trên thị trường gồm: cảm biến độ ẩm đất điện dung (chống ăn mòn khi chôn ngầm), cảm biến gia tốc và góc nghiêng vi cơ điện tử MPU-6050 (đo chuyển vị động học), và cảm biến rung chấn SW-420 (đóng vai trò ngắt cứng đánh thức tức thời). Trọng tâm nghiên cứu là xây dựng mô hình thuật toán xử lý dữ liệu và giao thức mạng LoRa đa chặng tự phục hồi, được đánh giá toàn diện trên nền tảng mô phỏng sự kiện rời rạc CupCarbon."
    )
    add_body_p(
        "Các đóng góp chính của nghiên cứu bao gồm:",
        bold_prefix="Đóng góp của bài báo: "
    )
    add_body_p(
        "Đề xuất mô hình toán học tính toán Chỉ số nguy cơ sạt lở đất đa biến phi tuyến (RI), kết hợp chặt chẽ giữa biến thiên độ bão hòa nước trong tầng đất, vận tốc góc biến dạng sườn dốc và xung chấn động cơ học, chuẩn hóa các trọng số sát với đặc tính cơ lý sườn dốc miền Bắc Việt Nam.",
        bold_prefix="1) "
    )
    add_body_p(
        "Thiết kế thuật toán quản lý năng lượng với chu kỳ ngủ sâu thích ứng ba cấp (Level 0/1/2) kết hợp giải thuật nén dữ liệu Delta và cơ chế leo thang báo động xuôi dòng, bảo toàn tỷ lệ thời gian giữa thiết kế thực địa và mô hình mô phỏng thu nhỏ, giúp tiết kiệm đến 83,3% số lần thức dậy ở trạng thái ổn định.",
        bold_prefix="2) "
    )
    add_body_p(
        "Xây dựng giao thức mạng LoRa đa chặng hoàn toàn không sử dụng bản tin xác nhận (ACK/NACK), kết hợp kỹ thuật phát lặp mù có độ trễ ngẫu nhiên (Blind Replication with Jitter) và bộ lọc khử trùng lặp theo số thứ tự (Sequence Number Deduplication), giải quyết triệt để vấn đề va chạm và nghẽn kênh.",
        bold_prefix="3) "
    )
    add_body_p(
        "Đề xuất giải thuật chuyển tuyến tự phục hồi phân tán chống lệch pha chu kỳ ngủ, phối hợp giữa cơ chế chuyển tuyến nhanh chủ động từ phía phát (Sender Fast-Failover) và cơ chế chấp nhận gói cháu tại phía thu (Receiver Grandchild Acceptance), duy trì kết nối mạng bền vững khi có nút trung gian bị phá hủy mà không cần giao thức bắt tay.",
        bold_prefix="4) "
    )
    add_body_p(
        "Kiểm chứng và đánh giá định lượng toàn diện trên môi trường CupCarbon thông qua 7 kịch bản mô phỏng chuẩn mực (KB-0 đến KB-6), tích hợp mô hình suy hao kênh truyền xác suất độc lập do mưa lớn, sạt lở đất và phá hủy nút, làm rõ sự đánh đổi giữa PDR, độ trễ và khả năng chịu lỗi của mạng.",
        bold_prefix="5) "
    )
    add_body_p(
        "Bố cục bài báo được tổ chức như sau: Phần 2 tổng quan các nghiên cứu liên quan. Phần 3 mô tả thiết kế thuật toán phần mềm, mô hình chỉ số sạt lở và giao thức mạng đề xuất. Phần 4 trình bày thiết lập mô phỏng và phân tích chi tiết kết quả thực nghiệm 7 kịch bản trên CupCarbon. Phần 5 thảo luận sâu về hiệu năng và các hạn chế kỹ thuật. Cuối cùng, Phần 6 tổng kết các kết quả đạt được và định hướng nghiên cứu tiếp theo."
    )

    # --- 2. TỔNG QUAN NGHIÊN CỨU LIÊN QUAN ---
    add_heading_1("2. TỔNG QUAN NGHIÊN CỨU LIÊN QUAN")
    add_body_p(
        "Việc ứng dụng mạng cảm biến không dây trong giám sát sạt lở đất và tai biến địa chất đã thu hút sự quan tâm sâu sắc của cộng đồng nghiên cứu quốc tế trong nhiều năm qua. Ragnoli và cộng sự [5] đã thực hiện một khảo sát toàn diện về các hệ thống WSN ứng dụng trong quan trắc sạt lở và đá rơi, chỉ ra rằng các nút mạng phân tán chi phí thấp có khả năng bao phủ các vùng địa hình phức tạp tốt hơn nhiều so với các trạm quan trắc địa kỹ thuật tập trung truyền thống. Nghiên cứu của Chu và cộng sự [4] về hệ thống SitkaNet tại vùng núi Đông Nam Alaska đã minh chứng tính khả thi của việc sử dụng các cảm biến vi cơ điện tử thương mại giá rẻ để theo dõi độ ẩm và áp lực nước lỗ rỗng, hỗ trợ cảnh báo sớm các hiện tượng sạt trượt sườn dốc với độ tin cậy đáng khích lệ."
    )
    add_body_p(
        "Về mặt công nghệ truyền thông, LoRa đã nhanh chóng khẳng định vị thế ưu thế trong các ứng dụng quan trắc môi trường đồi núi. Wang và cộng sự [2] đã đề xuất một hệ thống quan trắc sạt lở đất thời gian thực dựa trên kiến trúc LoRa, cho phép thu thập dữ liệu độ nghiêng và lượng mưa truyền trực tiếp về máy chủ trung tâm. Nghiên cứu của Wang chứng minh rằng tín hiệu LoRa có khả năng xuyên thấu tán rừng và vượt qua các vật cản đồi dốc tốt hơn đáng kể so với ZigBee hay Bluetooth. Tuy nhiên, kiến trúc của Wang chủ yếu dựa trên topo hình sao (Star Topology) thông qua giao thức LoRaWAN chuẩn. Trong điều kiện địa hình miền núi hiểm trở bị phân cắt bởi các hẻm vực sâu hoặc sườn núi kéo dài khuất tầm nhìn (Non-Line-of-Sight – NLoS), kết nối một chặng trực tiếp tới Gateway thường bị chặn hoàn toàn hoặc đòi hỏi đặt trụ ăng-ten rất cao với chi phí không khả thi."
    )
    add_body_p(
        "Để khắc phục hạn chế về cự ly và vật cản địa hình, cấu trúc mạng LoRa đa chặng (Multi-hop LoRa) đã được nghiên cứu triển khai. Ranasinghe và cộng sự [1] đã đề xuất kiến trúc LoRa nhảy cóc đa chặng đàn hồi (Resilient LoRa Leap) phục vụ hệ thống cảnh báo sớm động đất phân tán. Công trình này chứng minh rằng việc chia nhỏ đường truyền thành nhiều chặng ngắn giúp giảm công suất phát của từng nút, giảm nhiễu vô tuyến và mở rộng phạm vi giám sát dọc theo các tuyến địa hình kéo dài. Mặc dù vậy, nghiên cứu của Ranasinghe sử dụng cơ chế phát tán bản tin cảnh báo qua nhiều đường (multi-path flooding) kết hợp xác nhận ACK, điều này tạo ra hiện tượng bão bản tin (broadcast storm) và tiêu hao năng lượng lớn khi áp dụng vào mạng giám sát sạt lở đất vốn đòi hỏi tuổi thọ pin kéo dài nhiều tháng."
    )
    add_body_p(
        "Về phương pháp tối ưu hóa năng lượng, hướng tiếp cận thu thập dữ liệu thích ứng và hướng sự kiện (Adaptive and Event-driven Sensing) đã được đề xuất trong một số công trình gần đây. Joshi và cộng sự [3] đã thiết kế thiết bị SMARTMODE ứng dụng mạng ZigBee, có khả năng tự động chuyển đổi giữa chế độ tiết kiệm năng lượng và chế độ lấy mẫu tần suất cao khi các giá trị đo vượt ngưỡng. Tuy nhiên, công trình của Joshi chưa giải quyết được bài toán phối hợp chu kỳ ngủ giữa các nút trên tuyến đa chặng: khi một nút phát hiện sự kiện và thức dậy truyền tin, các nút chuyển tiếp phía sau vẫn có thể đang ngủ say, dẫn đến độ trễ tích lũy rất lớn hoặc mất gói nghiêm trọng."
    )
    add_body_p(
        "Về phương diện mô phỏng và kiểm chứng, CupCarbon được công nhận là một trong những nền tảng mô phỏng mạng cảm biến không dây dựa trên sự kiện rời rạc hàng đầu hiện nay [6], đặc biệt mạnh mẽ trong việc mô phỏng môi trường Smart City và IoT trên nền bản đồ số thực tế. López-Pavón và cộng sự [7] đã đánh giá chi tiết tính năng của CupCarbon, khẳng định khả năng mô phỏng trung thực các giao thức MAC và thuật toán định tuyến phân tán. Tuy nhiên, các mô hình mặc định trong CupCarbon thường giả định môi trường truyền sóng vô tuyến lý tưởng hoặc suy hao đồng nhất, chưa phản ánh được sự biến động khắc nghiệt của kênh truyền khi có mưa lũ lớn, sự gia tăng suy hao tín hiệu trong vùng sạt lở, cũng như tác động của sự cố phá hủy nút cứng."
    )
    add_body_p(
        "Tổng kết lại, các nghiên cứu hiện hữu vẫn tồn tại ba khoảng trống kỹ thuật lớn: (1) Thiếu một công thức hợp nhất dữ liệu đa biến phi tuyến phản ánh đúng bản chất cơ lý sạt lở sườn dốc; (2) Thiếu cơ chế đồng bộ và leo thang chu kỳ ngủ xuôi dòng trên mạng LoRa đa chặng không ACK; và (3) Thiếu giải thuật chuyển tuyến tự phục hồi phân tán có khả năng khắc phục hiện tượng lệch pha ngủ khi nút trung gian bị phá hủy đột ngột. Nghiên cứu này được thực hiện nhằm giải quyết trọn vẹn các thách thức nêu trên."
    )

    # --- 3. THIẾT KẾ HỆ THỐNG VÀ THUẬT TOÁN TỐI ƯU PHẦN MỀM ---
    add_heading_1("3. THIẾT KẾ HỆ THỐNG VÀ THUẬT TOÁN TỐI ƯU PHẦN MỀM")
    
    add_heading_2("3.1. Topology mạng và Khai báo thông số cảm biến đầu vào")
    add_body_p(
        "Hệ thống giám sát được thiết lập dọc theo một tuyến sườn dốc xung yếu dài 500 m, đại diện cho cung trượt taluy dương điển hình tại vùng núi phía Bắc. Cấu trúc mạng áp dụng topo chuỗi tuyến tính (Linear Daisy-Chain Topology) gồm 10 nút cảm biến phân tán (ký hiệu từ S1 đến S10) và một trạm cổng trung tâm (Gateway, ký hiệu S11) đặt tại chân dốc an toàn (Hình 1). Tọa độ địa lý được cố định tại kinh độ 103,840000°E và vĩ độ trải dài từ 22,335000°N (S11 – 0 m) đến 22,339505°N (S10 – 500 m trên đỉnh dốc). Khoảng cách vật lý giữa hai nút kế cận cố định ở mức d = 50 m."
    )
    add_body_p(
        "Để tập trung tối ưu hóa lớp thuật toán phần mềm và đảm bảo tính khả thi kinh tế cho triển khai thực địa diện rộng, hệ thống không đòi hỏi các phần cứng cảm biến chuyên dụng phức tạp mà chỉ khai báo sử dụng các nguồn tín hiệu từ ba module cảm biến thương mại phổ biến:",
        bold_prefix="Khai báo nguồn dữ liệu cảm biến đầu vào: "
    )
    add_body_p(
        "Cảm biến đo độ ẩm thể tích của đất theo nguyên lý đo hằng số điện môi. Điện cực được phủ lớp màng cách điện polymer, loại bỏ hoàn toàn hiện tượng ăn mòn điện hóa (electrochemical corrosion) vốn là nguyên nhân phá hủy các cảm biến độ ẩm dạng trở kháng khi chôn ngập lâu ngày trong môi trường đất ẩm axit. Tín hiệu đầu ra là điện áp tương tự (Analog), tỷ lệ nghịch với độ ẩm đất, được bộ chuyển đổi ADC 10-bit của vi điều khiển đọc định kỳ để xác định độ bão hòa nước.",
        bold_prefix="a) Cảm biến độ ẩm đất điện dung (Capacitive Soil Moisture Sensor v1.2): "
    )
    add_body_p(
        "Module vi cơ điện tử tích hợp con quay hồi chuyển 3 trục và gia tốc kế 3 trục (6 bậc tự do – 6-DoF), giao tiếp với vi điều khiển qua bus I2C. Cảm biến cung cấp vector gia tốc trọng trường để tính toán góc nghiêng hai trục (Pitch và Roll) và đo vận tốc góc tức thời của khối đất, phát hiện chuyển vị biến dạng trượt của mái dốc.",
        bold_prefix="b) Cảm biến gia tốc và góc nghiêng vi cơ điện tử MPU-6050: "
    )
    add_body_p(
        "Cảm biến rung chấn cơ học sử dụng tiếp điểm lò xo thường đóng (NC). Khi đất đá xuất hiện nứt toác cơ học hoặc xung chấn động mạnh, tiếp điểm lò xo dao động ngắt quãng tạo ra xung điện áp logic trên chân DO. Chân tín hiệu này được nối trực tiếp vào chân ngắt ngoài phần cứng (External Interrupt – EXTI) của vi điều khiển, có dòng tiêu thụ tĩnh ở trạng thái nghỉ xấp xỉ bằng 0 µA.",
        bold_prefix="c) Cảm biến rung chấn SW-420 (Kích hoạt ngắt phần cứng): "
    )
    add_body_p(
        "Cơ chế ngắt cứng của SW-420 đóng vai trò bản lề trong kiến trúc phần mềm: Trong trạng thái bình thường, vi điều khiển rơi vào chế độ ngủ sâu (Deep-Sleep) với dòng tiêu thụ tĩnh chỉ từ 10–15 µA. Khi sự cố sạt lở hoặc nứt toác xảy ra, xung sườn xuống từ SW-420 kích hoạt bộ ngắt EXTI, đánh thức vi điều khiển thức dậy ngay lập tức trong thời gian dưới 1 ms mà không cần chờ hết chu kỳ ngủ hẹn giờ (RTC Timer). Ngay sau khi thức dậy, vi điều khiển kích hoạt bus I2C đọc kiểm tra chéo góc biến dạng từ MPU-6050 để loại bỏ rung chấn giả do thú rừng hoặc gió bão, trước khi quyết định phát gói tin báo động khẩn cấp. Trong môi trường CupCarbon, cơ chế ngắt cứng này được trừu tượng hóa bằng lệnh kiểm tra sự kiện tự nhiên dreadsensor evt, tức thời đưa nút về chế độ khẩn cấp Level 0."
    )

    add_heading_2("3.2. Thuật toán hợp nhất dữ liệu và Công thức chỉ số nguy cơ sạt lở đa biến (RI)")
    add_body_p(
        "Trong các hệ thống quan trắc truyền thống, dữ liệu cảm biến thường được so sánh với các ngưỡng độc lập hoặc cộng dồn cơ học đơn giản. Tuy nhiên, theo lý thuyết cơ học đất, sạt lở là một quá trình tương tác cơ - thủy văn phức tạp. Nước ngấm làm bão hòa đất (giảm ứng suất hữu hiệu và góc ma sát trong) là yếu tố kích hoạt chậm (tiền đề); trong khi biến dạng góc và rung chấn cơ học là biểu hiện động học trực tiếp của sự đứt gãy cung trượt. Nếu chỉ có mưa lớn mà góc dốc không đổi, nguy cơ mới dừng ở mức cảnh báo; nhưng nếu độ ẩm cao xảy ra đồng thời với biến dạng góc, nguy cơ sạt lở sẽ tăng vọt theo hàm mũ."
    )
    add_body_p(
        "Từ cơ sở lý thuyết trên, nghiên cứu này đề xuất công thức tính toán Chỉ số nguy cơ sạt lở đất đa biến phi tuyến RI(t) ∈ [0, 100] tại thời điểm t như sau:"
    )
    add_equation_box(
        "RI(t) = RI_base + w_H · f(H) + w_θ · g(Δθ, ω) + w_V · V_vib + w_coup · [f(H) × g(Δθ, ω)]",
        eq_num="1"
    )
    add_body_p(
        "Trong đó:"
    )
    add_body_p(
        "RI_base = 20 ± ε: Chỉ số nền ở trạng thái sườn dốc ổn định, trong đó ε ∈ [-2, +2] là thành phần nhiễu vi khí hậu ngẫu nhiên phân bố đều.",
        italic_prefix="• "
    )
    add_body_p(
        "f(H) ∈ [0, 1]: Hàm bão hòa độ ẩm đất phi tuyến dạng Sigmoid, chuẩn hóa từ độ ẩm thể tích H:",
        italic_prefix="• "
    )
    add_equation_box("f(H) = 1 / (1 + exp(-k_H · (H - H_th)))", eq_num="2")
    add_body_p(
        "với H_th là ngưỡng bão hòa tới hạn của tầng vỏ phong hóa miền Bắc và k_H là hệ số dốc. Khi xảy ra mưa lớn kéo dài, f(H) → 1."
    )
    add_body_p(
        "g(Δθ, ω) ∈ [0, 1]: Hàm biến dạng động học thu được từ MPU-6050, kết hợp độ biến thiên góc nghiêng tổng hợp Δθ = √((ΔPitch)² + (ΔRoll)²) và vận tốc góc tức thời ω = dθ/dt:",
        italic_prefix="• "
    )
    add_equation_box("g(Δθ, ω) = min(1, c_1 · (Δθ / θ_max) + c_2 · (ω / ω_max))", eq_num="3")
    add_body_p(
        "V_vib ∈ {0, 1}: Trạng thái nhị phân từ cảm biến rung SW-420, nhận giá trị 1 khi có xung chấn động vượt ngưỡng kích hoạt ngắt và 0 khi ở trạng thái nghỉ.",
        italic_prefix="• "
    )
    add_body_p(
        "w_H, w_θ, w_V, w_coup: Các trọng số thành phần, được chuẩn hóa thực nghiệm theo đặc thù sườn dốc miền núi phía Bắc với w_H = 22, w_θ = 25, w_V = 20 và trọng số tương tác ghép đôi w_coup = 25.",
        italic_prefix="• "
    )
    add_body_p(
        "Chỉ số tổng hợp RI(t) được ánh xạ trực tiếp sang ba mức trạng thái vận hành của mạng cảm biến:",
        bold_prefix="Phân loại trạng thái vận hành: "
    )
    add_body_p(
        "Khi môi trường ổn định, f(H) ≈ 0, g ≈ 0, V_vib = 0, chỉ số RI dao động quanh giá trị 20 ± 2 (< 40). Nút gán cờ định kỳ (FLAG = 0), chỉ gửi giá trị độ lệch Delta và chuyển dần sang chế độ ngủ sâu.",
        bold_prefix="1) Trạng thái Bình thường (Normal, RI < 40): "
    )
    add_body_p(
        "Khi mưa lớn kéo dài làm bão hòa đất (f(H) → 1) nhưng sườn dốc chưa biến dạng (g ≈ 0, V_vib = 0), chỉ số tăng thêm đúng w_H = 22 đơn vị, đạt mức 42–44 (nằm trong khoảng [40, 85)). Nút kích hoạt cờ cảnh báo độ ẩm cao (FLAG = 100), chuyển chu kỳ thức về cấp 1 (15 s) và tăng cường bản sao phát.",
        bold_prefix="2) Trạng thái Cảnh báo mưa lớn (Pre-warning, 40 ≤ RI < 85): "
    )
    add_body_p(
        "Khi đất bão hòa nước kết hợp với chuyển vị góc dốc và kích hoạt rung chấn từ SW-420, thành phần tương tác ghép đôi [f(H) × g] bùng nổ, đẩy chỉ số RI vượt ngưỡng trần 85 (đạt giá trị giả lập 88–92 trong kịch bản). Nút lập tức gán cờ khẩn cấp (FLAG = 255), chuyển về chu kỳ thức nhanh cấp 0 (5 s) và kích hoạt cơ chế leo thang toàn tuyến.",
        bold_prefix="3) Trạng thái Nguy cấp sạt lở (Imminent Landslide, RI ≥ 85): "
    )

    add_heading_2("3.3. Cơ chế ngủ sâu thích ứng 3 cấp và Thuật toán nén dữ liệu Delta")
    add_body_p(
        "Để giải quyết triệt để sự đánh đổi giữa tuổi thọ pin và độ nhạy cảnh báo, hệ thống áp dụng cơ chế quản lý năng lượng thích ứng ba cấp (Level 0, Level 1, Level 2) kết hợp với thuật toán nén dữ liệu Delta hướng sự kiện."
    )
    add_body_p(
        "Trong các hệ thống thực địa triển khai thực tế (Operational Deployment Profile), sạt lở là hiện tượng tích lũy theo thời gian. Ở điều kiện an toàn, chu kỳ lấy mẫu danh định được thiết lập ở mức 15–30 phút (Level 2) để dòng tiêu thụ tĩnh duy trì tuổi thọ pin từ 1–2 năm; khi có mưa lớn, chu kỳ rút ngắn về 3–5 phút (Level 1); và khi xuất hiện biến dạng, chu kỳ chuyển sang lấy mẫu dày đặc 5–10 giây (Level 0). Tuy nhiên, trong môi trường mô phỏng CupCarbon với thời lượng phiên chạy tiêu chuẩn là 1000 s (≈ 16,6 phút), việc duy trì chu kỳ ngủ 15 phút sẽ khiến mỗi nút chỉ thức dậy đúng một lần, làm mất đi khả năng quan sát động học mạng đa chặng, độ trễ lan truyền và cơ chế tự phục hồi. Do đó, nghiên cứu áp dụng mô hình thu nhỏ thời gian có chủ đích (Scaled Simulation Profile) với các chu kỳ ngủ tương ứng là 5 s (Level 0), 15 s (Level 1) và 30 s (Level 2). Tỷ lệ tương đối giữa các cấp độ được bảo toàn nghiêm ngặt ở mức 1 : 3 : 6 (giảm 83,3% số lần thức ở Level 2 so với Level 0), phản ánh trung thực bản chất tiết kiệm năng lượng mà không làm mất tính tổng quát của thuật toán.",
        bold_prefix="Biện luận hai tầng thời gian (Operational Profile vs. Scaled Simulation Profile): "
    )
    add_body_p(
        "Tại mỗi chu kỳ thức dậy, nút tính toán độ lệch tuyệt đối giữa chỉ số đo hiện tại và chu kỳ liền trước: Δ = |RI(t) - RI(t-1)|. Nếu Δ < θ = 5,0 và cờ hiện hành FLAG = 0, môi trường được xem là hoàn toàn ổn định; nút chỉ gửi giá trị vi sai Δ (thay vì toàn bộ khung dữ liệu) và tăng bộ đếm ổn định stablecnt thêm 1. Khi stablecnt ≥ 3, nút chuyển từ Level 0 sang Level 1; khi stablecnt ≥ 6, nút chuyển xuống trạng thái ngủ sâu Level 2. Ngược lại, nếu Δ ≥ θ hoặc xuất hiện FLAG > 0, bộ đếm stablecnt lập tức bị đặt lại về 0 và nút chuyển ngay về Level 0 (Hình 2).",
        bold_prefix="Thuật toán nén Delta: "
    )
    add_body_p(
        "Một vấn đề nghiêm trọng trong mạng WSN đa chặng có chu kỳ ngủ là hiện tượng nút nguồn phát hiện sự cố khẩn cấp (Level 0 – 5 s) nhưng các nút trung gian phía hạ lưu vẫn đang ngủ say ở Level 1 (15 s) hoặc Level 2 (30 s), khiến gói tin cảnh báo bị ứ đọng tại bộ đệm chuyển tiếp và làm tăng độ trễ đầu-cuối. Để giải quyết, thuật toán tích hợp cơ chế leo thang báo động xuôi dòng: Bất kỳ nút trung gian nào khi nhận và chuyển tiếp thành công một gói tin mang cờ khẩn cấp (FLAG = 255) hoặc cờ báo mất nút (FLAG = 150) sẽ lập tức ép trạng thái của mình về Level 0 (chu kỳ 5 s) và duy trì trạng thái thức nhanh này trong thời gian tối thiểu 60 s tiếp theo. Cơ chế này thiết lập tức thời một 'đường cao tốc truyền tin' thông suốt từ vị trí sạt lở về trạm cổng.",
        bold_prefix="Cơ chế leo thang báo động xuôi dòng (Downstream Alarm Escalation): "
    )

    add_heading_2("3.4. Giao thức truyền thông LoRa đa chặng không ACK và Bộ lọc khử trùng lặp")
    add_body_p(
        "Kênh truyền LoRa có băng thông hẹp (125 kHz) và tốc độ truyền dữ liệu thấp. Nếu áp dụng cơ chế xác nhận bắt tay hai chiều (ACK/NACK) trên từng chặng, số lượng gói tin phát sóng trên mạng sẽ tăng gấp đôi, gây tắc nghẽn kênh nghiêm trọng và dễ dẫn đến xung đột gói khi nhiều nút cùng phát. Do đó, giao thức được thiết kế hoạt động hoàn toàn không ACK, đảm bảo độ tin cậy thông qua sự kết hợp giữa phát lặp mù có độ trễ ngẫu nhiên (Blind Replication with Jitter) và bộ lọc khử trùng lặp tại nút thu."
    )
    add_body_p(
        "Cấu trúc khung gói tin trên sóng vô tuyến được tinh giản tối đa (chiếm khoảng 6 byte dữ liệu hữu ích), bao gồm các trường: [SRC, FLAG, VAL, SEQ, PREV], cùng hai trường phục vụ đo kiểm mô phỏng [TGEN, TTX]. Trong đó: SRC là ID nút nguồn tạo gói (1–10); FLAG là cờ trạng thái (0: Delta, 100: Mưa lớn, 255: Sạt lở, 150: Báo mất nút, 200: Yêu cầu sửa đường); VAL là giá trị đo hoặc ID nút sự cố; SEQ là số thứ tự gói tăng dần riêng biệt cho từng nút nguồn; PREV là ID của nút vừa phát ở chặng liền trước; TGEN là thời điểm khởi tạo tại nguồn và TTX là thời điểm phát tại chặng hiện tại.",
        bold_prefix="Cấu trúc khung tin: "
    )
    add_body_p(
        "Khi nút phát gói tin gốc hoặc chuyển tiếp gói tin của nút khác, nút thực hiện phát liên tiếp N bản sao (N_REP) phụ thuộc vào mức độ ưu tiên của bản tin:",
        bold_prefix="Cơ chế phát lặp mù có độ trễ ngẫu nhiên (TX_COPIES): "
    )
    add_body_p(
        "Gói tin Delta định kỳ (FLAG = 0) trong điều kiện bình thường chỉ phát N = 1 bản sao. Khi có mưa, phát N = 2 bản sao để bù trừ suy hao kênh.",
        italic_prefix="• "
    )
    add_body_p(
        "Gói tin cảnh báo độ ẩm cao (FLAG = 100) phát N = 2 bản sao.",
        italic_prefix="• "
    )
    add_body_p(
        "Gói tin khẩn cấp sạt lở (FLAG = 255) và các gói điều khiển mạng (FLAG = 150, 200) được phát lặp N = 3 bản sao.",
        italic_prefix="• "
    )
    add_body_p(
        "Giữa các bản sao liên tiếp của cùng một gói tin, nút chèn một khoảng trễ ngẫu nhiên (Jitter) từ 100 ms đến 400 ms (JIT_MIN đến JIT_MAX), đồng thời nghỉ thêm từ 150 ms đến 250 ms sau mỗi cụm phát. Khoảng trễ ngẫu nhiên này phân tán thời điểm phát sóng, triệt tiêu xác suất va chạm đồng thời giữa các nút lân cận trên cùng tần số."
    )
    add_body_p(
        "Tại phía thu của các nút chuyển tiếp và Gateway, hệ thống duy trì một mảng trạng thái lưu số thứ tự lớn nhất đã tiếp nhận thành công từ từng nút nguồn: lastseq[1..10]. Khi một gói tin được nhận, nút kiểm tra cặp (SRC, SEQ). Nếu SEQ ≤ lastseq[SRC], gói tin bị xác định là bản sao trùng lặp và bị hủy bỏ ngay lập tức (ghi log [DUP]). Chỉ bản sao hợp lệ đầu tiên vượt qua bộ lọc mới được cập nhật lastseq, xử lý nghiệp vụ và chuyển tiếp tới chặng kế tiếp.",
        bold_prefix="Bộ lọc khử trùng lặp theo số thứ tự: "
    )

    add_heading_2("3.5. Giải thuật chuyển tuyến tự phục hồi phân tán chống lệch pha chu kỳ ngủ")
    add_body_p(
        "Trong cấu trúc mạng chuỗi tuyến tính, nếu một nút trung gian Sk bị đá rơi hoặc sạt lở phá hủy hoàn toàn (hỏng cứng), toàn bộ luồng dữ liệu từ các nút thượng lưu Sk+1 đến S10 sẽ bị gián đoạn. Các giao thức định tuyến cổ điển giải quyết bài toán này bằng cách để nút cha Sk-1 phát hiện sự im lặng sau một khoảng thời gian, sau đó phát gói tin yêu cầu sửa đường (REPAIR – FLAG 200) ngược lên cho nút con Sk+1. Tuy nhiên, giải pháp này gặp phải lỗ hổng nghiêm trọng do hiện tượng lệch pha chu kỳ ngủ (Sleep Desynchronization): Nút Sk-1 phải mất từ 70–90 s để phát hiện im lặng, trong khi nút con Sk+1 đang ở chu kỳ ngủ lệch pha sẽ không nhận được gói REPAIR và tiếp tục gửi dữ liệu vào 'hố đen' nút Sk đã chết, gây sụt giảm PDR thảm hại."
    )
    add_body_p(
        "Để khắc phục triệt để lỗ hổng này mà vẫn tuân thủ nguyên tắc không dùng bắt tay hai chiều, nghiên cứu đề xuất giải thuật chuyển tuyến tự phục hồi phân tán kết hợp hai cơ chế phần mềm độc lập:",
        bold_prefix="Giải pháp phối hợp hai chiều phân tán: "
    )
    add_body_p(
        "Tại phía gửi, khi nút Sk+1 nhận thấy nút kế tiếp Sk bị hỏng cứng (t ≥ T_fail), nút Sk+1 chủ động chuyển bước nhảy nexthop vượt cấp sang nút Sk-1 (hoặc trạm cổng S11 nếu Sk là S1), kích hoạt cờ nối vòng cự ly 100 m (bypass_next = 1) và ghi log [BYPASS_ON]. Quá trình này diễn ra tức thời mà không cần chờ gói tin đánh thức từ nút cha.",
        bold_prefix="1) Cơ chế chuyển tuyến nhanh chủ động từ phía gửi (Sender Fast-Failover): "
    )
    add_body_p(
        "Tại phía thu, trong điều kiện thông thường, bộ lọc láng giềng logic chỉ tiếp nhận gói tin có khoảng cách chỉ số logic bằng 1 (|PREV - myid| = 1) để ép bán kính truyền danh định 70 m. Tuy nhiên, khi nút cha Sk-1 nhận được gói tin có khoảng cách logic bằng 2 xuất phát từ đúng nút cháu Sk+1, bộ lọc logic tự động nhận dạng đây là gói chuyển tuyến hợp lệ, lập tức tiếp nhận (pkt_ok = 1), khóa trạng thái đón gói cháu (bypass_child = 1, bypass_child_id = Sk+1), cập nhật mốc thời gian nghe thấy gần nhất lastheard = tnow và chuyển tiếp gói về Gateway bình thường.",
        bold_prefix="2) Cơ chế chấp nhận gói cháu tại phía thu (Receiver Grandchild Acceptance): "
    )
    add_body_p(
        "Song song với cơ chế trên, nút cha Sk-1 vẫn duy trì thuật toán giám sát im lặng dự phòng: Ngưỡng thời gian im lặng tối đa được tính bằng T_sil = clamp(3 × T_sleep, 70 s, 90 s) (và cố định 100 s tại Gateway đối với nút S1). Nếu quá T_sil mà không nghe thấy tín hiệu từ nút con Sk lẫn nút cháu Sk+1, nút Sk-1 khẳng định nút con bị mất liên lạc, phát gói báo mất nút (FLAG = 150, VAL = k) về Gateway và phát 3 bản sao gói REPAIR (FLAG = 200, VAL = k) tới Sk+1 ở chế độ tăng công suất. Nếu sau đó kênh truyền phục hồi và Sk-1 lại nhận được gói trực tiếp từ Sk, nút Sk-1 lập tức hủy trạng thái nối vòng, ghi log [REVERT] và gửi gói hoàn tác (FLAG = 200, VAL = 0) tới Sk+1 để khôi phục cấu hình định tuyến ban đầu.",
        bold_prefix="3) Giám sát thời gian im lặng và hoàn tác (Silence Monitoring & REVERT): "
    )

    add_heading_2("3.6. Mô hình suy hao kênh truyền xác suất độc lập")
    add_body_p(
        "Nhằm đánh giá sát thực tế hiệu năng giao thức mà không phụ thuộc vào môi trường truyền sóng lý tưởng mặc định của phần mềm, một mô hình suy hao kênh truyền theo xác suất (P_LINK) được tích hợp trực tiếp tại khâu tiếp nhận của mọi nút cảm biến và Gateway. Xác suất hủy một bản sao gói tin phát từ nút a đến nút b tại thời điểm t = TTX được xác định bởi:"
    )
    add_equation_box(
        "p_drop = max(p_rain(t), p_ls(a, b, t)) + p_bypass_extra",
        eq_num="4"
    )
    add_body_p(
        "Trong đó:"
    )
    add_body_p(
        "p_rain(t): Suy hao kênh cơ sở do thời tiết mưa áp dụng cho mọi chặng truyền trong toàn mạng trong khoảng thời gian từ T_rain_start đến T_rain_end. p_rain nhận giá trị 0% khi thời tiết tốt, 12% khi mưa vừa và 25% khi mưa to.",
        italic_prefix="• "
    )
    add_body_p(
        "p_ls(a, b, t): Suy hao kênh do sạt lở đất, chỉ áp dụng cho các chặng có ít nhất một đầu nằm trong vùng sạt lở (từ S4 đến S7) khi t ≥ T_ls = 73 s. Với kịch bản sạt lở chậm, p_ls tăng tuyến tính từ mức mưa nền lên mức bão hòa 40–50% trong thời gian tăng dần T_ramp = 60 s. Với kịch bản sạt lở nhanh, p_ls nhảy bậc tức thời lên mức 80–85%.",
        italic_prefix="• "
    )
    add_body_p(
        "p_bypass_extra: Xác suất suy hao phạt bổ sung bằng +10% đối với các liên kết nối vòng có cự ly 100 m (|a - b| = 2) do suy giảm cường độ tín hiệu thu theo khoảng cách. Tổng xác suất p_drop trên một chặng được khống chế ở mức trần 95%.",
        italic_prefix="• "
    )

    # --- 4. KẾT QUẢ MÔ PHỎNG VÀ ĐÁNH GIÁ HIỆU NĂNG ---
    add_heading_1("4. KẾT QUẢ MÔ PHỎNG VÀ ĐÁNH GIÁ HIỆU NĂNG")
    
    add_heading_2("4.1. Thiết lập kịch bản mô phỏng trên nền tảng CupCarbon")
    add_body_p(
        "Hệ thống được đánh giá mô phỏng toàn diện trên nền tảng CupCarbon Klaines 8.3 thông qua bảy kịch bản thực nghiệm độc lập (từ KB-0 đến KB-6), mỗi kịch bản vận hành liên tục trong thời gian tiêu chuẩn 1000 s (tương đương hơn 16 phút mô phỏng thực thời). Các kịch bản được thiết kế có chủ đích để khảo sát từ điều kiện lý tưởng đến các tình huống thảm họa khắc nghiệt nhất:"
    )
    add_body_p(
        "Đường cơ sở đối chứng trong điều kiện thời tiết lý tưởng (W_rain = 0%), không có sạt lở và không có lỗi phần cứng.",
        bold_prefix="• KB-0 (Baseline): "
    )
    add_body_p(
        "Đánh giá ảnh hưởng của suy hao kênh truyền do mưa vừa (W_rain = 12%) và mưa to (W_rain = 25%) diễn ra từ t = 26 s đến 200 s.",
        bold_prefix="• KB-1 & KB-2 (Suy hao do mưa): "
    )
    add_body_p(
        "Mưa vừa kéo dài kết hợp sự kiện sạt lở tại S5 lúc t = 73 s theo hai chế độ: sạt lở chậm (p_ls tăng dần lên 40–50%) và sạt lở nhanh (p_ls nhảy bậc lên 80–85%).",
        bold_prefix="• KB-3 & KB-4 (Sạt lở chậm và nhanh): "
    )
    add_body_p(
        "Kiểm tra độc lập cơ chế tự phục hồi và nối vòng trong điều kiện thời tiết tốt khi nút trung gian S3 bị hỏng cứng tại thời điểm T_fail = 90 s.",
        bold_prefix="• KB-5 (Hỏng nút trung gian): "
    )
    add_body_p(
        "Tổ hợp thảm họa khắc nghiệt nhất: Mưa kéo dài kết hợp sạt lở nhanh tại S5 (t = 73 s) và nút S5 bị phá hủy hoàn toàn tại t = 93 s.",
        bold_prefix="• KB-6 (Thảm họa phức hợp): "
    )

    add_heading_2("4.2. Bảng tổng hợp kết quả định lượng")
    add_body_p(
        "Hiệu năng toàn mạng qua bảy kịch bản mô phỏng 1000 s được lượng hóa chi tiết trong Bảng 1. Hai chỉ số chính được đánh giá bao gồm: Tỷ lệ chuyển phát gói tin thành công đầu-cuối (Packet Delivery Ratio – PDR), tính bằng tỷ số giữa tổng số gói tin duy nhất nhận được tại Gateway trên tổng số gói tin gốc sinh ra tại các nút nguồn; và độ trễ truyền tin trung bình đầu-cuối từ lúc sinh gói tại nguồn (TGEN) đến khi bản sao đầu tiên tới Gateway."
    )

    # TABLE 1
    t1 = doc.add_table(rows=8, cols=7)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t1)
    
    headers_t1 = ["Kịch bản", "Mô tả kịch bản", "Gói sinh", "Gói nhận", "PDR (%)", "Độ trễ TB (s)", "Bản sao bị hủy (nguyên nhân)"]
    for j, h in enumerate(headers_t1):
        cell = t1.cell(0, j)
        cell.text = h
        set_cell_background(cell, "003366")
        set_cell_margins(cell, top=140, bottom=140, left=100, right=100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(10)
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
            
    data_t1 = [
        ["KB-0", "Thời tiết tốt, không lỗi", "358", "350", "97,8", "16,10", "0 (Kênh lý tưởng)"],
        ["KB-1", "Mưa vừa (W = 12%)", "387", "355", "91,7", "31,89", "73 (Mưa)"],
        ["KB-2", "Mưa to (W = 25%)", "389", "331", "85,1", "30,56", "141 (Mưa)"],
        ["KB-3", "Sạt lở chậm (P_ls = 40–50%)", "949", "678", "71,4", "6,91", "425 (Mưa) + 869 (Sạt lở)"],
        ["KB-4", "Sạt lở nhanh (P_ls = 80–85%)", "1028", "464", "45,1", "4,69", "240 (M) + 1367 (SL) + 112 (BP)"],
        ["KB-5", "Nút S3 hỏng (T_fail = 90 s)", "329", "309", "93,9", "13,57", "12 (Bypass)"],
        ["KB-6", "Mưa + Sạt lở + Nút S5 hỏng", "471", "150", "31,8", "6,83", "95 (M) + 381 (SL) + 224 (BP)"]
    ]
    
    for i, row in enumerate(data_t1):
        bg = "F4F8FA" if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row):
            cell = t1.cell(i+1, j)
            cell.text = val
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 1 else WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(9.5)
                if j in [0, 4]:
                    r.font.bold = True

    add_body_p("Bảng 1: Kết quả tổng hợp hiệu năng mạng qua bảy kịch bản mô phỏng (1000 s trên CupCarbon).", italic_prefix="Ghi chú: ")

    add_body_p(
        "Bên cạnh chỉ số PDR toàn mạng, khả năng chuyển phát tin cậy đối với các bản tin mang tính sống còn (bản tin cảnh báo mưa lớn FLAG 100 và báo động khẩn cấp sạt lở FLAG 255) được lượng hóa trong Bảng 2:"
    )

    # TABLE 2
    t2 = doc.add_table(rows=6, cols=3)
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t2)
    
    headers_t2 = ["Kịch bản mô phỏng", "Cảnh báo mưa lớn (FLAG = 100)", "Báo động sạt lở nguy cấp (FLAG = 255)"]
    for j, h in enumerate(headers_t2):
        cell = t2.cell(0, j)
        cell.text = h
        set_cell_background(cell, "003366")
        set_cell_margins(cell, top=140, bottom=140, left=150, right=150)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(10)
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
            
    data_t2 = [
        ["KB-1 (Mưa vừa)", "44 / 44 (100,0%)", "– (Không có sự kiện sạt lở)"],
        ["KB-2 (Mưa to)", "31 / 45 (68,9%)", "– (Không có sự kiện sạt lở)"],
        ["KB-3 (Sạt lở chậm)", "179 / 275 (65,1%)", "123 / 154 (79,9%)"],
        ["KB-4 (Sạt lở nhanh)", "64 / 342 (18,7%)", "35 / 159 (22,0%)"],
        ["KB-6 (Thảm họa phức hợp)", "38 / 235 (16,2%)", "0 / 3 (0,0% - Nút phát bị phá hủy sớm)"]
    ]
    
    for i, row in enumerate(data_t2):
        bg = "F4F8FA" if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row):
            cell = t2.cell(i+1, j)
            cell.text = val
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(9.5)
                if j == 0 or (j > 0 and "%" in val):
                    r.font.bold = True

    add_body_p("Bảng 2: Tỷ lệ phân phát thành công các bản tin cảnh báo sự kiện theo mức cờ ưu tiên.", italic_prefix="Ghi chú: ")

    add_heading_2("4.3. Phân tích chi tiết từng kịch bản thực nghiệm")
    add_body_p(
        "Trong kịch bản cơ sở, kênh truyền không xảy ra hiện tượng hủy gói ngẫu nhiên. Mạng đạt PDR tổng thể 97,8% với 350/358 gói tin được chuyển giao thành công về Gateway. Đáng chú ý, toàn bộ 4 nút cận Gateway (S1 đến S4) đạt PDR tuyệt đối 100%. Sự thiếu hụt 8 gói tin chỉ xuất hiện tại các nút xa (S5 đến S10, mỗi nút thiếu 1–2 gói). Phân tích nhật ký sự kiện khẳng định đây là các gói tin cuối cùng được sinh ra sát thời điểm t = 1000 s và vẫn đang nằm trong bộ đệm chuyển tiếp của các nút trung gian khi phiên mô phỏng dừng, không phải do mất gói trên kênh. Độ trễ truyền tin tăng tuyến tính theo số chặng: Nút S1 chỉ mất 0,06 s, trong khi nút S10 mất trung bình 32,50 s (tương ứng khoảng 3,6 s cho mỗi bước nhảy chuyển tiếp). Độ trễ trung bình toàn mạng đạt 16,10 s.",
        bold_prefix="Kịch bản KB-0 (Baseline): "
    )
    add_body_p(
        "Dưới tác động của mưa vừa (KB-1), PDR toàn mạng giảm xuống 91,7% với 73 bản sao bị hủy. Mức suy giảm PDR tích lũy rõ rệt theo khoảng cách: S1 duy trì 100%, trong khi S8, S9 và S10 giảm lần lượt còn 88,9%, 80,6% và 73,0%. Độ trễ trung bình tăng gấp đôi lên 31,89 s do các nút hạ lưu phải chờ xử lý các bản sao đến sau. Tuy nhiên, nhờ cơ chế phát lặp 2 bản sao cho cờ ưu tiên, toàn bộ 44/44 gói tin cảnh báo mưa lớn (FLAG = 100) đều được chuyển giao thành công về Gateway (đạt 100%). Khi cường độ mưa tăng lên mức bão (KB-2, suy hao 25%), PDR toàn mạng giảm còn 85,1% với 141 bản sao bị hủy, và tỷ lệ chuyển giao gói FLAG 100 đạt 68,9%.",
        bold_prefix="Kịch bản KB-1 & KB-2 (Suy hao do mưa): "
    )
    add_body_p(
        "Khi sự kiện sạt lở kích hoạt, tổng số gói tin sinh ra tăng vọt lên 949 gói (KB-3) và 1028 gói (KB-4) – gấp gần 3 lần kịch bản cơ sở, xác nhận cơ chế thích ứng hướng sự kiện đã vận hành chính xác. Với sạt lở chậm (KB-3), PDR đạt 71,4%; trong đó gói khẩn cấp (FLAG = 255) đạt tỷ lệ tới nơi 79,9% (123/154 gói) nhờ cơ chế phát lặp 3 bản sao. Ngược lại, trong kịch bản sạt lở nhanh (KB-4), suy hao kênh tức thời lên tới 80–85% làm PDR giảm còn 45,1%. Hệ thống ghi nhận 10 lần kích hoạt phát hiện im lặng (DETECT), 9 lần phát yêu cầu sửa đường (REPAIR_TX) và hoàn tác tuyến thành công (REVERT) khi kênh hồi phục.",
        bold_prefix="Kịch bản KB-3 & KB-4 (Sạt lở đất): "
    )
    add_body_p(
        "Kịch bản KB-5 kiểm chứng độc lập khả năng chịu lỗi phần cứng: Khi nút trung gian S3 bị ngắt hoạt động hoàn toàn lúc t = 90 s, cơ chế chuyển tuyến nhanh Sender Fast-Failover tại S4 lập tức kích hoạt lúc t = 93,3 s (chỉ sau 3,3 s kể từ sự cố), chuyển tuyến trực tiếp sang S2 ở cự ly 100 m. Bộ lọc Receiver Grandchild Acceptance tại S2 tiếp nhận thông suốt luồng dữ liệu. PDR toàn mạng duy trì ở mức cao ấn tượng 93,9% (chỉ giảm 3,9% so với điều kiện không có lỗi). Độ trễ trung bình toàn mạng giảm từ 16,10 s xuống 13,57 s do tuyến đường nối vòng đã bỏ qua một bước nhảy trung gian.",
        bold_prefix="Kịch bản KB-5 (Khả năng chịu lỗi hỏng nút S3): "
    )
    add_body_p(
        "KB-6 tái hiện tình huống khắc nghiệt nhất: Mưa kéo dài, sạt lở nhanh tại S5 (t = 73 s) và nút S5 bị đất đá vùi lấp hoàn toàn lúc t = 93 s. Sau sự cố, nút S6 thiết lập tuyến vòng sang S4 thành công lúc t = 107,8 s (chậm 11,8 s do suy hao kênh). Do liên kết nối vòng 100 m nằm trọn trong vùng sạt lở và chịu mức phạt suy hao lên tới 95%, PDR toàn mạng giảm xuống 31,8%. Ba nút gần trạm (S1–S3) vẫn đạt PDR 75–100%, trong khi các nút phía sau điểm sạt lở chịu tổn thất nặng nề.",
        bold_prefix="Kịch bản KB-6 (Thảm họa phức hợp): "
    )

    # --- 5. THẢO LUẬN ---
    add_heading_1("5. THẢO LUẬN")
    add_body_p(
        "Kết quả thực nghiệm mô phỏng cung cấp những hiểu biết sâu sắc về động học truyền thông của mạng cảm biến LoRa đa chặng trong điều kiện thiên tai khắc nghiệt, đồng thời làm rõ ba vấn đề kỹ thuật trọng tâm:"
    )
    add_body_p(
        "Thứ nhất, tính đánh đổi giữa cấu trúc chuỗi đa chặng và sự phân rã độ tin cậy theo khoảng cách. Do đặc thù topo tuyến tính, xác suất chuyển phát thành công của một gói tin qua k chặng độc lập tuân theo phân phối Bernoulli tích lũy: P_end-to-end = ∏ (1 - p_i^N). Trong điều kiện mưa vừa (KB-1, p = 12%), với N = 2 bản sao, xác suất thành công của mỗi chặng đạt 1 - (0,12)² = 98,56%. Sau 10 chặng truyền từ S10 về Gateway, xác suất tích lũy lý thuyết đạt (0,9856)¹⁰ ≈ 86,4%, hoàn toàn khớp với kết quả thực nghiệm 80,6–88,9% tại các nút cuối. Điều này khẳng định rằng trong mạng đa chặng không ACK, cơ chế phát lặp mù là bắt buộc để duy trì kết nối cho các nút ở xa trạm cổng."
    )
    add_body_p(
        "Thứ hai, hiện tượng 'độ trễ trung bình giảm giả tạo' trong điều kiện suy hao nặng. Một quan sát thoạt nhìn nghịch lý là độ trễ trung bình trong KB-3 (6,91 s) và KB-4 (4,69 s) lại thấp hơn nhiều so với kịch bản cơ sở KB-0 (16,10 s). Tuy nhiên, phân tích sâu cho thấy nguyên nhân không phải do mạng truyền nhanh hơn, mà do hầu hết các gói tin từ các nút xa (S6 đến S10 – vốn có độ trễ tích lũy từ 30–60 s) đã bị hủy trên kênh truyền do sạt lở. Tập gói tin đến được Gateway chủ yếu xuất phát từ các nút cận trạm (S1 đến S4) với độ trễ chỉ dưới 2 s, làm kéo giá trị trung bình xuống thấp. Vì vậy, trong các bài báo khoa học về mạng WSN thiên tai, độ trễ bắt buộc phải được phân tích đồng thời với PDR phân bố theo từng nút để tránh đưa ra những kết luận sai lệch."
    )
    add_body_p(
        "Thứ ba, hiệu quả và giới hạn của cơ chế tự phục hồi phân tán. Việc kết hợp Sender Fast-Failover và Receiver Grandchild Acceptance trong KB-5 đã chứng minh tính ưu việt vượt trội so với các cơ chế định tuyến truyền thống: Khôi phục kết nối chỉ sau 3,3 s mà không tốn bất kỳ bản tin bắt tay nào. Tuy nhiên, hạn chế cố hữu của topo tuyến tính là chỉ có khả năng nối vòng qua một nút hỏng đơn lẻ (khoảng cách 100 m). Nếu hai nút liền kề cùng bị phá hủy (khoảng cách 150 m), vượt quá bán kính phủ sóng của LoRa, mạng sẽ rơi vào trạng thái chia cắt hoàn toàn ([PARTITION])."
    )
    add_body_p(
        "Các giả định và hạn chế của nghiên cứu cần được ghi nhận minh bạch: (1) Kênh truyền trong CupCarbon áp dụng mô hình mất gói xác suất độc lập theo bản sao, chưa xét đến hiện tượng fading tương quan thời gian và đa đường (multipath); (2) Giả định các nút chuyển tiếp có lịch thức dậy đồng bộ cục bộ để tiếp nhận gói tin đệm; và (3) Kết quả nghiên cứu mới dừng ở quy mô mô phỏng sự kiện rời rạc, đòi hỏi các bước thực nghiệm thực địa trên phần cứng nhúng để kiểm chứng ảnh hưởng của vi khí hậu và tán cây rừng rậm."
    )

    # --- 6. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN ---
    add_heading_1("6. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN")
    add_body_p(
        "Nghiên cứu đã đề xuất, phát triển và đánh giá toàn diện một giao thức truyền thông LoRa P2P đa chặng thích ứng hướng sự kiện phục vụ hệ thống cảnh báo sớm sạt lở đất. Bằng cách tập trung vào tối ưu hóa thuật toán phần mềm, nghiên cứu đã khai thác hiệu quả các dữ liệu đầu vào từ cụm cảm biến chi phí thấp (độ ẩm đất điện dung, MPU-6050 và ngắt cứng SW-420) để xây dựng công thức tính toán chỉ số nguy cơ sạt lở đất đa biến phi tuyến (RI). Giao thức tích hợp thành công cơ chế ngủ sâu thích ứng ba cấp, nén dữ liệu Delta, phát lặp mù khử trùng lặp không ACK và giải thuật chuyển tuyến tự phục hồi phân tán."
    )
    add_body_p(
        "Kết quả thực nghiệm trên nền tảng CupCarbon qua bảy kịch bản chuẩn mực chứng minh mạng hoạt động cực kỳ tin cậy trong điều kiện bình thường (PDR 97,8%, trễ 16,10 s), chống chịu tốt trước suy hao do mưa (PDR 85,1–91,7%), duy trì tỷ lệ chuyển giao bản tin cảnh báo trọng yếu đạt 100% trong mưa lớn và phục hồi mạng hoàn hảo khi có nút trung gian bị phá hủy (PDR 93,9%). Nghiên cứu cung cấp cơ sở lý thuyết và bằng chứng thực nghiệm vững chắc cho việc triển khai các mạng giám sát thiên tai chi phí thấp tại các vùng miền núi khó khăn."
    )
    add_body_p(
        "Hướng phát triển tiếp theo của đề tài tập trung vào ba nhiệm vụ trọng tâm: (1) Thiết kế cơ chế định tuyến đa đường thích ứng (Mesh/Multi-path) để khắc phục hiện tượng chia cắt mạng khi nhiều nút liền kề bị phá hủy; (2) Tích hợp thuật toán học máy phân tán tại biên (TinyML) trên vi điều khiển nút để tự động nhận dạng sớm các pha trượt lở phức tạp; và (3) Chế tạo mô hình phần cứng thực nghiệm, tiến hành thử nghiệm thực địa tại một sườn dốc xung yếu ở miền núi phía Bắc Việt Nam nhằm kiểm chứng và hiệu chuẩn mô hình mô phỏng trong điều kiện thời tiết thực tế."
    )

    # --- TÀI LIỆU THAM KHẢO ---
    add_heading_1("TÀI LIỆU THAM KHẢO")
    
    refs = [
        "[1] V. Ranasinghe, C. Higgins, A. Le, and T. Fernando, \"Rapid and Resilient LoRa Leap: A Novel Multi-Hop Architecture for Decentralised Earthquake Early Warning Systems,\" Sensors, vol. 24, no. 18, Art. no. 5960, Sep. 2024. https://doi.org/10.3390/s24185960",
        "[2] C. Wang, W. Guo, K. Yang, X. Wang, and Q. Meng, \"Real-Time Monitoring System of Landslide Based on LoRa Architecture,\" Frontiers in Earth Science, vol. 10, Art. no. 899509, Jun. 2022. https://doi.org/10.3389/feart.2022.899509",
        "[3] A. Joshi, D. P. Kanungo, and R. K. Panigrahi, \"WSN-Based Smart Landslide Monitoring Device,\" IEEE Transactions on Instrumentation and Measurement, vol. 72, pp. 1–12, 2023. https://doi.org/10.1109/TIM.2023.3269746",
        "[4] M. Chu, J. A. Coe, D. P. Mason, and C. E. Smith, \"SitkaNet: A low-cost, distributed sensor network for landslide monitoring and study,\" HardwareX, vol. 9, Art. no. e00191, Apr. 2021. https://doi.org/10.1016/j.ohx.2021.e00191",
        "[5] M. Ragnoli, M. Scarsella, A. Leoni, G. Ferri, and V. Stornelli, \"Wireless Sensor Network-Based Rockfall and Landslide Monitoring Systems: A Review,\" Sensors, vol. 23, no. 16, Art. no. 7278, Aug. 2023. https://doi.org/10.3390/s23167278",
        "[6] K. Mehdi, M. Lounis, A. Bounceur, and T. Kechadi, \"CupCarbon: A Multi-Agent and Discrete Event Wireless Sensor Network Design and Simulation Tool,\" in Proc. 7th International Conference on Simulation Tools and Techniques (SIMUTOOLS), Lisbon, Portugal, 2014, pp. 1–6. https://doi.org/10.4108/icst.simutools.2014.254811",
        "[7] C. López-Pavón, S. Sendra, and J. F. Valenzuela-Valdés, \"Evaluation of CupCarbon Network Simulator for Wireless Sensor Networks,\" Network Protocols and Algorithms, vol. 10, no. 2, pp. 1–27, 2018. https://doi.org/10.5296/npa.v10i2.13201"
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
        run.font.size = Pt(10.5)

    filename = "Bao_Cao_Khoa_Hoc_LoRa_Landslide.docx"
    doc.save(filename)
    print(f"File successfully created: {filename}")

if __name__ == "__main__":
    build_paper()
