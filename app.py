from flask import Flask, render_template_string, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# Logika Perhitungan Cicilan Home Credit
def ambil_biaya_perlindungan(sisa_pokok: float) -> float:
    if 500_000 <= sisa_pokok <= 10_000_000:
        return 599_000
    elif 10_000_000 < sisa_pokok <= 30_000_000:
        return 899_000
    elif sisa_pokok > 30_000_000:
        return 1_299_000
    return 0.0

def ambil_biaya_admin(sisa_pokok: float, tenor: int) -> float:
    if tenor == 14:
        return 0.0
    if 500_000 <= sisa_pokok <= 5_000_000:
        return (sisa_pokok / 1_000_000) * 30_000
    else:
        if tenor in [3, 6, 9, 12]:
            return 199_000
        elif tenor in [15, 18, 21, 24]:
            return 299_000
    return 0.0

def get_salam_waktu() -> str:
    jam = datetime.now().hour
    if 4 <= jam < 11:
        return "SELAMAT PAGI 🌅"
    elif 11 <= jam < 15:
        return "SELAMAT SIANG ☀️"
    elif 15 <= jam < 18:
        return "SELAMAT SORE 🌇"
    else:
        return "SELAMAT MALAM 🌙"

# Tampilan Halaman Web (Frontend + Chat Telegram UI)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simulasi Cicilan HCI - Telegram Web</title>
    <style>
        body {
            background-color: #0e1621;
            color: #f5f5f5;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        .chat-header {
            background-color: #17212b;
            padding: 10px 15px;
            display: flex;
            align-items: center;
            border-bottom: 1px solid #0f1621;
            position: fixed;
            top: 0;
            width: 100%;
            box-sizing: border-box;
            z-index: 100;
        }
        .avatar {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #ff8800, #ff5500);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 18px;
            color: white;
            margin-right: 12px;
        }
        .chat-info h3 {
            margin: 0;
            font-size: 16px;
            color: #ffffff;
        }
        .chat-info p {
            margin: 2px 0 0 0;
            font-size: 12px;
            color: #829ab1;
        }
        .chat-container {
            flex: 1;
            margin-top: 60px;
            margin-bottom: 70px;
            padding: 15px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-width: 600px;
            width: 100%;
            align-self: center;
        }
        .message {
            max-width: 80%;
            padding: 10px 14px;
            border-radius: 12px;
            font-size: 14px;
            line-height: 1.4;
            word-wrap: break-word;
            white-space: pre-wrap;
        }
        .message.bot {
            background-color: #182533;
            color: #ffffff;
            align-self: flex-start;
            border-bottom-left-radius: 2px;
        }
        .message.user {
            background-color: #2b5278;
            color: #ffffff;
            align-self: flex-end;
            border-bottom-right-radius: 2px;
        }
        .time {
            font-size: 10px;
            color: #829ab1;
            text-align: right;
            margin-top: 4px;
        }
        .btn-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
            margin-top: 8px;
        }
        .tg-btn {
            background-color: #2b5278;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            text-align: center;
            text-decoration: none;
        }
        .tg-btn:hover { background-color: #386795; }
        .tg-btn.whatsapp { background-color: #25d366; }
        .tg-btn.whatsapp:hover { background-color: #20ba5a; }
        .chat-input-area {
            background-color: #17212b;
            padding: 10px 15px;
            display: flex;
            gap: 10px;
            position: fixed;
            bottom: 0;
            width: 100%;
            box-sizing: border-box;
            max-width: 600px;
            left: 50%;
            transform: translateX(-50%);
        }
        .chat-input-area input {
            flex: 1;
            background-color: #242f3d;
            border: none;
            padding: 12px 15px;
            border-radius: 20px;
            color: white;
            font-size: 14px;
            outline: none;
        }
        .chat-input-area button {
            background-color: #5288c1;
            border: none;
            width: 42px;
            height: 42px;
            border-radius: 50%;
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <div class="chat-header">
        <div class="avatar">HC</div>
        <div class="chat-info">
            <h3>Simulasi Cicilan HCI</h3>
            <p>bot</p>
        </div>
    </div>

    <div class="chat-container" id="chatContainer">
        <div class="message bot">
            ✨ <b>{{ salam }}</b> ✨<br>
            🏢 <b>HOME CREDIT INDONESIA</b><br><br>
            📦 Silakan ketik dan kirimkan <b>Harga Barang</b> yang ingin anda hitung:<br><br>
            <i>(Contoh: 3.500.000 atau 3500000)</i>
            <div class="time" id="initialTime"></div>
        </div>
    </div>

    <div class="chat-input-area" id="inputArea">
        <input type="text" id="userInput" placeholder="Ketik pesan..." autocomplete="off">
        <button id="sendBtn" onclick="sendMessage()">➤</button>
    </div>

    <script>
        let step = 'GET_PRICE';
        let dataSimulasi = { harga: 0, dp: 0, tenor: 0 };
        document.getElementById('initialTime').innerText = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        const inputField = document.getElementById('userInput');
        inputField.addEventListener("keypress", function(event) {
            if (event.key === "Enter") { sendMessage(); }
        });

        function appendMessage(text, sender, htmlButtons = '') {
            const container = document.getElementById('chatContainer');
            const msgDiv = document.createElement('div');
            msgDiv.className = `message ${sender}`;
            if(sender === 'bot') { msgDiv.innerHTML = text + htmlButtons; }
            else { msgDiv.innerText = text; }

            const timeDiv = document.createElement('div');
            timeDiv.className = 'time';
            timeDiv.innerText = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            msgDiv.appendChild(timeDiv);

            container.appendChild(msgDiv);
            container.scrollTop = container.scrollHeight;
        }

        async function sendMessage() {
            const text = inputField.value.trim();
            if (!text) return;
            appendMessage(text, 'user');
            inputField.value = '';

            try {
                const response = await fetch('/process', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ step: step, text: text, data: dataSimulasi })
                });
                const result = await response.json();
                step = result.next_step;
                dataSimulasi = result.data;

                if(result.loading) {
                    appendMessage("🔄 <i>Sedang menghitung rincian simulasi terbaik untuk Anda...</i>", 'bot');
                    setTimeout(() => {
                        const container = document.getElementById('chatContainer');
                        container.removeChild(container.lastChild);
                        appendMessage(result.reply, 'bot', result.buttons);
                        if(result.reset) {
                            step = 'GET_PRICE';
                            dataSimulasi = { harga: 0, dp: 0, tenor: 0 };
                        }
                    }, 1200);
                } else {
                    appendMessage(result.reply, 'bot', result.buttons);
                }
            } catch (error) {
                appendMessage("⚠️ Terjadi kesalahan koneksi.", 'bot');
            }
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, salam=get_salam_waktu())

@app.route("/process", methods=["POST"])
def process():
    req = request.json
    step = req.get("step")
    text = req.get("text").replace(".", "").replace(",", "").strip()
    data = req.get("data")

    if step == "GET_PRICE":
        try:
            harga = float(text)
            if harga < 500_000:
                return jsonify({"next_step": "GET_PRICE", "data": data, "reply": "⚠️ Minimal harga barang adalah Rp 500.000. Silakan masukkan harga yang valid:"})
            data["harga"] = harga
            return jsonify({
                "next_step": "GET_DP", "data": data, 
                "reply": f"✅ Harga Barang tercatat: <b>Rp {harga:,.0f}</b>\n\n💵 Masukkan jumlah <b>Uang Muka (DP)</b> yang ingin dibayarkan\n\n<i>(Ketik 0 jika tanpa DP)</i>"
            })
        except ValueError:
            return jsonify({"next_step": "GET_PRICE", "data": data, "reply": "⚠️ Format harga tidak valid. Masukkan angka saja tanpa titik/koma (contoh: 3500000):"})

    elif step == "GET_DP":
        try:
            dp = float(text)
            harga = data["harga"]
            if dp < 0 or dp >= harga:
                return jsonify({"next_step": "GET_DP", "data": data, "reply": "⚠️ DP tidak valid (tidak boleh melebihi atau sama dengan Harga Barang). Masukkan nominal DP lain:"})
            sisa_pokok = harga - dp
            if sisa_pokok < 500_000:
                return jsonify({"next_step": "GET_DP", "data": data, "reply": "⚠️ Sisa pokok setelah DP minimal Rp 500.000. Masukkan nominal DP yang lain:"})
            data["dp"] = dp
            info_tenor = "pilihan: 3, 6, 9, 12, 14 bulan" if 500_000 <= sisa_pokok <= 5_000_000 else "pilihan: 3, 6, 9, 12, 14, 15, 18, 21, 24 bulan"
            return jsonify({
                "next_step": "GET_TENOR", "data": data,
                "reply": f"✅ DP tercatat: <b>Rp {dp:,.0f}</b>\n\n⏳ Masukkan <b>Tenor Cicilan</b> dalam satuan bulan ({info_tenor})\n\n<i>(Contoh: 12 atau 14)</i>"
            })
        except ValueError:
            return jsonify({"next_step": "GET_DP", "data": data, "reply": "⚠️ Format DP tidak valid. Masukkan angka saja (contoh: 500000 atau 0):"})

    elif step == "GET_TENOR":
        try:
            tenor_input = int(text)
            harga = data["harga"]
            dp = data["dp"]
            sisa_pokok = harga - dp
            pilihan_valid = [3, 6, 9, 12, 14] if 500_000 <= sisa_pokok <= 5_000_000 else [3, 6, 9, 12, 14, 15, 18, 21, 24]

            if tenor_input not in pilihan_valid:
                return jsonify({"next_step": "GET_TENOR", "data": data, "reply": f"⚠️ Tenor tidak ada di pilihan!\nSilakan masukkan tenor yang tersedia: ({', '.join(map(str, pilihan_valid))}) bulan."})

            if tenor_input == 14:
                tampilan_tenor = "14 Bulan (Free 2x)"
                cicilan_per_bulan = harga / 12
            else:
                tampilan_tenor = f"{tenor_input} Bulan"
                biaya_perlindungan = ambil_biaya_perlindungan(sisa_pokok)
                biaya_admin = ambil_biaya_admin(sisa_pokok, tenor_input)
                total_biaya_bulanan = 10_000 * tenor_input
                if 500_000 <= sisa_pokok <= 5_000_000:
                    total_bunga = (sisa_pokok * 0.0225) * tenor_input
                    total_keseluruhan = sisa_pokok + biaya_perlindungan + biaya_admin + total_biaya_bulanan + total_bunga
                    cicilan_per_bulan = total_keseluruhan / tenor_input
                else:
                    total_pembiayaan = sisa_pokok + biaya_perlindungan + biaya_admin + total_biaya_bulanan
                    cicilan_per_bulan = total_pembiayaan / tenor_input

            pesan_wa = f"Halo Admin, saya ingin mengajukan cicilan Home Credit dengan rincian:\n- Harga Barang: Rp {harga:,.0f}\n- DP: Rp {dp:,.0f}\n- Tenor: {tampilan_tenor}\n- Cicilan: Rp {cicilan_per_bulan:,.0f} / bln"
            url_wa = f"https://wa.me/6285935491278?text={pesan_wa.replace(' ', '%20').replace(chr(10), '%0A')}"

            html_buttons = f"""
            <div class="btn-group">
                <a href="{url_wa}" target="_blank" class="tg-btn whatsapp">💬 Hubungi WhatsApp Admin</a>
                <button class="tg-btn" onclick="location.reload()">🔄 Hitung Simulasi Baru</button>
            </div>
            """

            pesan_hasil = (
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "📊  <b>HASIL SIMULASI CICILAN</b>  📊\n"
                "🏢  <b>Home Credit Indonesia</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🏷️  <b>Harga Barang</b>  : Rp {harga:,.0f}\n"
                f"💵  <b>Uang Muka (DP)</b> : Rp {dp:,.0f}\n"
                f"📅  <b>Tenor Cicilan</b>  : {tampilan_tenor}\n\n"
                "──────────────────────\n"
                f"💳  <b>ESTIMASI CICILAN</b> :\n"
                f"👉  <b>Rp {cicilan_per_bulan:,.0f} / bln</b>\n"
                "──────────────────────\n\n"
                "ℹ️  <b>Catatan Penting:</b>\n"
                "• Besaran cicilan, bunga, & admin dapat bervariasi tergantung NIK dan profil akun masing-masing.\n"
                "━━━━━━━━━━━━━━━━━━━━━━"
            )

            return jsonify({
                "next_step": "DONE", "data": data, "loading": True,
                "reply": pesan_hasil, "buttons": html_buttons, "reset": True
            })
        except ValueError:
            return jsonify({"next_step": "GET_TENOR", "data": data, "reply": "⚠️ Masukkan angka bulat untuk jumlah bulan yang valid:"})

    return jsonify({"next_step": "GET_PRICE", "data": data, "reply": "Silakan mulai ulang."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
