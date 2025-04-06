from flask import Flask, render_template_string, request, redirect, url_for import socket import threading import json

app = Flask(__name) PASSWORD = "kader11000" RESULTS = []

HTML_TEMPLATE = """

<!DOCTYPE html><html lang='en'>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>M-SEARCH RCE Scanner</title>
    <style>
        @keyframes banner-glow {
            0% { text-shadow: 0 0 5px #4CAF50; }
            50% { text-shadow: 0 0 20px #4CAF50; }
            100% { text-shadow: 0 0 5px #4CAF50; }
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            background-color: #f2f2f2;
        }
        .container {
            max-width: 900px;
            margin: 40px auto;
            background-color: #fff;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
        }
        h1.banner {
            text-align: center;
            font-size: 28px;
            color: #4CAF50;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
            margin-bottom: 30px;
            animation: banner-glow 2s infinite ease-in-out;
        }
        h2, h3 {
            text-align: center;
            color: #333;
        }
        form {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        input, select {
            padding: 10px;
            font-size: 16px;
            border: 1px solid #ccc;
            border-radius: 8px;
        }
        input[type="submit"] {
            background-color: #4CAF50;
            color: white;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        input[type="submit"]:hover {
            background-color: #45a049;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 30px;
        }
        th, td {
            border: 1px solid #ccc;
            padding: 12px;
            text-align: center;
        }
        th {
            background-color: #4CAF50;
            color: white;
        }
        .login-box {
            max-width: 300px;
            margin: 100px auto;
            background: #fff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            text-align: center;
        }
    </style>
</head>
<body>
<div class="container">
    <h1 class="banner">Powered by kader11000</h1>
{% if not authenticated %}
    <div class="login-box">
        <h3>Login</h3>
        <form method="POST">
            <input type="password" name="password" placeholder="Password" required><br>
            <input type="submit" value="Login">
        </form>
    </div>
{% else %}
    <h2>M-SEARCH + RCE Scanner</h2>
    <form method="POST" action="/scan-options">
        <label>Target IP(s) (comma separated):</label>
        <input type="text" name="target_ips" placeholder="192.168.1.1,10.0.0.2" required><label>Ports (comma separated):</label>
    <input type="text" name="ports" value="1900">

    <label>Payload Type:</label>
    <select name="payload">
        {% for name, val in payloads.items() %}
            <option value="{{ name }}">{{ name }}</option>
        {% endfor %}
    </select>

    <label>Remote Command (RCE):</label>
    <input type="text" name="rce_command" placeholder="id">

    <input type="submit" value="Scan">
</form>

{% if results %}
    <h3>Scan Results</h3>
    <table>
        <tr>
            <th>IP</th>
            <th>Triggered?</th>
            <th>Exploited?</th>
            <th>Command Output</th>
            <th>Response</th>
        </tr>
        {% for r in results %}
            <tr>
                <td>{{ r.ip }}</td>
                <td>{{ r.triggered }}</td>
                <td>{{ r.exploited }}</td>
                <td>{{ r.exec_result|safe }}</td>
                <td>{{ r.response|safe }}</td>
            </tr>
        {% endfor %}
    </table>
{% endif %}

{% endif %}

</div>
</body>
</html>
"""(The rest of the Python code remains unchanged)

