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
# CUSTOM CSS (DITAMBAHKAN DESAIN MODERN)
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .stButton>button {
        border-radius: 8px; font-weight: 600; border: none;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); transition: all 0.2s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
    
    /* CSS BARU UNTUK KEPATUHAN MODERN */
    .kepatuhan-card {
        background: white; padding: 25px; border-radius: 15px; 
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #f1f5f9; height: 100%;
    }
    .progress-bar-bg {
        background-color: #e2e8f0; border-radius: 10px; height: 12px; width: 100%; margin-top: 5px; overflow: hidden;
    }
    .progress-bar-fill {
        background: linear-gradient(90deg, #34d399 0%, #059669 100%); height: 100%; border-radius: 10px; transition: width 0.5s;
    }
    .badge-sudah {
        background-color: #ecfdf5; color: #065f46; padding: 6px 14px; border-radius: 20px; 
        display: inline-block; margin: 4px; font-size: 13px; font-weight: 600; border: 1px solid #a7f3d0;
    }
    .badge-belum {
        background-color: #fef2f2; color: #991b1b; padding: 6px 14px; border-radius: 20px; 
        display: inline-block; margin: 4px; font-size: 13px; font-weight: 600; border: 1px solid #fecaca;
    }
    
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
    st.markdown("Unggah laporan Bulanan atau Tahunan Anda di sini agar tersimpan aman di server.")
    st.write("---")
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        pilihan_program = ["Pilih Program..."] + DAFTAR_PROGRAM + ["Program Lainnya"]
        instansi = st.selectbox("1. Pilih Unit / Program:", pilihan_program)
        jenis_laporan = st.radio("2. Kategori Laporan:", ["Bulanan", "Tahunan"], horizontal=True)
        tahun_laporan = st.selectbox("3. Pilih Tahun:", DAFTAR_TAHUN, index=2) 
        
        if jenis_laporan == "Bulanan":
            bulan_laporan = st.selectbox("4. Pilih Bulan:", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
        else:
            bulan_laporan = "Tahunan"
            
    with col2:
        file_upload = st.file_uploader("5. Pilih File Dokumen (Excel/PDF/Word)", type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv'])
        st.write("") 
        if st.button("🚀 Unggah Dokumen ke Server", type="primary", use_container_width=True):
            if instansi == "Pilih Program...":
                st.warning("⚠️ Harap pilih Unit/Program terlebih dahulu!")
            elif file_upload is None:
                st.warning("⚠️ Harap masukkan file dokumen!")
            else:
                with st.spinner('Menyimpan ke brankas digital...'):
                    try:
                        status_gabungan = f"{jenis_laporan}|{bulan_laporan}|{tahun_laporan}"
                        nama_file_unik = f"{instansi}_{jenis_laporan}_{bulan_laporan}_{tahun_laporan}_{datetime.now().strftime('%H%M%S')}_{file_upload.name}"
                        file_bytes = file_upload.read()
                        
                        supabase.storage.from_("laporan_files").upload(path=nama_file_unik, file=file_bytes)
                        supabase.table("status_laporan").insert({"nama_instansi": instansi, "nama_file": nama_file_unik, "status": status_gabungan}).execute()
                        st.success(f"✅ Berhasil! Arsip {instansi} ({jenis_laporan} - {tahun_laporan}) telah tersimpan.")
                    except Exception as e:
                        st.error(f"❌ Terjadi kesalahan: {e}")

# ==========================================
# HALAMAN 2: DASHBOARD ADMIN
# ==========================================
elif menu == "Dashboard Admin":
    if not st.session_state['sudah_login']:
        st.title("🔐 Ruang Admin")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info("Silakan login untuk memantau data laporan internal.")
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
        col_header1, col_header2 = st.columns([3, 1])
        with col_header1:
            st.header(f"📊 Dashboard Arsip & Kepatuhan")
        with col_header2:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state['sudah_login'] = False
                st.rerun()
                
        st.write("---")
        
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
            
        tab1, tab2, tab3 = st.tabs(["🎯 Pantau Kepatuhan", "📂 Database Arsip Folder", "⚙️ Akun"])
        
        # --- TAB 1: STATUS KEPATUHAN (DESAIN BARU) ---
        with tab1:
            st.subheader("Cek Kepatuhan Pengumpulan Laporan")
            st.write("Pilih periode untuk melihat persentase unit yang sudah menyerahkan laporan.")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                pantau_tahun = st.selectbox("Pilih Tahun:", DAFTAR_TAHUN, index=2)
            with c2:
                pantau_jenis = st.radio("Kategori:", ["Bulanan", "Tahunan"], horizontal=True)
            with c3:
                if pantau_jenis == "Bulanan":
                    pantau_bulan = st.selectbox("Pilih Bulan:", ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
                else:
                    st.write("*(Laporan Tahunan Terpilih)*")
                    pantau_bulan = "Tahunan"
            
            st.write("") # Spasi
            
            if not df.empty:
                target_status = f"{pantau_jenis}|{pantau_bulan}|{pantau_tahun}"
                df_target = df[df['status'] == target_status]
                
                program_sudah = df_target['nama_instansi'].unique().tolist()
                program_belum = [p for p in DAFTAR_PROGRAM if p not in program_sudah]
                
                # Menghitung Persentase untuk Progress Bar
                total_program = len(DAFTAR_PROGRAM)
                jumlah_sudah = len(program_sudah)
                persen = int((jumlah_sudah / total_program) * 100) if total_program > 0 else 0
                
                # Menampilkan Progress Bar Modern
                st.markdown(f"""
                <div style="background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #f1f5f9; margin-bottom: 20px;">
                    <h4 style="margin-top: 0; color: #334155;">Tingkat Kepatuhan Keseluruhan: <span style="color: #059669;">{persen}%</span></h4>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width: {persen}%;"></div>
                    </div>
                    <small style="color: #64748b;">{jumlah_sudah} dari {total_program} Program telah melapor.</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Menampilkan Kartu Kepatuhan (Kiri: Sudah, Kanan: Belum)
                col_sudah, col_belum = st.columns(2)
                
                with col_sudah:
                    st.markdown("<div class='kepatuhan-card'>", unsafe_allow_html=True)
                    st.markdown(f"#### ✅ Sudah Lapor ({jumlah_sudah})")
                    if jumlah_sudah > 0:
                        badges = "".join([f"<span class='badge-sudah'>✔️ {p}</span>" for p in program_sudah])
                        st.markdown(badges, unsafe_allow_html=True)
                    else:
                        st.write("- Belum ada data masuk.")
                    st.markdown("</div>", unsafe_allow_html=True)
                        
                with col_belum:
                    st.markdown("<div class='kepatuhan-card'>", unsafe_allow_html=True)
                    st.markdown(f"#### ⏳ Belum Lapor ({len(program_belum)})")
                    if len(program_belum) > 0:
                        badges = "".join([f"<span class='badge-belum'>⏳ {p}</span>" for p in program_belum])
                        st.markdown(badges, unsafe_allow_html=True)
                    else:
                        st.markdown("<span style='color: #059669; font-weight: bold;'>🎉 Semua program sudah lapor!</span>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("Belum ada data di database.")

        # --- TAB 2: ARSIP DOKUMEN (SISTEM FOLDER) ---
        with tab2:
            st.subheader("📂 Ruang Arsip Digital")
            st.write("Klik pada nama program untuk membuka folder arsipnya.")
            
            if not df.empty:
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    filter_tahun = st.selectbox("Tampilkan Arsip Tahun:", ["Semua Tahun"] + DAFTAR_TAHUN, index=0)
                
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
                                    waktu_ts = pd.to_datetime(row['created_at'])
                                    if waktu_ts.tzinfo is None:
                                        waktu_ts = waktu_ts.tz_localize('UTC')
                                    waktu = waktu_ts.tz_convert('Asia/Jakarta').strftime('%d-%m-%Y %H:%M')
                                    
                                    nama_file = row['nama_file']
                                    link_dl = f"{SUPABASE_URL}/storage/v1/object/public/laporan_files/{nama_file}"
                                    
                                    st.markdown(f"""
                                        <div class='file-item'>
                                            &nbsp;&nbsp;&nbsp;&nbsp; 📄 {nama_file} <br>
                                            &nbsp;&nbsp;&nbsp;&nbsp; <small style="color:gray;">🕒 Diunggah: {waktu} WIB</small> | 
                                            <a href="{link_dl}" target="_blank">📥 Download File</a>
                                        </div>
                                    """, unsafe_allow_html=True)
                                st.write("")
                else:
                    st.info(f"Belum ada arsip untuk tahun {filter_tahun}.")
                
                st.write("---")
                if st.session_state['role'] == 'Admin':
                    with st.expander("🗑️ Hapus Laporan (Admin Only)"):
                        hapus_file = st.selectbox("Pilih file yang ingin dihapus permanen:", df['nama_file'].tolist())
                        if st.button("🚨 Hapus Data Permanen", type="primary"):
                            supabase.table("status_laporan").delete().eq("nama_file", hapus_file).execute()
                            supabase.storage.from_("laporan_files").remove([hapus_file])
                            st.success("File berhasil dihapus!")
                            st.rerun()
            else:
                st.info("Belum ada dokumen yang diunggah ke server.")

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
