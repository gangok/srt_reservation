# AWS Linux Deployment Guide

## Prerequisites
- AWS EC2 instance (Amazon Linux 2 or Ubuntu)
- Python 3.7+
- Internet connection

## Installation Steps

### 1. Update System
```bash
# For Amazon Linux 2
sudo yum update -y

# For Ubuntu
sudo apt update && sudo apt upgrade -y
```

### 2. Install Python and Dependencies
```bash
# For Amazon Linux 2
sudo yum install python3 python3-pip wget unzip -y

# For Ubuntu
sudo apt install python3 python3-pip wget unzip -y
```

### 3. Install Google Chrome
```bash
# For Amazon Linux 2
sudo yum install -y google-chrome-stable

# For Ubuntu
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt update
sudo apt install -y google-chrome-stable
```

### 4. Install Project Dependencies
```bash
# Clone or upload your project to the EC2 instance
cd /path/to/srt_reservation

# Install Python requirements (excluding playsound for headless environment)
pip3 install selenium==4.29.0 python-telegram-bot==13.10 PyYAML==6.0 webdriver_manager==4.0.2
```

### 5. Configure Telegram Bot
1. Create a Telegram bot via @BotFather
2. Get your chat ID
3. Update `config.yaml` with your telegram credentials:
```yaml
telegram_token: "YOUR_BOT_TOKEN"
telegram_chat_id: YOUR_CHAT_ID
```

### 6. Run the Application
```bash
# Test run
python3 quickstart.py --config config.yaml

# Run in background with nohup
nohup python3 quickstart.py --config config.yaml > srt_log.txt 2>&1 &

# Or use screen to run in detached session
screen -S srt_monitor
python3 quickstart.py --config config.yaml
# Press Ctrl+A then D to detach
```

## Key Changes for AWS Environment

1. **Headless Chrome**: The code now runs Chrome in headless mode, perfect for servers without GUI
2. **No Audio**: Removed playsound dependency since AWS instances typically don't have audio
3. **Telegram Only**: Notifications are sent only via Telegram
4. **No Login Required**: The application monitors tickets without requiring SRT login

## Monitoring

- Check logs: `tail -f srt_log.txt`
- View running processes: `ps aux | grep python`
- Reattach screen session: `screen -r srt_monitor`

## Security Considerations

- Keep your Telegram bot token secure
- Consider using AWS Systems Manager Parameter Store for sensitive configuration
- Use IAM roles instead of storing credentials in files
- Configure security groups to allow only necessary traffic

## Troubleshooting

- If Chrome crashes, increase EC2 instance memory (at least t3.small recommended)
- Check Chrome installation: `google-chrome --version`
- Verify network connectivity to SRT website
- Monitor system resources: `htop` or `top`