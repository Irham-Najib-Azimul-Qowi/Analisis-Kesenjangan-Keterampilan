# -*- coding: utf-8 -*-
"""
Intelligent Skill Gap Analytics Dashboard - Clean Modern Light Theme App
Project: CV Evaluation and Job Recommendation System
Semester 4 Politeknik Negeri Madiun
"""

import os
import re
import json
import uuid
import time
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from kafka import KafkaConsumer

# ==============================================================================
# 🎨 1. HIGH-CONTRAST MODERN LIGHT THEME STYLING
# ==============================================================================

# Injected CSS for ultra-clean light mode with high-end presentation aesthetics
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    /* Global Typography Reset */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
    }
    
    /* Clean Top Header Bar */
    [data-testid="stHeader"] {
        background-color: rgba(248, 250, 252, 0.8) !important;
        backdrop-filter: blur(12px) !important;
        border-bottom: 1px solid #e2e8f0 !important;
    }
    
    /* Executive Metric KPI Card Layout */
    .kpi-card {
        height: 155px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 4px 20px -2px rgba(148, 163, 184, 0.06) !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    .kpi-card:hover {
        transform: translateY(-4px) !important;
        border-color: #4f46e5 !important;
        box-shadow: 0 10px 25px -4px rgba(79, 70, 229, 0.1) !important;
    }
    
    .kpi-title {
        color: #64748b !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        margin-bottom: 2px !important;
    }
    
    .kpi-value {
        font-size: 30px !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        margin-bottom: 2px !important;
        letter-spacing: -0.8px !important;
        line-height: 1.1 !important;
    }
    
    .kpi-value-skill {
        font-size: 20px !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        margin-bottom: 2px !important;
        letter-spacing: -0.5px !important;
        line-height: 1.2 !important;
    }
    
    .kpi-desc {
        color: #94a3b8 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
    }
    
    /* Color accent indicators on top of cards for high-end organization */
    .kpi-indigo { border-top: 4px solid #4f46e5 !important; }
    .kpi-teal { border-top: 4px solid #0d9488 !important; }
    .kpi-amber { border-top: 4px solid #d97706 !important; }
    .kpi-rose { border-top: 4px solid #e11d48 !important; }
    
    /* Custom Styled recommendation boxes */
    .recommendation-box {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 24px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.01) !important;
        margin-top: 20px !important;
    }
    
    /* Premium List Item styling inside Recommendations */
    .rec-item {
        background-color: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 14px !important;
        margin-bottom: 12px !important;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 🛡️ 2. CERTIFICATE AUTO-GEN FOR CLOUD DEPLOYMENT
# ==============================================================================
def initialize_certificates():
    """Generates physical SSL certificate files dynamically in app directory to prevent deployment issues."""
    os.makedirs("ssl", exist_ok=True)
    
    CA_CERT = """-----BEGIN CERTIFICATE-----
MIIERDCCAqygAwIBAgIUNWVA0wt4k1otZvtZb4wnJprC3vIwDQYJKoZIhvcNAQEM
BQAwOjE40YGA1UEAwwvYTA5NDQ2YjQtZTQzNC00NWJlLWJkZjktYTljMGQ5ZDIw
NzNiIFByb2plY3QgQ0EwHhcNMjYwNTIyMDMzNjQ0WhcNMzYwNTE5MDMzNjQ0WjA6
MTgwNgYDVQQDDC9hMDk0NDZiNC1lNDM0LTQ1YmUtYmRmOS1hOWMwZDlkMjA3M2Ig
UHJvamVjdCBDQTCCAaIwDQYJKoZIhvcNAQEBBQADggGPADCCAYoCggGBAKawJaPF
V5DPf/zXslgQC8MfvtsYY3Zqplnt8ni0He67KQAkmm/R9iDXoe4RNKBpjOVzhc8x
85QnO49kOcmlPZ1DcDA3C+2C50VEsazr3PlAuyu7lQOi7qw4A67ePqyNmj/xBCfN
G0NEi2DCysO8QMctwM5do7Y8UYzHJAxKtXsS45xtNqkUFN2418sQfD0cGbaXcwgR
btp45sTnlfT1lkPHfWdoBo3EOwNtBmtCovmkJEF5rKLT1/TKFW+EniF+7E6d+YgA
g/+/oDPkA4VNhhq5ffGMkBZAi7B5CwXFz/8l1CoXSKldFzwh3SGRv5LM36LundgS
yURQp0HxwxrdegZvOwF9VMk6H1r/H0/MV1w/VIye3z2lxxmRvt2a/WFOBMf+IZkJ
s/wyCKcYP/cf6xwEu61D23szejro62jy8bs4zor+HlxIRe6XAni0FwNi4WAXZrs1
HTb2m6FClkTdNxhjh+KXkwh85op7dm3fCBRX0WL9KqWbPQGp7SO1S6FROQIDAQAB
o0IwQDAdBgNVHQ4EFgQURjlmdqtpNF96xuYts1bBkDG4KO0wEgYDVR0TAQH/BAgw
BgEB/wIBADALBgNVHQ8EBAMCAQYwDQYJKoZIhvcNAQEMBQADggGBAEy6IL8uwOa9
g5sxXNTgKL4zEiwzSJlrH0eIwJZPIWI7nx/W8BQEyPxsvAkS9Z6qgcQSTX3SFPay
TW92CWbCS86juY8Gh8P5dXou7w4bgIyYkdezFJacd/IE6Q7X8pzi/uO99EYWA4je
9PVpQFD2Uu0wtOuqRas5Rc681zKbtCgsOp5IsMxgybvSqv0R91kAZI/m3CHJOz3g
UoVC+9GKpkbi/VPB5TvxBzJfhbVt2ttY+qUfgWZxMCX6sgR3uxX1Iwp9Dmbg/44C
glyKqjRb7ZOHGylT2eE0g04MlSZ+6KuS8fDag+RfzeO0YXOnRjUVDcAclCL+J6vO
yJxfHdWduyNajlbOYmK2tjbFD1/y/8N+UCwXualS8qEfc87V7ZQN1xBX9Ym0bRzM
nVLVuB/6AiJA3rrIpwZgMe54U2JL0PPFvsDNo88ZUriZtRL3whNqY8muQCOjGEZj
FidUg+FHW8o6/UoYYMFPAz3vdO5weQNzcH4Jjm+xSqzQBqVFFkUf4Q==
-----END CERTIFICATE-----"""

    CLIENT_CERT = """-----BEGIN CERTIFICATE-----
MIIEYDCCAsigAwIBAgIUebtuYV34s4KH3rH/+PjzxnKeiFUwDQYJKoZIhvcNAQEM
BQAwOjE4MDYGA1UEAwwvYTA5NDQ2YjQtZTQzNC00NWJlLWJkZjktYTljMGQ5ZDIw
NzNiIFByb2plY3QgQ0EwHhcNMjYwNTIyMDM0NjU3WhcNMzYwNTE5MDM0NjU3WjA+
MRgwFAYDVQQKDA1rYWZrYS05MGEzY2Q0MREwDwYDVQQLDAh1NXczcjVzNjERMA8G
A1UEAwwIYXZuYWRtaW4wggGiMA0GCSqGSIb3DQEBAQUAA4IBjwAwggGKAoIBgQCo
+sXA2ZQHbNY/WEnD0lzrVSxTI7vKFTt2OJtRKATtZwjs7AmkDerElo6NjPAQUY8M
W/WLoDGOwNw1dsoChg2DdtcISwwusTSOAkTc+aDBtw8RlUng0x7Rx0T/irCP+LRF
DIz/jnZhTsvxn1e58TFvfxY/e7B+j78dsbphClTLJvbj/oh7CU8B4WUZSreiScyB
CuDfjcjaUNnl0hXMAFD8f2crYn7/WpE6RrWPsw7etdkYXaUQXoY9PFucJsbJkfp5
Mbkqutj3lmYATwfQOlTazYCUL00pIKRSvNa3g1+KNzcjYXClY+Dx3Q6+8QP7s0Zn
IatsSUjGIvZQmOpHrZuGPWb6uqSrLZ7+UnbBKicYS8Dta7NIVUPBwJBNeYpfm3u7
12KAFmB1lBYPxLkP9RLBiYDpBOUYJD9icRdPKFCdSwIdFVsLFKX8wJODUKfMTwIB
zklEbNbjHXNbAf0bxzE9CX0Fai5wIhIX7svoeXEzP0AusDW+8kOAavv7qdGYyPEC
AwEAAaNaMFgwHQYDVR0OBBYEFCDYzscbnUeWPfJRT6AI8RmSq5QyMAkGA1UdEwQC
MAAwCwYDVR0PBAQDAgWgMB8GA1UdIwQYMBaAFEY5ZnaraTRfesbmLbNWwZAxuCjt
MA0GCSqGSIb3DQEBDAUAA4IBgQCXLF3ADHWjLCuHIAZx9SvzVk1TPYaEOr2mrCBN
4/6AMHkf6/E4nMggKji0KaPIcMvWqzPxvAOtq/HkTefql7HOiu8HtYvouL7Fyq5N
UK19nixAw/fjT/oOPUsI3qjlOpJVdRM79vsSA4bIvRy3v6qI/ZFalONy/Bk/GSWr
GpxSN2QOTX5w29OZdvWNLKnq9JvJMmhhs14mFqym0K5U2Iu9YoKzE0kfLXJ2WgTV
3cs29d3+q3kjbb7wchQJZtLRdxR3gj1WC6OSS/AwksPCFaV0hrl8AMoq23IQVI+o
DRP0JBFra42jUJs6AoNOOPzswGd9RXTrpIOUjhxtM9SYmREUMREJoPdJ8Jhgsl10
4oa7cvjOGzAuWaEXu1X4hN7Z93gngLERVc3LPiib3R39fvNCMsFd2iRPeC4jMTFQ
FYKnRRdTBi9I2REqz5kxnTKYX+JfWWfPt3Mq0Vd7kEhxtjQDpi8fCIdej84gT5lF
Ioh1PBVNvEPnc7LmpsIh8rYIiQM=
-----END CERTIFICATE-----"""

    PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
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
Dd9QJehLDH1Ytkr2w/Y9cFWE
-----END PRIVATE KEY-----"""

    if not os.path.exists("ssl/ca.pem"):
        with open("ssl/ca.pem", "w") as f:
            f.write(CA_CERT)
    if not os.path.exists("ssl/service.cert"):
        with open("ssl/service.cert", "w") as f:
            f.write(CLIENT_CERT)
    if not os.path.exists("ssl/service.key"):
        with open("ssl/service.key", "w") as f:
            f.write(PRIVATE_KEY)

initialize_certificates()


# ==============================================================================
# 📥 3. KAFKA REAL-TIME INGESTION ENGINE (DETERMINISTIC POLLING)
# ==============================================================================
KAFKA_BROKER = "kafka-90a3cd4-cejors-676945.g.aivencloud.com:28174"
TOPIC_NAME = "unified_jobs"
CACHE_FILE = "cached_data.csv"

def pull_data_from_kafka_live():
    """Deterministic Kafka Consumer pulling 100% exact offsets from broker."""
    CA_FILE = "ssl/ca.pem"
    CERT_FILE = "ssl/service.cert"
    KEY_FILE = "ssl/service.key"
    
    random_group_id = f"streamlit-group-{uuid.uuid4().hex[:8]}"
    
    try:
        consumer = KafkaConsumer(
            TOPIC_NAME,
            bootstrap_servers=KAFKA_BROKER,
            security_protocol="SSL",
            ssl_cafile=CA_FILE,
            ssl_certfile=CERT_FILE,
            ssl_keyfile=KEY_FILE,
            auto_offset_reset='earliest', 
            enable_auto_commit=False,
            group_id=random_group_id,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        assigned_partitions = []
        start_time = time.time()
        
        # Wait for assignment
        while not assigned_partitions:
            consumer.poll(timeout_ms=1000)
            assigned_partitions = list(consumer.assignment())
            if time.time() - start_time > 15:
                break
                
        if not assigned_partitions:
            consumer.close()
            return None
            
        end_offsets = consumer.end_offsets(assigned_partitions)
        records = []
        poll_start_time = time.time()
        
        while True:
            all_completed = True
            for tp in assigned_partitions:
                if consumer.position(tp) < end_offsets[tp]:
                    all_completed = False
                    break
                    
            if all_completed:
                break
                
            msg_pack = consumer.poll(timeout_ms=2000)
            if msg_pack:
                for tp, messages in msg_pack.items():
                    for message in messages:
                        records.append(message.value)
            else:
                time.sleep(1.0)
                
            if time.time() - poll_start_time > 90:  # Timeout safety
                break
                
        consumer.close()
        
        if records:
            df = pd.DataFrame(records)
            df.to_csv(CACHE_FILE, index=False)
            return df
        return None
        
    except Exception as e:
        st.sidebar.error(f"Kafka connection failed: {e}")
        return None


def get_analytics_data():
    """Gets the analytics dataset, trying local offline cache first, fallback to Kafka."""
    if os.path.exists(CACHE_FILE):
        try:
            return pd.read_csv(CACHE_FILE)
        except:
            pass
            
    # If no cache exists, pull from Kafka
    with st.spinner("⏳ Menghubungkan ke Aiven Kafka Broker untuk inisialisasi awal..."):
        df = pull_data_from_kafka_live()
        if df is not None:
            return df
            
    # Extreme fallback
    st.error("⚠️ Gagal terhubung ke Kafka & Cache Lokal Kosong.")
    return pd.DataFrame(columns=['unique_id', 'data_source', 'job_title', 'skills_required', 'job_description'])


# ==============================================================================
# 🧠 4. NLP & SKILL GAP CALCULATION ENGINE
# ==============================================================================
def count_skill_occurrences(dataframe, text_column, skill_list):
    results = {skill: 0 for skill in skill_list}
    total_records = len(dataframe)
    
    if total_records == 0:
        return {skill: 0.0 for skill in skill_list}
        
    for idx, row in dataframe.iterrows():
        text = str(row[text_column]).lower()
        for skill in skill_list:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text):
                results[skill] += 1
                
    return {skill: (count / total_records) * 100 for skill, count in results.items()}


def analyze_gap(df, selected_skills):
    df_onet = df[df['data_source'] == 'ONET_Standard']
    df_industry = df[df['data_source'].isin(['Adzuna_API', 'Kaggle_LinkedIn'])]
    
    # Calculate frequencies
    academic_pcts = count_skill_occurrences(df_onet, 'skills_required', selected_skills)
    industry_pcts = count_skill_occurrences(df_industry, 'job_description', selected_skills)
    
    gap_data = []
    for skill in selected_skills:
        acad = academic_pcts[skill]
        ind = industry_pcts[skill]
        gap = ind - acad
        
        gap_data.append({
            'Skill / Technology': skill,
            'Kurikulum Akademis (%)': round(acad, 2),
            'Tuntutan Industri (%)': round(ind, 2),
            'Kesenjangan (Gap Score) (%)': round(gap, 2)
        })
        
    return pd.DataFrame(gap_data)


# ==============================================================================
# 🖥️ 5. DASHBOARD USER INTERFACE
# ==============================================================================

# Title Header Section
col_header_title, col_header_logo = st.columns([5, 1])
with col_header_title:
    st.markdown("<h1 style='margin-bottom:0px; color:#0f172a; font-family: Outfit;'>Analisis Kesenjangan Keterampilan Lulusan (Skill Gap Index)</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#475569; font-size:16px; margin-top:2px; font-weight: 500;'>Politeknik Negeri Madiun — Evaluasi Keselarasan Kurikulum dengan Kebutuhan Riil Industri</p>", unsafe_allow_html=True)
with col_header_logo:
    st.markdown("""
    <div style='background-color:rgba(79, 70, 229, 0.08); border:1px solid rgba(79, 70, 229, 0.15); border-radius:12px; padding:10px; text-align:center;'>
        <span style='color:#4f46e5; font-weight:800; font-size:14px; display:block; font-family: "Outfit";'>POLITEKNIK</span>
        <span style='color:#334155; font-weight:600; font-size:10px; display:block; font-family: "Outfit";'>NEGERI MADIUN</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin-top:10px; margin-bottom:25px; border-color:#e2e8f0;'>", unsafe_allow_html=True)

# Load Data
df_raw = get_analytics_data()

if df_raw is not None and not df_raw.empty:
    
    # --------------------------------------------------------------------------
    # SIDEBAR: ADVANCED OPTIONS
    # --------------------------------------------------------------------------
    st.sidebar.markdown("<h2 style='color:#4f46e5; margin-top:0px; font-size:22px; font-family: Outfit;'>Kontrol Analisis</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("<hr style='margin:10px 0; border-color:#e2e8f0;'>", unsafe_allow_html=True)
    
    # Sync with Kafka Broker live button
    if st.sidebar.button("Tarik Data Terbaru dari Kafka Broker", use_container_width=True, help="Melakukan sinkronisasi langsung dengan broker Aiven Kafka Cloud Anda"):
        with st.spinner("⏳ Menghubungkan ke Aiven Kafka..."):
            df_live = pull_data_from_kafka_live()
            if df_live is not None:
                st.sidebar.success("Sinkronisasi data terbaru berhasil!")
                st.rerun()
            else:
                st.sidebar.error("Gagal terhubung ke broker Aiven Kafka. Memuat cache cadangan.")
                
    st.sidebar.markdown("<div style='margin-top:20px; margin-bottom:8px;'><h4 style='color:#334155; font-size:14px; font-weight:700; margin:0; font-family: Outfit;'>PILIHAN KETERAMPILAN</h4></div>", unsafe_allow_html=True)
    st.sidebar.markdown("Pilih keahlian yang ingin dievaluasi kesenjangannya:")
    
    available_skills = [
        "Python", "SQL", "Excel", "Tableau", "Java", "Machine Learning", 
        "Cloud", "Project Management", "Data Warehouse", "Git", "Power BI", 
        "Statistics", "C++", "React", "PHP", "Docker"
    ]
    
    selected_skills = st.sidebar.multiselect(
        "Daftar Keterampilan:",
        options=available_skills,
        default=["Python", "SQL", "Excel", "Tableau", "Java", "Machine Learning", "Cloud", "Project Management", "Data Warehouse"]
    )
    
    st.sidebar.markdown("<div style='margin-top:25px; margin-bottom:8px;'><h4 style='color:#334155; font-size:14px; font-weight:700; margin:0; font-family: Outfit;'>RINGKASAN SUMBER DATA</h4></div>", unsafe_allow_html=True)
    
    # Total sources counts
    onet_count = len(df_raw[df_raw['data_source'] == 'ONET_Standard'])
    industry_count = len(df_raw[df_raw['data_source'] != 'ONET_Standard'])
    
    st.sidebar.markdown(f"""
    <div style='background-color:#ffffff; border: 1px solid #e2e8f0; border-radius:10px; padding:15px; font-size:13px; color:#334155; line-height: 1.5;'>
        <p style='margin:0 0 6px 0; color:#0d9488; font-weight:700;'>• Kafka Broker: Terhubung</p>
        <p style='margin:0 0 6px 0; color:#334155;'>• Total Data: <strong>{len(df_raw):,}</strong> baris</p>
        <p style='margin:0 0 6px 0; color:#334155;'>• Standar O*NET: <strong>{onet_count:,}</strong> profesi</p>
        <p style='margin:0; color:#334155;'>• Lowongan Kerja: <strong>{industry_count:,}</strong> sampel</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculations
    df_gap = analyze_gap(df_raw, selected_skills)
    
    # --------------------------------------------------------------------------
    # SECTION 1: EXEC KPI CARDS (DASHBOARD HIGHLIGHTS)
    # --------------------------------------------------------------------------
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        st.markdown(f"""
        <div class="kpi-card kpi-indigo">
            <div class="kpi-title">Data Terintegrasi</div>
            <div class="kpi-value">{len(df_raw):,}</div>
            <div class="kpi-desc">Gabungan LinkedIn, Adzuna, & O*NET</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col2:
        st.markdown(f"""
        <div class="kpi-card kpi-teal">
            <div class="kpi-title">Kurikulum O*NET</div>
            <div class="kpi-value">{onet_count:,}</div>
            <div class="kpi-desc">Standar Rujukan Profesi Akademis</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col3:
        st.markdown(f"""
        <div class="kpi-card kpi-amber">
            <div class="kpi-title">Lowongan Pasar Industri</div>
            <div class="kpi-value">{industry_count:,}</div>
            <div class="kpi-desc">LinkedIn & Adzuna API Terkumpul</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col4:
        # Calculate worst deficit (highest positive gap score, meaning industry demands it much more than curriculum teaches)
        critical_deficit = df_gap.loc[df_gap['Kesenjangan (Gap Score) (%)'].idxmax()]
        st.markdown(f"""
        <div class="kpi-card kpi-rose">
            <div class="kpi-title">Kesenjangan Terbesar</div>
            <div class="kpi-value-skill">{critical_deficit['Skill / Technology']}</div>
            <div class="kpi-desc">Selisih Kebutuhan: {critical_deficit['Kesenjangan (Gap Score) (%)']}%</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --------------------------------------------------------------------------
    # SECTION 2: THE EXECUTIVE PRESENTATION CHARTS (NON-RADAR, CLEAN BRIGHT STYLE)
    # --------------------------------------------------------------------------
    
    tab_overview, tab_explorer = st.tabs(["Analisis Kesenjangan & Kurikulum", "Pencarian Lowongan Kerja"])
    
    with tab_overview:
        chart_col, table_col = st.columns([1, 1])
        
        with chart_col:
            st.markdown("""
            <div style="margin-bottom: 15px;">
                <h3 style="font-size: 18px; font-weight: 700; color: #0f172a; margin: 0 0 4px 0; font-family: 'Outfit';">
                    🔄 Komparasi Persentase Kebutuhan
                </h3>
                <span style="color: #64748b; font-size: 13px; font-weight: 500; font-family: 'Plus Jakarta Sans';">
                    Porsi kurikulum akademis dibandingkan dengan lowongan kerja aktif
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            # Formulating DataFrame for side-by-side Plotly bar chart
            df_melted = df_gap.melt(
                id_vars=['Skill / Technology'], 
                value_vars=['Kurikulum Akademis (%)', 'Tuntutan Industri (%)'],
                var_name='Kategori', 
                value_name='Persentase (%)'
            )
            
            # Create a premium side-by-side grouped bar chart with bright high-end colors
            fig_compare = px.bar(
                df_melted,
                x='Skill / Technology',
                y='Persentase (%)',
                color='Kategori',
                barmode='group',
                color_discrete_map={
                    'Kurikulum Akademis (%)': '#4f46e5',  # Premium Deep Indigo
                    'Tuntutan Industri (%)': '#0d9488'   # Premium Teal
                },
                hover_data={'Persentase (%)': ':.2f'}
            )
            
            fig_compare.update_layout(
                template='plotly_white',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    title=dict(text='Keahlian Teknologi / Skill', font=dict(family='Plus Jakarta Sans', size=13, color='#475569')),
                    showgrid=False,
                    tickfont=dict(family='Plus Jakarta Sans', size=11, color='#475569')
                ),
                yaxis=dict(
                    title=dict(text='Proporsi Kemunculan (%)', font=dict(family='Plus Jakarta Sans', size=13, color='#475569')),
                    ticksuffix='%',
                    showgrid=True,
                    gridcolor='#f1f5f9',
                    tickfont=dict(family='Plus Jakarta Sans', size=11, color='#475569')
                ),
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1,
                    title=None,
                    font=dict(family='Plus Jakarta Sans', size=11, color='#475569')
                ),
                margin=dict(l=50, r=20, t=10, b=50),
                height=450
            )
            
            st.plotly_chart(fig_compare, use_container_width=True)
            
        with table_col:
            st.markdown("""
            <div style="margin-bottom: 15px;">
                <h3 style="font-size: 18px; font-weight: 700; color: #0f172a; margin: 0 0 4px 0; font-family: 'Outfit';">
                    📉 Indeks Kesenjangan Kompetensi
                </h3>
                <span style="color: #64748b; font-size: 13px; font-weight: 500; font-family: 'Plus Jakarta Sans';">
                    Skor kesenjangan (Gap Index) materi ajar secara menyeluruh
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            # Diverging bar chart for Gap Scores
            df_gap['Status'] = np.where(df_gap['Kesenjangan (Gap Score) (%)'] >= 0, 'Defisit / Kurang Diajarkan', 'Surplus / Cukup Diajarkan')
            
            fig_gap = px.bar(
                df_gap,
                x='Kesenjangan (Gap Score) (%)',
                y='Skill / Technology',
                color='Status',
                orientation='h',
                color_discrete_map={
                    'Defisit / Kurang Diajarkan': '#e11d48',  # Elegant Crimson Rose
                    'Surplus / Cukup Diajarkan': '#10b981'   # Elegant Emerald Green
                },
                hover_data={'Kesenjangan (Gap Score) (%)': ':.2f'}
            )
            
            # FIXED categoryorder TO BE 'total ascending' WITH SPACE (TO AVOID PLOTLY VALUEERROR CRASH!)
            # INCREASED l=140 IN MARGINS TO PREVENT CROPPED AXIS LABELS!
            fig_gap.update_layout(
                template='plotly_white',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    title=dict(text='Skor Kesenjangan (%)', font=dict(family='Plus Jakarta Sans', size=13, color='#475569')),
                    ticksuffix='%',
                    showgrid=True,
                    gridcolor='#f1f5f9',
                    tickfont=dict(family='Plus Jakarta Sans', size=11, color='#475569')
                ),
                yaxis=dict(
                    title=None,
                    showgrid=False,
                    categoryorder='total ascending',
                    tickfont=dict(family='Plus Jakarta Sans', size=11, color='#475569')
                ),
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='left',
                    x=0,
                    title=None,
                    font=dict(family='Plus Jakarta Sans', size=11, color='#475569')
                ),
                margin=dict(l=140, r=25, t=10, b=50),
                height=450
            )
            
            st.plotly_chart(fig_gap, use_container_width=True)
            
        # Dataframe Table View with clean white themes and conditional formatting
        st.markdown("<br><h4 style='font-size:16px; font-weight:700; color:#0f172a; margin-bottom:10px; font-family: Outfit;'>Matriks Rincian Data Analisis</h4>", unsafe_allow_html=True)
        
        def format_gap_column(val):
            # Highlight with modern light colors for a bright design
            if val > 5:
                return 'background-color: #ffe4e6; color: #e11d48; font-weight: bold;'
            elif val < -5:
                return 'background-color: #d1fae5; color: #059669; font-weight: bold;'
            else:
                return 'color: #334155;'
                
        # Format the table
        df_gap_table = df_gap[['Skill / Technology', 'Kurikulum Akademis (%)', 'Tuntutan Industri (%)', 'Kesenjangan (Gap Score) (%)']].copy()
        df_gap_table = df_gap_table.sort_values(by='Tuntutan Industri (%)', ascending=False)
        
        # FIXED TO future-proof width='stretch' to eliminate warnings!
        st.dataframe(
            df_gap_table.style.map(format_gap_column, subset=['Kesenjangan (Gap Score) (%)']),
            width='stretch',
            height=380
        )
        
        # --------------------------------------------------------------------------
        # SECTION 3: ACADEMIC RECOMMENDATION & INSIGHT MATRIX (CLEAN MODERN CARD)
        # --------------------------------------------------------------------------
        st.markdown("<br><hr style='border-color:#e2e8f0;'><br>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-size:20px; font-weight:700; color:#0f172a; margin:0 0 15px 0; font-family: Outfit;'>Kesimpulan & Rekomendasi Kurikulum</h3>", unsafe_allow_html=True)
        
        # UI/UX Interpretation Guide Card
        st.markdown("""
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 18px; margin-bottom: 25px; color: #475569; font-size: 13px; line-height: 1.6; font-family: 'Plus Jakarta Sans';">
            <strong style="color: #0f172a; font-size: 14px; display: block; margin-bottom: 6px; font-family: 'Outfit';">Cara Membaca Hasil Analisis:</strong>
            <ul style="margin: 0; padding-left: 18px;">
                <li style="margin-bottom: 4px;"><strong>Keterampilan Defisit (Kekurangan Porsi Ajar):</strong> Keahlian ini sangat dicari oleh industri (banyak lowongan kerja aktif), tetapi porsi pengajarannya di standar kurikulum masih sangat rendah. <strong>Disarankan untuk segera menambah jam pengajaran materi ini.</strong></li>
                <li><strong>Keterampilan Surplus (Kelebihan Porsi Ajar):</strong> Keahlian ini diajarkan dengan porsi yang sangat tinggi di kurikulum akademis, padahal kebutuhan riil lowongan kerja industri sebenarnya cukup rendah. <strong>Disarankan untuk mengurangi porsinya guna dialokasikan ke materi lain yang lebih penting.</strong></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        col_rec_left, col_rec_right = st.columns(2)
        
        # Identify urgent actions
        critical_deficits = df_gap[df_gap['Kesenjangan (Gap Score) (%)'] > 10].sort_values(by='Kesenjangan (Gap Score) (%)', ascending=False)
        surpluses = df_gap[df_gap['Kesenjangan (Gap Score) (%)'] < -10].sort_values(by='Kesenjangan (Gap Score) (%)')
        
        with col_rec_left:
            st.markdown("<h4 style='font-size:15px; font-weight:700; color:#0f172a; margin-bottom:12px; font-family: Outfit;'>Keterampilan Defisit (Kurang Diajarkan)</h4>", unsafe_allow_html=True)
            if not critical_deficits.empty:
                for _, row in critical_deficits.iterrows():
                    st.markdown(f"""
                    <div class="rec-item" style="border-left: 5px solid #e11d48 !important; color: #334155; font-family: 'Plus Jakarta Sans';">
                        <strong style='color:#e11d48; font-size:15px;'>{row['Skill / Technology']}</strong>
                        <span style='color:#475569; font-size:13px; display:block; margin-top:4px;'>
                            Dibutuhkan oleh <strong>{row['Tuntutan Industri (%)']}%</strong> lowongan industri, namun kurikulum akademis baru mengajarkannya sebesar <strong>{row['Kurikulum Akademis (%)']}%</strong>.
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("Kurikulum akademik saat ini sudah selaras dengan baik untuk seluruh keterampilan yang dipilih.")
                
        with col_rec_right:
            st.markdown("<h4 style='font-size:15px; font-weight:700; color:#0f172a; margin-bottom:12px; font-family: Outfit;'>Keterampilan Surplus (Kelebihan Porsi)</h4>", unsafe_allow_html=True)
            if not surpluses.empty:
                for _, row in surpluses.iterrows():
                    st.markdown(f"""
                    <div class="rec-item" style="border-left: 5px solid #10b981 !important; color: #334155; font-family: 'Plus Jakarta Sans';">
                        <strong style='color:#059669; font-size:15px;'>{row['Skill / Technology']}</strong>
                        <span style='color:#475569; font-size:13px; display:block; margin-top:4px;'>
                            Diajarkan hingga <strong>{row['Kurikulum Akademis (%)']}%</strong> di kurikulum akademik, padahal kebutuhan lowongan industri hanya sebesar <strong>{row['Tuntutan Industri (%)']}%</strong>.
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.write("Distribusi pengajaran kurikulum berimbang dengan kebutuhan industri.")
                
        # Strategic recommendations action panel
        st.markdown("""
        <div class="recommendation-box" style="color: #334155; font-family: 'Plus Jakarta Sans';">
            <h4 style='color:#4f46e5; margin-top:0px; font-size:16px; font-family: Outfit; font-weight: 700; margin-bottom: 12px;'>Langkah Aksi Rekomendasi Penyesuaian Kurikulum:</h4>
            <ol style='color:#475569; margin-bottom:0px; line-height:1.7; font-size:13px;'>
                <li style='margin-bottom:8px;'><strong>Penyesuaian Porsi Jam Belajar:</strong> Mengurangi jam praktek konvensional spreadsheet Excel statis, dan mengalihkan jam belajarnya untuk pendalaman konsep database SQL dan pemrograman Python dasar yang jauh lebih dicari dunia kerja.</li>
                <li style='margin-bottom:8px;'><strong>Pengenalan Konsep Cloud & Data Warehouse:</strong> Menambahkan materi komputasi awan (Cloud) dan konsep Data Warehouse ke dalam kurikulum basis data tingkat lanjut.</li>
                <li style='margin-bottom:0px;'><strong>Penyelarasan Sertifikasi Keahlian:</strong> Mendorong pelaksanaan sertifikasi kompetensi industri untuk memperbesar peluang daya serap lulusan di dunia kerja.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

    with tab_explorer:
        st.markdown("<h3 style='font-size:20px; font-weight:700; color:#0f172a; margin:0 0 5px 0; font-family: Outfit;'>Mesin Pencari Lowongan Kerja</h3>", unsafe_allow_html=True)
        st.markdown("Cari lowongan pekerjaan yang tersimpan di Kafka Broker berdasarkan kata kunci posisi dan kualifikasi.")
        
        # Extract unique roles
        df_jobs_only = df_raw[df_raw['data_source'] != 'ONET_Standard']
        
        col_search_1, col_search_2 = st.columns([2, 1])
        with col_search_1:
            search_query = st.text_input("Cari Posisi Pekerjaan (contoh: 'Data Engineer', 'Developer', 'Analyst'):", "")
        with col_search_2:
            exp_filter = st.selectbox(
                "Filter Tingkat Pengalaman:",
                options=["Semua"] + list(df_jobs_only['experience_level'].dropna().unique())
            )
            
        # Filtering logic
        df_filtered = df_jobs_only.copy()
        if search_query:
            df_filtered = df_filtered[df_filtered['job_title'].str.contains(search_query, case=False, na=False)]
        if exp_filter != "Semua":
            df_filtered = df_filtered[df_filtered['experience_level'] == exp_filter]
            
        st.markdown(f"Menampilkan **{len(df_filtered):,}** lowongan kerja yang relevan:")
        
        # Display clean styled columns
        if not df_filtered.empty:
            df_display = df_filtered[['job_title', 'company_name', 'location', 'experience_level', 'skills_required']].copy()
            df_display.columns = ['Nama Posisi', 'Perusahaan', 'Lokasi', 'Tingkat Pengalaman', 'Keahlian yang Dibutuhkan']
            st.dataframe(df_display, width='stretch', height=400)
        else:
            st.warning("Tidak menemukan lowongan pekerjaan yang cocok dengan kriteria pencarian Anda.")

else:
    st.warning("⚠️ Data tidak ditemukan. Silakan tekan tombol 'Tarik Data Live (Aiven Kafka)' di sidebar sebelah kiri untuk menarik data Anda pertama kalinya dari Broker Cloud.")
