from flask import Flask, render_template, request, jsonify
from datetime import datetime
import zoneinfo
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
    zona_waktu_wib = zoneinfo.ZoneInfo("Asia/Jakarta")
    jam = datetime.now(zona_waktu_wib).hour
    
    if 4 <= jam < 11:
        return "SELAMAT PAGI 🌅"
    elif 11 <= jam < 15:
        return "SELAMAT SIANG ☀️"
    elif 15 <= jam < 18:
        return "SELAMAT SORE 🌇"
    else:
        return "SELAMAT MALAM 🌙"

@app.route("/")
def index():
    return render_template("index.html", salam=get_salam_waktu())

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

            # Fungsi reset baru tanpa me-refresh halaman (riwayat chat aman)
            html_buttons = f'''
            <div class="btn-group">
                <a href="{url_wa}" target="_blank" class="wa-btn whatsapp">💬 Hubungi WhatsApp Admin</a>
                <button type="button" class="wa-btn" onclick="mulaiSimulasiBaru()">🔄 Hitung Simulasi Baru</button>
            </div>
            '''

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
                "salam_waktu": get_salam_waktu()
            })
        except ValueError:
            return jsonify({"next_step": "GET_TENOR", "data": data, "reply": "⚠️ Masukkan angka bulat untuk jumlah bulan yang valid:"})

    return jsonify({"next_step": "GET_PRICE", "data": data, "reply": "Silakan mulai ulang."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
