import streamlit as st
import streamlit as st
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
import requests

st.title("天气提醒小助手")

city_input = st.text_input("请输入城市名称", "上海")

if st.button("生成提醒文案"):
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
        goal="根据实时天气数据,写出一段贴心的穿衣/出行提醒文案",
        backstory="你是一名擅长根据天气情况给出生活建议的文案撰写人",
        llm=llm,
        tools=[get_weather]
    )

    写文案任务 = Task(
        description=f"查询{city_input}当前的天气,写一段50字左右的提醒文案",
        expected_output="一段50字左右的中文生活提醒文案",
        agent=文案助手
    )

    crew = Crew(agents=[文案助手], tasks=[写文案任务])
    result = crew.kickoff()

    st.write(result.raw)
