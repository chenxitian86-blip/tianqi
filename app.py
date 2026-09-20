import streamlit as st
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
import requests

st.title("天气提醒小助手")

city_input = st.text_input("请输入城市名称(目前仅支持东莞)", "东莞")

if st.button("生成提醒文案"):
    llm = LLM(model="deepseek/deepseek-chat", api_key="sk-e17f9a5ba4c24e6ba996f168e1089155")

    @tool("get_weather_tool")
    def get_weather(city: str) -> str:
        """查询实时气温"""
        response = requests.get("https://api.open-meteo.com/v1/forecast?latitude=31.23&longitude=121.47&current=temperature_2m")
        data = response.json()
        temp = data["current"]["temperature_2m"]
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

    st.write(result)
