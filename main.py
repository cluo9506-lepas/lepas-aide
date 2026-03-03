import os
import json
import requests
import feedparser
import google.generativeai as genai

# 1. 配置 API 和 Webhook（从 GitHub Secrets 中读取）
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
FEISHU_WEBHOOK = os.environ.get("FEISHU_WEBHOOK")

genai.configure(api_key=GEMINI_API_KEY)

# 2. 抓取最新的汽车行业新闻 (增加防屏蔽的浏览器伪装)
def fetch_news():
    rss_url = "https://www.autohome.com.cn/rss/news.xml"
    # 伪装成正常的电脑浏览器，突破汽车之家的拦截
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        print("📡 正在尝试突破拦截，抓取新闻...")
        response = requests.get(rss_url, headers=headers, timeout=10)
        feed = feedparser.parse(response.content)
        news_list = []
        for entry in feed.entries[:10]:
            news_list.append(f"- {entry.title} ({entry.link})")
        
        print(f"✅ 成功抓取到 {len(news_list)} 条新闻。")
        return "\n".join(news_list)
    except Exception as e:
        print(f"❌ 抓取新闻报错: {e}")
        return ""

# 3. 唤醒 T1G-helper (Gemini 大脑) 进行战局推演
def generate_radar_report(news_text):
    print("🧠 正在呼叫大师大脑进行深度战局推演...")
    prompt = f"""
    你是 LEPAS 汽车品牌的项目管理大师“T1G-helper”。
    核心项目：T1G（B/C级插混/纯电SUV）。国内成本极度承压：PHEV挑战 7.3万，BEV挑战 8.0万。
    战略：主打优雅驾控，顶格对标保时捷。由于国内吉利/比亚迪极度内卷，我们重心在右舵和欧盟市场的“出海闪电战”。
    
    请阅读以下抓取到的今日汽车新闻：
    {news_text}
    
    请输出 Markdown 格式的早报，格式如下：
    🚨 **【LEPAS 战情雷达】全球车企早报**
    🔴 **1. 核心情报提炼**（挑选与吉利、比亚迪、出海、价格战相关的新闻总结）
    🧠 **2. T1G-helper 战局推演**（结合我们的 T1G 战略给出犀利分析）
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    print("✅ 推演完成！")
    return response.text

# 4. 推送到飞书高管群
def send_to_feishu(report_text):
    print("🚀 准备发送至飞书...")
    headers = {"Content-Type": "application/json"}
    payload = {
        "msg_type": "text",
        "content": {"text": report_text}
    }
    response = requests.post(FEISHU_WEBHOOK, headers=headers, data=json.dumps(payload))
    print("✅ 飞书推送结果:", response.text)

if __name__ == "__main__":
    print("▶️ 启动 LEPAS 战情雷达...")
    today_news = fetch_news()
    
    if today_news:
        report = generate_radar_report(today_news)
        send_to_feishu(report)
        print("🎉 全部执行完毕！")
    else:
        print("🚨 致命警告：未能抓取到任何新闻，流程强制终止（请检查目标网站是否更换了反爬策略）。")
