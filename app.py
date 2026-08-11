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
# 2. FUNGSI DATABASE (KUNJUNGAN & PENYAKIT) - PERBAIKAN BUG
# ==========================================
def load_db_penyakit():
    try:
        res = supabase.storage.from_("laporan_files").download("db_penyakit.csv")
        return pd.read_csv(BytesIO(res))
    except:
        return pd.DataFrame(columns=['Tahun', 'Bulan', 'NAMA PENYAKIT', 'JML'])

def update_db_penyakit(df_new, tahun, bulan):
    df_lama = load_db_penyakit()
    if not df_lama.empty:
        df_lama = df_lama[~((df_lama['Tahun'] == tahun) & (df_lama['Bulan'] == bulan))]
    
    df_new['Tahun'] = tahun
    df_new['Bulan'] = bulan
    df_final = pd.concat([df_lama, df_new], ignore_index=True)
    
    data = df_final.to_csv(index=False).encode('utf-8')
    
    # PERBAIKAN BUG 409: Hapus file lama dulu (jika ada), baru upload yang baru
    try: supabase.storage.from_("laporan_files").remove(["db_penyakit.csv"])
    except: pass
    supabase.storage.from_("laporan_files").upload(path="db_penyakit.csv", file=data)

def load_db_kunjungan():
    try:
        res = supabase.storage.from_("laporan_files").download("db_kunjungan.csv")
        return pd.read_csv(BytesIO(res))
    except:
        return pd.DataFrame(columns=['Tahun', 'Bulan', 'Total'])

def update_db_kunjungan(total, tahun, bulan):
    df_lama = load_db_kunjungan()
    if not df_lama.empty:
        df_lama = df_lama[~((df_lama['Tahun'] == tahun) & (df_lama['Bulan'] == bulan))]
    
    df_new = pd.DataFrame([{'Tahun': tahun, 'Bulan': bulan, 'Total': total}])
    df_final = pd.concat([df_lama, df_new], ignore_index=True)
    
    data = df_final.to_csv(index=False).encode('utf-8')
    
    # PERBAIKAN BUG 409: Hapus file lama dulu (jika ada), baru upload yang baru
    try: supabase.storage.from_("laporan_files").remove(["db_kunjungan.csv"])
    except: pass
    supabase.storage.from_("laporan_files").upload(path="db_kunjungan.csv", file=data)

# ==========================================
# 3. CUSTOM CSS MODERN
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .stButton>button { border-radius: 8px; font-weight: bold; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); background-color: #0284c7; color: white; border: none; }
    .stButton>button:hover { background-color: #0369a1; color: white; transform: translateY(-2px); }
    .login-box { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border-top: 5px solid #0284c7; }
    .kepatuhan-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; height: 100%; }
    .progress-bar-bg { background-color: #e2e8f0; border-radius: 10px; height: 14px; width: 100%; overflow: hidden; margin-top: 10px; }
    .progress-bar-fill { background: linear-gradient(90deg, #34d399 0%, #059669 100%); height: 100%; border-radius: 10px; transition: width 0.8s ease-in-out; }
    .badge-sudah { background-color: #ecfdf5; color: #065f46; padding: 8px 16px; border-radius: 20px; display: inline-block; margin: 5px; font-weight: bold; font-size: 13px; border: 1px solid #a7f3d0; }
    .badge-belum { background-color: #fef2f2; color: #991b1b; padding: 8px 16px; border-radius: 20px; display: inline-block; margin: 5px; font-weight: bold; font-size: 13px; border: 1px solid #fecaca; }
    .file-item { padding: 8px 0px; border-bottom: 1px solid #f1f5f9; }
    .file-item a { text-decoration: none; color: #0284c7; font-weight: bold; }
    .big-metric { background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%); color: white; padding: 20px; border-radius: 15px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 20px;}
    .big-metric h3 { margin: 0; font-size: 18px; font-weight: 400; opacity: 0.9; }
    .big-metric h1 { margin: 0; font-size: 48px; font-weight: 800; }
    div[data-testid="metric-container"] { background: white; border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border-left: 5px solid #0ea5e9; }
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("🏥 Portal Internal")
menu = st.sidebar.radio("Navigasi Utama:", ["Upload Dokumen", "Dashboard Admin"])

DAFTAR_PROGRAM = ["Farmasi", "Gizi", "Ausrem", "KIA/KB", "Promkes", "Kesling", "P2P", "Laboratorium", "Tata Usaha"]
DAFTAR_TAHUN = ["2024", "2025", "2026", "2027", "2028", "2029"]
LIST_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

# ==========================================
# HALAMAN 1: UPLOAD LAPORAN (UMUM)
# ==========================================
if menu == "Upload Dokumen":
    st.title("📤 Portal Arsip & Laporan Internal")
    st.write("---")
    col1, col2 = st.columns([1, 1.5])
    with col1:
        instansi = st.selectbox("1. Pilih Unit / Program:", ["Pilih Program..."] + DAFTAR_PROGRAM + ["Program Lainnya"])
        jenis_laporan = st.radio("2. Kategori Laporan:", ["Bulanan", "Tahunan"], horizontal=True)
        tahun_laporan = st.selectbox("3. Pilih Tahun:", DAFTAR_TAHUN, index=2) 
        bulan_laporan = st.selectbox("4. Pilih Bulan:", LIST_BULAN) if jenis_laporan == "Bulanan" else "Tahunan"
    with col2:
        file_upload = st.file_uploader("5. Pilih File Dokumen (PDF/Word/Excel)", type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv'])
        st.write("")
        if st.button("🚀 Unggah Dokumen ke Server", use_container_width=True):
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
# HALAMAN 2: DASHBOARD ADMIN (FULL MODERN)
# ==========================================
elif menu == "Dashboard Admin":
    if not st.session_state['sudah_login']:
        st.write(""); st.write("")
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
        
        tab1, tab2, tab3 = st.tabs(["📈 Dashboard Eksekutif", "📂 Arsip Folder", "⚙️ Akun"])
        
        # --- TAB 1: DASHBOARD EKSEKUTIF (5 BAGIAN) ---
        with tab1:
            # 1. FILTER UTAMA (Mengendalikan seluruh halaman)
            f1, f2 = st.columns(2)
            with f1:
                dash_tahun = st.selectbox("📅 Pilih Tahun Pantauan:", DAFTAR_TAHUN, index=2)
            with f2:
                dash_bulan = st.selectbox("📆 Pilih Bulan Pantauan:", LIST_BULAN)
            
            st.write("---")
            
            # AMBIL SEMUA DATA DARI DATABASE
            respon = supabase.table("status_laporan").select("*").execute()
            df_status = pd.DataFrame(respon.data) if len(respon.data) > 0 else pd.DataFrame()
            df_kunjungan = load_db_kunjungan()
            df_penyakit = load_db_penyakit()
            
            # --- BAGIAN 1: KEPATUHAN BULANAN ---
            program_sudah = []
            program_belum = DAFTAR_PROGRAM
            if not df_status.empty:
                target_status = f"Bulanan|{dash_bulan}|{dash_tahun}"
                df_target = df_status[df_status['status'] == target_status]
                program_sudah = df_target['nama_instansi'].unique().tolist()
                program_belum = [p for p in DAFTAR_PROGRAM if p not in program_sudah]
            
            jml_sudah = len(program_sudah)
            total_p = len(DAFTAR_PROGRAM)
            persen_patuh = int((jml_sudah / total_p) * 100) if total_p > 0 else 0
            
            st.subheader(f"1. Status Kepatuhan Laporan (Periode {dash_bulan} {dash_tahun})")
            st.markdown(f"""
            <div style="background: white; padding: 20px; border-radius: 15px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 20px;">
                <h4 style="margin-top: 0; color: #334155;">Tingkat Kepatuhan Unit: <span style="color: #059669;">{persen_patuh}%</span></h4>
                <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {persen_patuh}%;"></div></div>
                <div style="margin-top: 15px;">
                    <strong>✅ Sudah Lapor ({jml_sudah}):</strong> {" ".join([f"<span class='badge-sudah'>{p}</span>" for p in program_sudah]) if program_sudah else "Belum ada"} <br>
                    <strong>⏳ Belum Lapor ({len(program_belum)}):</strong> {" ".join([f"<span class='badge-belum'>{p}</span>" for p in program_belum]) if program_belum else "Semua sudah lapor!"}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # --- BAGIAN 2 & 3: KUNJUNGAN & PENYAKIT BULANAN ---
            col_b1, col_b2 = st.columns([1, 2.5])
            
            with col_b1:
                st.subheader(f"2. Kunjungan Bulanan")
                kunj_bulan_ini = 0
                if not df_kunjungan.empty:
                    df_kb = df_kunjungan[(df_kunjungan['Tahun'] == dash_tahun) & (df_kunjungan['Bulan'] == dash_bulan)]
                    if not df_kb.empty:
                        kunj_bulan_ini = int(df_kb['Total'].sum())
                
                st.markdown(f"""
                <div class='big-metric'>
                    <h3>Total Pasien ({dash_bulan})</h3>
                    <h1>{kunj_bulan_ini:,}</h1>
                    <p style='margin:0;'>Orang</p>
                </div>
                """, unsafe_allow_html=True)
                
            with col_b2:
                st.subheader(f"3. 10 Besar Penyakit ({dash_bulan} {dash_tahun})")
                if not df_penyakit.empty:
                    df_pb = df_penyakit[(df_penyakit['Tahun'] == dash_tahun) & (df_penyakit['Bulan'] == dash_bulan)]
                    if not df_pb.empty:
                        df_pb_top10 = df_pb.groupby('NAMA PENYAKIT', as_index=False)['JML'].sum().sort_values('JML', ascending=False).head(10)
                        chart_pb = alt.Chart(df_pb_top10).mark_bar(color='#0ea5e9', cornerRadiusEnd=3).encode(
                            x=alt.X('JML:Q', title='Jumlah Kasus', axis=alt.Axis(grid=False)),
                            y=alt.Y('NAMA PENYAKIT:N', sort='-x', title=''),
                            tooltip=['NAMA PENYAKIT', 'JML']
                        ).properties(height=250)
                        st.altair_chart(chart_pb, use_container_width=True)
                    else:
                        st.info(f"Belum ada data penyakit untuk {dash_bulan} {dash_tahun}.")
                else:
                    st.info("Database penyakit masih kosong.")
            
            st.write("---")
            
            # --- BAGIAN 4 & 5: KUMULATIF TAHUNAN ---
            col_t1, col_t2 = st.columns(2)
            
            with col_t1:
                st.subheader(f"4. Tren Kunjungan Tahunan ({dash_tahun})")
                if not df_kunjungan.empty:
                    df_kt = df_kunjungan[df_kunjungan['Tahun'] == dash_tahun]
                    if not df_kt.empty:
                        df_kt['Bulan'] = pd.Categorical(df_kt['Bulan'], categories=LIST_BULAN, ordered=True)
                        df_kt = df_kt.sort_values('Bulan')
                        
                        chart_kt = alt.Chart(df_kt).mark_area(
                            line={'color':'#10b981'},
                            color=alt.Gradient(gradient='linear', stops=[alt.GradientStop(color='#10b981', offset=0), alt.GradientStop(color='white', offset=1)], x1=1, x2=1, y1=1, y2=0)
                        ).encode(
                            x=alt.X('Bulan:N', sort=LIST_BULAN, title=''),
                            y=alt.Y('Total:Q', title='Jumlah Pasien'),
                            tooltip=['Bulan', 'Total']
                        ).properties(height=300)
                        st.altair_chart(chart_kt, use_container_width=True)
                        st.success(f"**Total Kumulatif {dash_tahun}: {int(df_kt['Total'].sum()):,} Pasien**")
                    else:
                        st.info(f"Belum ada data kunjungan di tahun {dash_tahun}.")
                else:
                    st.info("Database kunjungan masih kosong.")
                    
            with col_t2:
                st.subheader(f"5. 10 Besar Penyakit Tahunan ({dash_tahun})")
                if not df_penyakit.empty:
                    df_pt = df_penyakit[df_penyakit['Tahun'] == dash_tahun]
                    if not df_pt.empty:
                        df_pt_top10 = df_pt.groupby('NAMA PENYAKIT', as_index=False)['JML'].sum().sort_values('JML', ascending=False).head(10)
                        chart_pt = alt.Chart(df_pt_top10).mark_bar(color='#f43f5e', cornerRadiusEnd=3).encode(
                            x=alt.X('JML:Q', title='Total Kasus Setahun', axis=alt.Axis(grid=False)),
                            y=alt.Y('NAMA PENYAKIT:N', sort='-x', title=''),
                            tooltip=['NAMA PENYAKIT', 'JML']
                        ).properties(height=300)
                        st.altair_chart(chart_pt, use_container_width=True)
                    else:
                        st.info(f"Belum ada data penyakit di tahun {dash_tahun}.")
                else:
                    st.info("Database penyakit masih kosong.")
                    
            st.write("")
            
            # ==========================================
            # KONTROL INPUT ADMIN
            # ==========================================
            with st.expander("⚙️ Input Data Dashboard (Admin Only)"):
                st.write("Gunakan menu ini untuk memasukkan data penyakit dan kunjungan per bulan.")
                inp1, inp2 = st.columns(2)
                
                with inp1:
                    st.markdown("**(A) Upload Excel 10 Besar Penyakit**")
                    with st.form("form_penyakit"):
                        p_tahun = st.selectbox("Untuk Tahun:", DAFTAR_TAHUN, index=2)
                        p_bulan = st.selectbox("Untuk Bulan:", LIST_BULAN)
                        file_p = st.file_uploader("Pilih file Excel Penyakit", type=['xls', 'xlsx'])
                        if st.form_submit_button("🔄 Proses & Simpan ke Database"):
                            if file_p is not None:
                                try:
                                    df_raw = pd.read_excel(file_p)
                                    df_raw.columns = df_raw.columns.astype(str).str.strip().str.upper()
                                    if "NAMA PENYAKIT" not in df_raw.columns:
                                        df_raw = pd.read_excel(file_p, skiprows=1)
                                        df_raw.columns = df_raw.columns.astype(str).str.strip().str.upper()
                                        
                                    if "NAMA PENYAKIT" in df_raw.columns and "JML" in df_raw.columns:
                                        df_clean = df_raw.dropna(subset=['NAMA PENYAKIT', 'JML'])
                                        df_clean = df_clean[['NAMA PENYAKIT', 'JML']]
                                        df_clean['JML'] = pd.to_numeric(df_clean['JML'], errors='coerce').fillna(0)
                                        df_top10 = df_clean.sort_values('JML', ascending=False).head(10)
                                        update_db_penyakit(df_top10, p_tahun, p_bulan)
                                        st.success(f"✅ Data Penyakit {p_bulan} {p_tahun} tersimpan!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Format gagal. Pastikan ada judul 'NAMA PENYAKIT' dan 'JML'.")
                                except Exception as e: st.error(f"Error: {e}")
                            else:
                                st.warning("Pilih file excel dulu.")
                                
                with inp2:
                    st.markdown("**(B) Upload Excel Kunjungan (Auto-Read)**")
                    with st.form("form_kunjungan"):
                        k_tahun = st.selectbox("Untuk Tahun:", DAFTAR_TAHUN, index=2)
                        k_bulan = st.selectbox("Untuk Bulan:", LIST_BULAN)
                        file_k = st.file_uploader("Pilih file Excel Kunjungan", type=['xls', 'xlsx'])
                        if st.form_submit_button("🔄 Ekstrak Angka Kunjungan"):
                            if file_k is not None:
                                try:
                                    # Membaca tanpa header
                                    df_k = pd.read_excel(file_k, header=None)
                                    total_pasien = 0
                                    found = False
                                    for idx, row in df_k.iterrows():
                                        # PERBAIKAN BUG FLOAT FOUND: Memaksa semua nilai menjadi string secara paksa
                                        row_str = " ".join([str(val) for val in row.values]).lower()
                                        
                                        if "jumlah kunjungan puskesmas" in row_str and "baru dan lama" in row_str:
                                            # Ambil semua angka di baris tersebut
                                            nums = pd.to_numeric(row, errors='coerce').dropna()
                                            if len(nums) >= 2:
                                                total_pasien = int(nums.iloc[0] + nums.iloc[1])
                                            elif len(nums) == 1:
                                                total_pasien = int(nums.iloc[0])
                                            found = True
                                            break
                                    
                                    if found:
                                        update_db_kunjungan(total_pasien, k_tahun, k_bulan)
                                        st.success(f"✅ Angka ditemukan! Total: {total_pasien}. Tersimpan untuk {k_bulan} {k_tahun}.")
                                        st.rerun()
                                    else:
                                        st.error("❌ Gagal menemukan kalimat 'Jumlah kunjungan puskesmas (baru dan lama)' di dalam file.")
                                except Exception as e: st.error(f"Error: {e}")
                            else:
                                st.warning("Pilih file excel kunjungan dulu.")

        # --- TAB 2 & 3: (ARSIP & AKUN TETAP AMAN) ---
        with tab2:
            st.subheader("📂 Ruang Arsip Digital (Explorer)")
            if not df_status.empty:
                def urai_status(teks):
                    try:
                        parts = str(teks).split('|')
                        if len(parts) == 3: return parts[0], parts[1], parts[2]
                        return "Bulanan", teks, "2026" 
                    except: return "-", "-", "-"
                
                df_arsip = df_status.copy()
                df_arsip['Jenis Laporan'], df_arsip['Bulan'], df_arsip['Tahun'] = zip(*df_arsip['status'].map(urai_status))
                urutan_bulan = {"Januari":1, "Februari":2, "Maret":3, "April":4, "Mei":5, "Juni":6, "Juli":7, "Agustus":8, "September":9, "Oktober":10, "November":11, "Desember":12, "Tahunan":13}
                df_arsip['Urutan_Bulan'] = df_arsip['Bulan'].map(urutan_bulan)

                filter_tahun_arsip = st.selectbox("Filter Tahun Arsip:", ["Semua Tahun"] + DAFTAR_TAHUN, index=0)
                if filter_tahun_arsip != "Semua Tahun":
                    df_arsip = df_arsip[df_arsip['Tahun'] == filter_tahun_arsip]
                
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
                else: st.info(f"Belum ada arsip untuk tahun {filter_tahun_arsip}.")
                
                st.write("---")
                if st.session_state['role'] == 'Admin':
                    with st.expander("🗑️ Hapus Dokumen Permanen (Admin)"):
                        hapus_file = st.selectbox("Pilih file yang salah upload:", df_status['nama_file'].tolist())
                        if st.button("🚨 Hapus File Ini", type="primary"):
                            supabase.table("status_laporan").delete().eq("nama_file", hapus_file).execute()
                            supabase.storage.from_("laporan_files").remove([hapus_file])
                            st.success("File dihapus!")
                            st.rerun()
            else: st.info("Gudang arsip masih kosong.")

        with tab3:
            st.subheader("Manajemen Hak Akses & Akun")
            if st.session_state['role'] == 'Admin':
                with st.form("form_tambah_akun"):
                    baru_user = st.text_input("Username Baru")
                    baru_pass = st.text_input("Password Baru")
                    baru_role = st.selectbox("Hak Akses", ["Kepala Puskesmas", "Admin", "Tim TU"])
                    if st.form_submit_button("Buat Akun ✅"):
                        supabase.table("akun_pengguna").insert({"username": baru_user, "password": baru_pass, "role": baru_role}).execute()
                        st.success(f"Akun '{baru_user}' dibuat!")
            else: st.warning("Hanya Admin utama yang bisa mengakses menu ini.")
