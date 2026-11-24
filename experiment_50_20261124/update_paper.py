"""Generate the final paper directly from the frozen 50-seed summary."""
from pathlib import Path
import json
import re
import shutil
from run_experiment import OUT

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'output/revision_refs_20261124/main_revised.tex'
DEST=ROOT/'output/paper_50seeds_20261124'

def main():
    data=json.loads((OUT/'paper_tables.json').read_text(encoding='utf-8'))
    G=data['groups']; C=data['comparisons']
    def g(sc,name='FULL'):return G[f'{sc}/{name}']
    def f(v):return f'{v:.2f}'.replace('.',',')
    def k(sc,name='FULL'):return str(g(sc,name)['count'])+'/50'
    def tex(name):return r'\texttt{'+name.replace('_',r'\_')+'}'
    e=g(3)['energy']; ne=g(3,'NO_ESCALATE')['energy']; saving=e-ne; pct=saving/e*100
    bp=C['5/NO_BYPASS']['pdr']; lo,hi=bp['ci95']
    s=SOURCE.read_text(encoding='utf-8')
    s=s.replace(r'\usepackage[utf8]{inputenc}',r'\usepackage{fontspec}'+ '\n' +r'\setmainfont{Times New Roman}'+ '\n' +r'\setsansfont{Arial}'+ '\n' +r'\setmonofont{Courier New}').replace(r'\usepackage[T5]{fontenc}','')
    def paragraph(prefix,new):
        nonlocal s
        a=s.index(prefix); b=s.find('\n\n',a)
        assert b>=0
        s=s[:a]+new+s[b:]
    def table(label,new):
        nonlocal s
        at=s.index(r'\label{'+label+'}')
        a=s.rfind(r'\begin{table',0,at)
        end=r'\end{table*}' if s[a:].startswith(r'\begin{table*}') else r'\end{table}'
        b=s.index(end,at)+len(end)
        s=s[:a]+new+s[b:]

    a=s.index(r'\begin{abstract}');b=s.index(r'\end{abstract}',a)
    abstract=rf'''Bài báo đánh giá khả năng đưa cảnh báo sạt lở đất đầu tiên tới gateway trong 30~s qua chuỗi mười nút cảm biến LoRa điểm-điểm. Nghiên cứu kết hợp dữ liệu vết CupCarbon với 2.450 lần chạy Python V3, gồm 49 cặp cấu hình--kịch bản trên 50 hạt giống ghép cặp. Hai đối chứng dùng chu kỳ cố định 5~s hoặc 30~s, một bản sao mỗi chặng và không khôi phục tuyến. Ở kịch bản sạt lở chậm, giao thức đầy đủ đạt {k(3)} sự kiện đúng hạn, so với {k(3,'BASE_5')} và {k(3,'BASE_30')} của hai đối chứng. Cận dưới Wilson 95\% danh nghĩa của giao thức đầy đủ là {f(g(3)['wilson'][0]*100)}\%, vượt mục tiêu thiết kế 90\%; phép đánh giá vẫn mang tính thăm dò. Khi bỏ truyền lặp, số sự kiện đúng hạn còn {k(3,'NO_REPEAT')}. Tắt nâng mức tại relay giữ {k(3,'NO_ESCALATE')} và giảm {f(pct)}\% tải vô tuyến mô hình hóa trung bình tại nút bận nhất. Khi S3 hỏng, vòng tránh tăng PDR trung bình {f(bp['mean'])} điểm phần trăm so với cấu hình tắt vòng tránh (khoảng tin cậy ghép cặp 95\%: {f(lo)}--{f(hi)}). Khi liên kết suy giảm đột ngột hoặc nguồn cảnh báo hỏng, giao thức đầy đủ chỉ đạt lần lượt {k(4)} và {k(6)}; các kết quả cho thấy phạm vi cải thiện và giới hạn chịu lỗi của thiết kế.'''
    s=s[:a]+r'\begin{abstract}'+'\n'+abstract+'\n'+s[b:]
    s=s.replace('1.225 lần chạy ghép cặp seeds','2.450 lần chạy trên các hạt giống ghép cặp')
    a=s.index(r'    \item \textbf{Đánh giá đóng góp theo quy tắc:}')
    b=s.index('\n',a)
    s=s[:a]+rf'    \item \textbf{{Đánh giá tổng thể và theo quy tắc:}} Ở SC-3, \texttt{{FULL}} đạt {k(3)}, so với {k(3,"BASE_5")} và {k(3,"BASE_30")} của hai đối chứng. Bỏ truyền lặp làm kết quả giảm xuống {k(3,"NO_REPEAT")}; vòng tránh tăng PDR ở SC-5 thêm {f(bp["mean"])} điểm phần trăm so với tắt vòng tránh.'+s[b:]
    paragraph(r'Lô mô phỏng \texttt{LORA\_STRESS}',r'''Lô mô phỏng \texttt{LORA\_STRESS} trên V3 gồm 49 cặp cấu hình--kịch bản, mỗi cặp chạy với 50 hạt giống ghép cặp (2.450 lần chạy). Thiết kế ban đầu dùng 30 hạt giống, được mở rộng qua đợt trung gian 35 rồi tới 50 sau khi xem xét kết quả ban đầu. Cỡ mẫu cuối được chốt trước đợt chạy bổ sung, không dừng theo mức thành công. Vì vậy, các khoảng tin cậy 95\% được báo cáo là danh nghĩa và việc đối chiếu mục tiêu 90\% mang tính thăm dò. Đợt cuối chạy lại toàn bộ 49 cặp với các hạt giống 1--50; các lượt lặp lại phục vụ đối chiếu phiên bản không được tính thành quan sát độc lập. Lịch sử mở rộng chỉ mô tả tại đây; mọi kết quả V3 dưới đây sử dụng bộ 50 hạt giống.''')
    paragraph(r'Các cấu hình \texttt{FULL}, \texttt{FIXED\_5}',r'''Các cấu hình \texttt{BASE\_5}, \texttt{BASE\_30}, \texttt{FULL}, \texttt{FIXED\_5}, \texttt{FIXED\_30} và \texttt{NO\_REPEAT} được chạy trên cả bảy kịch bản. \texttt{NO\_ESCALATE} được chạy ở SC-3, SC-4 và SC-6. \texttt{NO\_BYPASS} và \texttt{ORACLE\_BYPASS} được chạy ở SC-5 và SC-6; cấu hình oracle dùng thông tin biết trước về sự cố làm mốc tham chiếu. Số cấu hình ở SC-0--SC-6 lần lượt là 6, 6, 6, 7, 7, 8 và 9. Các baseline tắt cả phát hiện mất liên lạc và phát bản tin điều khiển, ngoài việc tắt nâng mức và vòng tránh.''')
    needle=r'Khu vực dự kiến triển khai tại miền Bắc Việt Nam sử dụng băng tần LPWAN'
    a=s.index(needle);b=s.index('Các thông số vô tuyến gồm',a)
    s=s[:a]+r'Băng tần dự kiến triển khai là 920--923~MHz~\cite{r13}; metadata của đợt V3 cuối ghi tần số danh định 920~MHz. Manifest các đợt trước ghi 868~MHz. Tần số sóng mang không tham gia tính airtime hoặc xác suất mất gói trong code V3 hiện tại, nên việc sửa metadata không thay đổi động lực mô phỏng và không tương đương với hiệu chuẩn truyền sóng ở 920~MHz. '+s[b:]
    # Add explicit engine differences, avoiding an implied shared MAC implementation.
    needle=r'Mô hình V3 dùng ngưỡng im lặng 90~s.'
    s=s.replace(needle,r'V3 loại trùng bằng tập các cặp \texttt{(SRC, SEQ)} đã nhận, cho phép nhận một gói mới đến không đúng thứ tự; SenScript dùng ngưỡng số thứ tự theo nguồn như giả mã ban đầu. V3 dùng một bản sao cho cờ 0, hai cho cờ 100 và ba cho cờ 255/150/200; các baseline và \texttt{NO\_REPEAT} dùng một bản sao. Trễ 100--400~ms trong V3 áp dụng giữa các bản sao; V3 không dùng khoảng nghỉ 150--250~ms sau cụm như SenScript. Các khác biệt này được giữ cố định giữa những cấu hình so sánh trong cùng engine. '+needle)
    # Event-oriented protocol; simulation-only machinery is explicit.
    s=s.replace(r'và $L_{\mathrm{seq}}[1\ldots 10] \leftarrow 0$.',r'và bộ nhớ loại trùng rỗng (V3) hoặc $L_{\mathrm{seq}}[1\ldots 10] \leftarrow 0$ (SenScript).')
    s=s.replace(r'\textbf{Trong khi} nút cảm biến còn hoạt động:',r'\textbf{Xử lý theo sự kiện} khi nút còn hoạt động; Bước~3--5 chỉ thực hiện khi đến hạn lấy mẫu, Bước~6--8 khi có gói nhận, Bước~9 khi đến hạn kiểm tra im lặng:')
    s=s.replace('Đọc đồng hồ mô phỏng. Nếu đã đến thời điểm sự cố được lập lịch cho nút này, ghi nhận', 'Môi trường mô phỏng đọc đồng hồ và gây sự cố theo lịch; nếu nút này hỏng, ghi nhận')
    s=s.replace('Thu thập hoặc sinh giá trị trạng thái theo~\\eqref{eq:sensor-state} và các ngắt ngoại vi.', 'Khi đến hạn lấy mẫu, sinh trạng thái theo~\\eqref{eq:sensor-state}; ngắt cảm biến phần cứng không được mô hình hóa trong V3.')
    s=s.replace('Áp dụng~\\eqref{eq:pdrop} và xử lý', 'Môi trường SenScript áp dụng~\\eqref{eq:pdrop}; V3 áp dụng kênh, airtime và xung đột khi truyền. Nút xử lý')
    s=s.replace(r'Với mỗi gói dữ liệu hợp lệ, loại bỏ dưới dạng \texttt{DUP} nếu $\texttt{SEQ} \leq L_{\mathrm{seq}}[\texttt{SRC}]$. Ngược lại, cập nhật $L_{\mathrm{seq}}[\texttt{SRC}] \leftarrow \texttt{SEQ}$ và chuyển tiếp đúng số bản sao quy định.',r'Với mỗi gói hợp lệ, kiểm tra bộ nhớ loại trùng: V3 loại gói có cặp \texttt{(SRC, SEQ)} đã nhận; SenScript loại nếu $\texttt{SEQ} \leq L_{\mathrm{seq}}[\texttt{SRC}]$. Nếu mới, cập nhật bộ nhớ tương ứng và chuyển tiếp theo số bản sao quy định.')
    s=s.replace('Chờ đến chu kỳ lấy mẫu kế tiếp rồi lặp lại.', 'Lập lịch sự kiện kế tiếp. Trong V3, tiếp tục xử lý thu/phát và kiểm tra im lặng trong thời gian chờ lấy mẫu; không chặn chuyển tiếp theo chu kỳ cảm biến.')
    # Sample-size and figure reference updates outside historical methodology.
    s=s.replace('trên 35 hạt giống','trên 50 hạt giống').replace('Trên 35 hạt giống','Trên 50 hạt giống')
    s=s.replace('Hình~4',r'Hình~\ref{F4}')
    s=s.replace(r'\includegraphics[width=\columnwidth]{figures/fig0.png}',r'\includegraphics[width=0.95\textwidth]{figures/fig0.png}')
    paragraph('Kết quả mô phỏng ghép cặp hạt giống trên Python V3',rf'''Kết quả ghép cặp trên V3 (Bảng~\ref{{T5}}, Hình~\ref{{F4}}) và tải vô tuyến (Bảng~\ref{{T7}}) cho phép đánh giá từng thành phần. Ở SC-3, \texttt{{FULL}} đạt {k(3)} sự kiện đúng hạn (Wilson 95\% danh nghĩa: {f(g(3)['wilson'][0]*100)}--100,00\%). Bỏ truyền lặp làm kết quả giảm xuống {k(3,'NO_REPEAT')}; tác động này áp dụng cho kịch bản và tập hạt giống được khảo sát.''')
    paragraph('So sánh với các cấu hình chu kỳ cố định',rf'''Ở SC-3, \texttt{{FIXED\_30}} đạt {k(3,'FIXED_30')}, còn \texttt{{FIXED\_5}} đạt {k(3,'FIXED_5')} (cận dưới Wilson 95\%: {f(g(3,'FIXED_5')['wilson'][0]*100)}\%). Tải đỉnh trung bình của \texttt{{FIXED\_5}} là {f(g(3,'FIXED_5')['energy'])} giây phát tương đương, so với {f(e)} của \texttt{{FULL}}. Chu kỳ 30~s trùng thời hạn cảnh báo và pha lấy mẫu giới hạn 0--5~s cần được xem xét khi diễn giải kết quả.''')
    paragraph('Ngược lại, cơ chế nâng mức chu kỳ lấy mẫu',rf'''Tắt nâng mức tại relay (Bước~8) giữ SC-3 ở {k(3,'NO_ESCALATE')} sự kiện đúng hạn, đồng thời ghi nhận {k(4,'NO_ESCALATE')} ở SC-4 và {k(6,'NO_ESCALATE')} ở SC-6, so với {k(4)} và {k(6)} của \texttt{{FULL}}. Tại SC-3, tải đỉnh trung bình giảm từ {f(e)} xuống {f(ne)}, tương ứng {f(saving)} giây phát tương đương ({f(pct)}\%). Đây là mức chênh lệch quan sát trên các hạt giống ghép cặp.''')
    paragraph('Cuối cùng, các kịch bản khắc nghiệt',rf'''Khi liên kết suy giảm đột ngột (SC-4) hoặc nguồn S5 hỏng (SC-6), không cấu hình được thử nghiệm nào đạt tỷ lệ quan sát 90\% trong thời hạn 30~s. \texttt{{FULL}} đạt lần lượt {k(4)} và {k(6)}. Các lần chạy đơn lẻ CupCarbon cũng ghi nhận cảnh báo trễ ở SC-4 (122,863~s) và SC-6 (57,923~s), trong khi SC-3 đạt 27,863~s (Bảng~\ref{{T4}}).''')
    names=['BASE_5','BASE_30','FULL','FIXED_5','FIXED_30','NO_REPEAT','NO_ESCALATE','NO_BYPASS','ORACLE_BYPASS']
    rows=[]
    for name in names:
        vals=[k(sc,name) if f'{sc}/{name}' in G else 'NR' for sc in (3,4,6)]
        rows.append(tex(name)+' & '+' & '.join(vals)+r' \\')
    table('T5',r'''\begin{table}[!t]
\caption{Sự kiện cảnh báo đúng hạn trên 50 hạt giống V3}
\label{T5}\centering\footnotesize
\begin{tabular}{lccc}\toprule
Cấu hình & SC-3 & SC-4 & SC-6 \\ \midrule
'''+ '\n'.join(rows)+r'''
\bottomrule\end{tabular}
\par\smallskip\raggedright NR: không chạy cặp cấu hình--kịch bản. Mỗi ô là số sự kiện đạt thời hạn 30~s trên 50 hạt giống.
\end{table}''')
    rows=[]
    for name in names:
        rows.append(tex(name)+' & '+' & '.join(f(g(sc,name)['energy']) if f'{sc}/{name}' in G else 'NR' for sc in range(7))+r' \\')
    table('T7',r'''\begin{table*}[!t]
\caption{Tải vô tuyến cực đại trung bình trên 50 hạt giống (giây phát tương đương)}
\label{T7}\centering\footnotesize
\begin{tabular}{lccccccc}\toprule
Cấu hình & SC-0 & SC-1 & SC-2 & SC-3 & SC-4 & SC-5 & SC-6 \\ \midrule
'''+ '\n'.join(rows)+r'''
\bottomrule\end{tabular}
\par\smallskip\raggedright Trung bình qua hạt giống của $\max_{i\in\{1,\ldots,10\}}(\mathrm{TX}_i+0{,}4\mathrm{RX}_i)$. NR: không chạy.
\end{table*}''')
    # Direct before/after section with paired inference, no unmeasured baseline claims.
    rows=[]
    for sc in range(7):
        rows.append(f'SC-{sc} & '+' & '.join(f(g(sc,n)['pdr']) for n in ('BASE_5','BASE_30','FULL'))+r' \\')
    direct=r'''\subsection{So sánh trực tiếp trước và sau áp dụng thuật toán}
Trước--sau được hiểu là đối chiếu cấu hình trên cùng kịch bản và hạt giống. Bảng~\ref{T5} so sánh thời hạn cảnh báo, Bảng~\ref{TbaselinePDR} so sánh PDR và Bảng~\ref{T7} cho tải vô tuyến.

'''
    direct+=rf'''Tại SC-3, \texttt{{FULL}} đạt {k(3)}, so với {k(3,'BASE_5')} của \texttt{{BASE\_5}} và {k(3,'BASE_30')} của \texttt{{BASE\_30}}. '''
    for name in ('BASE_5','BASE_30'):
        c=C[f'3/{name}']['on_time'];low,high=c['ci95']
        direct+=rf'''So với {tex(name)}, mức tăng là {f(c['mean']*100)} điểm phần trăm (khoảng tin cậy bootstrap ghép cặp 95\%: {f(low*100)}--{f(high*100)}); có {c['full_only']} hạt giống chỉ \texttt{{FULL}} đạt hạn và {c['other_only']} hạt giống chỉ đối chứng đạt hạn. '''
    direct+=rf'''Tải đỉnh trung bình tại SC-3 là {f(e)} với \texttt{{FULL}}, {f(g(3,'BASE_5')['energy'])} với \texttt{{BASE\_5}} và {f(g(3,'BASE_30')['energy'])} với \texttt{{BASE\_30}}; do đó lợi ích về thời hạn cần được xem cùng chi phí vô tuyến.

Ở SC-5, PDR của \texttt{{FULL}} là {f(g(5)['pdr'])}\%, so với {f(g(5,'BASE_5')['pdr'])}\% và {f(g(5,'BASE_30')['pdr'])}\% của hai đối chứng. Khi không có sự cố hoặc khi cảnh báo chịu suy giảm đột ngột, mức cải thiện không đồng đều giữa cấu hình và chỉ số; bài báo không giả định \texttt{{FULL}} luôn tốt hơn đối chứng.

'''
    direct+=rf'''Cụ thể, PDR của \texttt{{FULL}} tại SC-0 là {f(g(0)['pdr'])}\%, thấp hơn {f(g(0,'BASE_5')['pdr'])}\% và {f(g(0,'BASE_30')['pdr'])}\% của hai đối chứng; tại SC-4, các giá trị tương ứng là {f(g(4)['pdr'])}\%, {f(g(4,'BASE_5')['pdr'])}\% và {f(g(4,'BASE_30')['pdr'])}\%. Ở SC-3, lợi ích rõ nhất nằm ở cảnh báo đúng hạn, trong khi chênh lệch PDR toàn bộ dữ liệu so với hai baseline nhỏ và các khoảng tin cậy ghép cặp đều chứa 0.

'''
    direct+=r'''\begin{table}[!t]
\caption{PDR dữ liệu trung bình trước--sau trên 50 hạt giống (\%)}
\label{TbaselinePDR}\centering\footnotesize
\begin{tabular}{lccc}\toprule
Kịch bản & \texttt{BASE\_5} & \texttt{BASE\_30} & \texttt{FULL} \\ \midrule
'''+ '\n'.join(rows)+r'''
\bottomrule\end{tabular}
\end{table}

'''
    s=s.replace(r'\subsection{Độ tin cậy và thời hạn cảnh báo}',direct+r'\subsection{Độ tin cậy và thời hạn cảnh báo}',1)
    paragraph('Ở SC-3, việc loại bỏ cơ chế lặp gói tin',rf'''Ở SC-3, \texttt{{FULL}} và \texttt{{NO\_ESCALATE}} đạt {k(3)}, còn \texttt{{NO\_REPEAT}} đạt {k(3,'NO_REPEAT')}. Ở SC-5, PDR trung bình tăng từ {f(g(5,'NO_BYPASS')['pdr'])}\% khi tắt vòng tránh lên {f(g(5)['pdr'])}\% với \texttt{{FULL}}. Trên 50 cặp ghép, mức tăng là {f(bp['mean'])} điểm phần trăm (khoảng tin cậy $t$ ghép cặp 95\%: {f(lo)}--{f(hi)}). Ở SC-6, S5 hỏng trước thời hạn 10~s; \texttt{{FULL}} và \texttt{{NO\_BYPASS}} đạt lần lượt {k(6)} và {k(6,'NO_BYPASS')}. Khôi phục tuyến không thay thế được nguồn đã ngừng sinh cảnh báo.''')
    a=s.index('Trên 50 hạt giống ở SC-3, tải đỉnh trung bình');b=s.index('\n\n',a)
    s=s[:a]+rf'Trên 50 hạt giống ở SC-3, tải đỉnh trung bình giảm từ {f(e)} ở \texttt{{FULL}} xuống {f(ne)} ở \texttt{{NO\_ESCALATE}}, tiết kiệm {f(saving)} giây phát tương đương ({f(pct)}\%) và giữ kết quả {k(3)}. Thời gian phát cực đại trung bình tương ứng là {f(g(3)["tx_max"])}~s và {f(g(3,"NO_ESCALATE")["tx_max"])}~s.'+s[b:]
    a=s.index(r'\section{Kết luận}');b=s.index(r'\begin{thebibliography}',a)
    s=s[:a]+rf'''\section{{Kết luận}}

Trên 50 hạt giống ghép cặp, giao thức đầy đủ đạt {k(3)} sự kiện cảnh báo đúng hạn ở kịch bản sạt lở chậm, so với {k(3,'BASE_5')} và {k(3,'BASE_30')} của hai đối chứng đa chặng cố định. Cận dưới Wilson 95\% danh nghĩa là {f(g(3)['wilson'][0]*100)}\%; việc đối chiếu mục tiêu 90\% vẫn mang tính thăm dò. Bỏ truyền lặp làm kết quả giảm xuống {k(3,'NO_REPEAT')}; tắt nâng mức tại relay giữ {k(3,'NO_ESCALATE')} và giảm {f(pct)}\% tải đỉnh trung bình. Các kết quả này ủng hộ tiếp tục thử nghiệm truyền lặp và đánh giá lại nhu cầu nâng mức relay.

Khi S3 hỏng, vòng tránh tăng PDR thêm {f(bp['mean'])} điểm phần trăm so với cấu hình tắt vòng tránh. Tuy nhiên, \texttt{{FULL}} chỉ đạt {k(4)} khi liên kết suy giảm đột ngột và {k(6)} khi nguồn cảnh báo cũng hỏng. Thiết kế chưa đáp ứng mục tiêu trong các điều kiện này. Thử nghiệm thực địa cần đo đặc tính liên kết 920--923~MHz trên sườn dốc và kiểm tra sự đánh đổi giữa thời hạn, phân phối dữ liệu và tải vô tuyến.

'''+s[b:]
    # Inference methods and exact scope of nominal confidence intervals.
    needle=r'Các cấu hình \texttt{BASE\_5}, \texttt{BASE\_30}, \texttt{FULL}'
    pos=s.index(needle)
    methods=r'''Với tỷ lệ đạt hạn, nhóm báo cáo Wilson hai phía 95\% danh nghĩa; tỷ lệ quan sát đạt 90\% và cận dưới Wilson đạt 90\% được phân biệt. Chênh lệch tỷ lệ giữa FULL và đối chứng dùng bootstrap ghép cặp 20.000 lần lấy lại mẫu theo hạt giống. Chênh lệch PDR dùng khoảng tin cậy $t$ ghép cặp với 49 bậc tự do. Các khoảng tin cậy là theo từng phép so sánh, chưa hiệu chỉnh nhiều phép so sánh. Những sự kiện không nhận được cảnh báo vẫn nằm trong mẫu số của tỷ lệ đạt hạn, không được gán độ trễ bằng 0.

'''
    s=s[:pos]+methods+s[pos:]
    DEST.mkdir(parents=True,exist_ok=True)
    (DEST/'figures').mkdir(exist_ok=True)
    for n in (1,2,3):shutil.copy2(Path(r'C:\Users\nguye\Downloads')/f'fig{n}.png',DEST/'figures'/f'fig{n}.png')
    shutil.copy2(ROOT/'output/figures/data_processing_ieee/data_processing_ieee_concise.png',DEST/'figures/fig0.png')
    shutil.copy2(OUT/'figures/fig4.png',DEST/'figures/fig4.png')
    shutil.copy2(OUT/'figures/baseline_comparison.png',DEST/'figures/baseline_comparison.png')
    assert '/35' not in s and '1.225' not in s
    assert not (set(re.findall(r'\\(?:ref|eqref)\{([^}]+)\}',s))-set(re.findall(r'\\label\{([^}]+)\}',s)))
    (DEST/'main.tex').write_text(s,encoding='utf-8')
    print(DEST)

if __name__=='__main__':main()
