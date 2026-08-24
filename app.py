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

# Layout lebih rapi
st.set_page_config(page_title="Simpel Puskesmas", page_icon="🏥", layout="centered")

# ==========================================
# 2. VARIABEL & DAFTAR UNIT
# ==========================================
DAFTAR_PROGRAM = ["Farmasi", "Gizi", "Ausrem", "KIA/KB", "Promkes", "Kesling", "P2P", "Laboratorium", "Tata Usaha"]
DAFTAR_ROLE = ["Admin", "Kepala Puskesmas"] + DAFTAR_PROGRAM
DAFTAR_TAHUN = ["2024", "2025", "2026", "2027", "2028", "2029"]
LIST_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

# ==========================================
# 3. SUPER CSS: UI/UX MODERN & ELEGAN (STARTUP STYLE)
# ==========================================
st.markdown("""
    <style>
    /* Mengambil Font Premium dari Google */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    /* Reset Dasar & Anti Reload */
    html, body, [class*="css"], [data-testid="stAppViewContainer"], .main, .block-container {
        overscroll-behavior-y: none !important;
        overscroll-behavior-x: none !important;
        touch-action: pan-y !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    /* Background Lembut Mewah */
    .stApp { 
        background-color: #f4f7f9 !important; 
    }
    
    /* Menghilangkan Sampah Streamlit */
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    
    /* Padding Layar HP */
    .block-container { padding-top: 10px !important; padding-bottom: 80px !important; max-width: 600px; }
    
    /* KARTU ELEGAN (Glassmorphism ringan) */
    .mobile-card {
        background: #ffffff; 
        padding: 30px 25px; 
        border-radius: 24px;
        box-shadow: 0 10px 40px -10px rgba(0,0,0,0.08);
        border: 1px solid rgba(255,255,255,0.7);
        margin-bottom: 25px;
    }
    
    /* TOMBOL UTAMA (Efek Glow & Hover) */
    .stButton>button {
        border-radius: 14px !important; 
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%) !important;
        color: white !important; 
        font-weight: 700 !important; 
        font-size: 15px !important;
        border: none !important; 
        padding: 12px 20px !important;
        box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.39) !important; 
        width: 100%;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover { 
        transform: translateY(-3px) !important; 
        box-shadow: 0 6px 20px 0 rgba(37, 99, 235, 0.4) !important; 
    }
    
    /* TOMBOL LOGOUT (Merah Elegan) */
    .btn-logout>button { 
        background: linear-gradient(135deg, #ef4444 0%, #f87171 100%) !important; 
        box-shadow: 0 4px 14px 0 rgba(239, 68, 68, 0.3) !important;
        padding: 8px 15px !important;
        border-radius: 12px !important;
    }
    
    /* KOLOM INPUT & SELECTBOX HALUS */
    .stTextInput>div>div>input, .stSelectbox>div>div>div { 
        border-radius: 12px !important; 
        border: 1px solid #e2e8f0 !important; 
        padding: 12px 16px !important;
        box-shadow: none !important;
        background-color: #f8fafc !important;
        color: #1e293b !important;
        font-weight: 500 !important;
    }
    .stTextInput>div>div>input:focus, .stSelectbox>div>div>div:focus {
        border-color: #3b82f6 !important;
        background-color: #ffffff !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
    }
    
    /* BADGE STATUS MODERN */
    .badge-sudah { background-color: #dcfce7; color: #166534; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 12px; display: inline-block; margin: 4px 2px; border: 1px solid #bbf7d0;}
    .badge-belum { background-color: #fee2e2; color: #991b1b; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 12px; display: inline-block; margin: 4px 2px; border: 1px solid #fecaca;}
    
    /* LIST DOKUMEN */
    .file-item { padding: 16px 0px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center;}
    .file-item a { text-decoration: none; color: white; background-color: #0284c7; padding: 8px 18px; border-radius: 20px; font-weight: 600; font-size: 12px; transition: 0.2s;}
    .file-item a:hover { background-color: #0369a1; }
    
    /* HEADER TEKS */
    h2, h3 { color: #0f172a !important; font-weight: 800 !important; letter-spacing: -0.5px;}
    p { color: #475569; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. HALAMAN LOGIN (DESAIN STARTUP)
# ==========================================
if not st.session_state['sudah_login']:
    st.write("")
    st.write("")
    st.markdown("<div class='mobile-card'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #1e293b; margin-bottom: 5px; font-size: 28px;'>✨ Simpel PKM</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; font-size: 14px; margin-bottom:30px;'>Workspace Laporan Digital</p>", unsafe_allow_html=True)
    with st.form("form_login"):
        input_user = st.text_input("Username", placeholder="Ketik username Anda...")
        input_pass = st.text_input("Password", type="password", placeholder="Ketik password...")
        st.write("")
        if st.form_submit_button("Masuk Sekarang 🚀"):
            cek_akun = supabase.table("akun_pengguna").select("*").eq("username", input_user).eq("password", input_pass).execute()
            if len(cek_akun.data) > 0:
                st.session_state['sudah_login'] = True
                st.session_state['username'] = cek_akun.data[0]['username']
                st.session_state['role'] = cek_akun.data[0]['role']
                pkm_db = cek_akun.data[0].get('id_puskesmas')
                st.session_state['id_puskesmas'] = pkm_db if pkm_db else "PKM_UTAMA"
                st.rerun()
            else:
                st.error("❌ Username atau Password salah!")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# 5. HALAMAN UTAMA
# ==========================================
pkm_aktif = st.session_state['id_puskesmas']

respon = supabase.table("status_laporan").select("*").eq("id_puskesmas", pkm_aktif).execute()
df_status = pd.DataFrame(respon.data) if len(respon.data) > 0 else pd.DataFrame()

# HEADER PROFIL ELEGAN
st.markdown("<div class='mobile-card' style='padding: 20px; margin-bottom: 15px;'>", unsafe_allow_html=True)
col_prof1, col_prof2 = st.columns([3, 1.2])
with col_prof1:
    st.markdown(f"<h3 style='margin:0; font-size:18px;'>Halo, {st.session_state['username']}! 👋</h3><p style='margin:0; font-size:13px; color:#64748b;'>🏢 {pkm_aktif} | 🔑 {st.session_state['role']}</p>", unsafe_allow_html=True)
with col_prof2:
    st.markdown("<div class='btn-logout'>", unsafe_allow_html=True)
    if st.button("🚪 Keluar"):
        st.session_state['sudah_login'] = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# MENU NAVIGASI
st.markdown("<p style='font-weight: 600; color: #334155; margin-bottom: -10px; padding-left: 5px;'>Pilih Menu Aplikasi:</p>", unsafe_allow_html=True)
if st.session_state['role'] == 'Admin':
    menu = st.selectbox("Navigasi", ["📤 Kirim Laporan", "📊 Pantau Kepatuhan", "📂 Gudang Arsip", "⚙️ Kelola Akun"], label_visibility="collapsed")
elif st.session_state['role'] == 'Kepala Puskesmas':
    menu = st.selectbox("Navigasi", ["📊 Pantau Kepatuhan", "📂 Gudang Arsip"], label_visibility="collapsed")
else:
    menu = st.selectbox("Navigasi", ["📤 Kirim Laporan", "📊 Pantau Kepatuhan", "📂 Gudang Arsip"], label_visibility="collapsed")

st.write("") 

# ------------------------------------------
# MENU: UPLOAD LAPORAN
# ------------------------------------------
if menu == "📤 Kirim Laporan":
    st.markdown("<div class='mobile-card'>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: #1e293b; margin-top:0; margin-bottom: 20px;'>📤 Kirim Dokumen</h3>", unsafe_allow_html=True)
    
    if st.session_state['role'] in DAFTAR_PROGRAM:
        instansi = st.selectbox("1. Unit / Program:", [st.session_state['role']], disabled=True)
    else:
        instansi = st.selectbox("1. Pilih Unit / Program:", ["Pilih Program..."] + DAFTAR_PROGRAM)
        
    jenis_laporan = st.radio("2. Kategori Laporan:", ["Bulanan", "Tahunan"], horizontal=True)
    
    c1, c2 = st.columns(2)
    with c1: tahun_laporan = st.selectbox("3. Tahun:", DAFTAR_TAHUN, index=2) 
    with c2: bulan_laporan = st.selectbox("4. Bulan:", LIST_BULAN) if jenis_laporan == "Bulanan" else st.selectbox("4. Bulan:", ["Tahunan"], disabled=True)
    
    st.write("")
    file_upload = st.file_uploader("5. Pilih File (PDF/Excel)", type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv'])
    
    st.write("")
    if st.button("Kirim Laporan Sekarang ✨"):
        if instansi != "Pilih Program..." and file_upload is not None:
            with st.spinner('Menyandikan data ke server aman...'):
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
                    st.success("✅ Laporan berhasil diamankan di server!")
                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan: {e}")
        else:
            st.warning("⚠️ Mohon lengkapi unit dan lampirkan filenya.")
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------
# MENU: PANTAU KEPATUHAN
# ------------------------------------------
elif menu == "📊 Pantau Kepatuhan":
    st.markdown("<div class='mobile-card'>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: #1e293b; margin-top:0; margin-bottom: 20px;'>📊 Kepatuhan Lapor</h3>", unsafe_allow_html=True)
    
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
    
    # Visualisasi Progress Bar Elegan
    st.markdown(f"<p style='font-size: 14px; margin-bottom: 5px;'>Progress Kepatuhan: <strong style='color:#0f172a;'>{persen}%</strong></p>", unsafe_allow_html=True)
    st.progress(persen)
    st.write("")
    
    st.markdown("<p style='font-weight: 700; color: #166534; margin-bottom: 5px;'>✨ Unit Selesai Lapor</p>", unsafe_allow_html=True)
    if program_sudah:
        st.markdown("".join([f"<span class='badge-sudah'>✔️ {p}</span>" for p in program_sudah]), unsafe_allow_html=True)
    else: st.info("Belum ada data masuk.")
        
    st.write("")
    st.markdown("<p style='font-weight: 700; color: #991b1b; margin-bottom: 5px;'>⏳ Menunggu Laporan</p>", unsafe_allow_html=True)
    if program_belum:
        st.markdown("".join([f"<span class='badge-belum'>⏳ {p}</span>" for p in program_belum]), unsafe_allow_html=True)
    else: st.success("Luar Biasa! Semua unit sudah lapor! 🎉")

    st.write("---")
    data_rekap = [{"Unit": p, "Status": "Sudah Lapor" if p in program_sudah else "Belum Lapor"} for p in DAFTAR_PROGRAM]
    csv_rekap = pd.DataFrame(data_rekap).to_csv(index=False).encode('utf-8')
    st.download_button("📥 Unduh Rekap Data (Excel)", data=csv_rekap, file_name=f"Rekap_{pkm_aktif}_{dash_bulan}.csv", mime="text/csv")
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------
# MENU: GUDANG ARSIP
# ------------------------------------------
elif menu == "📂 Gudang Arsip":
    st.markdown("<div class='mobile-card'>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: #1e293b; margin-top:0; margin-bottom: 20px;'>📂 Pusat Dokumen</h3>", unsafe_allow_html=True)
    
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
        
        st.write("")
        if not df_arsip.empty:
            grup_utama = df_arsip.groupby(['nama_instansi', 'Jenis Laporan', 'Tahun'])
            for (program, jenis, tahun), data_grup in grup_utama:
                with st.expander(f"📁 {program} ({tahun})"):
                    data_grup = data_grup.sort_values('Urutan_Bulan')
                    grup_bulan = data_grup.groupby('Bulan', sort=False)
                    for bulan, data_bulan in grup_bulan:
                        st.markdown(f"<p style='font-weight:700; color:#3b82f6; margin-top:10px;'>{bulan}</p>", unsafe_allow_html=True)
                        for _, row in data_bulan.iterrows():
                            nf = row['nama_file']
                            link_dl = f"{SUPABASE_URL}/storage/v1/object/public/laporan_files/{nf}"
                            nama_tampil = "_".join(nf.split('_')[1:]) if len(nf.split('_')) > 1 else nf
                            st.markdown(f"<div class='file-item'><span style='font-weight:500; color:#475569;'>📄 {nama_tampil[:22]}...</span><a href='{link_dl}' target='_blank'>Unduh</a></div>", unsafe_allow_html=True)
        else: st.info(f"Belum ada arsip pada filter ini.")
        
        if st.session_state['role'] == 'Admin':
            st.write("---")
            with st.expander("🗑️ Hapus Dokumen Permanen"):
                hapus_file = st.selectbox("Pilih file yang akan dihapus:", df_status['nama_file'].tolist())
                st.write("")
                if st.button("Hapus Permanen ⚠️", type="primary"):
                    supabase.table("status_laporan").delete().eq("nama_file", hapus_file).execute()
                    supabase.storage.from_("laporan_files").remove([hapus_file])
                    st.success("File Terhapus!")
                    st.rerun()
    else: st.info("Gudang Arsip masih kosong.")
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------------------
# MENU: KELOLA AKUN
# ------------------------------------------
elif menu == "⚙️ Kelola Akun" and st.session_state['role'] == 'Admin':
    st.markdown("<div class='mobile-card'>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: #1e293b; margin-top:0; margin-bottom: 20px;'>⚙️ Kontrol Admin ({pkm_aktif})</h3>", unsafe_allow_html=True)
    
    with st.form("form_tambah_akun"):
        st.markdown(f"<p style='font-weight:600;'>Tambah Akun Baru</p>", unsafe_allow_html=True)
        baru_user = st.text_input("Username Baru", placeholder="Tanpa spasi...")
        baru_pass = st.text_input("Password", type="password", placeholder="Buat sandi yang kuat...")
        baru_role = st.selectbox("Role / Unit Bagian", DAFTAR_ROLE)
        st.write("")
        if st.form_submit_button("Daftarkan Akun ✅"):
            if baru_user and baru_pass:
                cek = supabase.table("akun_pengguna").select("*").eq("username", baru_user).execute()
                if len(cek.data) > 0: st.error("❌ Username sudah terpakai di sistem!")
                else:
                    supabase.table("akun_pengguna").insert({
                        "username": baru_user.replace(" ", ""), 
                        "password": baru_pass, 
                        "role": baru_role,
                        "id_puskesmas": pkm_aktif  
                    }).execute()
                    st.success(f"Akun '{baru_user}' berhasil didaftarkan!")
            else: st.warning("Mohon isi Username dan Password.")
            
    st.write("---")
    st.markdown(f"<p style='font-weight:600;'>📋 Daftar Pengguna Aktif</p>", unsafe_allow_html=True)
    
    res_akun = supabase.table("akun_pengguna").select("username, role, id_puskesmas").eq("id_puskesmas", pkm_aktif).execute()
    if len(res_akun.data) > 0:
        df_akun = pd.DataFrame(res_akun.data)
        df_akun.columns = ["Username", "Role / Unit", "ID Puskesmas"]
        st.dataframe(df_akun, use_container_width=True, hide_index=True)
    else:
        st.write("Belum ada akun lain terdaftar.")
    
    st.markdown("</div>", unsafe_allow_html=True)

    # MENU KEAMANAN
    st.markdown("<div class='mobile-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #1e293b; margin-top:0; margin-bottom: 20px;'>🔐 Keamanan & Sandi</h3>", unsafe_allow_html=True)
    with st.form("form_ganti_password"):
        pass_lama = st.text_input("Password Saat Ini", type="password")
        pass_baru = st.text_input("Password Baru", type="password")
        pass_konfirmasi = st.text_input("Ulangi Password Baru", type="password")
        st.write("")
        if st.form_submit_button("Perbarui Keamanan 🔒"):
            if pass_lama and pass_baru and pass_konfirmasi:
                cek_lama = supabase.table("akun_pengguna").select("*").eq("username", st.session_state['username']).eq("password", pass_lama).execute()
                if len(cek_lama.data) > 0:
                    if pass_baru == pass_konfirmasi:
                        supabase.table("akun_pengguna").update({"password": pass_baru}).eq("username", st.session_state['username']).execute()
                        st.success("✅ Sandi berhasil diperbarui!")
                    else:
                        st.error("❌ Sandi baru dan konfirmasi tidak cocok!")
                else:
                    st.error("❌ Sandi lama salah!")
            else:
                st.warning("⚠️ Mohon lengkapi semua isian.")
    st.markdown("</div>", unsafe_allow_html=True)
