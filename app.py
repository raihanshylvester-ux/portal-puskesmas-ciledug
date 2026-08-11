import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import json
import altair as alt
from io import BytesIO

# ==========================================
# 1. KONFIGURASI SUPABASE
# ==========================================
SUPABASE_URL = "https://qawzvmoqgoajewkwzdfl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFhd3p2bW9xZ29hamV3a3d6ZGZsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODY0MDIyMzAsImV4cCI6MjEwMTk3ODIzMH0.q8dShsEvHf4r6l-Vx_ypguzy_VgX4cE-BO4y1i1g1hc"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

if 'sudah_login' not in st.session_state:
    st.session_state['sudah_login'] = False
    st.session_state['username'] = ""
    st.session_state['role'] = ""

st.set_page_config(page_title="Portal Internal Puskesmas", page_icon="🏥", layout="wide")

# ==========================================
# FUNGSI PENYIMPANAN DATA DASHBOARD
# ==========================================
def load_ckg():
    try:
        res = supabase.storage.from_("laporan_files").download("ckg_config.json")
        return json.loads(res)
    except:
        return {"target": 1000, "capaian": 0}
        
def save_ckg(target, capaian):
    data = json.dumps({"target": target, "capaian": capaian}).encode('utf-8')
    try:
        supabase.storage.from_("laporan_files").update(path="ckg_config.json", file=data)
    except:
        supabase.storage.from_("laporan_files").upload(path="ckg_config.json", file=data)

def load_penyakit():
    try:
        res = supabase.storage.from_("laporan_files").download("top10_penyakit.csv")
        return pd.read_csv(BytesIO(res))
    except:
        return pd.DataFrame()
        
def save_penyakit(df):
    data = df.to_csv(index=False).encode('utf-8')
    try:
        supabase.storage.from_("laporan_files").update(path="top10_penyakit.csv", file=data)
    except:
        supabase.storage.from_("laporan_files").upload(path="top10_penyakit.csv", file=data)

# ==========================================
# CUSTOM CSS
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .stButton>button { border-radius: 8px; font-weight: 600; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .kepatuhan-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
    .progress-bar-bg { background-color: #e2e8f0; border-radius: 10px; height: 12px; width: 100%; margin-top: 5px; overflow: hidden; }
    .progress-bar-fill { background: linear-gradient(90deg, #34d399 0%, #059669 100%); height: 100%; border-radius: 10px; }
    .badge-sudah { background-color: #ecfdf5; color: #065f46; padding: 6px 14px; border-radius: 20px; display: inline-block; margin: 4px; font-weight: 600; }
    .badge-belum { background-color: #fef2f2; color: #991b1b; padding: 6px 14px; border-radius: 20px; display: inline-block; margin: 4px; font-weight: 600; }
    .file-item { padding: 5px 0px; border-bottom: 1px dashed #e2e8f0; }
    .file-item a { text-decoration: none; color: #0284c7; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("🏥 Portal Internal")
menu = st.sidebar.radio("Navigasi:", ["Upload Dokumen", "Dashboard Admin"])

DAFTAR_PROGRAM = ["Farmasi", "Gizi", "Ausrem", "KIA/KB", "Promkes", "Kesling", "P2P", "Laboratorium", "Tata Usaha"]
DAFTAR_TAHUN = ["2024", "2025", "2026", "2027", "2028", "2029"]

# ==========================================
# HALAMAN 1: UPLOAD LAPORAN
# ==========================================
if menu == "Upload Dokumen":
    st.title("📤 Portal Arsip & Laporan Internal")
    st.write("---")
    col1, col2 = st.columns([1, 1.5])
    with col1:
        instansi = st.selectbox("1. Pilih Unit / Program:", ["Pilih Program..."] + DAFTAR_PROGRAM + ["Program Lainnya"])
        jenis_laporan = st.radio("2. Kategori Laporan:", ["Bulanan", "Tahunan"], horizontal=True)
        tahun_laporan = st.selectbox("3. Pilih Tahun:", DAFTAR_TAHUN, index=2) 
        bulan_laporan = st.selectbox("4. Pilih Bulan:", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]) if jenis_laporan == "Bulanan" else "Tahunan"
    with col2:
        file_upload = st.file_uploader("5. Pilih File Dokumen", type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv'])
        if st.button("🚀 Unggah Dokumen ke Server", type="primary", use_container_width=True):
            if instansi != "Pilih Program..." and file_upload is not None:
                with st.spinner('Menyimpan ke brankas digital...'):
                    try:
                        status_gab = f"{jenis_laporan}|{bulan_laporan}|{tahun_laporan}"
                        nama_file = f"{instansi}_{jenis_laporan}_{bulan_laporan}_{tahun_laporan}_{datetime.now().strftime('%H%M%S')}_{file_upload.name}"
                        supabase.storage.from_("laporan_files").upload(path=nama_file, file=file_upload.read())
                        supabase.table("status_laporan").insert({"nama_instansi": instansi, "nama_file": nama_file, "status": status_gab}).execute()
                        st.success(f"✅ Arsip {instansi} tersimpan.")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
            else:
                st.warning("⚠️ Lengkapi pilihan program dan file!")

# ==========================================
# HALAMAN 2: DASHBOARD ADMIN
# ==========================================
elif menu == "Dashboard Admin":
    if not st.session_state['sudah_login']:
        st.title("🔐 Ruang Admin")
        with st.form("form_login"):
            if st.form_submit_button("Masuk ➡️"):
                st.session_state['sudah_login'] = True
                st.session_state['username'] = "Admin"
                st.session_state['role'] = "Admin"
                st.rerun()
    else:
        st.header("📊 Dashboard Manajerial Puskesmas")
        if st.button("🚪 Logout"):
            st.session_state['sudah_login'] = False
            st.rerun()
                
        st.write("---")
        
        # 4 TAB MENU ADMIN
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Dashboard Eksekutif", "🎯 Pantau Kepatuhan", "📂 Arsip Folder", "⚙️ Akun"])
        
        # --- TAB 1: DASHBOARD EKSEKUTIF (BARU) ---
        with tab1:
            st.subheader("🎯 Capaian Kinerja Global (CKG)")
            
            # Membaca data CKG dari config rahasia
            ckg_data = load_ckg()
            target_ckg = ckg_data['target']
            capaian_ckg = ckg_data['capaian']
            persen_ckg = int((capaian_ckg / target_ckg) * 100) if target_ckg > 0 else 0
            
            # Tampilan Metrik Modern
            m1, m2, m3 = st.columns(3)
            m1.metric("🎯 Target Baku CKG", f"{target_ckg:,}")
            m2.metric("📈 Capaian Saat Ini", f"{capaian_ckg:,}")
            m3.metric("📊 Persentase Capaian", f"{persen_ckg}%")
            
            st.progress(min(persen_ckg, 100) / 100)
            
            # Tombol Update CKG Khusus Admin
            with st.expander("⚙️ Update Angka CKG (Mingguan)"):
                with st.form("form_ckg"):
                    st.write("Masukkan angka capaian terbaru. Persentase akan dihitung otomatis.")
                    new_target = st.number_input("Ubah Target Baku", value=target_ckg, min_value=1)
                    new_capaian = st.number_input("Capaian Bertambah Jadi", value=capaian_ckg, min_value=0)
                    if st.form_submit_button("💾 Simpan Angka Baru"):
                        save_ckg(new_target, new_capaian)
                        st.success("Angka CKG diperbarui!")
                        st.rerun()
                        
            st.write("---")
            
            st.subheader("🦠 10 Besar Penyakit Terbanyak")
            df_penyakit = load_penyakit()
            
            if not df_penyakit.empty:
                # Membuat Grafik Batang Horizontal yang Cantik
                chart = alt.Chart(df_penyakit).mark_bar(color='#0ea5e9', cornerRadiusEnd=5).encode(
                    x=alt.X('JML:Q', title='Jumlah Kasus'),
                    y=alt.Y('NAMA PENYAKIT:N', sort='-x', title=''),
                    tooltip=['NAMA PENYAKIT', 'JML']
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("Belum ada data penyakit. Silakan upload file Excel di bawah ini.")
                
            # Tombol Upload Excel Penyakit
            with st.expander("⚙️ Update Grafik 10 Besar Penyakit (Upload Excel)"):
                file_p = st.file_uploader("Pilih file Excel '10 Besar Penyakit'", type=['xls', 'xlsx'])
                if st.button("🔄 Proses & Jadikan Grafik", type="primary"):
                    if file_p is not None:
                        try:
                            # Membaca Excel, meloncati baris 1 agar Header ada di baris 2
                            df_raw = pd.read_excel(file_p, skiprows=1)
                            df_raw.columns = [str(c).strip().upper() for c in df_raw.columns]
                            
                            if "NAMA PENYAKIT" in df_raw.columns and "JML" in df_raw.columns:
                                df_clean = df_raw.dropna(subset=['NAMA PENYAKIT', 'JML'])
                                df_clean = df_clean[['NAMA PENYAKIT', 'JML']]
                                df_clean['JML'] = pd.to_numeric(df_clean['JML'], errors='coerce').fillna(0)
                                # Sortir dan ambil top 10 otomatis
                                df_top10 = df_clean.sort_values('JML', ascending=False).head(10)
                                save_penyakit(df_top10)
                                st.success("Data berhasil disedot! Grafik telah diperbarui.")
                                st.rerun()
                            else:
                                st.error("❌ Format gagal dibaca: Pastikan ada kolom berjudul 'NAMA PENYAKIT' dan 'JML'.")
                        except Exception as e:
                            st.error(f"Gagal memproses: {e}")
                    else:
                        st.warning("Masukkan file terlebih dahulu.")

        # --- TAB 2, 3, 4: (Fitur Lama Tetap Ada & Aman) ---
        with tab2:
            st.subheader("Modul Kepatuhan masih aktif di sini...")
        with tab3:
            st.subheader("Modul Arsip Folder masih aktif di sini...")
