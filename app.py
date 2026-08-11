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
# CUSTOM CSS MODERN
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    .stButton>button { border-radius: 8px; font-weight: bold; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); background-color: #0284c7; color: white; border: none; }
    .stButton>button:hover { background-color: #0369a1; color: white; transform: translateY(-2px); }
    .login-box { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border-top: 5px solid #0284c7; }
    .kepatuhan-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
    .progress-bar-bg { background-color: #e2e8f0; border-radius: 10px; height: 14px; width: 100%; overflow: hidden; margin-top: 10px; }
    .progress-bar-fill { background: linear-gradient(90deg, #34d399 0%, #059669 100%); height: 100%; border-radius: 10px; transition: width 0.8s ease-in-out; }
    .badge-sudah { background-color: #ecfdf5; color: #065f46; padding: 8px 16px; border-radius: 20px; display: inline-block; margin: 5px; font-weight: bold; font-size: 13px; border: 1px solid #a7f3d0; }
    .badge-belum { background-color: #fef2f2; color: #991b1b; padding: 8px 16px; border-radius: 20px; display: inline-block; margin: 5px; font-weight: bold; font-size: 13px; border: 1px solid #fecaca; }
    .file-item { padding: 8px 0px; border-bottom: 1px solid #f1f5f9; }
    .file-item a { text-decoration: none; color: #0284c7; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("🏥 Portal Internal")
menu = st.sidebar.radio("Navigasi Utama:", ["Upload Dokumen", "Dashboard Admin"])

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
        file_upload = st.file_uploader("5. Pilih File Dokumen (PDF/Word/Excel)", type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv'])
        st.write("")
        if st.button("🚀 Unggah Dokumen", use_container_width=True):
            if instansi != "Pilih Program..." and file_upload is not None:
                with st.spinner('Menyimpan ke server aman...'):
                    try:
                        status_gab = f"{jenis_laporan}|{bulan_laporan}|{tahun_laporan}"
                        nama_file = f"{instansi}_{jenis_laporan}_{bulan_laporan}_{tahun_laporan}_{datetime.now().strftime('%H%M%S')}_{file_upload.name}"
                        supabase.storage.from_("laporan_files").upload(path=nama_file, file=file_upload.read())
                        supabase.table("status_laporan").insert({"nama_instansi": instansi, "nama_file": nama_file, "status": status_gab}).execute()
                        st.success(f"✅ Dokumen {instansi} berhasil diarsipkan.")
                    except Exception as e:
                        st.error(f"❌ Error saat menyimpan: {e}")
            else:
                st.warning("⚠️ Mohon lengkapi pilihan instansi dan file!")

# ==========================================
# HALAMAN 2: DASHBOARD ADMIN
# ==========================================
elif menu == "Dashboard Admin":
    if not st.session_state['sudah_login']:
        # TAMPILAN LOGIN MODERN
        st.write("")
        st.write("")
        col_L1, col_L2, col_L3 = st.columns([1, 1.5, 1])
        with col_L2:
            st.markdown("<div class='login-box'>", unsafe_allow_html=True)
            st.markdown("<h2 style='text-align: center; color: #0284c7;'>🔐 Sistem Internal</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: gray;'>Silakan login untuk mengakses data manajerial.</p>", unsafe_allow_html=True)
            with st.form("form_login"):
                input_user = st.text_input("Username")
                input_pass = st.text_input("Password", type="password")
                if st.form_submit_button("Masuk ke Dashboard ➡️", use_container_width=True):
                    cek_akun = supabase.table("akun_pengguna").select("*").eq("username", input_user).eq("password", input_pass).execute()
                    if len(cek_akun.data) > 0:
                        st.session_state['sudah_login'] = True
                        st.session_state['username'] = cek_akun.data[0]['username']
                        st.session_state['role'] = cek_akun.data[0]['role']
                        st.rerun()
                    else:
                        st.error("❌ Username atau Password salah!")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        # HEADER ADMIN
        col_header1, col_header2 = st.columns([3, 1])
        with col_header1:
            st.header(f"📊 Dashboard Manajerial Puskesmas")
            st.markdown(f"*Login sebagai: **{st.session_state['username']}** ({st.session_state['role']})*")
        with col_header2:
            if st.button("🚪 Keluar / Logout", use_container_width=True):
                st.session_state['sudah_login'] = False
                st.rerun()
                
        st.write("---")
        
        # TAB MENU ADMIN LENGKAP
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Dashboard Eksekutif", "🎯 Pantau Kepatuhan", "📂 Arsip Folder", "⚙️ Akun"])
        
        # --- TAB 1: DASHBOARD EKSEKUTIF ---
        with tab1:
            st.subheader("🎯 Capaian Kinerja Global (CKG)")
            
            ckg_data = load_ckg()
            target_ckg = ckg_data['target']
            capaian_ckg = ckg_data['capaian']
            persen_ckg = int((capaian_ckg / target_ckg) * 100) if target_ckg > 0 else 0
            
            m1, m2, m3 = st.columns(3)
            m1.metric("🎯 Target Baku CKG", f"{target_ckg:,}")
            m2.metric("📈 Capaian Saat Ini", f"{capaian_ckg:,}")
            m3.metric("📊 Persentase Capaian", f"{persen_ckg}%")
            
            st.markdown(f"""
            <div class="progress-bar-bg">
                <div class="progress-bar-fill" style="width: {min(persen_ckg, 100)}%;"></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            with st.expander("⚙️ Update Angka CKG (Akses Admin)"):
                with st.form("form_ckg"):
                    new_target = st.number_input("Target Baku", value=target_ckg, min_value=1)
                    new_capaian = st.number_input("Capaian Saat Ini", value=capaian_ckg, min_value=0)
                    if st.form_submit_button("💾 Simpan Angka Baru"):
                        save_ckg(new_target, new_capaian)
                        st.success("Angka CKG berhasil diperbarui!")
                        st.rerun()
                        
            st.write("---")
            st.subheader("🦠 10 Besar Penyakit Terbanyak")
            
            df_penyakit = load_penyakit()
            if not df_penyakit.empty:
                chart = alt.Chart(df_penyakit).mark_bar(color='#0284c7', cornerRadiusEnd=5).encode(
                    x=alt.X('JML:Q', title='Jumlah Kasus'),
                    y=alt.Y('NAMA PENYAKIT:N', sort='-x', title=''),
                    tooltip=['NAMA PENYAKIT', 'JML']
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("Belum ada data penyakit. Silakan upload file Excel di bawah ini.")
                
            with st.expander("⚙️ Update Grafik 10 Besar Penyakit (Upload Excel)"):
                file_p = st.file_uploader("Pilih file Excel '10 Besar Penyakit'", type=['xls', 'xlsx'])
                if st.button("🔄 Sedot Data & Jadikan Grafik"):
                    if file_p is not None:
                        try:
                            # PEMBACAAN EXCEL PINTAR (Bebas Spasi & Skip Baris)
                            df_raw = pd.read_excel(file_p)
                            df_raw.columns = df_raw.columns.astype(str).str.strip().str.upper()
                            
                            # Jika tidak ada kolom NAMA PENYAKIT, coba loncat 1 baris
                            if "NAMA PENYAKIT" not in df_raw.columns:
                                df_raw = pd.read_excel(file_p, skiprows=1)
                                df_raw.columns = df_raw.columns.astype(str).str.strip().str.upper()
                                
                            if "NAMA PENYAKIT" in df_raw.columns and "JML" in df_raw.columns:
                                df_clean = df_raw.dropna(subset=['NAMA PENYAKIT', 'JML'])
                                df_clean = df_clean[['NAMA PENYAKIT', 'JML']]
                                df_clean['JML'] = pd.to_numeric(df_clean['JML'], errors='coerce').fillna(0)
                                df_top10 = df_clean.sort_values('JML', ascending=False).head(10)
                                save_penyakit(df_top10)
                                st.success("✅ Data berhasil disedot!")
                                st.rerun()
                            else:
                                st.error("❌ Gagal menemukan kolom. Pastikan judul kolom tepat tertulis 'NAMA PENYAKIT' dan 'JML'.")
                        except Exception as e:
                            st.error(f"Gagal memproses file: {e}")
                    else:
                        st.warning("Pilih file terlebih dahulu.")

        # --- TAB 2: STATUS KEPATUHAN ---
        with tab2:
            st.subheader("Cek Kepatuhan Pengumpulan Laporan")
            
            def urai_status(teks):
                try:
                    parts = str(teks).split('|')
                    if len(parts) == 3: return parts[0], parts[1], parts[2]
                    return "Bulanan", teks, "2026" 
                except:
                    return "-", "-", "-"

            respon = supabase.table("status_laporan").select("*").execute()
            df = pd.DataFrame(respon.data) if len(respon.data) > 0 else pd.DataFrame()
            if not df.empty:
                df['Jenis Laporan'], df['Bulan'], df['Tahun'] = zip(*df['status'].map(urai_status))
                urutan_bulan = {"Januari":1, "Februari":2, "Maret":3, "April":4, "Mei":5, "Juni":6, "Juli":7, "Agustus":8, "September":9, "Oktober":10, "November":11, "Desember":12, "Tahunan":13}
                df['Urutan_Bulan'] = df['Bulan'].map(urutan_bulan)

            c1, c2, c3 = st.columns(3)
            with c1:
                pantau_tahun = st.selectbox("Pantau Tahun:", DAFTAR_TAHUN, index=2)
            with c2:
                pantau_jenis = st.radio("Pantau Kategori:", ["Bulanan", "Tahunan"], horizontal=True)
            with c3:
                if pantau_jenis == "Bulanan":
                    pantau_bulan = st.selectbox("Pantau Bulan:", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
                else:
                    pantau_bulan = "Tahunan"
            
            st.write("")
            if not df.empty:
                target_status = f"{pantau_jenis}|{pantau_bulan}|{pantau_tahun}"
                df_target = df[df['status'] == target_status]
                
                program_sudah = df_target['nama_instansi'].unique().tolist()
                program_belum = [p for p in DAFTAR_PROGRAM if p not in program_sudah]
                
                total_p = len(DAFTAR_PROGRAM)
                jml_sudah = len(program_sudah)
                persen_patuh = int((jml_sudah / total_p) * 100) if total_p > 0 else 0
                
                st.markdown(f"""
                <div style="background: white; padding: 20px; border-radius: 15px; border: 1px solid #f1f5f9; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 20px;">
                    <h4 style="margin-top: 0; color: #334155;">Tingkat Kepatuhan: <span style="color: #059669;">{persen_patuh}%</span></h4>
                    <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {persen_patuh}%;"></div></div>
                </div>
                """, unsafe_allow_html=True)
                
                col_sudah, col_belum = st.columns(2)
                with col_sudah:
                    st.markdown("<div class='kepatuhan-card'><h4>✅ Sudah Lapor</h4>", unsafe_allow_html=True)
                    if jml_sudah > 0:
                        st.markdown("".join([f"<span class='badge-sudah'>✔️ {p}</span>" for p in program_sudah]), unsafe_allow_html=True)
                    else:
                        st.write("Belum ada data.")
                    st.markdown("</div>", unsafe_allow_html=True)
                        
                with col_belum:
                    st.markdown("<div class='kepatuhan-card'><h4>⏳ Belum Lapor</h4>", unsafe_allow_html=True)
                    if len(program_belum) > 0:
                        st.markdown("".join([f"<span class='badge-belum'>⏳ {p}</span>" for p in program_belum]), unsafe_allow_html=True)
                    else:
                        st.success("Semua program sudah lapor!")
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("Belum ada data arsip di database.")

        # --- TAB 3: ARSIP DOKUMEN ---
        with tab3:
            st.subheader("📂 Ruang Arsip Digital (Explorer)")
            if not df.empty:
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    filter_tahun = st.selectbox("Filter Tahun Arsip:", ["Semua Tahun"] + DAFTAR_TAHUN, index=0)
                
                df_arsip = df.copy()
                if filter_tahun != "Semua Tahun":
                    df_arsip = df_arsip[df_arsip['Tahun'] == filter_tahun]
                
                if not df_arsip.empty:
                    grup_utama = df_arsip.groupby(['nama_instansi', 'Jenis Laporan', 'Tahun'])
                    for (program, jenis, tahun), data_grup in grup_utama:
                        with st.expander(f"📁 {program} - {jenis} ({tahun})"):
                            data_grup = data_grup.sort_values('Urutan_Bulan')
                            grup_bulan = data_grup.groupby('Bulan', sort=False)
                            for bulan, data_bulan in grup_bulan:
                                st.markdown(f"**📂 {bulan}**")
                                for _, row in data_bulan.iterrows():
                                    wts = pd.to_datetime(row['created_at'])
                                    if wts.tzinfo is None: wts = wts.tz_localize('UTC')
                                    waktu = wts.tz_convert('Asia/Jakarta').strftime('%d-%m-%Y %H:%M')
                                    nf = row['nama_file']
                                    link_dl = f"{SUPABASE_URL}/storage/v1/object/public/laporan_files/{nf}"
                                    
                                    st.markdown(f"""
                                        <div class='file-item'>
                                            &nbsp;&nbsp;&nbsp;&nbsp; 📄 {nf} <br>
                                            &nbsp;&nbsp;&nbsp;&nbsp; <small style="color:gray;">🕒 {waktu} WIB</small> | 
                                            <a href="{link_dl}" target="_blank">📥 Download File</a>
                                        </div>
                                    """, unsafe_allow_html=True)
                else:
                    st.info(f"Belum ada arsip untuk tahun {filter_tahun}.")
                
                st.write("---")
                if st.session_state['role'] == 'Admin':
                    with st.expander("🗑️ Hapus Dokumen Permanen (Admin)"):
                        hapus_file = st.selectbox("Pilih file yang salah upload:", df['nama_file'].tolist())
                        if st.button("🚨 Hapus File Ini", type="primary"):
                            supabase.table("status_laporan").delete().eq("nama_file", hapus_file).execute()
                            supabase.storage.from_("laporan_files").remove([hapus_file])
                            st.success("File dihapus!")
                            st.rerun()
            else:
                st.info("Gudang arsip masih kosong.")

        # --- TAB 4: MANAJEMEN AKUN ---
        with tab4:
            st.subheader("Manajemen Hak Akses & Akun")
            if st.session_state['role'] == 'Admin':
                with st.form("form_tambah_akun"):
                    baru_user = st.text_input("Username Baru")
                    baru_pass = st.text_input("Password Baru")
                    baru_role = st.selectbox("Hak Akses", ["Kepala Puskesmas", "Admin", "Tim TU"])
                    if st.form_submit_button("Buat Akun ✅"):
                        supabase.table("akun_pengguna").insert({"username": baru_user, "password": baru_pass, "role": baru_role}).execute()
                        st.success(f"Akun '{baru_user}' dibuat!")
            else:
                st.warning("Hanya Admin utama yang bisa mengakses menu ini.")
