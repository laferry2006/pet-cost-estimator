"""
Pet Cost Estimator - Streamlit App
==================================
帮助想要养宠物的人估算养宠开销
"""

import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import numpy as np

# 页面配置
st.set_page_config(
    page_title="宠物养宠开销估算器",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4ECDC4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    .category-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #FF6B6B;
        margin: 0.5rem 0;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #FF6B6B;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-size: 1.1rem;
        font-weight: bold;
        width: 100%;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# 加载数据
@st.cache_data
def load_data():
    with open('pet_price_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# 宠物信息
PET_INFO = {
    'cat': {'name': '猫咪 🐱', 'emoji': '🐱', 'desc': '独立优雅，适合上班族'},
    'dog': {'name': '狗狗 🐶', 'emoji': '🐶', 'desc': '忠诚活泼，需要陪伴'},
    'fish': {'name': '鱼类 🐠', 'emoji': '🐠', 'desc': '安静省心，适合新手'},
    'bird': {'name': '鸟类 🦜', 'emoji': '🦜', 'desc': '聪明可爱，能学说话'},
    'hamster': {'name': '仓鼠 🐹', 'emoji': '🐹', 'desc': '小巧可爱，成本低'},
    'rabbit': {'name': '兔子 🐰', 'emoji': '🐰', 'desc': '温顺乖巧，需要空间'}
}

# 国家映射
COUNTRY_NAMES = {
    'India': '🇮🇳 印度',
    'USA': '🇺🇸 美国',
    'Singapore': '🇸🇬 新加坡',
    'Belgium': '🇧🇪 比利时',
    'Germany': '🇩🇪 德国',
    'Turkey': '🇹🇷 土耳其',
    'Vietnam': '🇻🇳 越南',
    'Sri Lanka': '🇱🇰 斯里兰卡',
    'Japan': '🇯🇵 日本'
}

# 类别图标
CATEGORY_ICONS = {
    '洗护': '🛁',
    '食物': '🍖',
    '玩具及工具': '🎾',
    '医疗': '💊'
}

# 主页面
st.markdown('<p class="main-header">🐾 宠物养宠开销估算器</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">根据真实宠物店数据，帮你估算养宠物的各项开销</p>', unsafe_allow_html=True)

# 加载数据
data = load_data()

# 侧边栏 - 用户选择
with st.sidebar:
    st.markdown("## 🎯 你的选择")
    st.markdown("---")
    
    # 宠物类型选择
    st.markdown("### 1️⃣ 选择宠物类型")
    selected_pet = st.selectbox(
        "你想养什么宠物？",
        options=list(PET_INFO.keys()),
        format_func=lambda x: PET_INFO[x]['name']
    )
    
    # 显示宠物描述
    st.info(f"**{PET_INFO[selected_pet]['desc']}**")
    
    st.markdown("---")
    
    # 地区选择
    st.markdown("### 2️⃣ 选择所在地区")
    selected_country = st.selectbox(
        "你所在的国家/地区？",
        options=list(COUNTRY_NAMES.keys()),
        format_func=lambda x: COUNTRY_NAMES[x]
    )
    
    st.markdown("---")
    
    # 需求程度选择
    st.markdown("### 3️⃣ 选择需求程度")
    st.caption("根据你的需求选择每个类别的消费水平")
    
    demand_levels = {}
    for category in ['洗护', '食物', '玩具及工具', '医疗']:
        demand_levels[category] = st.select_slider(
            f"{CATEGORY_ICONS[category]} {category}",
            options=['基础', '标准', '高级'],
            value='标准'
        )
    
    st.markdown("---")
    
    # 计算按钮
    calculate = st.button("💰 计算开销", use_container_width=True)

# 主内容区
if calculate:
    # 获取数据
    pet_data = data['country_data'].get(selected_pet, {})
    country_data = pet_data.get(selected_country, {})
    
    # 如果该国家没有数据，使用全球平均
    if not country_data:
        country_data = data['global_data'].get(selected_pet, {})
        st.warning(f"⚠️ {COUNTRY_NAMES[selected_country]} 数据有限，使用全球平均值估算")
    
    # 计算各项开销
    costs = {}
    multipliers = {'基础': 0.7, '标准': 1.0, '高级': 1.5}
    
    for category in ['洗护', '食物', '玩具及工具', '医疗']:
        if category in country_data:
            base_price = country_data[category]['avg_price']
            multiplier = multipliers[demand_levels[category]]
            costs[category] = round(base_price * multiplier, 2)
        else:
            # 使用全球平均
            global_price = data['global_data'].get(selected_pet, {}).get(category, {}).get('avg_price', 5000)
            multiplier = multipliers[demand_levels[category]]
            costs[category] = round(global_price * multiplier, 2)
    
    total_cost = sum(costs.values())
    
    # 显示结果
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📊 开销明细")
        
        # 创建开销明细表格
        cost_df = pd.DataFrame({
            '类别': [f"{CATEGORY_ICONS[cat]} {cat}" for cat in costs.keys()],
            '需求等级': [demand_levels[cat] for cat in costs.keys()],
            '预估开销 (₹)': [f"₹{cost:,.0f}" for cost in costs.values()]
        })
        
        st.dataframe(cost_df, use_container_width=True, hide_index=True)
        
        # 总开销卡片
        st.markdown(f"""
        <div class="result-card">
            <h3>💰 预估总开销</h3>
            <h1 style="font-size: 3rem; margin: 0;">₹{total_cost:,.0f}</h1>
            <p>基于 {PET_INFO[selected_pet]['name']} 在 {COUNTRY_NAMES[selected_country]} 的数据</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📈 开销分布")
        
        # 饼图
        fig_pie = go.Figure(data=[go.Pie(
            labels=list(costs.keys()),
            values=list(costs.values()),
            hole=0.4,
            marker_colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'],
            textinfo='label+percent',
            textfont_size=14
        )])
        
        fig_pie.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1),
            margin=dict(t=20, b=20, l=20, r=20),
            height=350
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # 条形图
        fig_bar = go.Figure(data=[go.Bar(
            x=list(costs.keys()),
            y=list(costs.values()),
            marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'],
            text=[f"₹{v:,.0f}" for v in costs.values()],
            textposition='outside'
        )])
        
        fig_bar.update_layout(
            xaxis_title="类别",
            yaxis_title="开销 (₹)",
            showlegend=False,
            margin=dict(t=20, b=20, l=20, r=20),
            height=300
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # 详细建议
    st.markdown("---")
    st.markdown("### 💡 养宠建议")
    
    advice_col1, advice_col2, advice_col3 = st.columns(3)
    
    with advice_col1:
        st.markdown("""
        <div class="category-card">
            <h4>🛁 洗护建议</h4>
            <p>猫咪和狗狗需要定期洗澡和美容，鱼类和仓鼠则相对省心。</p>
        </div>
        """, unsafe_allow_html=True)
    
    with advice_col2:
        st.markdown("""
        <div class="category-card">
            <h4>🍖 食物建议</h4>
            <p>选择高质量宠物粮，注意营养均衡，不要喂食人类食物。</p>
        </div>
        """, unsafe_allow_html=True)
    
    with advice_col3:
        st.markdown("""
        <div class="category-card">
            <h4>💊 医疗建议</h4>
            <p>定期疫苗接种和体检，预留紧急医疗费用。</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 数据来源说明
    st.markdown("---")
    st.caption("📊 数据来源：Pet Store Records 2020 (Kaggle) | 数据仅供参考，实际开销可能因地区和时间而异")

else:
    # 初始状态 - 显示欢迎信息
    st.markdown("---")
    
    # 欢迎图片区域
    welcome_col1, welcome_col2, welcome_col3 = st.columns([1, 2, 1])
    
    with welcome_col2:
        st.markdown("""
        <div style="text-align: center; padding: 3rem;">
            <h2>👋 欢迎使用宠物开销估算器！</h2>
            <p style="font-size: 1.2rem; color: #666;">
                在左侧选择你想要的宠物类型、所在地区以及各项需求等级，<br>
                点击"计算开销"按钮，即可获取详细的养宠开销估算。
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # 宠物类型展示
    st.markdown("### 🐾 支持的宠物类型")
    
    pet_cols = st.columns(6)
    for idx, (pet_key, pet_info) in enumerate(PET_INFO.items()):
        with pet_cols[idx]:
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px;">
                <div style="font-size: 3rem;">{pet_info['emoji']}</div>
                <div style="font-weight: bold; margin-top: 0.5rem;">{pet_info['name'].split()[0]}</div>
                <div style="font-size: 0.8rem; color: #666;">{pet_info['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # 功能特点
    st.markdown("---")
    st.markdown("### ✨ 功能特点")
    
    feature_col1, feature_col2, feature_col3, feature_col4 = st.columns(4)
    
    with feature_col1:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 2rem;">📊</div>
            <div style="font-weight: bold;">真实数据</div>
            <div style="font-size: 0.9rem; color: #666;">基于真实宠物店销售数据</div>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col2:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 2rem;">🌍</div>
            <div style="font-weight: bold;">多地区</div>
            <div style="font-size: 0.9rem; color: #666;">支持9个国家/地区</div>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col3:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 2rem;">📈</div>
            <div style="font-weight: bold;">可视化</div>
            <div style="font-size: 0.9rem; color: #666;">直观的图表展示</div>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col4:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 2rem;">💡</div>
            <div style="font-weight: bold;">个性化</div>
            <div style="font-size: 0.9rem; color: #666;">根据需求定制</div>
        </div>
        """, unsafe_allow_html=True)

# 页脚
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #999; padding: 1rem;">
    <p>🐾 Pet Cost Estimator | Made with ❤️ for future pet owners</p>
    <p style="font-size: 0.8rem;">Data Source: Kaggle - Pet Store Records 2020</p>
</div>
""", unsafe_allow_html=True)
