name: Delta 1 - Reddit Video to Google Drive

on:
  workflow_dispatch:  # يتيح التشغيل اليدوي
  schedule:
    - cron: '0 0 * * *'  # يعمل يوميًا عند منتصف الليل UTC

jobs:
  upload-video:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install praw yt-dlp google-auth-oauthlib google-auth-httplib2 google-api-python-client

      - name: Run Delta 1 script
        env:
          REDDIT_CLIENT_ID: ${{ secrets.REDDIT_CLIENT_ID }}
          REDDIT_CLIENT_SECRET: ${{ secrets.REDDIT_CLIENT_SECRET }}
          REDDIT_USER_AGENT: ${{ secrets.REDDIT_USER_AGENT }}
          REDDIT_POST_URL: ${{ secrets.REDDIT_POST_URL }}
          GOOGLE_CREDENTIALS: ${{ secrets.GDRIVE_TOKEN_BASE64 }}
        run: |
          python delta1.py

      - name: Upload logs (optional)
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: logs
          path: "*.log"
