import os
import json
import requests
import feedparser
import google.generativeai as genai

# ==========================================
# 1. 环境变量读取与校验
# ==========================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
FEISHU_WEBHOOK = os.environ.get("FEISHU_WEBHOOK")

if not GEMINI_API_KEY or not FEISHU_WEBHOOK:
    print("🚨 致命错误：未找到 API Key 或 Webhook 地址，请检查 GitHub Secrets 配置！")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

# ==========================================
# 2. 抓取新闻（双源备用，防拦截）
# ==========================================
def fetch_news():
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
            print(f"📡 正在尝试抓取情报源: {url}")
            response = requests.get(url, headers=headers, timeout=15)
            feed = feedparser.parse(response.content)
            
            if len(feed.entries) > 0:
                for entry in feed.entries[:10]:
                    news_list.append(f"- {entry.title} ({entry.link})")
                print(f"✅ 成功从该源抓取到 {len(news_list)} 条情报！")
                break
            else:
                print("⚠️ 该源返回数据为空，尝试下一个备用源...")
        except Exception as e:
            print(f"❌ 抓取该源时发生故障: {e}")
            
    return "\n".join(news_list)

# ==========================================
# 3. 唤醒大师大脑进行战局推演 (带模型容错)
# ==========================================
def generate_radar_report(news_text):
    print("🧠 正在呼叫大脑进行深度战局推演...")
    prompt = f"""
    你是 LEPAS 汽车品牌的项目管理大师“T1G-helper”。
    核心项目：T1G（B/C级插混/纯电SUV）。国内成本极度承压：PHEV挑战 7.3万，BEV挑战 8.0万。
    战略：主打优雅驾控，顶格对标保时捷。由于国内吉利/比亚迪极度内卷，我们重心在右舵和欧盟市场的“出海闪电战”。
    
    请阅读以下抓取到的今日汽车新闻：
    {news_text}
    
    请输出 Markdown 格式的早报，格式如下：
    🚨 **【LEPAS 战情雷达】全球车企早报**
    🔴 **1. 核心情报提炼**（挑选与吉利、比亚迪、出海、价格战相关的新闻总结）
    🧠 **2. T1G-helper 战局推演**（结合我们的 T1G 战略给出针对性的威胁评估和应对建议）
    """
    
    # 核心容错逻辑：先用 1.5-flash，报错则自动降级到最稳定的 gemini-pro
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
    except Exception as e:
        print(f"⚠️ 默认模型调用受限 ({e})，正在无缝切换至备用模型 gemini-pro...")
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
    print("✅ 战局推演完成！")
    return response.text

# ==========================================
# 4. 推送到飞书高管群
# ==========================================
def send_to_feishu(report_text):
    print("🚀 准备发送至飞书...")
    headers = {"Content-Type": "application/json"}
    payload = {
        "msg_type": "text",
        "content": {"text": report_text}
    }
    try:
        response = requests.post(FEISHU_WEBHOOK, headers=headers, data=json.dumps(payload), timeout=10)
        print("✅ 飞书推送响应状态:", response.text)
    except Exception as e:
        print(f"❌ 飞书网络推送异常: {e}")

# ==========================================
# 主程序入口
# ==========================================
if __name__ == "__main__":
    print("▶️ 启动 LEPAS 战情雷达系统...")
    today_news = fetch_news()
    
    if today_news.strip():
        report = generate_radar_report(today_news)
        send_to_feishu(report)
        print("🎉 全部流程执行完毕，请查收飞书消息！")
    else:
        print("🚨 警告：未能抓取到任何有效新闻，为防止发送空消息，流程安全终止。")
