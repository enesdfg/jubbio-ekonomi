import asyncio
import websockets
import json
import yfinance as yf
import os

# --- AYARLAR ---
# Railway panelinde 'Variables' kısmına JUBBIO_TOKEN eklemeyi unutma!
TOKEN = os.getenv("JUBBIO_TOKEN", "BURAYA_TOKENINI_YAZ")
GATEWAY_URL = "wss://gateway.jubbio.com" 

# Takip edilecek popüler coinler
COINS = {
    "BTC-USD": "Bitcoin", 
    "ETH-USD": "Ethereum",
    "SOL-USD": "Solana", 
    "BNB-USD": "BNB", 
    "XRP-USD": "Ripple"
}

def get_market_data():
    msg = "🚀 **Piyasa Durumu (Anlık)**\n━━━━━━━━━━━━━━━━\n"
    for symbol, name in COINS.items():
        try:
            ticker = yf.Ticker(symbol)
            price = ticker.history(period="1d")['Close'].iloc[-1]
            msg += f"🔹 **{name}**: `${price:,.2f}`\n"
        except:
            msg += f"🔹 **{name}**: Veri alınamadı\n"
    msg += "━━━━━━━━━━━━━━━━"
    return msg

async def start_bot():
    while True:
        try:
            print(f"Bağlantı kuruluyor: {GATEWAY_URL}")
            async with websockets.connect(GATEWAY_URL) as ws:
                # Giriş Yap ve Sadece Slash Komutunu Tanımla
                identify = {
                    "op": "identify",
                    "d": {
                        "token": TOKEN,
                        "commands": [
                            {
                                "name": "fiyat", 
                                "description": "Kripto para piyasa fiyatlarını listeler"
                            }
                        ]
                    }
                }
                await ws.send(json.dumps(identify))
                print("✅ Bot Slash Komutları ile Aktif!")

                async for message in ws:
                    data = json.loads(message)
                    
                    # Sadece INTERACTION_CREATE (Slash Komutu) Dinle
                    if data.get("t") == "INTERACTION_CREATE":
                        interaction_data = data["d"]
                        command_name = interaction_data.get("data", {}).get("name")
                        
                        if command_name == "fiyat":
                            interaction_id = interaction_data.get("id")
                            
                            # Etkileşime Cevap Ver
                            response = {
                                "op": "callback",
                                "d": {
                                    "interaction_id": interaction_id,
                                    "type": "channel_message",
                                    "data": {
                                        "content": get_market_data()
                                    }
                                }
                            }
                            await ws.send(json.dumps(response))
                            print("✅ /fiyat komutu yanıtlandı.")

        except Exception as e:
            print(f"⚠️ Bağlantı hatası: {e}. 10 saniye sonra tekrar denenecek...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(start_bot())
