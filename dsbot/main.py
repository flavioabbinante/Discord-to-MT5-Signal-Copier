import discord
import requests
import re
from telegram import Bot
import config

# Inizializzazione Bot Telegram per notifiche
tg_bot = Bot(token=config.TG_TOKEN)
message_map = {}

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'✅ Self-Bot Online su Raspberry: {self.user}')

    async def on_message(self, message):
        # FILTER: Process messages only from the specific channel ID
        if message.channel.id != config.DISCORD_CH_ID:
            return

        try:
            content = message.content
            u_content = content.upper()
            # ... resto del codice per il parsing e l'invio alla VPS
            reply_to_id = message_map.get(message.reference.message_id) if message.reference else None

            # 1. Identificazione Simbolo
            simbolo_match = re.search(r'(XAUUSD|EURUSD|GBPUSD|BTCUSD|ETHUSD|GOLD)', u_content)
            simbolo = simbolo_match.group(0) if simbolo_match else "XAUUSD"

            headers = {"X-API-KEY": config.API_KEY_VPS}

            # --- CASO CHIUSURA ---
            if "CLOSED" in u_content:
                payload = {"simbolo": simbolo}
                try:
                    r = requests.post(f"{config.VPS_URL}/close", json=payload, headers=headers, timeout=10)
                    data = r.json()
                    text_final = f"🏁 <b>TRADE CHIUSO: {simbolo}</b>\nVPS: {data.get('count', 0)} posizioni chiuse."
                except Exception as e:
                    text_final = f"❌ Errore connessione VPS in chiusura: {e}"
                
                await tg_bot.send_message(config.TG_CHAT_ID, text_final, parse_mode='HTML', reply_to_message_id=reply_to_id)

            # --- CASO APERTURA ---
            elif "ENTRY:" in u_content:
                tipo = "BUY" if "BUY" in u_content else "SELL"

                def get_val(label, text):
                    matches = re.findall(label + r":?\s*(\d+\.\d+|\d+)", text)
                    return float(max(matches, key=len)) if matches else 0.0

                entry = get_val("ENTRY", u_content)
                sl = get_val("SL", u_content)
                tp = get_val("TP", u_content)

                # Prepariamo l'invio alla VPS a Dallas
                payload = {
                    "simbolo": simbolo,
                    "tipo": tipo,
                    "sl": sl,
                    "tp": tp,
                    "entry": entry
                }

                try:
                    r = requests.post(f"{config.VPS_URL}/trade", json=payload, headers=headers, timeout=10)
                    res_data = r.json()
                    
                    # Gestione esito basata sul retcode di MT5 restituito dalla VPS
                    if res_data.get('retcode') == 10009:
                        status = "✅ MT5 OK (Dallas)"
                    else:
                        status = f"❌ MT5 ERROR: {res_data.get('status')}"
                except Exception as e:
                    status = f"❌ Errore connessione VPS Dallas: {e}"

                # Notifica su Telegram
                text_final = (
                    f"💎 <b>{tipo} {simbolo}</b>\n{status}\n\n"
                    f"📍 <b>Entry:</b> <code>{entry}</code>\n"
                    f"🎯 <b>TP:</b> <code>{tp}</code>\n"
                    f"🛡️ <b>SL:</b> <code>{sl}</code>"
                )
                sent_msg = await tg_bot.send_message(config.TG_CHAT_ID, text_final, parse_mode='HTML', reply_to_message_id=reply_to_id)
                message_map[message.id] = sent_msg.message_id

        except Exception as e:
            print(f"❌ Errore nel processare il messaggio: {e}")

client = MyClient()
client.run(config.USER_TOKEN)