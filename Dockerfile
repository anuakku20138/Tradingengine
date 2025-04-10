version: '3.8'

services:
  trading-bot:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: nifty50-trading-bot
    restart: unless-stopped
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_CHANNEL_ID=${TELEGRAM_CHANNEL_ID}
      - PORT=8080
      - LOG_LEVEL=INFO
      - TZ=Asia/Kolkata
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
