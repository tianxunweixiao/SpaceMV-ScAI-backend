import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import glob
import json

# --------------------------------------------Basic Page Configuration-------------------------------------------------------
st.set_page_config(
    page_title="ScAI仿真可视化平台",
    layout="wide",
    page_icon="🛰️",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    /* 全局背景 */
    .stApp {
        background-color: #FAFAFA; 
    }

    /* 顶部内边距 */
    .block-container {
        padding-top: 3rem;
        padding-bottom: 2rem;
    }

    /* 指标卡样式 */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF; 
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #E0E0E0;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }

    /* 指标标签颜色 */
    div[data-testid="stMetricLabel"] > div {
        color: #555555 !important;
        font-size: 14px;
        font-weight: 500;
    }

    /* 指标数值颜色 */
    div[data-testid="stMetricValue"] {
        color: #0068C9 !important; /* Streamlit 经典蓝 */
        font-weight: 700;
        font-size: 26px !important;
    }

    /* 侧边栏按钮 */
    div.stDownloadButton > button {
        width: 100%;
        background-color: #0068C9; 
        color: white;
        border: none;
        padding: 0.6rem;
        border-radius: 8px;
        font-weight: bold;
    }
    div.stDownloadButton > button:hover {
        background-color: #005cbf;
        color: white;
        border-color: #005cbf;
    }

    /* 侧边栏背景 */
    section[data-testid="stSidebar"] {
        background-color: #F0F2F6;
        border-right: 1px solid #E6E6E6;
    }
</style>
""", unsafe_allow_html=True)



# -----------------------------------Parsing JSON files for visual rendering----------------------------------------------
#@st.cache_data(ttl=3600)
def parse_pos_json(file_path):
    """posLLA.json"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        data = []
        sorted_keys = sorted(raw_data.keys())

        for time_str in sorted_keys:
            coords = raw_data[time_str]
            data.append({
                "time": time_str,
                "lon": coords[0],
                "lat": coords[1],
                "alt": coords[2]
            })
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"❌ 轨迹解析失败: {os.path.basename(file_path)} - {str(e)}")
        return pd.DataFrame()

#@st.cache_data(ttl=3600)
def parse_sensor_json(file_path):
    """sensorProjection.json"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        processed_data = {}
        for time_str, polygon in raw_data.items():
            lats = [p[0] for p in polygon]
            lons = [p[1] for p in polygon]
            lats, lons = ensure_clockwise_winding(lats, lons)
            processed_data[time_str] = {"lats": lats, "lons": lons}

        return processed_data
    except Exception as e:
        st.warning(f"⚠️ 传感器解析失败: {os.path.basename(file_path)}")
        return {}

#@st.cache_data(ttl=3600)
def parse_targets_json(file_path):
    """targets.json"""
    targets = {"points": [], "lines": [], "polygons": []}
    if not os.path.exists(file_path):
        return targets

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        # point
        if "point" in raw_data and raw_data["point"]:
            p_data = raw_data["point"]
            if isinstance(p_data[0], list):
                targets["points"] = [{"lat": p[0], "lon": p[1]} for p in p_data]
            else:
                targets["points"] = [{"lat": p_data[0], "lon": p_data[1]}]

        # line
        if "line" in raw_data and raw_data["line"]:
            line_points = raw_data["line"]
            targets["lines"].append({
                "lats": [p[0] for p in line_points],
                "lons": [p[1] for p in line_points]
            })

        # polygon
        if "polygon" in raw_data and raw_data["polygon"]:
            poly_points = raw_data["polygon"]
            lats = [p[0] for p in poly_points]
            lons = [p[1] for p in poly_points]
            if lats[0] != lats[-1] or lons[0] != lons[-1]:
                lats.append(lats[0])
                lons.append(lons[0])
            lats, lons = ensure_clockwise_winding(lats, lons)
            targets["polygons"].append({
                "lats": lats,
                "lons": lons
            })

    except Exception as e:
        st.warning(f"⚠️ 目标文件解析异常: {e}")

    return targets


def load_data_from_server_path(root_path):
    if not os.path.exists(root_path):
        return None, None, "服务器路径不存在"

    pos_dir = os.path.join(root_path, "poslla")
    sensor_dir = os.path.join(root_path, "sensorprojection")
    target_file = os.path.join(root_path, "targets", "targets.json")

    pos_files = glob.glob(os.path.join(pos_dir, "*.json"))
    if not pos_files:
        return None, None, "poslla 文件夹为空"

    satellites = {}

    for p_file in pos_files:
        filename = os.path.basename(p_file)
        sat_id = filename.replace("posLLA_", "").replace(".json", "")

        df = parse_pos_json(p_file)
        if df.empty: continue

        s_file = os.path.join(sensor_dir, f"sensorProjection_{sat_id}.json")
        sensor_data = parse_sensor_json(s_file) if os.path.exists(s_file) else {}

        satellites[sat_id] = {
            "df": df,
            "sensor": sensor_data
        }

    targets = parse_targets_json(target_file)
    return satellites, targets, None


def handle_dateline_crossing(lons, lats):
    """Handling Cross-Date Line Drawing"""
    clean_lons, clean_lats = [], []
    for i in range(len(lons)):
        clean_lons.append(lons[i])
        clean_lats.append(lats[i])
        if i < len(lons) - 1:
            if abs(lons[i + 1] - lons[i]) > 300:
                clean_lons.append(None)
                clean_lats.append(None)
    return clean_lons, clean_lats


def ensure_clockwise_winding(lats, lons):
    if len(lats) < 3:
        return lats, lons

    area = 0.0
    for i in range(len(lats)):
        j = (i + 1) % len(lats)
        area += (lons[j] - lons[i]) * (lats[j] + lats[i])

    if area < 0:
        return lats[::-1], lons[::-1]

    return lats, lons
# --------------------------------------------------Data loading----------------------------------------------------

query_params = st.query_params
data_path_arg = query_params.get("data_path", None)
zip_path_arg = query_params.get("zip_path", None)

if not data_path_arg:
    st.info("👋 欢迎使用ScAI仿真可视化服务。请等待后端重定向数据...")
    st.stop()

with st.spinner(f"正在加载仿真数据..."):
    sat_data, targets_data, error_msg = load_data_from_server_path(data_path_arg)

if error_msg:
    st.error(f"❌ 数据加载失败: {error_msg}")
    st.stop()


# Layout and Visualization

# Sidebar
with st.sidebar:
    st.header("🎛️ 控制面板")

    if zip_path_arg and os.path.exists(zip_path_arg):
        st.success("✅ 覆盖性分析已完成")
        file_name = os.path.basename(zip_path_arg)
        try:
            with open(zip_path_arg, "rb") as fp:
                btn = st.download_button(
                    label=f"📥 下载结果报告",
                    data=fp,
                    file_name=file_name,
                    mime="application/zip"
                )
        except Exception as e:
            st.error(f"文件读取失败: {e}")
    else:
        if zip_path_arg:
            st.warning("⚠️ 指定的下载文件不存在")

    st.divider()

    st.subheader("👁️ 图层显示")
    all_sats = list(sat_data.keys())
    selected_sats = st.multiselect("选择卫星", all_sats, default=all_sats)

    show_traj = st.toggle("显示星下点轨迹", value=True)
    show_sensor = st.toggle("显示传感器视场", value=True)
    show_targets = st.toggle("显示地面目标", value=True)

    st.divider()
    sim_speed = st.slider("🚀 动画速度 (ms/帧)", 10, 500, 50)

# Main Interface Information Bar
task_name = os.path.basename(os.path.normpath(data_path_arg))
sat_count = len(sat_data)
first_sat = list(sat_data.keys())[0]
time_start = sat_data[first_sat]['df'].iloc[0]['time']
time_end = sat_data[first_sat]['df'].iloc[-1]['time']

c1, c2, c3 = st.columns(3)
c1.metric("仿真目标", task_name)
c2.metric("仿真模式", "🌌 星座组网" if sat_count > 1 else "🛰️ 单星任务")
c3.metric("卫星数量", f"{sat_count} 颗")

# Visualization Plotting
if not selected_sats:
    st.warning("请在左侧选择至少一颗卫星进行展示")
else:
    base_df = sat_data[first_sat]["df"]
    step = max(1, int(len(base_df) / 200))
    plot_df = base_df.iloc[::step].reset_index(drop=True)

    fig = go.Figure()

    # --- A. Static Layer: Ground Targets ---
    static_trace_count = 0
    show_target_legend_point = True
    show_target_legend_line = True
    show_target_legend_polygon = True

    if show_targets and targets_data:
        # point
        for i, p in enumerate(targets_data["points"]):
            fig.add_trace(go.Scattergeo(
                lon=[p['lon']], lat=[p['lat']],
                mode='markers',
                marker=dict(size=12, color='#D32F2F', symbol='star', line=dict(width=1, color='white')),  # 深红带白边
                name='地面点目标',
                hoverinfo='text',
                text=f"地面点目标",
                showlegend=show_target_legend_point
            ))
            static_trace_count += 1
            show_target_legend_point = False

        # line
        for l in targets_data["lines"]:
            # Cross-Day Boundary for Processing Lines
            l_lons, l_lats = handle_dateline_crossing(l['lons'], l['lats'])
            fig.add_trace(go.Scattergeo(
                lon=l_lons, lat=l_lats,
                mode='lines',
                line=dict(width=3, color='#2E7D32'),
                name='地面线目标',
                showlegend=show_target_legend_line
            ))
            static_trace_count += 1
            show_target_legend_line = False

        # polygon
        for poly in targets_data["polygons"]:
            lons = poly['lons']
            lats = poly['lats']

            # Polygons with a longitudinal span exceeding 180 degrees are considered to cross the International Date Line.
            lon_span = max(lons) - min(lons)
            should_fill = 'toself'
            if lon_span > 180:
                should_fill = 'none'  
                lons, lats = handle_dateline_crossing(lons, lats)

            fig.add_trace(go.Scattergeo(
                lon=lons, lat=lats,
                mode='lines', fill=should_fill,
                fillcolor='rgba(156, 39, 176, 0.2)',  
                line=dict(width=2, color='#7B1FA2'),  
                name='地面面目标',
                showlegend=show_target_legend_polygon
            ))
            static_trace_count += 1
            show_target_legend_polygon = False

    # --- B. Star-Pointed Trajectory Line ---
    show_traj_legend = True
    if show_traj:
        for sat_name in selected_sats:
            sat_df = sat_data[sat_name]['df']
            lons_clean, lats_clean = handle_dateline_crossing(
                sat_df['lon'].tolist(),
                sat_df['lat'].tolist()
            )
            fig.add_trace(go.Scattergeo(
                lon=lons_clean,
                lat=lats_clean,
                mode='lines',
                line=dict(width=1.5, color='rgba(25, 118, 210, 0.5)', dash='dot'),
                name=f"卫星星下点轨迹",
                legendgroup='trajectory',
                showlegend=show_traj_legend,
                hoverinfo='skip'
            ))
            static_trace_count += 1
            show_traj_legend = False

    # --- C. Dynamic Placeholder Trace ---
    sat_trace_mapping = {}
    show_sat_pos = True
    show_sen_pro = True

    for sat_name in selected_sats:
        sat_trace_mapping[sat_name] = {}

        # Satellite Real-Time Location
        sat_trace_mapping[sat_name]['pos'] = len(fig.data)
        fig.add_trace(go.Scattergeo(
            lon=[sat_data[sat_name]['df'].iloc[0]['lon']],
            lat=[sat_data[sat_name]['df'].iloc[0]['lat']],
            mode='markers+text',

            marker=dict(size=5, symbol='circle', color='#1976D2',
                        line=dict(width=2, color='white')),
            text=sat_name,
            textposition='top center',

            textfont=dict(size=12, color='#333333', family="Arial Black"),
            name=f"卫星实时位置",
            showlegend=show_sat_pos,
            hovertemplate='<b>%{text}</b><br>经度: %{lon:.2f}<br>纬度: %{lat:.2f}<extra></extra>'
        ))
        show_sat_pos = False

        # Satellite Field of View
        if show_sensor:
            sat_trace_mapping[sat_name]['sensor'] = len(fig.data)
            fig.add_trace(go.Scattergeo(
                lon=[], lat=[],
                mode='lines', fill='toself',
                fillcolor='rgba(211, 47, 47, 0.15)',
                line=dict(width=1.5, color='#D32F2F'),
                name=f"传感器视场范围",
                showlegend=show_sen_pro,
                hoverinfo='name'
            ))
            show_sen_pro = False

    dynamic_trace_indices = []
    for sat_name in selected_sats:
        dynamic_trace_indices.append(sat_trace_mapping[sat_name]['pos'])
        if show_sensor and 'sensor' in sat_trace_mapping[sat_name]:
            dynamic_trace_indices.append(sat_trace_mapping[sat_name]['sensor'])

    # --- D. Constructing frames ---
    frames = []
    for i, row in plot_df.iterrows():
        frame_data = []
        idx = i * step
        current_time_str = row['time']

        show_sat_pos = True
        show_sen_pro = True

        for sat_name in selected_sats:
            
            sat_df = sat_data[sat_name]['df']
            if idx < len(sat_df):
                curr_pos = sat_df.iloc[idx]
                frame_data.append(go.Scattergeo(
                    lon=[curr_pos['lon']],
                    lat=[curr_pos['lat']],
                    mode='markers+text',
                    marker=dict(size=5, symbol='circle', color='#1976D2',
                                line=dict(width=2, color='white')),
                    text=sat_name,
                    textposition='top center',
                    textfont=dict(size=12, color='#333333', family="Arial Black"),
                    showlegend=show_sat_pos,
                    hovertemplate='<b>%{text}</b><br>经度: %{lon:.2f}<br>纬度: %{lat:.2f}<extra></extra>'
                ))
            else:
                last_pos = sat_df.iloc[-1]
                frame_data.append(go.Scattergeo(
                    lon=[last_pos['lon']],
                    lat=[last_pos['lat']],
                    mode='markers+text',
                    marker=dict(size=5, symbol='circle', color='#9E9E9E',
                                line=dict(width=2, color='white')),
                    text=sat_name,
                    textposition='top center',
                    showlegend=show_sat_pos,
                    textfont=dict(size=12, color='#666666')
                ))
            show_sat_pos = False

            
            if show_sensor:
                sensor_dict = sat_data[sat_name]['sensor']
                if current_time_str in sensor_dict:
                    fov = sensor_dict[current_time_str]
                    lons, lats = fov['lons'].copy(), fov['lats'].copy()
                    if lons and lats:
                        if lons[0] != lons[-1] or lats[0] != lats[-1]:
                            lons.append(lons[0])
                            lats.append(lats[0])

                        
                        lon_span = max(lons) - min(lons)
                        current_fill = 'toself' if lon_span < 180 else 'none'
                        lons_clean, lats_clean = handle_dateline_crossing(lons, lats)

                        valid_points = [(lon, lat) for lon, lat in zip(lons_clean, lats_clean)
                                        if lon is not None and lat is not None]

                        if valid_points:
                            clean_lons, clean_lats = zip(*valid_points)
                            frame_data.append(go.Scattergeo(
                                lon=list(clean_lons), lat=list(clean_lats),
                                mode='lines', fill=current_fill,
                                fillcolor='rgba(211, 47, 47, 0.15)',
                                line=dict(width=1.5, color='#D32F2F'),
                                hoverinfo='name', showlegend=show_sen_pro
                            ))
                        else:
                            frame_data.append(go.Scattergeo(lon=[], lat=[], mode='lines', line=dict(width=0),
                                                            showlegend=show_sen_pro))
                    else:
                        frame_data.append(
                            go.Scattergeo(lon=[], lat=[], mode='lines', line=dict(width=0), showlegend=show_sen_pro))
                else:
                    frame_data.append(
                        go.Scattergeo(lon=[], lat=[], mode='lines', line=dict(width=0), showlegend=show_sen_pro))
                show_sen_pro = False

        frames.append(go.Frame(
            data=frame_data,
            name=str(i),
            traces=dynamic_trace_indices
        ))

    if frames:
        fig.frames = frames
        print(frames)
    # --- E. Layout Settings ---
    fig.update_layout(
        title={
            'text': f"🛰️ 仿真时间窗口: {time_start} → {time_end}",
            'font': {'size': 20, 'color': '#333333', 'family': 'Arial Black'},
            'x': 0.5,
            'xanchor': 'center'
        },
        geo=dict(
            projection_type="equirectangular",
            showland=True,
            showocean=True,
            showcountries=True,
            showrivers=True,
            showlakes=True,
            landcolor="#F5F5F5",  
            oceancolor="#E3F2FD",  
            countrycolor="#BDBDBD", 
            coastlinecolor="#9E9E9E",  
            rivercolor="#B3E5FC",
            lakecolor="#E3F2FD",
            lataxis=dict(range=[-90, 90], showgrid=True, gridcolor="#E0E0E0", gridwidth=0.5),
            lonaxis=dict(range=[-180, 180], showgrid=True, gridcolor="#E0E0E0", gridwidth=0.5),
            bgcolor="#FFFFFF"
        ),
        font=dict(color="#333333", family="Arial"),
        legend=dict(
            x=0.01,
            y=0.99,
            xanchor='left',
            yanchor='top',
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#DDDDDD',
            borderwidth=1,
            font=dict(size=12, color='#333333')
        ),

        updatemenus=[{
            "type": "buttons",
            "showactive": False,
            "x": 0.12, "y": 0.01,
            "xanchor": "left", "yanchor": "bottom",
            "bgcolor": "#FFFFFF",
            "bordercolor": "#CCCCCC",
            "borderwidth": 1,
            "font": {"color": "#333333"},
            "buttons": [
                {
                    "label": "▶ 播放",
                    "method": "animate",
                    "args": [None, {
                        "frame": {"duration": sim_speed, "redraw": True},
                        "fromcurrent": True,
                        "mode": "immediate",
                        "transition": {"duration": 0}
                    }]
                },
                {
                    "label": "⏸ 暂停",
                    "method": "animate",
                    "args": [[None], {
                        "frame": {"duration": 0, "redraw": False},
                        "mode": "immediate"
                    }]
                },
                {
                    "label": "⏮ 重置",
                    "method": "animate",
                    "args": [[str(0)], {
                        "frame": {"duration": 0, "redraw": True},
                        "mode": "immediate"
                    }]
                }
            ]
        }],

        sliders=[{
            "steps": [
                {
                    "args": [
                        [str(k)],
                        {
                            "frame": {"duration": 0, "redraw": True},
                            "mode": "immediate",
                            "transition": {"duration": 0}
                        }
                    ],
                    "label": row['time'].split(' ')[1] if ' ' in row['time'] else row['time'],
                    "method": "animate"
                }
                for k, row in plot_df.iterrows()
            ],
            "active": 0,
            "currentvalue": {
                "prefix": "⏱ 当前时间: ",
                "visible": True,
                "font": {"color": "#0068C9", "size": 14, "weight": "bold"},  
                "xanchor": "left"
            },
            "len": 0.95,
            "x": 0.03,
            "y": -0.01,
            "pad": {"t": 50, "b": 10},
            "bgcolor": "#F0F0F0", 
            "bordercolor": "#CCCCCC",
            "borderwidth": 1,
            "tickcolor": "#333333",
            "font": {"color": "#333333"}
        }],
        margin={"r": 10, "t": 60, "l": 10, "b": 60},
        height=750,
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#FFFFFF',
    )

    st.plotly_chart(fig, width='stretch')