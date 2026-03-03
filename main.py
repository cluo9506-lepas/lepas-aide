import os
import json
import requests
import feedparser
import google.generativeai as genai

# 1. 配置 API 和 Webhook（从 GitHub Secrets 中读取）
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
FEISHU_WEBHOOK = os.environ.get("FEISHU_WEBHOOK")

genai.configure(api_key=GEMINI_API_KEY)
# 2. 抓取最新的汽车行业新闻 (采用双源备用机制，突破拦截)
def fetch_news():
    # 优先使用 IT之家(涵盖极多新能源车战报)，备用新浪汽车
    rss_urls = [
        "https://www.ithome.com/rss/", 
        "http://rss.sina.com.cn/news/allnews/auto.xml"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    news_list = []
    for url in rss_urls:
        try:
            print(f"📡 正在尝试侦听情报源: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            feed = feedparser.parse(response.content)
            
            # 只要拿到有效的 entries，就提取标题和链接
            if len(feed.entries) > 0:
                for entry in feed.entries[:10]:
                    news_list.append(f"- {entry.title} ({entry.link})")
                print(f"✅ 成功从该源窃取到 {len(news_list)} 条高价值情报！")
                break # 拿到情报就立刻撤退，不再请求下一个源
            else:
                print("⚠️ 该源返回了 0 条数据，可能是被盾了，尝试下一个...")
                
        except Exception as e:
            print(f"❌ 侦听该源时发生故障: {e}")
            
    return "\n".join(news_list)
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
