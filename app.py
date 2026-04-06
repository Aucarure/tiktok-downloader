from flask import Flask, request, send_file, render_template_string, jsonify
import yt_dlp
import os
import tempfile

app = Flask(__name__)

historial = []

HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>TikTok Downloader</title>
    <link href="https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@300;400;500;600;700&family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg:        #080808;
            --surface:   #111111;
            --border:    rgba(255,255,255,0.07);
            --accent:    #e8e8e8;
            --muted:     rgba(255,255,255,0.35);
            --subtle:    rgba(255,255,255,0.06);
            --red:       #ff3b30;
            --red-dim:   rgba(255,59,48,0.12);
            --radius:    16px;
            --transition: 0.22s cubic-bezier(0.4,0,0.2,1);
        }

        *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg);
            color: var(--accent);
            min-height: 100vh;
            display: flex;
            align-items: flex-start;
            justify-content: center;
            padding: 60px 20px 80px;
            -webkit-font-smoothing: antialiased;
        }

        /* Subtle noise grain overlay */
        body::before {
            content: '';
            position: fixed;
            inset: 0;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.035'/%3E%3C/svg%3E");
            pointer-events: none;
            z-index: 0;
            opacity: 0.6;
        }

        .wrapper {
            width: 100%;
            max-width: 520px;
            position: relative;
            z-index: 1;
            animation: fadeUp 0.7s cubic-bezier(0.4,0,0.2,1) both;
        }

        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(24px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        /* ── Header ── */
        .header {
            text-align: center;
            margin-bottom: 44px;
        }
        .header-eyebrow {
            font-family: 'Syne', sans-serif;
            font-size: 10px;
            font-weight: 500;
            letter-spacing: 0.25em;
            text-transform: uppercase;
            color: var(--muted);
            margin-bottom: 10px;
        }
        .header h1 {
            font-family: 'Syne', sans-serif;
            font-size: 32px;
            font-weight: 700;
            letter-spacing: -0.03em;
            color: #fff;
            line-height: 1.1;
        }
        .header h1 span {
            color: var(--red);
        }
        .header p {
            margin-top: 8px;
            font-size: 13px;
            color: var(--muted);
            font-weight: 300;
            letter-spacing: 0.01em;
        }

        /* ── Card ── */
        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 28px;
            margin-bottom: 16px;
            backdrop-filter: blur(12px);
            transition: border-color var(--transition);
        }
        .card:hover {
            border-color: rgba(255,255,255,0.11);
        }

        /* ── Input ── */
        .input-wrap {
            position: relative;
            margin-bottom: 14px;
        }
        .input-icon {
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--muted);
            font-size: 15px;
            pointer-events: none;
            transition: color var(--transition);
        }
        input[type=text] {
            width: 100%;
            padding: 13px 14px 13px 40px;
            background: var(--subtle);
            border: 1px solid var(--border);
            border-radius: 10px;
            color: #fff;
            font-size: 13px;
            font-family: 'Inter', sans-serif;
            font-weight: 400;
            letter-spacing: 0.01em;
            transition: border-color var(--transition), background var(--transition);
            outline: none;
        }
        input[type=text]::placeholder { color: rgba(255,255,255,0.22); }
        input[type=text]:focus {
            border-color: rgba(255,255,255,0.22);
            background: rgba(255,255,255,0.05);
        }
        input[type=text]:focus + .input-icon,
        .input-wrap:focus-within .input-icon {
            color: rgba(255,255,255,0.55);
        }

        /* ── Select ── */
        .select-wrap {
            position: relative;
            margin-bottom: 20px;
        }
        .select-wrap::after {
            content: '⌄';
            position: absolute;
            right: 14px;
            top: 50%;
            transform: translateY(-52%);
            color: var(--muted);
            pointer-events: none;
            font-size: 16px;
        }
        select {
            width: 100%;
            padding: 13px 38px 13px 14px;
            background: var(--subtle);
            border: 1px solid var(--border);
            border-radius: 10px;
            color: rgba(255,255,255,0.75);
            font-size: 13px;
            font-family: 'Inter', sans-serif;
            font-weight: 400;
            appearance: none;
            outline: none;
            cursor: pointer;
            transition: border-color var(--transition);
        }
        select:focus { border-color: rgba(255,255,255,0.22); }

        /* ── Buttons ── */
        .btn-row { display: flex; gap: 10px; }
        button {
            flex: 1;
            padding: 13px 18px;
            border: none;
            border-radius: 10px;
            font-size: 13px;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            letter-spacing: 0.01em;
            cursor: pointer;
            transition: all var(--transition);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }
        .btn-info {
            background: var(--subtle);
            border: 1px solid var(--border);
            color: rgba(255,255,255,0.7);
        }
        .btn-info:hover {
            background: rgba(255,255,255,0.09);
            color: #fff;
            border-color: rgba(255,255,255,0.14);
        }
        .btn-info:active { transform: scale(0.98); }
        .btn-download {
            background: var(--red);
            color: #fff;
            box-shadow: 0 0 0 0 rgba(255,59,48,0);
        }
        .btn-download:hover {
            background: #ff5247;
            box-shadow: 0 4px 20px rgba(255,59,48,0.28);
        }
        .btn-download:active { transform: scale(0.98); }

        /* ── Loading ── */
        .loading {
            display: none;
            align-items: center;
            justify-content: center;
            gap: 8px;
            margin-top: 18px;
            font-size: 12px;
            color: var(--muted);
            letter-spacing: 0.04em;
        }
        .loading.show { display: flex; }
        .spinner {
            width: 14px;
            height: 14px;
            border: 1.5px solid rgba(255,255,255,0.12);
            border-top-color: rgba(255,255,255,0.55);
            border-radius: 50%;
            animation: spin 0.75s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        /* ── Error ── */
        .msg-error {
            display: none;
            margin-top: 14px;
            padding: 11px 14px;
            background: var(--red-dim);
            border: 1px solid rgba(255,59,48,0.22);
            border-radius: 10px;
            font-size: 12.5px;
            color: #ff6b63;
            line-height: 1.5;
        }

        /* ── Info Box ── */
        .info-box {
            display: none;
            margin-top: 20px;
            background: var(--subtle);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
            animation: fadeUp 0.3s ease both;
        }
        .info-box.show { display: block; }
        .info-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 11px 16px;
            border-bottom: 1px solid var(--border);
        }
        .info-row:last-child { border-bottom: none; }
        .info-label {
            font-size: 11.5px;
            color: var(--muted);
            font-weight: 400;
            letter-spacing: 0.02em;
        }
        .info-value {
            font-size: 12.5px;
            color: rgba(255,255,255,0.85);
            font-weight: 500;
            max-width: 58%;
            text-align: right;
            word-break: break-word;
        }

        /* ── Video Preview ── */
        video {
            display: none;
            width: 100%;
            border-radius: 10px;
            margin-top: 16px;
            border: 1px solid var(--border);
        }
        video.show { display: block; }

        /* ── Section Label ── */
        .section-label {
            font-family: 'Syne', sans-serif;
            font-size: 10px;
            font-weight: 600;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: var(--muted);
            margin-bottom: 16px;
        }

        /* ── History ── */
        .hist-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 11px 0;
            border-bottom: 1px solid var(--border);
        }
        .hist-item:last-child { border-bottom: none; }
        .hist-title {
            font-size: 12.5px;
            color: rgba(255,255,255,0.65);
            max-width: 72%;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .hist-dot {
            width: 5px; height: 5px;
            background: var(--red);
            border-radius: 50%;
            margin-right: 8px;
            flex-shrink: 0;
        }
        .hist-left { display: flex; align-items: center; max-width: 72%; min-width: 0; }
        .hist-time {
            font-size: 11px;
            color: rgba(255,255,255,0.2);
            font-weight: 300;
        }
        .empty-hist {
            font-size: 12.5px;
            color: rgba(255,255,255,0.2);
            text-align: center;
            padding: 14px 0;
            letter-spacing: 0.02em;
        }

        /* ── Footer ── */
        .footer {
            text-align: center;
            margin-top: 32px;
            font-size: 11px;
            color: rgba(255,255,255,0.15);
            letter-spacing: 0.04em;
        }
    </style>
</head>
<body>
<div class="wrapper">

    <!-- Header -->
    <div class="header">
        <p class="header-eyebrow">Herramienta de descarga</p>
        <h1>TikTok<span>.</span></h1>
        <p>Videos sin marca de agua, en segundos.</p>
    </div>

    <!-- Main Card -->
    <div class="card">
        <div class="input-wrap">
            <input type="text" id="url" placeholder="https://www.tiktok.com/@usuario/video/…" autocomplete="off" spellcheck="false"/>
            <span class="input-icon">↗</span>
        </div>

        <div class="select-wrap">
            <select id="quality">
                <option value="best">Alta calidad</option>
                <option value="worst">Baja calidad — más rápido</option>
            </select>
        </div>

        <div class="btn-row">
            <button class="btn-info" onclick="getInfo()">Obtener info</button>
            <button class="btn-download" onclick="downloadVideo()">↓ Descargar</button>
        </div>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            Procesando…
        </div>

        <div class="msg-error" id="error-msg"></div>

        <div class="info-box" id="info-box">
            <div class="info-row">
                <span class="info-label">Título</span>
                <span class="info-value" id="i-title"></span>
            </div>
            <div class="info-row">
                <span class="info-label">Autor</span>
                <span class="info-value" id="i-autor"></span>
            </div>
            <div class="info-row">
                <span class="info-label">Duración</span>
                <span class="info-value" id="i-dur"></span>
            </div>
            <div class="info-row">
                <span class="info-label">Vistas</span>
                <span class="info-value" id="i-views"></span>
            </div>
        </div>

        <video id="preview" controls></video>
    </div>

    <!-- History Card -->
    <div class="card">
        <p class="section-label">Historial</p>
        <div id="historial">
            {% if historial %}
                {% for h in historial %}
                <div class="hist-item">
                    <div class="hist-left">
                        <div class="hist-dot"></div>
                        <span class="hist-title">{{ h.titulo }}</span>
                    </div>
                    <span class="hist-time">{{ h.hora }}</span>
                </div>
                {% endfor %}
            {% else %}
                <p class="empty-hist">Sin descargas recientes</p>
            {% endif %}
        </div>
    </div>

    <p class="footer">Solo acepta enlaces de TikTok</p>
</div>

<script>
function showError(msg) {
    const el = document.getElementById('error-msg');
    el.textContent = msg;
    el.style.display = 'block';
}
function hideError() {
    const el = document.getElementById('error-msg');
    el.style.display = 'none';
}
function setLoading(val) {
    document.getElementById('loading').className = val ? 'loading show' : 'loading';
}

async function getInfo() {
    const url = document.getElementById('url').value.trim();
    if (!url) return showError('Ingresa un link primero.');
    hideError();
    setLoading(true);
    document.getElementById('info-box').className = 'info-box';
    document.getElementById('preview').className = 'video';

    const res = await fetch('/info', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({url})
    });
    const data = await res.json();
    setLoading(false);

    if (data.error) return showError(data.error);

    document.getElementById('i-title').textContent = data.titulo;
    document.getElementById('i-autor').textContent = data.autor;
    document.getElementById('i-dur').textContent = data.duracion;
    document.getElementById('i-views').textContent = data.vistas;
    document.getElementById('info-box').className = 'info-box show';

    if (data.preview_url) {
        const v = document.getElementById('preview');
        v.src = data.preview_url;
        v.className = 'show';
    }
}

async function downloadVideo() {
    const url = document.getElementById('url').value.trim();
    const quality = document.getElementById('quality').value;
    if (!url) return showError('Ingresa un link primero.');
    hideError();
    setLoading(true);

    const res = await fetch('/download', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({url, quality})
    });

    setLoading(false);
    if (!res.ok) {
        const data = await res.json();
        return showError(data.error || 'Error al descargar.');
    }

    const blob = await res.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'tiktok-video.mp4';
    a.click();
    location.reload();
}
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML, historial=historial[-10:][::-1])

@app.route('/info', methods=['POST'])
def info():
    data = request.get_json()
    url = data.get('url', '').strip()

    if 'tiktok.com' not in url:
        return jsonify({'error': 'Solo se aceptan links de TikTok.'})

    try:
        ydl_opts = {'quiet': True, 'no_warnings': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        duracion = f"{int(info.get('duration', 0) // 60)}:{int(info.get('duration', 0) % 60):02d}"
        vistas = f"{info.get('view_count', 0):,}" if info.get('view_count') else 'N/A'

        return jsonify({
            'titulo': info.get('title', 'Sin título')[:60],
            'autor': info.get('uploader', 'Desconocido'),
            'duracion': duracion,
            'vistas': vistas,
            'preview_url': info.get('url', '')
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url', '').strip()
    quality = data.get('quality', 'best')

    if 'tiktok.com' not in url:
        return jsonify({'error': 'Solo se aceptan links de TikTok.'}), 400

    try:
        tmp_dir = tempfile.mkdtemp()
        output_path = os.path.join(tmp_dir, '%(title)s.%(ext)s')

        ydl_opts = {
            'outtmpl': output_path,
            'format': quality,
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)
            historial.append({
                'titulo': info_dict.get('title', 'Sin título')[:50],
                'hora': __import__('datetime').datetime.now().strftime('%H:%M')
            })

        return send_file(filename, as_attachment=True, download_name='tiktok-video.mp4')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)