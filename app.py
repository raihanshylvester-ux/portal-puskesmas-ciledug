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

# ==========================================
# SISTEM SESSION (Mengingat Status Login)
# ==========================================
if 'sudah_login' not in st.session_state:
    st.session_state['sudah_login'] = False
    st.session_state['username'] = ""
    st.session_state['role'] = ""

# ==========================================
# 2. PENGATURAN HALAMAN & MENU WEB
# ==========================================
st.set_page_config(page_title="Portal Pelaporan Puskesmas Ciledug", page_icon="🏥", layout="wide")
st.sidebar.title("Navigasi 🏥")
menu = st.sidebar.radio("Pilih Halaman:", ["Upload Laporan", "Sistem Internal (Login)"])

# ==========================================
# 3. HALAMAN UPLOAD LAPORAN (Untuk Umum)
# ==========================================
if menu == "Upload Laporan":
    st.title("📤 Portal Pelaporan Puskesmas Ciledug")
    st.info("💡 **INFO PENTING:** Mulai bulan depan, harap gunakan format template standar.")
    
    template_df = pd.DataFrame({"Tanggal Laporan": [], "Jumlah Kunjungan Pasien": [], "Catatan/Kendala": []})
    st.download_button("📥 Download Template Laporan Standar", data=template_df.to_csv(index=False).encode('utf-8'), file_name='Template_Laporan_Puskesmas.csv', mime='text/csv')
    st.write("---")
    
    daftar_puskesmas = ["Pilih Puskesmas...", "Puskesmas Ciledug", "Puskesmas Pabuaran", "Puskesmas Karangsembung", "Puskesmas Waled", "Puskesmas Lainnya"]
    instansi = st.selectbox("Nama Instansi:", daftar_puskesmas)
    file_upload = st.file_uploader("Pilih File Laporan", type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv'])
    
    if st.button("Kirim Laporan"):
        if instansi == "Pilih Puskesmas...":
            st.warning("⚠️ Harap pilih nama instansi terlebih dahulu!")
        elif file_upload is None:
            st.warning("⚠️ Harap masukkan file laporan yang ingin dikirim!")
        else:
            with st.spinner('Sedang mengirim laporan...'):
                try:
                    nama_file_unik = f"{instansi}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_upload.name}"
                    file_bytes = file_upload.read()
                    supabase.storage.from_("laporan_files").upload(path=nama_file_unik, file=file_bytes)
                    supabase.table("status_laporan").insert({"nama_instansi": instansi, "nama_file": nama_file_unik, "status": "Sudah Lapor"}).execute()
                    st.success(f"✅ Laporan berhasil terkirim!")
                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan: {e}")

# ==========================================
# 4. HALAMAN INTERNAL & LOGIN
# ==========================================
elif menu == "Sistem Internal (Login)":
    
    if not st.session_state['sudah_login']:
        st.title("🔐 Login Sistem Internal")
        st.write("Silakan masukkan Username dan Password Anda.")
        
        with st.form("form_login"):
            input_user = st.text_input("Username")
            input_pass = st.text_input("Password", type="password")
            tombol_masuk = st.form_submit_button("Masuk ➡️")
            
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
        st.success(f"Selamat datang, **{st.session_state['username']}**! (Hak Akses: {st.session_state['role']})")
        if st.button("🚪 Keluar (Logout)"):
            st.session_state['sudah_login'] = False
            st.session_state['username'] = ""
            st.session_state['role'] = ""
            st.rerun()
            
        st.write("---")
        
        tab1, tab2 = st.tabs(["📊 Data Laporan Masuk", "⚙️ Manajemen Akun Pengguna"])
        
        # --- TAB 1: DATA LAPORAN & TONG SAMPAH ---
        with tab1:
            st.subheader("📋 Daftar Laporan Puskesmas")
            
            # Fitur Pencarian/Filter
            kolom_filter1, kolom_filter2 = st.columns(2)
            with kolom_filter1:
                pilihan_filter = ["Semua Puskesmas", "Puskesmas Ciledug", "Puskesmas Pabuaran", "Puskesmas Karangsembung", "Puskesmas Waled", "Puskesmas Lainnya"]
                filter_puskesmas = st.selectbox("🔍 Filter berdasarkan Instansi:", pilihan_filter)
                
            if st.button("🔄 Perbarui Data"):
                st.rerun()
                
            try:
                # Mengambil data dari database, diurutkan dari yang terbaru
                respon = supabase.table("status_laporan").select("*").order("created_at", desc=True).execute()
                
                if len(respon.data) > 0:
                    df = pd.DataFrame(respon.data)
                    
                    # Menyaring data berdasarkan pilihan filter
                    if filter_puskesmas != "Semua Puskesmas":
                        df = df[df['nama_instansi'] == filter_puskesmas]
                        
                    if not df.empty:
                        df['created_at'] = pd.to_datetime(df['created_at']).dt.tz_convert('Asia/Jakarta').dt.strftime('%d-%m-%Y %H:%M:%S')
                        nama_bucket = "laporan_files"
                        df['link_download'] = df['nama_file'].apply(lambda x: f"{SUPABASE_URL}/storage/v1/object/public/{nama_bucket}/{x}")
                        
                        df_tampil = df[['created_at', 'nama_instansi', 'nama_file', 'status', 'link_download']]
                        df_tampil.columns = ['Waktu Upload (WIB)', 'Nama Instansi', 'Nama File', 'Status', 'Aksi']
                        
                        st.dataframe(df_tampil, use_container_width=True, column_config={"Aksi": st.column_config.LinkColumn("File Laporan", display_text="📥 Download")})
                        st.info(f"Total laporan ditemukan: {len(df)} dokumen.")
                        
                        # FITUR TONG SAMPAH (Hanya Admin yang bisa lihat)
                        if st.session_state['role'] == 'Admin':
                            st.write("---")
                            st.subheader("🗑️ Hapus Laporan Salah Upload")
                            with st.expander("Klik di sini untuk menghapus data"):
                                hapus_file = st.selectbox("Pilih file yang ingin dihapus permanen:", df['nama_file'].tolist())
                                st.warning("⚠️ Perhatian: File yang dihapus tidak bisa dikembalikan!")
                                if st.button("🚨 Hapus Data Ini", type="primary"):
                                    with st.spinner('Sedang menghapus...'):
                                        # Hapus dari database tabel
                                        supabase.table("status_laporan").delete().eq("nama_file", hapus_file).execute()
                                        # Hapus file aslinya dari storage
                                        supabase.storage.from_("laporan_files").remove([hapus_file])
                                        st.success(f"File berhasil dihapus!")
                                        st.rerun()
                    else:
                        st.warning(f"Belum ada laporan yang masuk dari {filter_puskesmas}.")
                else:
                    st.info("Database masih kosong. Belum ada laporan yang masuk.")
            except Exception as e:
                st.error(f"Gagal memuat data laporan: {e}")

        # --- TAB 2: MANAJEMEN AKUN ---
        with tab2:
            st.subheader("Buat Akun Baru")
            if st.session_state['role'] == 'Admin':
                with st.form("form_tambah_akun"):
                    baru_user = st.text_input("Username Baru")
                    baru_pass = st.text_input("Password Baru")
                    baru_role = st.selectbox("Pilih Hak Akses", ["Kepala Puskesmas", "Admin"])
                    tombol_buat = st.form_submit_button("Buat Akun ✅")
                    
                    if tombol_buat:
                        try:
                            supabase.table("akun_pengguna").insert({"username": baru_user, "password": baru_pass, "role": baru_role}).execute()
                            st.success(f"Akun '{baru_user}' berhasil dibuat!")
                        except:
                            st.error("Gagal membuat akun. Pastikan tabel akun_pengguna sudah ada di Supabase.")
            else:
                st.warning("⚠️ Maaf, hanya Admin utama yang memiliki hak akses untuk membuat akun baru.")
