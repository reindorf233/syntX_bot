from telegram import Bot
from config import config

def simple_test():
    """Simple bot test without asyncio conflicts"""
    bot = Bot(token=config.telegram_bot_token)
    
    try:
        # Test bot info
        me = bot.get_me()
        print(f"✅ Bot Username: {me.username}")
        print(f"✅ Bot Name: {me.first_name}")
        print(f"✅ Bot ID: {me.id}")
        
        # Test sending a message to yourself (or your chat ID)
        # Replace YOUR_CHAT_ID with your actual Telegram chat ID
        test_message = bot.send_message(
            chat_id="YOUR_CHAT_ID",  # Replace this!
            text="🚀 Test message from Deriv SyntX Bot!\n\nBot is working perfectly!"
        )
        print("✅ Test message sent successfully!")
        print("✅ Bot is fully functional!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔍 Testing Deriv SyntX Bot...")
    print("📝 Note: Replace YOUR_CHAT_ID with your actual Telegram chat ID")
    simple_test()
