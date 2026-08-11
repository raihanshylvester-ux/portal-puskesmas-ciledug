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

st.set_page_config(page_title="Portal Puskesmas Ciledug", page_icon="🏥", layout="wide")

# ==========================================
# CUSTOM CSS (UNTUK MEMPERCANTIK TAMPILAN)
# ==========================================
st.markdown("""
    <style>
    /* Mempercantik tombol */
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
    }
    /* Mempercantik kotak metrik/statistik */
    div[data-testid="metric-container"] {
        background-color: #e0f2fe;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=100) # Tambah logo di menu
st.sidebar.title("Navigasi Utama")
menu = st.sidebar.radio("", ["Upload Laporan", "Sistem Internal (Login)"])

# ==========================================
# HALAMAN UPLOAD LAPORAN
# ==========================================
if menu == "Upload Laporan":
    st.title("🏥 Portal Pelaporan Puskesmas Ciledug")
    st.markdown("Selamat datang! Silakan gunakan portal ini untuk mengunggah dokumen laporan bulanan instansi Anda secara aman.")
    
    st.info("💡 **INFO PENTING:** Mulai bulan depan, harap gunakan format template standar di bawah ini.")
    template_df = pd.DataFrame({"Tanggal Laporan": [], "Jumlah Kunjungan Pasien": [], "Catatan/Kendala": []})
    st.download_button("📥 Download Template Laporan Standar", data=template_df.to_csv(index=False).encode('utf-8'), file_name='Template_Laporan_Puskesmas.csv', mime='text/csv')
    
    st.write("---")
    
    col1, col2 = st.columns([1, 2]) # Membagi layar agar form tidak terlalu lebar
    with col1:
        daftar_puskesmas = ["Pilih Puskesmas...", "Puskesmas Ciledug", "Puskesmas Pabuaran", "Puskesmas Karangsembung", "Puskesmas Waled", "Puskesmas Lainnya"]
        instansi = st.selectbox("Nama Instansi:", daftar_puskesmas)
    with col2:
        file_upload = st.file_uploader("Pilih File Laporan", type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv'])
    
    if st.button("🚀 Kirim Laporan Sekarang", type="primary"):
        if instansi == "Pilih Puskesmas...":
            st.warning("⚠️ Harap pilih nama instansi terlebih dahulu!")
        elif file_upload is None:
            st.warning("⚠️ Harap masukkan file laporan yang ingin dikirim!")
        else:
            with st.spinner('Memproses dan mengamankan data...'):
                try:
                    nama_file_unik = f"{instansi}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_upload.name}"
                    file_bytes = file_upload.read()
                    supabase.storage.from_("laporan_files").upload(path=nama_file_unik, file=file_bytes)
                    supabase.table("status_laporan").insert({"nama_instansi": instansi, "nama_file": nama_file_unik, "status": "Sudah Lapor"}).execute()
                    st.success(f"✅ Laporan berhasil terkirim! Terima kasih.")
                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan: {e}")

# ==========================================
# HALAMAN INTERNAL & LOGIN
# ==========================================
elif menu == "Sistem Internal (Login)":
    
    if not st.session_state['sudah_login']:
        st.title("🔐 Login Dashboard Admin")
        
        # Membuat form login lebih rapi di tengah
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.write("Silakan masukkan kredensial Anda.")
            with st.form("form_login"):
                input_user = st.text_input("Username")
                input_pass = st.text_input("Password", type="password")
                tombol_masuk = st.form_submit_button("Masuk ➡️", use_container_width=True)
                
                if tombol_masuk:
                    cek_akun = supabase.table("akun_pengguna").select("*").eq("username", input_user).eq("password", input_pass).execute()
                    if len(cek_akun.data) > 0:
                        st.session_state['sudah_login'] = True
                        st.session_state['username'] = cek_akun.data[0]['username']
                        st.session_state['role'] = cek_akun.data[0]['role']
                        st.rerun()
                    else:
                        st.error("❌ Username atau Password salah!")
                        
    else:
        col_header1, col_header2 = st.columns([3, 1])
        with col_header1:
            st.title(f"👋 Halo, {st.session_state['username']}!")
            st.markdown(f"**Hak Akses:** {st.session_state['role']}")
        with col_header2:
            st.write("") # Spasi
            if st.button("🚪 Keluar (Logout)", use_container_width=True):
                st.session_state['sudah_login'] = False
                st.session_state['username'] = ""
                st.session_state['role'] = ""
                st.rerun()
                
        st.write("---")
        
        tab1, tab2 = st.tabs(["📊 Dashboard Data", "⚙️ Pengaturan Akun"])
        
        with tab1:
            try:
                respon = supabase.table("status_laporan").select("*").order("created_at", desc=True).execute()
                df = pd.DataFrame(respon.data) if len(respon.data) > 0 else pd.DataFrame()
                
                # --- METRIK STATISTIK ---
                st.subheader("📈 Ringkasan Laporan")
                metrik1, metrik2, metrik3 = st.columns(3)
                with metrik1:
                    st.metric(label="Total Seluruh Laporan", value=len(df) if not df.empty else 0)
                with metrik2:
                    if not df.empty:
                        laporan_hari_ini = sum(pd.to_datetime(df['created_at']).dt.date == datetime.now().date())
                        st.metric(label="Laporan Masuk Hari Ini", value=laporan_hari_ini)
                    else:
                        st.metric(label="Laporan Masuk Hari Ini", value=0)
                with metrik3:
                    if not df.empty:
                        instansi_aktif = df['nama_instansi'].nunique()
                        st.metric(label="Instansi Aktif", value=instansi_aktif)
                    else:
                        st.metric(label="Instansi Aktif", value=0)
                
                st.write("---")
                st.subheader("📋 Detail Laporan Masuk")
                
                if not df.empty:
                    kolom_filter1, kolom_filter2 = st.columns(2)
                    with kolom_filter1:
                        pilihan_filter = ["Semua Puskesmas"] + list(df['nama_instansi'].unique())
                        filter_puskesmas = st.selectbox("🔍 Filter Instansi:", pilihan_filter)
                        
                    if filter_puskesmas != "Semua Puskesmas":
                        df = df[df['nama_instansi'] == filter_puskesmas]
                        
                    df['created_at'] = pd.to_datetime(df['created_at']).dt.tz_convert('Asia/Jakarta').dt.strftime('%d-%m-%Y %H:%M:%S')
                    nama_bucket = "laporan_files"
                    df['link_download'] = df['nama_file'].apply(lambda x: f"{SUPABASE_URL}/storage/v1/object/public/{nama_bucket}/{x}")
                    df_tampil = df[['created_at', 'nama_instansi', 'nama_file', 'status', 'link_download']]
                    df_tampil.columns = ['Waktu Upload (WIB)', 'Nama Instansi', 'Nama File', 'Status', 'Aksi']
                    
                    st.dataframe(df_tampil, use_container_width=True, column_config={"Aksi": st.column_config.LinkColumn("File Laporan", display_text="📥 Download")})
                    
                    if st.session_state['role'] == 'Admin':
                        with st.expander("🗑️ Hapus Laporan (Admin Only)"):
                            hapus_file = st.selectbox("Pilih file yang ingin dihapus:", df['nama_file'].tolist())
                            if st.button("🚨 Hapus Data Permanen"):
                                supabase.table("status_laporan").delete().eq("nama_file", hapus_file).execute()
                                supabase.storage.from_("laporan_files").remove([hapus_file])
                                st.success("File berhasil dihapus!")
                                st.rerun()
                else:
                    st.info("Belum ada data laporan.")
            except Exception as e:
                st.error("Gagal memuat dashboard.")

        with tab2:
            st.subheader("Manajemen Akun Pengguna")
            if st.session_state['role'] == 'Admin':
                with st.form("form_tambah_akun"):
                    baru_user = st.text_input("Username Baru")
                    baru_pass = st.text_input("Password Baru")
                    baru_role = st.selectbox("Pilih Hak Akses", ["Kepala Puskesmas", "Admin"])
                    if st.form_submit_button("Buat Akun ✅"):
                        supabase.table("akun_pengguna").insert({"username": baru_user, "password": baru_pass, "role": baru_role}).execute()
                        st.success(f"Akun '{baru_user}' berhasil dibuat!")
            else:
                st.warning("⚠️ Maaf, hanya Admin utama yang memiliki hak akses untuk fitur ini.")
