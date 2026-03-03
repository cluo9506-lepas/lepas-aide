name: T1G Battle Radar Daily

on:
  schedule:
    # 注意：这里是 UTC 时间。UTC 01:00 = 北京时间 09:00
    - cron: '0 1 * * *'
  workflow_dispatch: # 允许你随时手动点击运行测试

jobs:
  run-radar:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Dependencies
        run: |
          pip install requests feedparser google-generativeai

      - name: Execute Radar Script
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          FEISHU_WEBHOOK: ${{ secrets.FEISHU_WEBHOOK }}
        run: python main.py
