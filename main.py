import os
import json
import requests
import feedparser
import google.generativeai as genai

# 1. 配置 API 和 Webhook（从 GitHub Secrets 中读取）
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
FEISHU_WEBHOOK = os.environ.get("FEISHU_WEBHOOK")

genai.configure(api_key=GEMINI_API_KEY)

# 2. 抓取最新的汽车行业新闻
def fetch_news():
    rss_url = "https://www.autohome.com.cn/rss/news.xml" # 汽车之家新闻源
    feed = feedparser.parse(rss_url)
    news_list = []
    for entry in feed.entries[:10]:
        news_list.append(f"- {entry.title} ({entry.link})")
    return "\n".join(news_list)

# 3. 唤醒 T1G-helper (Gemini 大脑) 进行战局推演
def generate_radar_report(news_text):
    prompt = f"""
    你是 LEPAS 汽车品牌的项目管理大师“T1G-helper”。
    核心项目：T1G（B/C级插混/纯电SUV）。国内成本极度承压：PHEV挑战 7.3万，BEV挑战 8.0万。
    战略：主打优雅驾控，顶格对标保时捷。由于国内吉利/比亚迪极度内卷，我们重心在右舵和欧盟市场的“出海闪电战”。
    
    请阅读以下抓取到的今日汽车新闻：
    {news_text}
    
    请输出 Markdown 格式的早报，格式如下：
    🚨 **【LEPAS 战情雷达】全球车企早报**
    🔴 **1. 核心情报提炼**（挑选与吉利、比亚迪、出海相关的新闻总结）
    🧠 **2. T1G-helper 战局推演**（结合我们的 T1G 战略给出犀利分析）
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

# 4. 推送到飞书高管群
def send_to_feishu(report_text):
    headers = {"Content-Type": "application/json"}
    payload = {
        "msg_type": "text",
        "content": {"text": report_text}
    }
    response = requests.post(FEISHU_WEBHOOK, headers=headers, data=json.dumps(payload))
    print("飞书推送结果:", response.text)

if __name__ == "__main__":
    print("启动 LEPAS 战情雷达...")
    today_news = fetch_news()
    if today_news:
        report = generate_radar_report(today_news)
        send_to_feishu(report)
        print("执行完毕！")
