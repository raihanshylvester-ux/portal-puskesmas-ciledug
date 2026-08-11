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

st.set_page_config(page_title="Portal Internal Puskesmas", page_icon="🏥", layout="wide")

# ==========================================
# CUSTOM CSS (TAMPILAN FRESH & MODERN)
# ==========================================
st.markdown("""
    <style>
    /* Latar belakang yang lebih bersih */
    .stApp { background-color: #f8fafc; }
    
    /* Tombol modern */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
    
    /* Kotak Metrik / Statistik */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
        border-left: 5px solid #0ea5e9;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    
    /* Box Kepatuhan */
    .box-sudah { background-color: #dcfce7; padding: 15px; border-radius: 10px; border: 1px solid #bbf7d0; }
    .box-belum { background-color: #fee2e2; padding: 15px; border-radius: 10px; border: 1px solid #fecaca; }
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("🏥 Portal Internal")
menu = st.sidebar.radio("Navigasi:", ["Upload Laporan Bulanan", "Dashboard Admin"])

# --- DAFTAR PROGRAM MASTER (Bisa bos tambah/ubah nanti) ---
DAFTAR_PROGRAM = [
    "Farmasi", "Gizi", "Ausrem", "KIA/KB", "Promkes", 
    "Kesling", "P2P", "Laboratorium", "Tata Usaha"
]

# ==========================================
# HALAMAN 1: UPLOAD LAPORAN
# ==========================================
if menu == "Upload Laporan Bulanan":
    st.title("📤 Portal Laporan Internal Puskesmas")
    st.markdown("Silakan unggah dokumen laporan bulanan dari unit/program Anda di sini.")
    
    st.write("---")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        pilihan_program = ["Pilih Program..."] + DAFTAR_PROGRAM + ["Program Lainnya"]
        instansi = st.selectbox("Pilih Unit / Program:", pilihan_program)
        bulan_laporan = st.selectbox("Laporan Untuk Bulan:", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
    
    with col2:
        file_upload = st.file_uploader("Pilih File Dokumen (Excel/PDF/Word)", type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv'])
    
    if st.button("🚀 Unggah Laporan", type="primary"):
        if instansi == "Pilih Program...":
            st.warning("⚠️ Harap pilih Unit/Program terlebih dahulu!")
        elif file_upload is None:
            st.warning("⚠️ Harap masukkan file laporan!")
        else:
            with st.spinner('Menyimpan ke server aman...'):
                try:
                    # Nama file dibuat super rapi: Program_Bulan_Tahun_NamaFile Asli
                    tahun_sekarang = datetime.now().strftime('%Y')
                    nama_file_unik = f"{instansi}_{bulan_laporan}_{tahun_sekarang}_{datetime.now().strftime('%H%M%S')}_{file_upload.name}"
                    file_bytes = file_upload.read()
                    
                    supabase.storage.from_("laporan_files").upload(path=nama_file_unik, file=file_bytes)
                    supabase.table("status_laporan").insert({"nama_instansi": instansi, "nama_file": nama_file_unik, "status": bulan_laporan}).execute()
                    
                    st.success(f"✅ Laporan {instansi} untuk bulan {bulan_laporan} berhasil disimpan!")
                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan: {e}")

# ==========================================
# HALAMAN 2: DASHBOARD & LOGIN
# ==========================================
elif menu == "Dashboard Admin":
    
    if not st.session_state['sudah_login']:
        st.title("🔐 Ruang Admin")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info("Silakan login untuk memantau data laporan bulanan.")
            with st.form("form_login"):
                input_user = st.text_input("Username")
                input_pass = st.text_input("Password", type="password")
                if st.form_submit_button("Masuk ➡️", use_container_width=True):
                    cek_akun = supabase.table("akun_pengguna").select("*").eq("username", input_user).eq("password", input_pass).execute()
                    if len(cek_akun.data) > 0:
                        st.session_state['sudah_login'] = True
                        st.session_state['username'] = cek_akun.data[0]['username']
                        st.session_state['role'] = cek_akun.data[0]['role']
                        st.rerun()
                    else:
                        st.error("❌ Kredensial tidak valid!")
                        
    else:
        # Header Admin
        col_header1, col_header2 = st.columns([3, 1])
        with col_header1:
            st.header(f"📊 Dashboard Pemantauan Laporan")
            st.markdown(f"Login sebagai: **{st.session_state['username']}** ({st.session_state['role']})")
        with col_header2:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state['sudah_login'] = False
                st.rerun()
                
        st.write("---")
        
        # Ambil Data
        respon = supabase.table("status_laporan").select("*").order("created_at", desc=True).execute()
        df = pd.DataFrame(respon.data) if len(respon.data) > 0 else pd.DataFrame()
        
        # Buat 3 Tab: Kepatuhan (Baru), Arsip Data, Pengaturan
        tab1, tab2, tab3 = st.tabs(["🎯 Status Kepatuhan", "📂 Arsip Dokumen", "⚙️ Akun"])
        
        # --- TAB 1: STATUS KEPATUHAN (SUDAH VS BELUM LAPOR) ---
        with tab1:
            st.subheader("Cek Kepatuhan Pengumpulan Laporan")
            pilih_bulan = st.selectbox("Pantau Bulan:", ["Agustus", "Juli", "Juni", "Mei", "April", "Maret", "Februari", "Januari", "September", "Oktober", "November", "Desember"])
            
            if not df.empty:
                # Saring data khusus untuk bulan yang dipilih (yang tersimpan di kolom 'status')
                df_bulan_ini = df[df['status'] == pilih_bulan]
                program_sudah = df_bulan_ini['nama_instansi'].unique().tolist()
                program_belum = [p for p in DAFTAR_PROGRAM if p not in program_sudah]
                
                col_sudah, col_belum = st.columns(2)
                
                with col_sudah:
                    st.markdown(f"<div class='box-sudah'><h4>✅ Sudah Lapor ({len(program_sudah)})</h4></div>", unsafe_allow_html=True)
                    st.write("")
                    if len(program_sudah) > 0:
                        for p in program_sudah:
                            st.success(p, icon="✔️")
                    else:
                        st.write("- Belum ada data")
                        
                with col_belum:
                    st.markdown(f"<div class='box-belum'><h4>❌ Belum Lapor ({len(program_belum)})</h4></div>", unsafe_allow_html=True)
                    st.write("")
                    if len(program_belum) > 0:
                        for p in program_belum:
                            st.error(p, icon="⏳")
                    else:
                        st.write("- Semua program sudah lapor! 🎉")
            else:
                st.info("Belum ada data di database.")

        # --- TAB 2: ARSIP DOKUMEN ---
        with tab2:
            st.subheader("Semua Data Laporan Masuk")
            if not df.empty:
                df['created_at'] = pd.to_datetime(df['created_at']).dt.tz_convert('Asia/Jakarta').dt.strftime('%d-%m-%Y %H:%M')
                nama_bucket = "laporan_files"
                df['link_download'] = df['nama_file'].apply(lambda x: f"{SUPABASE_URL}/storage/v1/object/public/{nama_bucket}/{x}")
                
                df_tampil = df[['created_at', 'nama_instansi', 'status', 'nama_file', 'link_download']]
                df_tampil.columns = ['Waktu Upload', 'Program/Unit', 'Bulan Laporan', 'Nama File Asli', 'Aksi']
                
                st.dataframe(df_tampil, use_container_width=True, column_config={"Aksi": st.column_config.LinkColumn("Dokumen", display_text="📥 Download")})
                
                if st.session_state['role'] == 'Admin':
                    with st.expander("🗑️ Hapus Laporan Salah Upload"):
                        hapus_file = st.selectbox("Pilih file yang ingin dihapus:", df['nama_file'].tolist())
                        if st.button("Hapus Permanen", type="primary"):
                            supabase.table("status_laporan").delete().eq("nama_file", hapus_file).execute()
                            supabase.storage.from_("laporan_files").remove([hapus_file])
                            st.success("File dihapus!")
                            st.rerun()
            else:
                st.info("Belum ada laporan.")

        # --- TAB 3: MANAJEMEN AKUN ---
        with tab3:
            st.subheader("Manajemen Hak Akses")
            if st.session_state['role'] == 'Admin':
                with st.form("form_tambah_akun"):
                    baru_user = st.text_input("Username Baru")
                    baru_pass = st.text_input("Password Baru")
                    baru_role = st.selectbox("Hak Akses", ["Kepala Puskesmas", "Admin", "Tim TU"])
                    if st.form_submit_button("Buat Akun ✅"):
                        supabase.table("akun_pengguna").insert({"username": baru_user, "password": baru_pass, "role": baru_role}).execute()
                        st.success(f"Akun '{baru_user}' dibuat!")
            else:
                st.warning("Hanya Admin utama yang bisa membuat akun baru.")
