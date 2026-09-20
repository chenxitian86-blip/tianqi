import streamlit as st
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
import requests
from datetime import datetime

st.set_page_config(page_title="天气提醒小助手", page_icon="🌤️", layout="centered")

st.markdown("""
    <style>
    .card {
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 16px;
        font-size: 16px;
        line-height: 1.6;
    }
    .card-weather { background-color: #E3F2FD; border-left: 5px solid #2196F3; }
    .card-suggest { background-color: #E8F5E9; border-left: 5px solid #4CAF50; }
    .card-warm { background-color: #FFF3E0; border-left: 5px solid #FF9800; }
    .card-title { font-weight: bold; font-size: 18px; margin-bottom: 8px; }
    </style>
""", unsafe_allow_html=True)

st.title("🌤️ 天气提醒小助手")

weekday_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
today = datetime.now()
today_str = f"{today.year}年{today.month}月{today.day}日 {weekday_names[today.weekday()]}"

col1, col2 = st.columns([2, 1])
with col1:
    city_input = st.text_input("城市名称", "上海", placeholder="例如:上海、北京、广州")
with col2:
    st.write("")
    st.write("")
    st.write(f"📅 {today_str}")

if st.button("✨ 生成提醒文案", type="primary", use_container_width=True):
    if not city_input.strip():
        st.warning("请先输入城市名称")
    else:
        with st.spinner(f"正在查询{city_input}的天气,生成文案中..."):
            llm = LLM(model="deepseek/deepseek-chat", api_key="sk-928f84c158094119b8c7e1d50d0c2f51")

            @tool("get_weather_tool")
            def get_weather(city: str) -> str:
                """根据城市名称,查询该城市当前的实时气温"""
                geo_response = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=zh")
                geo_data = geo_response.json()

                if "results" not in geo_data:
                    return f"未找到{city}这个城市,请检查名称是否正确"

                lat = geo_data["results"][0]["latitude"]
                lon = geo_data["results"][0]["longitude"]

                weather_response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m")
                weather_data = weather_response.json()
                temp = weather_data["current"]["temperature_2m"]

                return f"{city}当前气温是{temp}度"

            文案助手 = Agent(
                role="生活提醒文案专家",
                goal="根据实时天气数据和日期,写出贴心的天气提醒、今日活动建议和暖心话语",
                backstory="你是一名擅长根据天气和日期给出生活建议、并且很会说暖心话的文案撰写人",
                llm=llm,
                tools=[get_weather]
            )

            写文案任务 = Task(
                description=f"今天是{today_str}。查询{city_input}当前的天气,然后完成三件事:1.用一段50字左右的话描述天气并给出穿衣建议;2.结合今天是工作日还是周末以及天气情况,推荐一个适合今天做的活动(一句话);3.写一句温暖治愈的话送给用户(一句话,不要老套的鸡汤)。",
                expected_output="严格按以下格式输出,不要添加其他内容:\n【天气提醒】...\n【今日建议】...\n【暖心一句】...",
                agent=文案助手
            )

            crew = Crew(agents=[文案助手], tasks=[写文案任务])
            result = crew.kickoff()
            raw_text = result.raw

        weather_part = raw_text.split("【今日建议】")[0].replace("【天气提醒】", "").strip()
        suggest_part = raw_text.split("【今日建议】")[1].split("【暖心一句】")[0].strip()
        warm_part = raw_text.split("【暖心一句】")[1].strip()

        st.markdown(f'<div class="card card-weather"><div class="card-title">🌡️ 天气提醒</div>{weather_part}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card card-suggest"><div class="card-title">💡 今日建议</div>{suggest_part}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="card card-warm"><div class="card-title">💛 暖心一句</div>{warm_part}</div>', unsafe_allow_html=True)
