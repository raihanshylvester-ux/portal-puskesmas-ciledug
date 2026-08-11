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
# 2. PENGATURAN HALAMAN & MENU WEB
# ==========================================
st.set_page_config(page_title="Portal Pelaporan Puskesmas Ciledug", page_icon="🏥", layout="wide")

st.sidebar.title("Navigasi 🏥")
menu = st.sidebar.radio("Pilih Halaman:", ["Upload Laporan", "Dashboard Admin"])

# ==========================================
# 3. HALAMAN UPLOAD LAPORAN
# ==========================================
if menu == "Upload Laporan":
    st.title("📤 Portal Pelaporan Puskesmas Ciledug")
    
    # --- BAGIAN BARU: Info Template Standar ---
    st.info("💡 **INFO PENTING:** Mulai bulan depan, harap gunakan format template standar sebelum mengupload laporan.")
    
    # Membuat template kosong untuk didownload petugas
    template_df = pd.DataFrame({"Tanggal Laporan": [], "Jumlah Kunjungan Pasien": [], "Catatan/Kendala": []})
    st.download_button(
        label="📥 Download Template Laporan Standar",
        data=template_df.to_csv(index=False).encode('utf-8'),
        file_name='Template_Laporan_Puskesmas.csv',
        mime='text/csv'
    )
    
    st.write("---") # Garis pembatas
    
    st.write("Silakan pilih instansi dan upload file laporan Anda di bawah ini:")
    
    # Pilihan Instansi diperbarui
    daftar_puskesmas = ["Pilih Puskesmas...", "Puskesmas Ciledug", "Puskesmas Pabuaran", "Puskesmas Karangsembung", "Puskesmas Waled", "Puskesmas Lainnya"]
    instansi = st.selectbox("Nama Instansi:", daftar_puskesmas)
    
    file_upload = st.file_uploader("Pilih File Laporan (PDF/Word/Excel/CSV)", type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv'])
    
    if st.button("Kirim Laporan"):
        if instansi == "Pilih Puskesmas...":
            st.warning("⚠️ Harap pilih nama instansi terlebih dahulu!")
        elif file_upload is None:
            st.warning("⚠️ Harap masukkan file laporan yang ingin dikirim!")
        else:
            with st.spinner('Sedang mengirim laporan ke server...'):
                try:
                    nama_file_unik = f"{instansi}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_upload.name}"
                    file_bytes = file_upload.read()
                    
                    supabase.storage.from_("laporan_files").upload(path=nama_file_unik, file=file_bytes)
                    
                    supabase.table("status_laporan").insert({
                        "nama_instansi": instansi,
                        "nama_file": nama_file_unik,
                        "status": "Sudah Lapor"
                    }).execute()
                    
                    st.success(f"✅ Laporan dari {instansi} berhasil terkirim!")
                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan: {e}")

# ==========================================
# 4. HALAMAN DASHBOARD ADMIN DENGAN PASSWORD
# ==========================================
elif menu == "Dashboard Admin":
    st.title("📊 Dashboard Pantauan Laporan")
    
    # --- BAGIAN BARU: Gembok Password ---
    PASSWORD_RAHASIA = "ciledug2026" # <--- BOS BISA GANTI PASSWORD INI NANTI
    
    input_password = st.text_input("🔑 Masukkan Password Admin:", type="password")
    
    if input_password == PASSWORD_RAHASIA:
        st.success("✅ Akses Diberikan. Selamat datang, Admin!")
        st.write("Berikut adalah daftar instansi yang sudah masuk ke database.")
        
        if st.button("🔄 Perbarui Data"):
            st.rerun()
            
        try:
            respon = supabase.table("status_laporan").select("*").execute()
            data = respon.data
            
            if len(data) > 0:
                df = pd.DataFrame(data)
                df['created_at'] = pd.to_datetime(df['created_at']).dt.tz_convert('Asia/Jakarta').dt.strftime('%d-%m-%Y %H:%M:%S')
                nama_bucket = "laporan_files"
                df['link_download'] = df['nama_file'].apply(lambda x: f"{SUPABASE_URL}/storage/v1/object/public/{nama_bucket}/{x}")
                df = df[['created_at', 'nama_instansi', 'nama_file', 'status', 'link_download']]
                df.columns = ['Waktu Upload (WIB)', 'Nama Instansi', 'Nama File', 'Status', 'Aksi']
                
                st.dataframe(
                    df, 
                    use_container_width=True,
                    column_config={
                        "Aksi": st.column_config.LinkColumn("File Laporan", display_text="📥 Download File")
                    }
                )
                st.info(f"Total laporan masuk: {len(data)} dokumen.")
            else:
                st.info("Belum ada laporan yang masuk.")
                
        except Exception as e:
            st.error(f"❌ Gagal mengambil data: {e}")
            
    # Jika password diisi tapi salah
    elif input_password != "":
        st.error("❌ Password Salah! Anda tidak memiliki izin untuk melihat halaman ini.")
