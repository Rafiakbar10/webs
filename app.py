from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

def get_salam():
    hour = datetime.now().hour
    if 4 <= hour < 11:
        return "SELAMAT PAGI 🌅"
    elif 11 <= hour < 15:
        return "SELAMAT SIANG ☀️"
    elif 15 <= hour < 18:
        return "SELAMAT SORE 🌇"
    else:
        return "SELAMAT MALAM 🌙"

@app.route('/')
def index():
    salam = get_salam()
    return render_template('index.html', salam=salam)

@app.route('/process', methods=['POST'])
def process():
    req = request.get_json()
    step = req.get('step')
    text = req.get('text', '').strip()
    data = req.get('data', {})

    if step == 'GET_PRICE':
        clean_text = text.replace('.', '').replace(',', '').replace('Rp', '').strip()
        if not clean_text.isdigit():
            reply = "⚠️ <b>Format harga tidak valid!</b><br><br>Silakan ketik dan kirimkan angka harga barang saja secara benar:<br><i>(Contoh: 3.500.000 atau 3500000)</i>"
            return jsonify({'next_step': 'GET_PRICE', 'data': data, 'reply': reply, 'buttons': ''})
        
        harga = int(clean_text)
        data['harga'] = harga
        
        reply = f"✅ <b>Harga Barang tercatat:</b> Rp {harga:,}<br><br>💰 Masukkan jumlah <b>Uang Muka (DP)</b> yang ingin dibayarkan:<br><i>(Ketik 0 jika tanpa DP)</i>"
        return jsonify({'next_step': 'GET_DP', 'data': data, 'reply': reply, 'buttons': ''})

    elif step == 'GET_DP':
        clean_text = text.replace('.', '').replace(',', '').replace('Rp', '').strip()
        if not clean_text.isdigit():
            reply = "⚠️ <b>Format Uang Muka (DP) tidak valid!</b><br><br>Silakan masukkan angka nominal DP atau ketik <b>0</b> jika tanpa DP:"
            return jsonify({'next_step': 'GET_DP', 'data': data, 'reply': reply, 'buttons': ''})
        
        dp = int(clean_text)
        if dp >= data['harga']:
            reply = f"⚠️ Uang Muka (DP) tidak boleh melebihi atau sama dengan Harga Barang!<br><br>Silakan masukkan nominal DP yang lebih kecil dari Rp {data['harga']:,}:"
            return jsonify({'next_step': 'GET_DP', 'data': data, 'reply': reply, 'buttons': ''})

        data['dp'] = dp
        reply = f"✅ <b>DP tercatat:</b> Rp {dp:,}<br><br>⏳ Masukkan <b>Tenor Cicilan</b> dalam satuan bulan (pilihan: 3, 6, 9, 12 bulan):<br><i>(Contoh: 12)</i>"
        return jsonify({'next_step': 'GET_TENOR', 'data': data, 'reply': reply, 'buttons': ''})

    elif step == 'GET_TENOR':
        clean_text = text.replace('bulan', '').replace('bln', '').strip()
        if not clean_text.isdigit() or int(clean_text) not in [3, 6, 9, 12]:
            reply = "⚠️ <b>Pilihan Tenor tidak valid!</b><br><br>Silakan pilih tenor yang tersedia: <b>3, 6, 9,</b> atau <b>12</b> bulan."
            return jsonify({'next_step': 'GET_TENOR', 'data': data, 'reply': reply, 'buttons': ''})
        
        tenor = int(clean_text)
        data['tenor'] = tenor

        harga = data['harga']
        dp = data['dp']
        sisa_pokok = harga - dp
        
        bunga_per_bulan = 0.025
        admin_fee = 199000
        
        total_hutang = sisa_pokok + (sisa_pokok * bunga_per_bulan * tenor) + admin_fee
        cicilan_per_bulan = int(total_hutang / tenor)

        reply = (
            "━━━━━━━━━━━━━━━━━━━<br>"
            "📊 <b>HASIL SIMULASI CICILAN</b> 📊<br>"
            "🏢 <b>Home Credit Indonesia</b><br>"
            "━━━━━━━━━━━━━━━━━━━<br><br>"
            f"🏷️ <b>Harga Barang</b> : Rp {harga:,}<br>"
            f"💵 <b>Uang Muka (DP)</b> : Rp {dp:,}<br>"
            f"📅 <b>Tenor Cicilan</b> : {tenor} Bulan<br>"
            "━━━━━━━━━━━━━━━━━━━<br><br>"
            "💳 <b>ESTIMASI CICILAN :</b><br>"
            f"👉 <b>Rp {cicilan_per_bulan:,} / bln</b><br>"
            "━━━━━━━━━━━━━━━━━━━<br><br>"
            "ℹ️ <b>Catatan Penting:</b><br>"
            "• Besaran cicilan, bunga, & admin dapat bervariasi tergantung NIK dan profil akun masing-masing."
        )

        buttons = """
        <div class="btn-group">
            <a href="https://wa.me/6285935491278?text=Halo%20Admin,%20saya%20tertarik%20mengajukan%20cicilan%20Home%20Credit." target="_blank" class="wa-btn whatsapp">💬 Hubungi WhatsApp Admin</a>
            <button type="button" class="wa-btn" onclick="mulaiSimulasiBaru()">🔄 Hitung Simulasi Baru</button>
        </div>
        """

        return jsonify({'next_step': 'DONE', 'data': data, 'reply': reply, 'buttons': buttons, 'loading': True})

    return jsonify({'next_step': 'GET_PRICE', 'data': {}, 'reply': 'Silakan mulai simulasi baru.', 'buttons': ''})

if __name__ == '__main__':
    app.run(debug=True)
