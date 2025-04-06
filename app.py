from flask import Flask, request, redirect, session, url_for, render_template_string, send_file
import socket, time, json, os

app = Flask(__name__)
app.secret_key = "super-secret-key"

SHODAN_API_KEY = "D0E8rHMlLMyRdOnjF9WXSQ7juLDz1Owk"
PAYLOADS_FILE = "payloads.json"
RESULTS = []

def load_presets():
    if os.path.exists(PAYLOADS_FILE):
        with open(PAYLOADS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_presets(presets):
    with open(PAYLOADS_FILE, "w", encoding="utf-8") as f:
        json.dump(presets, f, ensure_ascii=False, indent=2)

def scan_msearch(ip_list, ports=[1900], timeout=3, custom_payload=""):
    RESULTS.clear()

    base_msg = (
        'M-SEARCH * HTTP/1.1\r\n'
        'HOST: 239.255.255.250:1900\r\n'
        'MAN: "ssdp:discover"\r\n'
        'MX: 1\r\n'
    )

    full_msg = base_msg + (custom_payload.strip() + '\r\n\r\n' if custom_payload else 'ST: ssdp:all\r\n\r\n')
    payload_check = custom_payload.strip().split('\r\n')[0] if custom_payload else "ssdp:all"

    for ip in ip_list:
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(timeout)
                sock.sendto(full_msg.encode(), (ip, port))
                data, addr = sock.recvfrom(2048)
                response = data.decode(errors="ignore")
                triggered = "Yes" if payload_check.lower() in response.lower() else "No"
                RESULTS.append({
                    "ip": f"{ip}:{port}",
                    "response": response.replace("\r\n", "<br>"),
                    "triggered": triggered
                })
            except:
                pass
            finally:
                sock.close()
            time.sleep(0.2)

@app.route("/", methods=["GET"])
def index():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    return render_template_string(RESULT_TEMPLATE, results=RESULTS)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password") == "kader11000":
            session["authenticated"] = True
            return redirect(url_for("index"))
    return '''
    <form method="post">
        <h3>Login</h3>
        <input type="password" name="password" placeholder="Enter password">
        <button type="submit">Login</button>
    </form>
    '''

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/scan-options")
def scan_options():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    return render_template_string(SCAN_OPTIONS_TEMPLATE, presets=load_presets())

@app.route("/scan-manual", methods=["POST"])
def scan_manual():
    if not session.get("authenticated"):
        return redirect(url_for("login"))

    raw_ips = request.form.get("manual_ips", "")
    raw_ports = request.form.get("ports", "1900")
    selected_payload = request.form.get("preset_payload", "")
    custom_payload = request.form.get("custom_payload", "")

    ip_list = [ip.strip() for ip in raw_ips.replace(",", "\n").splitlines() if ip.strip()]
    ports = [int(p.strip()) for p in raw_ports.split(",") if p.strip().isdigit()]
    payload_to_use = custom_payload.strip() if custom_payload.strip() else selected_payload

    if ip_list and ports:
        scan_msearch(ip_list, ports=ports, custom_payload=payload_to_use)
    return redirect(url_for("index"))

@app.route("/add-payload", methods=["POST"])
def add_payload():
    if not session.get("authenticated"):
        return redirect(url_for("login"))

    name = request.form.get("payload_name", "").strip()
    content = request.form.get("payload_content", "").strip()
    if name and content:
        presets = load_presets()
        presets[name] = content.replace("\r", "").replace("\n", "\\r\\n")
        save_presets(presets)
    return redirect(url_for("scan_options"))

@app.route("/export-html")
def export_html():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    html = render_template_string(RESULT_TEMPLATE, results=RESULTS)
    with open("msearch_results.html", "w", encoding="utf-8") as f:
        f.write(html)
    return send_file("msearch_results.html", as_attachment=True)

# HTML Templates
SCAN_OPTIONS_TEMPLATE = """
<h2>M-SEARCH Scanner Options</h2>
<form method="post" action="{{ url_for('scan_manual') }}">
    <label>Target IPs:</label><br>
    <textarea name="manual_ips" rows="4" placeholder="192.168.1.1, 8.8.8.8"></textarea><br><br>
    
    <label>Ports:</label>
    <input type="text" name="ports" placeholder="1900, 2000"><br><br>
    
    <label>Select Preset Payload:</label>
    <select name="preset_payload">
        {% for label, payload in presets.items() %}
            <option value="{{ payload }}">{{ label }}</option>
        {% endfor %}
    </select><br><br>

    <label>Or enter a custom payload:</label><br>
    <textarea name="custom_payload" rows="4" placeholder="ST: upnp:rootdevice\r\nX-Exploit: test\r\n"></textarea><br><br>

    <button type="submit">Scan Now</button>
</form>

<hr>

<h3>Add New Payload</h3>
<form method="post" action="{{ url_for('add_payload') }}">
    <label>Payload Name:</label>
    <input type="text" name="payload_name" required><br>
    
    <label>Payload Content:</label><br>
    <textarea name="payload_content" rows="3" required></textarea><br>

    <button type="submit">Save Payload</button>
</form>

<br><a href="/">Back to Results</a>
"""

RESULT_TEMPLATE = """
<h2>Scan Results</h2>
<table border="1" cellpadding="6">
    <tr>
        <th>IP</th>
        <th>Triggered Payload?</th>
        <th>Response</th>
    </tr>
    {% for entry in results %}
    <tr>
        <td>{{ entry.ip }}</td>
        <td>{{ entry.triggered }}</td>
        <td>{{ entry.response|safe }}</td>
    </tr>
    {% endfor %}
</table>
<br>
<a href="/scan-options">New Scan</a> | 
<a href="/export-html">Export HTML</a> | 
<a href="/logout">Logout</a>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
