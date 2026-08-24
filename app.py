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

st.set_page_config(page_title="Sistem Laporan Puskesmas", page_icon="🏥", layout="wide")

# ==========================================
# 2. VARIABEL & DAFTAR UNIT
# ==========================================
DAFTAR_PROGRAM = ["Farmasi", "Gizi", "Ausrem", "KIA/KB", "Promkes", "Kesling", "P2P", "Laboratorium", "Tata Usaha"]
DAFTAR_ROLE = ["Admin", "Kepala Puskesmas"] + DAFTAR_PROGRAM
DAFTAR_TAHUN = ["2024", "2025", "2026", "2027", "2028", "2029"]
LIST_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

# ==========================================
# 3. CUSTOM CSS
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .stButton>button { border-radius: 8px; font-weight: bold; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); background-color: #0284c7; color: white; border: none; }
    .stButton>button:hover { background-color: #0369a1; color: white; transform: translateY(-2px); }
    .login-box { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border-top: 5px solid #0284c7; margin: auto; max-width: 400px; margin-top: 10vh;}
    .kepatuhan-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; height: 100%;}
    .progress-bar-bg { background-color: #e2e8f0; border-radius: 10px; height: 14px; width: 100%; overflow: hidden; margin-top: 10px; }
    .progress-bar-fill { background: linear-gradient(90deg, #34d399 0%, #059669 100%); height: 100%; border-radius: 10px; transition: width 0.8s ease-in-out; }
    .badge-sudah { background-color: #ecfdf5; color: #065f46; padding: 8px 16px; border-radius: 20px; display: inline-block; margin: 5px; font-weight: bold; font-size: 13px; border: 1px solid #a7f3d0; }
    .badge-belum { background-color: #fef2f2; color: #991b1b; padding: 8px 16px; border-radius: 20px; display: inline-block; margin: 5px; font-weight: bold; font-size: 13px; border: 1px solid #fecaca; }
    .file-item { padding: 12px 0px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center;}
    .file-item a { text-decoration: none; color: white; background-color: #0ea5e9; padding: 6px 15px; border-radius: 5px; font-weight: bold; font-size: 13px; transition: background-color 0.2s;}
    .file-item a:hover { background-color: #0284c7; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. SISTEM LOGIN
# ==========================================
if not st.session_state['sudah_login']:
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #0284c7;'>🏥 Portal Puskesmas</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray; margin-bottom:20px;'>Silakan login menggunakan akun unit Anda.</p>", unsafe_allow_html=True)
    with st.form("form_login"):
        input_user = st.text_input("Username", placeholder="Ketik username...")
        input_pass = st.text_input("Password", type="password", placeholder="Ketik password...")
        if st.form_submit_button("Masuk Aplikasi ➡️", use_container_width=True):
            cek_akun = supabase.table("akun_pengguna").select("*").eq("username", input_user).eq("password", input_pass).execute()
            if len(cek_akun.data) > 0:
                st.session_state['sudah_login'] = True
                st.session_state['username'] = cek_akun.data[0]['username']
                st.session_state['role'] = cek_akun.data[0]['role']
                st.rerun()
            else:
                st.error("❌ Username atau Password salah!")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# 5. HALAMAN UTAMA & SIDEBAR
# ==========================================
st.sidebar.title("🏥 Navigasi")
st.sidebar.markdown(f"👤 **{st.session_state['username']}**<br><small>({st.session_state['role']})</small>", unsafe_allow_html=True)
st.sidebar.write("---")

if st.session_state['role'] == 'Admin':
    menu = st.sidebar.radio("Pilih Menu:", ["📤 Upload Laporan", "📊 Pantau Kepatuhan", "📂 Gudang Arsip", "⚙️ Kelola Akun"])
elif st.session_state['role'] == 'Kepala Puskesmas':
    menu = st.sidebar.radio("Pilih Menu:", ["📊 Pantau Kepatuhan", "📂 Gudang Arsip"])
else:
    menu = st.sidebar.radio("Pilih Menu:", ["📤 Upload Laporan", "📊 Pantau Kepatuhan", "📂 Gudang Arsip"])

st.sidebar.write("---")
if st.sidebar.button("🚪 Keluar Aplikasi", use_container_width=True):
    st.session_state['sudah_login'] = False
    st.rerun()

respon = supabase.table("status_laporan").select("*").execute()
df_status = pd.DataFrame(respon.data) if len(respon.data) > 0 else pd.DataFrame()

# ------------------------------------------
# MENU: UPLOAD LAPORAN
# ------------------------------------------
if menu == "📤 Upload Laporan":
    st.header("📤 Kirim Laporan ke Server")
    st.write("Silakan unggah dokumen laporan Anda di sini.")
    st.write("---")
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.markdown("### 📝 Identitas Laporan")
        if st.session_state['role'] in DAFTAR_PROGRAM:
            instansi = st.selectbox("1. Unit / Program:", [st.session_state['role']], disabled=True)
        else:
            instansi = st.selectbox("1. Pilih Unit / Program:", ["Pilih Program..."] + DAFTAR_PROGRAM + ["Program Lainnya"])
            
        jenis_laporan = st.radio("2. Kategori Laporan:", ["Bulanan", "Tahunan"], horizontal=True)
        tahun_laporan = st.selectbox("3. Pilih Tahun:", DAFTAR_TAHUN, index=2) 
        bulan_laporan = st.selectbox("4. Pilih Bulan:", LIST_BULAN) if jenis_laporan == "Bulanan" else "Tahunan"
        
    with col2:
        st.markdown("### 📎 Upload File")
        file_upload = st.file_uploader("5. Pilih File Dokumen (PDF/Word/Excel)", type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv'])
        st.write("")
        if st.button("🚀 Kirim Laporan Sekarang", use_container_width=True):
            if instansi != "Pilih Program..." and file_upload is not None:
                with st.spinner('Proses pengiriman ke Pusat Data...'):
                    try:
                        timestamp = datetime.now().strftime('%d%m%Y_%H%M%S')
                        nama_file = f"{instansi}_{jenis_laporan}_{bulan_laporan}_{tahun_laporan}_{timestamp}_{file_upload.name}"
                        status_gab = f"{jenis_laporan}|{bulan_laporan}|{tahun_laporan}"
                        
                        supabase.storage.from_("laporan_files").upload(path=nama_file, file=file_upload.read())
                        supabase.table("status_laporan").insert({
                            "nama_instansi": instansi, 
                            "nama_file": nama_file, 
                            "status": status_gab
                        }).execute()
                        st.success(f"✅ Laporan berhasil dikirim dan tercatat di sistem!")
                    except Exception as e:
                        st.error(f"❌ Terjadi kesalahan jaringan: {e}")
            else:
                st.warning("⚠️ Mohon lengkapi pilihan Unit dan masukkan filenya!")

# ------------------------------------------
# MENU: PANTAU KEPATUHAN (DENGAN FITUR EXCEL)
# ------------------------------------------
elif menu == "📊 Pantau Kepatuhan":
    st.header("🎯 Pantau Kepatuhan Pelaporan")
    st.write("Monitor unit mana saja yang sudah dan belum mengirimkan laporan.")
    st.write("---")
    
    f1, f2, f3 = st.columns(3)
    with f1: dash_tahun = st.selectbox("Tahun:", DAFTAR_TAHUN, index=2)
    with f2: dash_jenis = st.selectbox("Kategori:", ["Bulanan", "Tahunan"])
    with f3: dash_bulan = st.selectbox("Bulan:", LIST_BULAN) if dash_jenis == "Bulanan" else "Tahunan"
    st.write("---")
    
    program_sudah = []
    program_belum = DAFTAR_PROGRAM
    
    if not df_status.empty:
        target_status = f"{dash_jenis}|{dash_bulan}|{dash_tahun}"
        df_target = df_status[df_status['status'] == target_status]
        program_sudah = df_target['nama_instansi'].unique().tolist()
        program_belum = [p for p in DAFTAR_PROGRAM if p not in program_sudah]
    
    jml_sudah = len(program_sudah)
    total_p = len(DAFTAR_PROGRAM)
    persen_patuh = int((jml_sudah / total_p) * 100) if total_p > 0 else 0
    
    st.markdown(f"""
    <div class='kepatuhan-card' style="margin-bottom: 20px;">
        <h4 style="margin-top: 0; color: #334155;">Tingkat Kepatuhan Keseluruhan: <span style="color: #059669;">{persen_patuh}%</span></h4>
        <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {persen_patuh}%;"></div></div>
    </div>
    """, unsafe_allow_html=True)
    
    col_s, col_b = st.columns(2)
    with col_s:
        st.markdown(f"<div class='kepatuhan-card'><h4>✅ Sudah Lapor ({jml_sudah})</h4>", unsafe_allow_html=True)
        if program_sudah:
            st.markdown("".join([f"<span class='badge-sudah'>✔️ {p}</span>" for p in program_sudah]), unsafe_allow_html=True)
        else: st.write("Belum ada unit yang lapor.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_b:
        st.markdown(f"<div class='kepatuhan-card'><h4>⏳ Belum Lapor ({len(program_belum)})</h4>", unsafe_allow_html=True)
        if program_belum:
            st.markdown("".join([f"<span class='badge-belum'>⏳ {p}</span>" for p in program_belum]), unsafe_allow_html=True)
        else: st.success("Luar biasa! 100% unit sudah lapor! 🎉")
        st.markdown("</div>", unsafe_allow_html=True)

    # FITUR DOWNLOAD EXCEL (CSV) REKAP KEPATUHAN
    st.write("---")
    st.markdown("#### 📥 Unduh Laporan Rekapitulasi")
    
    # Merakit data untuk excel
    data_rekap = []
    for p in DAFTAR_PROGRAM:
        status_lapor = "Sudah Lapor" if p in program_sudah else "Belum Lapor"
        data_rekap.append({
            "Nama Unit": p,
            "Kategori Laporan": dash_jenis,
            "Bulan": dash_bulan,
            "Tahun": dash_tahun,
            "Status": status_lapor
        })
    df_rekap = pd.DataFrame(data_rekap)
    csv_rekap = df_rekap.to_csv(index=False).encode('utf-8')
    
    col_dl, col_blank = st.columns([1, 2])
    with col_dl:
        st.download_button(
            label="📊 Download Rekap Data (Excel/CSV)",
            data=csv_rekap,
            file_name=f"Rekap_Kepatuhan_{dash_jenis}_{dash_bulan}_{dash_tahun}.csv",
            mime="text/csv",
            use_container_width=True
        )

# ------------------------------------------
# MENU: GUDANG ARSIP
# ------------------------------------------
elif menu == "📂 Gudang Arsip":
    st.header("📂 Gudang Arsip Digital")
    st.write("Unduh file laporan yang tersimpan di server.")
    st.write("---")
    
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
            filter_tahun_arsip = st.selectbox("Tampilkan Arsip Tahun:", DAFTAR_TAHUN, index=2)
            df_arsip = df_arsip[df_arsip['Tahun'] == filter_tahun_arsip]
        else:
            filter_tahun_arsip = st.selectbox("Tampilkan Arsip Tahun:", ["Semua Tahun"] + DAFTAR_TAHUN, index=0)
            if filter_tahun_arsip != "Semua Tahun":
                df_arsip = df_arsip[df_arsip['Tahun'] == filter_tahun_arsip]
        
        if not df_arsip.empty:
            grup_utama = df_arsip.groupby(['nama_instansi', 'Jenis Laporan', 'Tahun'])
            for (program, jenis, tahun), data_grup in grup_utama:
                with st.expander(f"📁 {program} | {jenis} ({tahun})"):
                    data_grup = data_grup.sort_values('Urutan_Bulan')
                    grup_bulan = data_grup.groupby('Bulan', sort=False)
                    for bulan, data_bulan in grup_bulan:
                        st.markdown(f"<h5 style='margin-bottom:0px; margin-top:15px; color:#0284c7;'>📂 {bulan}</h5>", unsafe_allow_html=True)
                        for _, row in data_bulan.iterrows():
                            wts = pd.to_datetime(row['created_at'])
                            if wts.tzinfo is None: wts = wts.tz_localize('UTC')
                            waktu = wts.tz_convert('Asia/Jakarta').strftime('%d %b %Y - %H:%M')
                            nf = row['nama_file']
                            link_dl = f"{SUPABASE_URL}/storage/v1/object/public/laporan_files/{nf}"
                            
                            st.markdown(f"""
                                <div class='file-item'>
                                    <div>
                                        <span style='font-size: 15px;'>📄 <b>{nf.split('_', 5)[-1]}</b></span><br>
                                        <small style='color:gray;'>🕒 Diunggah: {waktu} WIB</small>
                                    </div>
                                    <a href='{link_dl}' target='_blank'>📥 Download</a>
                                </div>
                            """, unsafe_allow_html=True)
        else: st.info(f"Belum ada arsip yang tersimpan di kriteria ini.")
        
        st.write("---")
        if st.session_state['role'] == 'Admin':
            with st.expander("🗑️ Hapus Dokumen Permanen (Admin Only)"):
                hapus_file = st.selectbox("Pilih nama file yang ingin dihapus:", df_status['nama_file'].tolist())
                if st.button("🚨 Hapus File Secara Permanen", type="primary"):
                    supabase.table("status_laporan").delete().eq("nama_file", hapus_file).execute()
                    supabase.storage.from_("laporan_files").remove([hapus_file])
                    st.success("✅ File berhasil dihapus!")
                    st.rerun()
    else: st.info("Gudang arsip Cloud saat ini masih kosong.")

# ------------------------------------------
# MENU: KELOLA AKUN (HANYA ADMIN)
# ------------------------------------------
elif menu == "⚙️ Kelola Akun" and st.session_state['role'] == 'Admin':
    st.header("⚙️ Manajemen Pengguna")
    st.write("Buat akun baru untuk memberikan akses masuk ke Kepala Puskesmas atau Unit program.")
    st.write("---")
    
    col_buat, col_daftar = st.columns([1, 1.2])
    
    with col_buat:
        st.markdown("#### ➕ Buat Akun Baru")
        with st.form("form_tambah_akun"):
            baru_user = st.text_input("Username (Tanpa Spasi)")
            baru_pass = st.text_input("Password (Min. 6 Karakter)")
            baru_role = st.selectbox("Role / Unit Bagian", DAFTAR_ROLE)
            
            if st.form_submit_button("Simpan Akun ✅"):
                if baru_user and baru_pass:
                    cek = supabase.table("akun_pengguna").select("*").eq("username", baru_user).execute()
                    if len(cek.data) > 0:
                        st.error("❌ Username sudah terpakai, pilih nama lain!")
                    else:
                        supabase.table("akun_pengguna").insert({
                            "username": baru_user.replace(" ", ""), 
                            "password": baru_pass, 
                            "role": baru_role
                        }).execute()
                        st.success(f"✅ Akun '{baru_user}' ({baru_role}) berhasil didaftarkan!")
                else:
                    st.warning("Username dan Password tidak boleh kosong.")
                    
    with col_daftar:
        st.markdown("#### 📋 Daftar Akun Terdaftar")
        res_akun = supabase.table("akun_pengguna").select("username, role").execute()
        if len(res_akun.data) > 0:
            df_akun = pd.DataFrame(res_akun.data)
            df_akun.columns = ["Username", "Role / Unit"]
            st.dataframe(df_akun, use_container_width=True, hide_index=True)
        else:
            st.write("Belum ada data akun.")
