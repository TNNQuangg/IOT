import sys
import os
import subprocess
import time
import datetime
import re

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SCENARIOS = [
    (0, "KB-0: Baseline (Thoi tiet dep, khong loi)", 1000.0),
    (1, "KB-1: Mua vua (W = 12%)", 1000.0),
    (2, "KB-2: Mua to (W = 25%)", 1000.0),
    (3, "KB-3: Sat lo dat cham (P_loss = 40-50%)", 1000.0),
    (4, "KB-4: Sat lo dat nhanh (P_loss = 80-85%)", 1000.0),
    (5, "KB-5: Nut 3 hong cung (T_fail = 90s)", 1000.0),
    (6, "KB-6: Tham hoa phuc hop (Mua + Sat lo + Nut 5 hong)", 1000.0),
]

LOG_FILE = "log.txt"

def parse_simulation_log(log_text):
    gen_packets = {}
    gw_packets = {}
    drops = {'RAIN': 0, 'LANDSLIDE': 0, 'BYPASS': 0, 'NONE': 0}
    events = []
    filtered_log_lines = []
    
    for line in log_text.splitlines():
        line_str = line.strip()
        # Keep all meaningful domain logs
        if any(tag in line_str for tag in ['[GEN]', '[TX]', '[RX]', '[DROP]', '[GW]', '[GATEWAY]',
                                           '[FAIL]', '[DETECT]', '[REPAIR_TX]', '[BYPASS_ON]', 
                                           '[CONFIRM]', '[REVERT]', '[SUMMARY]']):
            filtered_log_lines.append(line_str)
            
        if '[GEN]' in line_str:
            m = re.search(r't=\s*([\d\.]+)\s+node=\s*(\d+)\s+src=\s*(\d+)\s+seq=\s*([\d\.]+)', line_str)
            if m:
                t, node, src, seq = float(m.group(1)), int(m.group(2)), int(m.group(3)), float(m.group(4))
                if src not in gen_packets: gen_packets[src] = {}
                if seq not in gen_packets[src]: gen_packets[src][seq] = t
        elif '[GW]' in line_str:
            m = re.search(r't=\s*([\d\.]+)\s+src=\s*(\d+)\s+seq=\s*([\d\.]+).*?lat=\s*([\d\.]+)', line_str)
            if m:
                t, src, seq, lat = float(m.group(1)), int(m.group(2)), float(m.group(3)), float(m.group(4))
                if src not in gw_packets: gw_packets[src] = {}
                if seq not in gw_packets[src]: gw_packets[src][seq] = (t, lat)
        elif '[DROP]' in line_str:
            m = re.search(r'cause=\s*([A-Z_]+)', line_str)
            if m:
                cause = m.group(1)
                drops[cause] = drops.get(cause, 0) + 1
        elif any(k in line_str for k in ['[FAIL]', '[DETECT]', '[REPAIR_TX]', '[BYPASS_ON]', '[CONFIRM]', '[REVERT]']):
            clean = line_str.split(' - ')[-1] if ' - ' in line_str else line_str
            events.append(clean)

    # Compute stats
    node_stats = []
    total_gen = 0
    total_rx = 0
    all_lats = []
    
    for src in range(1, 11):
        g_cnt = len(gen_packets.get(src, {}))
        rx_dict = gw_packets.get(src, {})
        rx_cnt = len(rx_dict)
        total_gen += g_cnt
        total_rx += rx_cnt
        pdr = (rx_cnt / g_cnt * 100.0) if g_cnt > 0 else 0.0
        
        lats = [v[1] for v in rx_dict.values()]
        all_lats.extend(lats)
        avg_lat = sum(lats)/len(lats) if lats else 0.0
        min_lat = min(lats) if lats else 0.0
        max_lat = max(lats) if lats else 0.0
        node_stats.append((src, g_cnt, rx_cnt, pdr, avg_lat, min_lat, max_lat))
        
    tot_pdr = (total_rx / total_gen * 100.0) if total_gen > 0 else 0.0
    tot_avg_lat = sum(all_lats)/len(all_lats) if all_lats else 0.0
    
    return {
        'total_gen': total_gen,
        'total_rx': total_rx,
        'tot_pdr': tot_pdr,
        'tot_avg_lat': tot_avg_lat,
        'node_stats': node_stats,
        'drops': drops,
        'events': events,
        'filtered_log_lines': filtered_log_lines
    }

def format_analysis_report(sc, name, duration, stats):
    lines = []
    lines.append("="*80)
    lines.append(f"KICH BAN {sc}: {name}")
    lines.append(f"Thoi gian mo phong: {duration:.1f}s | Thoi diem chay: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("="*80)
    lines.append(f"{'SRC':<5} | {'GEN':<6} | {'GW_RX':<6} | {'PDR (%)':<9} | {'AVG LAT (s)':<12} | {'MIN LAT (s)':<12} | {'MAX LAT (s)':<12}")
    lines.append("-" * 80)
    
    for src, g_cnt, rx_cnt, pdr, avg_lat, min_lat, max_lat in stats['node_stats']:
        lines.append(f"S{src:<4} | {g_cnt:<6} | {rx_cnt:<6} | {pdr:>8.1f}% | {avg_lat:>11.2f} | {min_lat:>11.2f} | {max_lat:>11.2f}")
        
    lines.append("-" * 80)
    lines.append(f"{'TONG':<5} | {stats['total_gen']:<6} | {stats['total_rx']:<6} | {stats['tot_pdr']:>8.1f}% | {stats['tot_avg_lat']:>11.2f}")
    
    lines.append("\n* Thong ke mat goi (Drops):")
    active_drops = {k: v for k, v in stats['drops'].items() if v > 0 and k != 'NONE'}
    if active_drops:
        for k, v in active_drops.items():
            lines.append(f"  - Do {k}: {v} ban sao bi huy")
    else:
        lines.append("  - Khong co goi tin nao bi huy boi mo hinh kenh truyen.")
        
    lines.append("\n* Su kien mang & Xu ly su co (Events):")
    if stats['events']:
        for ev in stats['events']:
            lines.append(f"  -> {ev}")
    else:
        lines.append("  -> Mang hoat dong binh thuong, khong co loi hoac canh bao.")
    lines.append("="*80 + "\n")
    return "\n".join(lines)

def run_single_scenario(sc, name, duration, temp_log):
    cmd = ['java', '-cp', 'cupcarbon.jar;.', 'TestSimulation', str(sc), str(duration), temp_log]
    subprocess.run(cmd, check=True)
    with open(temp_log, 'r', encoding='utf-8', errors='ignore') as f:
        log_text = f.read()
    return log_text

def run_all_scenarios():
    print("="*80)
    print("   HE THONG TU DONG CHAY TOAN BO 7 KICH BAN MO PHONG CUPCARBON (1000s/KICH BAN)")
    print("   Toan bo log chi tiet va ket qua phan tich se duoc ghi vao: log.txt")
    print("="*80 + "\n")
    
    start_time_all = time.time()
    
    # Initialize log.txt
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write("="*85 + "\n")
        f.write("          NHAT KY MO PHONG TOAN BO 7 KICH BAN LORA WSN - CUPCARBON\n")
        f.write(f"          Thoi gian bat dau: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("          Thoi gian moi kich ban: 1000.0 giay\n")
        f.write("="*85 + "\n\n")

    benchmark_summary = []
    temp_log = "temp_sim_run.log"

    for idx, (sc, name, duration) in enumerate(SCENARIOS):
        print(f"[{idx+1}/7] Dang chay Kich ban {sc}: {name} ({duration:.0f}s)...", end="", flush=True)
        t0 = time.time()
        
        try:
            log_text = run_single_scenario(sc, name, duration, temp_log)
            elapsed = time.time() - t0
            
            # Parse
            stats = parse_simulation_log(log_text)
            benchmark_summary.append((sc, name, duration, stats['total_gen'], stats['total_rx'], stats['tot_pdr'], stats['tot_avg_lat']))
            
            # Write to log.txt:
            # 1. Section Header & Analysis Report
            report_str = format_analysis_report(sc, name, duration, stats)
            
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(report_str)
                f.write(f"--- [NHAT KY LOG CHI TIET KICH BAN {sc} (Tong {len(stats['filtered_log_lines'])} su kien)] ---\n")
                for line in stats['filtered_log_lines']:
                    f.write(line + "\n")
                f.write("\n\n")
                
            print(f" Xong ({elapsed:.1f}s) -> PDR: {stats['tot_pdr']:.1f}%, Latency: {stats['tot_avg_lat']:.2f}s, Phat: {stats['total_gen']}, Nhan: {stats['total_rx']}")
            
        except Exception as e:
            print(f" That bai: {e}")

    total_time_all = time.time() - start_time_all

    # Format Benchmark Summary Table
    sum_lines = []
    sum_lines.append("\n" + "="*85)
    sum_lines.append("                  BANG TONG HOP BENCHMARK TOAN BO 7 KICH BAN (1000s)")
    sum_lines.append(f"                  Tong thoi gian thuc thi: {total_time_all:.1f} giay")
    sum_lines.append("="*85)
    sum_lines.append(f"{'KB':<5} | {'Ten kich ban':<40} | {'Phat':<5} | {'Nhan':<5} | {'PDR (%)':<8} | {'Lat TB':<8}")
    sum_lines.append("-" * 85)
    for sc, name, dur, gen, rx, pdr, lat in benchmark_summary:
        short_name = name.split(':')[1].strip()
        sum_lines.append(f"KB-{sc:<2} | {short_name:<40} | {gen:<5} | {rx:<5} | {pdr:>7.1f}% | {lat:>6.2f}s")
    sum_lines.append("="*85 + "\n")
    
    summary_text = "\n".join(sum_lines)
    print(summary_text)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(summary_text)
        f.write(f"Ket thuc toan bo phien mo phong luc: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Clean temporary log
    if os.path.exists(temp_log):
        try: os.remove(temp_log)
        except: pass

    print(f"[HOAN TAT] Toan bo log chi tiet va bao cao phan tich da duoc ghi thanh cong vao: {LOG_FILE}\n")

def main():
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        sc = int(sys.argv[1])
        duration = float(sys.argv[2]) if len(sys.argv) > 2 else 1000.0
        name = next((n for s, n, d in SCENARIOS if s == sc), f"KB-{sc}")
        print(f">>> Dang chay rieng Kich ban {sc}: {name} ({duration}s)...")
        temp_log = "temp_single.log"
        log_text = run_single_scenario(sc, name, duration, temp_log)
        stats = parse_simulation_log(log_text)
        report = format_analysis_report(sc, name, duration, stats)
        print(report)
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            f.write(report)
            f.write(f"--- [NHAT KY LOG CHI TIET KICH BAN {sc}] ---\n")
            for line in stats['filtered_log_lines']:
                f.write(line + "\n")
        if os.path.exists(temp_log):
            try: os.remove(temp_log)
            except: pass
        print(f"[HOAN TAT] Log da duoc ghi vao {LOG_FILE}!")
    else:
        # Default: run ALL 7 scenarios, each 1000s, log into log.txt
        run_all_scenarios()

if __name__ == '__main__':
    main()
