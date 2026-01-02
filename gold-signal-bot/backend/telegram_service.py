import requests
import json
import os

class TelegramService:
    def __init__(self, bot_token=None):
        self.bot_token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # In a real app, this would be a database table
        self.subscriptions_file = os.path.join(os.path.dirname(__file__), "data", "telegram_subscriptions.json")
        self._ensure_data_dir()
        self.subscriptions = self._load_subscriptions()

    def _ensure_data_dir(self):
        data_dir = os.path.dirname(self.subscriptions_file)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        if not os.path.exists(self.subscriptions_file):
            with open(self.subscriptions_file, "w") as f:
                json.dump({}, f)

    def _load_subscriptions(self):
        try:
            with open(self.subscriptions_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_subscriptions(self):
        with open(self.subscriptions_file, "w") as f:
            json.dump(self.subscriptions, f, indent=4)

    def subscribe_user(self, chat_id, strategy_id):
        """Map a Telegram chat_id to a specific strategy_id."""
        if strategy_id not in self.subscriptions:
            self.subscriptions[strategy_id] = []
        
        if chat_id not in self.subscriptions[strategy_id]:
            self.subscriptions[strategy_id].append(chat_id)
            self._save_subscriptions()
            return True
        return False

    def send_signal(self, strategy_id, signal_data):
        """Broadcast signal to all users subscribed to this strategy."""
        if strategy_id not in self.subscriptions:
            return

        message = self._format_signal_message(strategy_id, signal_data)
        for chat_id in self.subscriptions[strategy_id]:
            self._send_raw_message(chat_id, message)

    def _format_signal_message(self, strategy_id, signal_data):
        direction_icon = "🟢 BUY" if signal_data['signal'] == 'BUY' else "🔴 SELL"
        return (
            f"🚀 *FundedLab Signal Alert*\n"
            f"━━━━━━━━━━━━━━━\n"
            f"Strategy: `{strategy_id}`\n"
            f"Action: {direction_icon}\n"
            f"Price: `{signal_data['price']}`\n"
            f"SL: `{signal_data['sl']}`\n"
            f"TP: `{signal_data['tp']}`\n"
            f"Confidence: `{signal_data.get('confidence', 'N/A')}%`\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📡 _Powered by FundedLab AI_"
        )

    def _send_raw_message(self, chat_id, text):
        if not self.bot_token:
            print(f"DEBUG [Telegram]: Would send to {chat_id}: {text}")
            return

        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        try:
            requests.post(url, json=payload)
        except Exception as e:
            print(f"Error sending Telegram message: {e}")

# Global instance
telegram_service = TelegramService()
