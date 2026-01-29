# 🚀 Discord-to-MT5 Signal Copier

This project is an automated trading bot that parses signals from a Discord account (via Self-bot) and executes them on **MetaTrader 5**. The system is designed with a **distributed architecture** to maximize account safety and execution performance.

## 🏗️ System Architecture
The system is split into two main components to ensure Discord account security and trading stability:

* **Raspberry Pi:**
    * Runs the **Discord Self-bot** from a residential IP to prevent bans (Discord often flags data center IPs).
    * Parses incoming messages for key data: `Symbol`, `Type` (Buy/Sell), `Entry`, `SL`, and `TP`.
    * Forwards trade data to the VPS via encrypted HTTP requests using a secure **API Key**.
    * Sends real-time status notifications to **Telegram**.
* **Windows VPS:**
    * Runs a lightweight **Flask** micro-server to receive commands.
    * Interacts directly with the **MetaTrader 5** terminal (optimized for FP Markets).
    * Executes trades in milliseconds due to low-latency proximity to broker servers.



## 🛠️ Setup & Configuration

### Part 1: Raspberry Pi (Signal Parser)
1.  **Install Requirements:** `pip install -r requirements.txt`.
2.  **Configuration:** Rename `config_example.py` to `config.py` and fill in your Discord Token, Telegram credentials, and VPS IP.
3.  **Run:** `python main.py`.

### Part 2: Windows VPS (Trade Executor)
1.  **Environment:** Install **Python 3.8/3.9** and the **MetaTrader 5** terminal.
2.  **MT5 Settings:** Enable **Algo Trading** and **Allow DLL imports** in the MT5 Options menu.
3.  **Firewall:** Open **Port 5000** in the Windows Firewall to allow incoming signals from the Raspberry Pi.
4.  **Run:** `python vps_server.py`.

## 🔒 Security Features
* **Anti-Ban Strategy:** The self-bot operates from a home IP, avoiding Discord's data center detection.
* **API Protection:** Communication is secured with an `X-API-KEY` header. The VPS will reject any request without a matching key.
* **Error Handling:** If the VPS is unreachable, the Raspberry Pi sends an immediate emergency alert via Telegram.

## 📋 Requirements
* **Hardware:** Raspberry Pi Zero 2 W or similar.
* **VPS**: Windows Server 2012 R2 or later (2016, 2019, 2022 recommended)
* **Libraries:** `discord.py-self`, `MetaTrader5`, `Flask`, `python-telegram-bot`.