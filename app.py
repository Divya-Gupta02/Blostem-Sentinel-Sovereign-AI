import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime
from textblob import TextBlob
 
 # --- 1. INITIALIZATION & SESSION STATE ---
if 'solved_ids' not in st.session_state:
 st.session_state.solved_ids = set()
if 'audit_log' not in st.session_state:
 st.session_state.audit_log = []
if 'locked_id' not in st.session_state:
 st.session_state.locked_id = None
 
st.set_page_config(page_title="Blostem Sentinel: Sovereign AI", layout="wide")
 
 # --- 2. HIGH-END THEMING (Typography & Glassmorphism) ---
st.markdown("""
     <style>
     @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=JetBrains+Mono&display=swap');
 
     html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
     .mono { font-family: 'JetBrains Mono', monospace; font-weight: 500; }
 
     /* Metric Card Styling */
     .metric-card {
         background: white; border: 1px solid #e2e8f0; padding: 20px;
         border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
     }
     .metric-value { font-family: 'JetBrains Mono'; font-size: 2rem; font-weight: 700; color: #0f172a; }
 
     /* Audit Log Styling */
     .audit-entry { font-family: 'JetBrains Mono'; font-size: 0.8rem; padding: 4px 0; border-bottom: 1px solid #f1f5f9; }
 
     /* Sidebar Compactness */
     section[data-testid="stSidebar"] { width: 300px !important; }
     </style>
     """, unsafe_allow_html=True)
 
 # --- 3. CORE LOGIC & DATA GENERATION ---
@st.cache_data
def load_data(rows=50):
 df = pd.DataFrame({
  'CustomerId': range(1000, 1000 + rows),
  'Churn_Risk': np.random.randint(10, 98, rows),
  'Predicted_LTV': np.random.randint(5000, 150000, rows),
  'Confidence': np.random.uniform(85, 99.9, rows),
  'Feedback': np.random.choice(['High fees', 'Slow app', 'Great service', 'Transfer failed'], rows),
  'Tx_Frequency': np.random.randint(1, 100, rows),
  'Market_Sentiment': np.random.uniform(-1, 1, rows)
 })
def tag_category(row):
 t = row['Feedback'].lower()
 if any(w in t for w in ['fee', 'rate', 'transfer']): return 'Financial'
 if any(w in t for w in ['app', 'slow', 'failed']): return 'Technical'
 return 'General Service'
df['Category'] = df.apply(tag_category, axis=1)
df['Is_Critical'] = (df['Churn_Risk'] > 80) & (df['Predicted_LTV'] > 100000)
return df
def add_audit(action):
 now = datetime.now().strftime("%H:%M:%S")
 st.session_state.audit_log.insert(0, f"[{now}] - {action}")
 
 # Formatted list label 
def format_id_display(cust_id, full_df):
 if cust_id in st.session_state.solved_ids:
  return f"✅ ID: {cust_id} (RESOLVED)"
 user_row = full_df[full_df['CustomerId'] == cust_id].iloc[0]
 if user_row['Is_Critical']:
  return f"🔴 ID: {cust_id} (HIGH ALERT)"
 return f"👤 ID: {cust_id}"
 
 # --- 4. DATA INGESTION & FILTERING ---
with st.sidebar:
 st.title("📁 Ingestion")
 uploaded = st.file_uploader("Upload CSV", type="csv", label_visibility="collapsed")
 df = pd.read_csv(uploaded) if uploaded else load_data()
 
 st.divider()
 st.subheader("🎛️ Parameters")
 risk_range = st.slider("Min Risk Score", 0, 100, 40)
 ltv_range = st.slider("Min LTV ($)", 0, 150000, 20000)
 scale_type = st.radio("Chart Scale", ["Linear", "Logarithmic"], horizontal=True)
 
     # NEW: Category Filter
 selected_categories = st.multiselect(
  "Filter Category",
   options=['Financial', 'Technical', 'General Service'],
   default=['Financial', 'Technical', 'General Service']
 )
 
 # Filtering logic
mask = (df['Churn_Risk'] >= risk_range) & \
        (df['Predicted_LTV'] >= ltv_range) & \
        (df['Category'].isin(selected_categories))
filtered_df = df[mask].copy()
 
 # All available IDs for the selector
available_ids = filtered_df['CustomerId'].unique().tolist()
 # Only unsolved IDs for priority logic
priority_df = filtered_df[~filtered_df['CustomerId'].isin(st.session_state.solved_ids)]
 
 # --- 5. TOP HEADER METRICS ---
st.title("🛡️ Blostem Sentinel: Sovereign AI")
m1, m2, m3, m4 = st.columns(4)
with m1: st.markdown(f'<div class="metric-card"><p>Risk Segment</p><p class="metric-value">{len(priority_df)}</p></div>', unsafe_allow_html=True)
with m2: st.markdown(f'<div class="metric-card"><p>Total Exposure</p><p class="metric-value">${priority_df["Predicted_LTV"].sum():,}</p></div>', unsafe_allow_html=True)
with m3: st.markdown(f'<div class="metric-card"><p>Sovereign Status</p><p class="metric-value" style="color:#10b981;">SECURE</p></div>', unsafe_allow_html=True)
with m4: st.markdown(f'<div class="metric-card"><p>Regulatory</p><p class="metric-value" style="font-size:1.2rem;">RBI COMPLIANT</p></div>', unsafe_allow_html=True)
 
st.divider()
 
 # --- 6. MAIN INTERFACE ---
col_left, col_right = st.columns([1.8, 1])
with col_left:
 st.subheader("📊 Strategic Risk Mapping")
 
 scale_choice = 'log' if scale_type == "Logarithmic" else 'linear'
 
 scatter = alt.Chart(filtered_df).mark_circle(size=120, stroke="white", strokeWidth=1).encode(
  x=alt.X('Churn_Risk', title='Risk Score (%)', scale=alt.Scale(domain=[0, 100])),
  y=alt.Y('Predicted_LTV', title='Predicted LTV ($)', scale=alt.Scale(type=scale_choice)),
  color=alt.Color('Category', scale=alt.Scale(domain=['Financial', 'Technical', 'General Service'], range=['#3b82f6', '#ef4444', '#64748b'])),
  tooltip=[
   alt.Tooltip('CustomerId', title='ID'),
   alt.Tooltip('Churn_Risk', title='Risk (%)'),
   alt.Tooltip('Predicted_LTV', title='LTV ($)', format="$,.0f"),
   alt.Tooltip('Category', title='Category')
  ]
 )
 
  rule_x = alt.Chart(pd.DataFrame({'x': [50]})).mark_rule(strokeDash=[4,4], color='#cbd5e1').encode(x='x')
  rule_y = alt.Chart(pd.DataFrame({'y': [75000]})).mark_rule(strokeDash=[4,4], color='#cbd5e1').encode(y='y')
 
  st.altair_chart(scatter + rule_x + rule_y, use_container_width=True)
 
  st.subheader("📜 System Activity Audit")
  log_container = st.container(height=150)
  for entry in st.session_state.audit_log[:10]:
   log_container.markdown(f'<div class="audit-entry">{entry}</div>', unsafe_allow_html=True)
with col_right:
 st.subheader("⚡ Action Engine")
 
 if available_ids:
  ids = sorted(available_ids)
  if st.session_state.locked_id not in ids: st.session_state.locked_id = ids[0]
 
         # Updated Selectbox with Format Function to show icons
  selected_id = st.selectbox(
   "Select Target Profile",
    ids,
    index=ids.index(st.session_state.locked_id),
    format_func=lambda x: format_id_display(x, filtered_df)
  )
  st.session_state.locked_id = selected_id
  user = filtered_df[filtered_df['CustomerId'] == selected_id].iloc[0]
 
  st.markdown(f"### 🧠 AI Rationale (ID-{selected_id})")
  st.progress(user['Confidence']/100, text=f"Model Confidence: {user['Confidence']:.1f}%")
 
  feat_data = pd.DataFrame({
   'Factor': ['Tx Frequency', 'LTV Drop', 'Market Sentiment', 'Service Usage'],
   'Weight': [user['Tx_Frequency'], np.random.randint(20, 80), abs(user['Market_Sentiment']*100), 45]
  })
  feat_chart = alt.Chart(feat_data).mark_bar(cornerRadiusEnd=4, color="#3b82f6").encode(
   x=alt.X('Weight', title=None, axis=None),
   y=alt.Y('Factor', sort='-x', title=None)
  ).properties(height=120)
  st.altair_chart(feat_chart, use_container_width=True)
 
         # Handling UI 
  if selected_id in st.session_state.solved_ids:
   st.success("Protocol Active: This account is currently secured.")
  else:
   st.info(f"**Observation:** Anomalous {user['Category']} behavior detected. Liquidity variance exceeds safety threshold.")
 
  c1, c2 = st.columns(2)
  with c1:
   if st.button("🚀 Deploy Protocol", use_container_width=True):
    st.session_state.solved_ids.add(selected_id)
    add_audit(f"ID-{selected_id} resolved via stabilization protocol.")
    st.rerun()
  with c2:
   if st.button("🛑 Regulatory Halt", type="secondary", use_container_width=True):
    add_audit(f"CRITICAL: Regulatory Halt initiated for ID-{selected_id}.")
    st.error("Account Frozen for Compliance")
     else:
         st.success("🎉 Sovereign Watchlist Clear")




