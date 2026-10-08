import paramiko, json, sys, time, os

sys.stdout.reconfigure(encoding='utf-8')

# Credentials
FLEET = [
    {"name": "五四云-1023", "ip": "156.225.28.106", "port": 22, "user": "root", "pass": "Us0OaJgKY8fM", "exp": "2026-10-23", "spec": "16C16G/29G"},
    {"name": "花屿云-1024", "ip": "154.219.105.203", "port": 22, "user": "root", "pass": "pvjsNFRT9661", "exp": "2026-10-24", "spec": "16C32G/97G"},
    {"name": "五四云-1021", "ip": "156.225.28.62", "port": 22, "user": "root", "pass": "jiwnIJAH6957", "exp": "2026-10-21", "spec": "16C16G/29G+200G"},
    {"name": "五四云-1106", "ip": "156.225.28.57", "port": 22, "user": "root", "pass": "Xp3LVqOFF0qV", "exp": "2026-11-06", "spec": "16C16G/29G+200G"},
    {"name": "量芯云-1011", "ip": "154.94.225.214", "port": 22, "user": "root", "pass": "mKRQAqFw2VLD", "exp": "2026-10-11", "spec": "4C4G/39G"},
    {"name": "小特云-待补", "ip": "103.236.91.189", "port": 28807, "user": "root", "pass": "VvUo7JILxY59", "exp": "待面板查", "spec": "16C16G/30G"},
    {"name": "量芯云-1030", "ip": "156.224.28.101", "port": 22222, "user": "root", "pass": "FRCzPDWK5HAL", "exp": "2026-10-30", "spec": "4C8G/39G"},
    {"name": "五四云-1030A", "ip": "156.225.28.208", "port": 22, "user": "root", "pass": "u10iMz2yXkgl", "exp": "2026-10-30", "spec": "16C16G/29G+200G"},
    {"name": "五四云-1030B", "ip": "156.225.28.4", "port": 22, "user": "root", "pass": "TZ1TxSjcVW9e", "exp": "2026-10-30", "spec": "16C16G/29G+200G"},
]

PROBE_CMD = r'''
echo "=== HOST ==="; hostname; uname -sr; uptime
echo "=== DISK ==="; df -h /; df -h /opt 2>/dev/null
echo "=== LISTEN ==="; ss -tlnp 2>/dev/null
echo "=== RUNNING_SERVICES ==="; systemctl list-units --type=service --state=running --no-pager 2>/dev/null | head -30
echo "=== KEY_PROCESSES ==="; ps -eo pid,user,args 2>/dev/null | grep -E 'python|node|docker|dsh|worker|server|gunicorn|uvicorn|linying|rk|wb|tg|faka|mizheng' | grep -v grep | head -35
echo "=== CRON ==="; crontab -l 2>/dev/null || echo "(no crontab)"
echo "=== OPT_DIRS ==="; ls -la /opt 2>/dev/null
'''

results = {}

# Probe function (direct or via 1023 jump)
def run_direct(m):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(m["ip"], port=m["port"], username=m["user"], password=m["pass"], timeout=10)
    stdin, stdout, stderr = c.exec_command(PROBE_CMD, timeout=30)
    out = stdout.read().decode('utf-8', 'replace')
    c.close()
    return out

def run_via_jump(m, jump):
    # Connect jump host first
    jc = paramiko.SSHClient()
    jc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    jc.connect(jump["ip"], port=jump["port"], username=jump["user"], password=jump["pass"], timeout=10)
    
    # Establish direct-tcpip channel
    vmtransport = jc.get_transport()
    dest_addr = (m["ip"], m["port"])
    local_addr = ('127.0.0.1', 0)
    channel = vmtransport.open_channel("direct-tcpip", dest_addr, local_addr, timeout=10)
    
    # Connect target via channel
    tc = paramiko.SSHClient()
    tc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    tc.connect(m["ip"], port=m["port"], username=m["user"], password=m["pass"], sock=channel, timeout=10)
    stdin, stdout, stderr = tc.exec_command(PROBE_CMD, timeout=30)
    out = stdout.read().decode('utf-8', 'replace')
    tc.close()
    jc.close()
    return out

jump_host = FLEET[0] # 五四云-1023

for m in FLEET:
    name = m["name"]
    print(f"[*] Probing {name} ({m['ip']}:{m['port']}) ...", flush=True)
    try:
        out = run_direct(m)
        print(f"    [+] {name} Direct connection OK!")
        results[name] = {"status": "ALIVE", "mode": "direct", "data": out, "meta": m}
    except Exception as e:
        print(f"    [-] Direct failed ({e}), trying via jump host 五四云-1023 ...", flush=True)
        try:
            out = run_via_jump(m, jump_host)
            print(f"    [+] {name} Jump connection via 1023 OK!")
            results[name] = {"status": "ALIVE", "mode": "jump", "data": out, "meta": m}
        except Exception as e2:
            print(f"    [X] {name} Both failed: {e2}")
            results[name] = {"status": "DOWN", "error": str(e2), "meta": m}

with open(r'D:\multiagent-architect\scratch\fleet_probe_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n[✓] Fleet probe completed! Results written to fleet_probe_results.json")
