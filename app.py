import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

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
    st.session_state['id_puskesmas'] = ""

st.set_page_config(page_title="Simpel Puskesmas", page_icon="🏥", layout="centered")

# ==========================================
# 2. VARIABEL & DAFTAR UNIT
# ==========================================
DAFTAR_PROGRAM = ["Farmasi", "Gizi", "Ausrem", "KIA/KB", "Promkes", "Kesling", "P2P", "Laboratorium", "Tata Usaha"]
DAFTAR_ROLE = ["Admin", "Kepala Puskesmas"] + DAFTAR_PROGRAM
DAFTAR_TAHUN = ["2024", "2025", "2026", "2027", "2028", "2029"]
LIST_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

# ==========================================
# 3. SUPER CSS: UI PREMIUM & PEMBERSIH WATERMARK
# ==========================================
st.markdown("""
    <style>
    html, body, [class*="css"], [data-testid="stAppViewContainer"], .main, .block-container {
        overscroll-behavior-y: none !important;
        overscroll-behavior-x: none !important;
        touch-action: pan-y !important;
    }
    .stApp { 
        background-color: #f8fafc !important; 
        font-family: 'Segoe UI', Roboto, sans-serif; 
    }
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    .viewerBadge_link__1S137 {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    
    .block-container { padding-top: 15px !important; padding-bottom: 80px !important; }
    
    .mobile-card {
        background: #ffffff; 
        padding: 24px; 
        border-radius: 16px;
        box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.06);
        border: 1px solid #f1f5f9;
        margin-bottom: 20px;
    }
    
    .stButton>button {
        border-radius: 12px !important; 
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: white !important; 
        font-weight: 600 !important; 
        border: none !important; 
        padding: 10px 20px !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.2) !important; 
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(2, 132, 199, 0.3) !important; }
    
    .btn-logout>button { background: linear-gradient(135deg, #ef4444, #b91c1c) !important; padding: 5px 15px !important;}
    .stTextInput input, .stSelectbox select { border-radius: 8px !important; }
    
    .badge-sudah { background-color: #ecfdf5; color: #059669; padding: 6px 12px; border-radius: 20px; font-weight: bold; font-size: 12px; display: inline-block; margin: 3px; border: 1px solid #a7f3d0;}
    .badge-belum { background-color: #fef2f2; color: #dc2626; padding: 6px 12px; border-radius: 20px; font-weight: bold; font-size: 12px; display: inline-block; margin: 3px; border: 1px solid #fecaca;}
    
    .file-item { padding: 12px 0px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center;}
    .file-item a { text-decoration: none; color: white; background-color: #0ea5e9; padding: 6px 15px; border-radius: 20px; font-weight: bold; font-size: 12px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. HALAMAN LOGIN
# ==========================================
if not st.session_state['sudah_login']:
    st.markdown("<div class='mobile-card' style='margin-top: 10vh;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #0284c7; margin-bottom: 5px;'>🏥 Simpel Puskesmas</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 14px; margin-bottom:25px;'>Portal Laporan & Arsip Digital</p>", unsafe_allow_html=True)
    with st.form("form_login"):
        input_user = st.text_input("👤 Username")
        input_pass = st.text_input("🔑 Password", type="password")
        st.write("")
        if st.form_submit_button("Masuk Aplikasi ➡️"):
            cek_akun = supabase.table("akun_pengguna").select("*").eq("username", input_user).eq("password", input_pass).execute()
            if len(cek_akun.data) > 0:
                st.session_state['sudah_login'] = True
                st.session_state['username'] = cek_akun.data[0]['username']
                st.session_state['role'] = cek_akun.data[0]['role']
                # Tangkap id_puskesmas dari database (jika kosong, set default PKM_UTAMA)
                pkm_db = cek_akun.data[0].get('id_puskesmas')
                st.session_state['id_puskesmas'] = pkm_db if pkm_db else "PKM_UTAMA"
                st.rerun()
            else:
                st.error("❌ Username atau Password salah!")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# 5. HALAMAN UTAMA (DENGAN ISOLASI DATA MULTI-TENANCY)
# ==========================================
pkm_aktif = st.session_state['id_puskesmas']

# Ambil data HANYA milik Puskesmas yang sedang login
respon = supabase.table("status_laporan").select("*").eq("id_puskesmas", pkm_aktif).execute()
df_status = pd.DataFrame(respon.data) if len(respon.data) > 0 else pd.DataFrame()

# HEADER PROFIL
col_prof1, col_prof2 = st.columns([3, 1.5])
with col_prof1:
    st.markdown(f"**Halo, {st.session_state['username']}!** 👋<br><small style='color:#64748b;'>Instansi: {pkm_aktif} | Akses: {st.session_state['role']}</small>", unsafe_allow_html=True)
with col_prof2:
    st.markdown("<div class='btn-logout'>", unsafe_allow_html=True)
    if st.button("🚪 Logout"):
        st.session_state['sudah_login'] = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.write("---")

# DROPDOWN MENU UTAMA
if st.session_state['role'] == 'Admin':
    menu = st.selectbox("📌 Navigasi Menu:", ["📤 Upload Laporan", "📊 Pantau Kepatuhan", "📂 Gudang Arsip", "⚙️ Kelola Akun"])
elif st.session_state['role'] == 'Kepala Puskesmas':
    menu = st.selectbox("📌 Navigasi Menu:", ["📊 Pantau Kepatuhan", "📂 Gudang Arsip"])
else:
    menu = st.selectbox("📌 Navigasi Menu:", ["📤 Upload Laporan", "📊 Pantau Kepatuhan", "📂 Gudang Arsip"])

st.write("") 

# ------------------------------------------
# MENU: UPLOAD LAPORAN
# ------------------------------------------
if menu == "📤 Upload Laporan":
    st.markdown("<div class='mobile-card'>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: #0284c7; margin-top:0; margin-bottom: 20px;'>📤 Kirim Laporan</h3>", unsafe_allow_html=True)
    
    if st.session_state['role'] in DAFTAR_PROGRAM:
        instansi = st.selectbox("1. Unit / Program:", [st.session_state['role']], disabled=True)
    else:
        instansi = st.selectbox("1. Pilih Unit / Program:", ["Pilih Program..."] + DAFTAR_PROGRAM)
        
    jenis_laporan = st.radio("2. Kategori Laporan:", ["Bulanan", "Tahunan"], horizontal=True)
    tahun_laporan = st.selectbox("3. Tahun:", DAFTAR_TAHUN, index=2) 
    bulan_laporan = st.selectbox("4. Bulan:", LIST_BULAN) if jenis_laporan == "Bulanan" else "Tahunan"
    file_upload = st.file_uploader("5. Pilih File (PDF/Excel)", type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv'])
    
    st.write("")
    if st.button("🚀 Upload Sekarang"):
        if instansi != "Pilih Program..." and file_upload is not None:
            with st.spinner('Mengirim ke server aman...'):
                try:
                    timestamp = datetime.now().strftime('%d%m%Y_%H%M%S')
                    nama_file = f"{pkm_aktif}_{instansi}_{jenis_laporan}_{bulan_laporan}_{tahun_laporan}_{timestamp}_{file_upload.name}"
                    status_gab = f"{jenis_laporan}|{bulan_laporan}|{tahun_laporan}"
                    
                    supabase.storage.from_("laporan_files").upload(path=nama_file, file=file_upload.read())
                    supabase.table("status_laporan").insert({
                        "nama_instansi": instansi, 
                        "nama_file": nama_file, 
                        "status": status_gab,
                        "id_puskesmas": pkm_aktif
                    }).execute()
                    st.success("✅ Laporan berhasil terkirim ke server!")
                except Exception as e:
                    st.error(f"❌ Gagal: {e}")
        else:
            st.warning("⚠️ Mohon lengkapi unit dan masukkan filenya!")
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------
# MENU: PANTAU KEPATUHAN
# ------------------------------------------
elif menu == "📊 Pantau Kepatuhan":
    st.markdown("<div class='mobile-card'>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: #0284c7; margin-top:0; margin-bottom: 20px;'>🎯 Pantau Kepatuhan</h3>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1: dash_jenis = st.selectbox("Kategori:", ["Bulanan", "Tahunan"])
    with c2: dash_tahun = st.selectbox("Tahun:", DAFTAR_TAHUN, index=2)
    dash_bulan = st.selectbox("Bulan:", LIST_BULAN) if dash_jenis == "Bulanan" else "Tahunan"
    
    program_sudah = []
    program_belum = DAFTAR_PROGRAM
    
    if not df_status.empty:
        target_status = f"{dash_jenis}|{dash_bulan}|{dash_tahun}"
        df_target = df_status[df_status['status'] == target_status]
        program_sudah = df_target['nama_instansi'].unique().tolist()
        program_belum = [p for p in DAFTAR_PROGRAM if p not in program_sudah]
    
    jml_sudah = len(program_sudah)
    persen = int((jml_sudah / len(DAFTAR_PROGRAM)) * 100)
    
    st.markdown(f"**Tingkat Kepatuhan {pkm_aktif}: {persen}%**")
    st.progress(persen)
    
    st.markdown("#### ✅ Sudah Lapor")
    if program_sudah:
        st.markdown("".join([f"<span class='badge-sudah'>✔️ {p}</span>" for p in program_sudah]), unsafe_allow_html=True)
    else: st.info("Belum ada unit yang lapor.")
        
    st.markdown("#### ⏳ Belum Lapor")
    if program_belum:
        st.markdown("".join([f"<span class='badge-belum'>⏳ {p}</span>" for p in program_belum]), unsafe_allow_html=True)
    else: st.success("Luar Biasa! 100% Lapor! 🎉")

    st.write("---")
    data_rekap = [{"Unit": p, "Status": "Sudah Lapor" if p in program_sudah else "Belum Lapor"} for p in DAFTAR_PROGRAM]
    csv_rekap = pd.DataFrame(data_rekap).to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Rekap Excel", data=csv_rekap, file_name=f"Rekap_{pkm_aktif}_{dash_bulan}.csv", mime="text/csv")
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------
# MENU: GUDANG ARSIP
# ------------------------------------------
elif menu == "📂 Gudang Arsip":
    st.markdown("<div class='mobile-card'>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: #0284c7; margin-top:0; margin-bottom: 20px;'>📂 Gudang Arsip</h3>", unsafe_allow_html=True)
    
    if not df_status.empty:
        def urai_status(teks):
            try:
                p = str(teks).split('|')
                if len(p) == 3: return p[0], p[1], p[2]
                return "Bulanan", teks, "2026"
            except: return "-", "-", "-"
        
        df_arsip = df_status.copy()
        df_arsip['Jenis Laporan'], df_arsip['Bulan'], df_arsip['Tahun'] = zip(*df_arsip['status'].map(urai_status))
        urutan_bulan = {"Januari":1, "Februari":2, "Maret":3, "April":4, "Mei":5, "Juni":6, "Juli":7, "Agustus":8, "September":9, "Oktober":10, "November":11, "Desember":12, "Tahunan":13}
        df_arsip['Urutan_Bulan'] = df_arsip['Bulan'].map(urutan_bulan)

        if st.session_state['role'] in DAFTAR_PROGRAM:
            df_arsip = df_arsip[df_arsip['nama_instansi'] == st.session_state['role']]
            filter_tahun_arsip = st.selectbox("Pilih Tahun:", DAFTAR_TAHUN, index=2)
            df_arsip = df_arsip[df_arsip['Tahun'] == filter_tahun_arsip]
        else:
            filter_tahun_arsip = st.selectbox("Pilih Tahun:", ["Semua Tahun"] + DAFTAR_TAHUN, index=0)
            if filter_tahun_arsip != "Semua Tahun": df_arsip = df_arsip[df_arsip['Tahun'] == filter_tahun_arsip]
        
        if not df_arsip.empty:
            grup_utama = df_arsip.groupby(['nama_instansi', 'Jenis Laporan', 'Tahun'])
            for (program, jenis, tahun), data_grup in grup_utama:
                with st.expander(f"📁 {program} ({tahun})"):
                    data_grup = data_grup.sort_values('Urutan_Bulan')
                    grup_bulan = data_grup.groupby('Bulan', sort=False)
                    for bulan, data_bulan in grup_bulan:
                        st.markdown(f"**{bulan}**")
                        for _, row in data_bulan.iterrows():
                            nf = row['nama_file']
                            link_dl = f"{SUPABASE_URL}/storage/v1/object/public/laporan_files/{nf}"
                            # Menampilkan nama file asli tanpa prefix id_puskesmas
                            nama_tampil = "_".join(nf.split('_')[1:]) if len(nf.split('_')) > 1 else nf
                            st.markdown(f"<div class='file-item'><span>📄 {nama_tampil[:25]}...</span><a href='{link_dl}' target='_blank'>Unduh</a></div>", unsafe_allow_html=True)
        else: st.info(f"Belum ada arsip pada filter ini.")
        
        if st.session_state['role'] == 'Admin':
            st.write("---")
            with st.expander("🗑️ Hapus Dokumen Permanen"):
                hapus_file = st.selectbox("Pilih file:", df_status['nama_file'].tolist())
                if st.button("Hapus Permanen", type="primary"):
                    supabase.table("status_laporan").delete().eq("nama_file", hapus_file).execute()
                    supabase.storage.from_("laporan_files").remove([hapus_file])
                    st.success("File Terhapus!")
                    st.rerun()
    else: st.info("Gudang Arsip saat ini masih kosong.")
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------
# MENU: KELOLA AKUN (DENGAN INPUT ID PUSKESMAS)
# ------------------------------------------
elif menu == "⚙️ Kelola Akun" and st.session_state['role'] == 'Admin':
    st.markdown("<div class='mobile-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #0284c7; margin-top:0; margin-bottom: 20px;'>⚙️ Manajemen Akun Multi-Puskesmas</h3>", unsafe_allow_html=True)
    
    with st.form("form_tambah_akun"):
        baru_pkm = st.text_input("ID Puskesmas / Instansi (Contoh: PKM_CILEDUG)")
        baru_user = st.text_input("Username (Tanpa Spasi)")
        baru_pass = st.text_input("Password")
        baru_role = st.selectbox("Role / Unit Bagian", DAFTAR_ROLE)
        st.write("")
        if st.form_submit_button("Simpan Akun ✅"):
            if baru_pkm and baru_user and baru_pass:
                cek = supabase.table("akun_pengguna").select("*").eq("username", baru_user).execute()
                if len(cek.data) > 0: st.error("❌ Username sudah terpakai!")
                else:
                    supabase.table("akun_pengguna").insert({
                        "username": baru_user.replace(" ", ""), 
                        "password": baru_pass, 
                        "role": baru_role,
                        "id_puskesmas": baru_pkm.upper().replace(" ", "_")
                    }).execute()
                    st.success(f"Akun '{baru_user}' untuk Puskesmas '{baru_pkm}' berhasil didaftarkan!")
            else: st.warning("Mohon isi semua data (ID Puskesmas, Username, Password) dengan lengkap.")
            
    st.write("---")
    st.markdown("**Daftar Akun Terdaftar:**")
    res_akun = supabase.table("akun_pengguna").select("username, role, id_puskesmas").execute()
    if len(res_akun.data) > 0:
        df_akun = pd.DataFrame(res_akun.data)
        df_akun.columns = ["Username", "Role / Unit", "ID Puskesmas"]
        st.dataframe(df_akun, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)
