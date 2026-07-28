from flask import Flask, render_template_string, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

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

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>WhatsApp - Simulasi Cicilan HCI</title>
    <style>
        * {
            box-sizing: border-box;
        }
        html, body {
            background-color: #0b141a;
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100vh;
            overflow: hidden;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }

        /* Kontainer Utama Flexbox agar input selalu di bawah */
        .wa-mobile-container {
            width: 100%;
            height: 100%;
            max-width: 600px;
            margin: 0 auto;
            background-color: #0b141a;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100vh;
            height: 100dvh;
        }

        /* Header WhatsApp */
        .wa-header {
            background-color: #202c33;
            padding: 8px 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 56px;
            flex-shrink: 0;
            z-index: 10;
            color: #aebac1;
        }
        .wa-header-left {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .back-arrow {
            font-size: 20px;
            cursor: pointer;
            color: #aebac1;
        }
        .wa-avatar {
            width: 38px;
            height: 38px;
            background-color: #6a5acd;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 15px;
            color: white;
        }
        .wa-contact-name {
            margin: 0;
            font-size: 16px;
            color: #e9edef;
            font-weight: 500;
        }
        .wa-header-right {
            display: flex;
            align-items: center;
            gap: 18px;
            font-size: 18px;
        }

        /* Ruang Chat Wallpaper yang bisa di-scroll */
        .wa-chat-container {
            flex: 1;
            padding: 12px 15px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
            background-color: #0b141a;
            background-image: radial-gradient(#111b21 1.2px, transparent 1.2px);
            background-size: 24px 24px;
        }

        /* Kotak Enkripsi Kuning */
        .encryption-notice {
            background-color: #182229;
            color: #ffd279;
            font-size: 11px;
            text-align: center;
            padding: 10px 14px;
            border-radius: 8px;
            margin: 2px auto 8px auto;
            max-width: 92%;
            line-height: 1.4;
            box-shadow: 0 1px 0.5px rgba(0,0,0,0.3);
            flex-shrink: 0;
        }

        .chat-date-badge {
            background-color: #182229;
            color: #8696a0;
            font-size: 11px;
            padding: 5px 10px;
            border-radius: 6px;
            align-self: center;
            margin: 4px 0;
            box-shadow: 0 1px 0.5px rgba(0,0,0,0.2);
            flex-shrink: 0;
        }

        /* Gelembung Pesan */
        .message {
            max-width: 82%;
            padding: 8px 12px;
            border-radius: 7.5px;
            font-size: 14px;
            line-height: 1.45;
            word-wrap: break-word;
            position: relative;
            white-space: pre-wrap;
            box-shadow: 0 1px 0.5px rgba(0,0,0,0.2);
        }
        .message.bot {
            background-color: #202c33;
            color: #e9edef;
            align-self: flex-start;
            border-top-left-radius: 0;
        }
        .message.user {
            background-color: #005c4b;
            color: #e9edef;
            align-self: flex-end;
            border-top-right-radius: 0;
        }
        .message-meta {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 3px;
            margin-top: 3px;
            float: right;
            margin-left: 8px;
        }
        .time {
            font-size: 10px;
            color: #8696a0;
        }
        .check-icon {
            font-size: 12px;
            color: #53bdeb;
            font-weight: bold;
        }

        /* Tombol Aksi */
        .btn-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
            margin-top: 8px;
        }
        .wa-btn {
            background-color: #005c4b;
            color: white;
            border: none;
            padding: 9px 12px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            text-align: center;
            text-decoration: none;
            transition: background 0.2s;
        }
        .wa-btn:hover { background-color: #006c58; }
        .wa-btn.whatsapp { background-color: #00a884; font-weight: 600; }
        .wa-btn.whatsapp:hover { background-color: #009072; }

        /* Popup Emoji Picker */
        .emoji-picker {
            position: absolute;
            bottom: 65px;
            left: 10px;
            background-color: #202c33;
            border: 1px solid #2a3942;
            border-radius: 12px;
            padding: 8px;
            display: none;
            grid-template-columns: repeat(5, 1fr);
            gap: 6px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            z-index: 100;
        }
        .emoji-item {
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            padding: 4px;
            border-radius: 6px;
        }
        .emoji-item:hover { background-color: #2a3942; }

        /* Footer Input WhatsApp Android */
        .wa-input-area {
            background-color: #0b141a;
            padding: 8px 10px;
            display: flex;
            align-items: center;
            gap: 8px;
            height: 60px;
            flex-shrink: 0;
            z-index: 10;
        }
        .input-wrapper {
            flex: 1;
            background-color: #202c33;
            display: flex;
            align-items: center;
            border-radius: 24px;
            padding: 0 12px;
            gap: 8px;
            height: 44px;
        }
        .wa-input-area .icon-btn {
            background: none;
            border: none;
            color: #8696a0;
            font-size: 20px;
            cursor: pointer;
            padding: 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .wa-input-area input {
            flex: 1;
            background: transparent;
            border: none;
            color: white;
            font-size: 15px;
            outline: none;
        }
        .wa-input-area input::placeholder { color: #8696a0; }
        
        /* Tombol Mikrofon / Kirim Bulat */
        .mic-send-btn {
            background-color: #00a884;
            border: none;
            width: 44px;
            height: 44px;
            border-radius: 50%;
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            flex-shrink: 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.3);
        }
    </style>
</head>
<body>

    <div class="wa-mobile-container">
        <!-- Header WhatsApp Android -->
        <div class="wa-header">
            <div class="wa-header-left">
                <span class="back-arrow">←</span>
                <div class="wa-avatar">R</div>
                <div>
                    <h3 class="wa-contact-name">Rafii</h3>
                </div>
            </div>
            <div class="wa-header-right">
                <span>📹</span>
                <span>📞</span>
                <span>⋮</span>
            </div>
        </div>

        <!-- Popup Emoji -->
        <div class="emoji-picker" id="emojiPicker">
            <button class="emoji-item" type="button" onclick="addEmoji('😊')">😊</button>
            <button class="emoji-item" type="button" onclick="addEmoji('👍')">👍</button>
            <button class="emoji-item" type="button" onclick="addEmoji('🔥')">🔥</button>
            <button class="emoji-item" type="button" onclick="addEmoji('⭐')">⭐</button>
            <button class="emoji-item" type="button" onclick="addEmoji('🤝')">🤝</button>
            <button class="emoji-item" type="button" onclick="addEmoji('📱')">📱</button>
            <button class="emoji-item" type="button" onclick="addEmoji('💻')">💻</button>
            <button class="emoji-item" type="button" onclick="addEmoji('💸')">💸</button>
            <button class="emoji-item" type="button" onclick="addEmoji('✨')">✨</button>
            <button class="emoji-item" type="button" onclick="addEmoji('🙏')">🙏</button>
        </div>

        <!-- Ruang Chat -->
        <div class="wa-chat-container" id="chatContainer">
            <div class="encryption-notice">
                🔒 Pesan dan telepon terenkripsi secara end-to-end. Hanya orang di obrolan ini yang bisa membaca, mendengarkan, atau membagikannya. <b>Pelajari selengkapnya.</b>
            </div>
            <div class="chat-date-badge">Hari ini</div>

            <div class="message bot">
                ✨ <b>{{ salam }}</b> ✨<br><br>
                🏢 <b>HOME CREDIT INDONESIA</b><br><br>
                📦 Silakan ketik dan kirimkan <b>Harga Barang</b> yang ingin anda hitung:<br><br>
                <i>(Contoh: 3.500.000 atau 3500000)</i>
                <div class="message-meta">
                    <span class="time" id="initialTime"></span>
                </div>
            </div>
        </div>

        <!-- Area Input WhatsApp Android (Flexbox Bawah) -->
        <div class="wa-input-area">
            <div class="input-wrapper">
                <button type="button" class="icon-btn" onclick="toggleEmojiPicker(event)">😊</button>
                <input type="text" id="userInput" placeholder="Pesan" autocomplete="off">
                <button type="button" class="icon-btn" onclick="showInfoAttach()">📎</button>
                <button type="button" class="icon-btn" onclick="showInfoAttach()">📷</button>
            </div>
            <button type="button" class="mic-send-btn" id="sendMicBtn" onclick="handleSendAction()">🎤</button>
        </div>
    </div>

    <script>
        let step = 'GET_PRICE';
        let dataSimulasi = { harga: 0, dp: 0, tenor: 0 };

        function getCurrentTime() {
            return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }

        document.getElementById('initialTime').innerText = getCurrentTime();

        const inputField = document.getElementById('userInput');
        const sendMicBtn = document.getElementById('sendMicBtn');

        inputField.addEventListener("input", function() {
            if (inputField.value.trim().length > 0) {
                sendMicBtn.innerHTML = "➤";
            } else {
                sendMicBtn.innerHTML = "🎤";
            }
        });

        inputField.addEventListener("keypress", function(event) {
            if (event.key === "Enter") { handleSendAction(); }
        });

        function handleSendAction() {
            if (inputField.value.trim().length > 0) {
                sendMessage();
            } else {
                alert("🎤 Fitur suara belum aktif. Silakan ketik nominal pesan.");
            }
        }

        function toggleEmojiPicker(e) {
            e.stopPropagation();
            const picker = document.getElementById('emojiPicker');
            picker.style.display = picker.style.display === 'grid' ? 'none' : 'grid';
        }

        function addEmoji(emoji) {
            inputField.value += emoji;
            document.getElementById('emojiPicker').style.display = 'none';
            inputField.focus();
            sendMicBtn.innerHTML = "➤";
        }

        function showInfoAttach() {
            alert("ℹ️ Menu Tambahan:\nSilakan ketik nominal Harga Barang atau DP secara langsung pada kolom pesan.");
        }

        document.addEventListener('click', function(e) {
            const picker = document.getElementById('emojiPicker');
            if (!e.target.closest('.emoji-picker') && !e.target.closest('.icon-btn')) {
                picker.style.display = 'none';
            }
        });

        function appendMessage(text, sender, htmlButtons = '') {
            const container = document.getElementById('chatContainer');
            const msgDiv = document.createElement('div');
            msgDiv.className = `message ${sender}`;
            
            if(sender === 'bot') {
                msgDiv.innerHTML = text + htmlButtons;
                const meta = document.createElement('div');
                meta.className = 'message-meta';
                meta.innerHTML = `<span class="time">${getCurrentTime()}</span>`;
                msgDiv.appendChild(meta);
            } else {
                msgDiv.innerText = text;
                const meta = document.createElement('div');
                meta.className = 'message-meta';
                meta.innerHTML = `<span class="time">${getCurrentTime()}</span><span class="check-icon">✓✓</span>`;
                msgDiv.appendChild(meta);
            }

            container.appendChild(msgDiv);
            container.scrollTop = container.scrollHeight;
        }

        async function sendMessage() {
            const text = inputField.value.trim();
            if (!text) return;

            appendMessage(text, 'user');
            inputField.value = '';
            sendMicBtn.innerHTML = "🎤";
            document.getElementById('emojiPicker').style.display = 'none';

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
                "next_step": "GET_DP", 
                "data": data, 
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
                "next_step": "GET_TENOR", 
                "data": data,
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

            html_buttons = f'<div class="btn-group"><a href="{url_wa}" target="_blank" class="wa-btn whatsapp">💬 Hubungi WhatsApp Admin</a><button type="button" class="wa-btn" onclick="location.reload()">🔄 Hitung Simulasi Baru</button></div>'

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
                "next_step": "DONE", 
                "data": data, 
                "loading": True,
                "reply": pesan_hasil, 
                "buttons": html_buttons, 
                "reset": True
            })
        except ValueError:
            return jsonify({"next_step": "GET_TENOR", "data": data, "reply": "⚠️ Masukkan angka bulat untuk jumlah bulan yang valid:"})

    return jsonify({"next_step": "GET_PRICE", "data": data, "reply": "Silakan mulai ulang."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
