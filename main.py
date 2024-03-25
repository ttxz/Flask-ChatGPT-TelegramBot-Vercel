# -*- coding: utf-8 -*-

import logging

import telegram, os
from flask import Flask, request
from telegram.ext import Dispatcher, MessageHandler, Filters, CallbackQueryHandler, Updater, CommandHandler
from telegram import InlineKeyboardButton,InlineKeyboardMarkup

import openai


openai.api_key = os.getenv("OPENAI_API_KEY") 


chat_language = os.getenv("INIT_LANGUAGE", default = "zh") #amend here to change your preset language
	
MSG_LIST_LIMIT = int(os.getenv("MSG_LIST_LIMIT", default = 20))
LANGUAGE_TABLE = {
	  "zh": "哈囉！",
	  "en": "Hello!",
      "jp": "こんにちは"
	}


class Prompts:
    def __init__(self):
        self.msg_list = []
        self.msg_list.append(f"AI:{LANGUAGE_TABLE[chat_language]}")
	    
    def add_msg(self, new_msg):
        if len(self.msg_list) >= MSG_LIST_LIMIT:
            self.remove_msg()
        self.msg_list.append(new_msg)
	
    def remove_msg(self):
        self.msg_list.pop(0)
	
    def generate_prompt(self):
        return '\n'.join(self.msg_list)	
	
class ChatGPT:  
    def __init__(self):
        self.prompt = Prompts()
        self.model = os.getenv("OPENAI_MODEL", default = "gpt-3.5-turbo-instruct")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", default = 0))
        self.frequency_penalty = float(os.getenv("OPENAI_FREQUENCY_PENALTY", default = 0))
        self.presence_penalty = float(os.getenv("OPENAI_PRESENCE_PENALTY", default = 0.6))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", default = 240))
	
    def get_response(self):
        response = openai.Completion.create(
	            model=self.model,
	            prompt=self.prompt.generate_prompt(),
	            temperature=self.temperature,
	            frequency_penalty=self.frequency_penalty,
	            presence_penalty=self.presence_penalty,
	            max_tokens=self.max_tokens
                )
        
        print("AI回答內容：")        
        print(response['choices'][0]['text'].strip())

        print("AI原始回覆資料內容：")      
        print(response)
        
        return response['choices'][0]['text'].strip()
	
    def add_msg(self, text):
        self.prompt.add_msg(text)


#####################

telegram_bot_token = str(os.getenv("TELEGRAM_BOT_TOKEN"))



# Load data from config.ini file
#config = configparser.ConfigParser()
#config.read('config.ini')

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Initial Flask app
app = Flask(__name__)

# Initial bot by Telegram access token
bot = telegram.Bot(token=telegram_bot_token)
updater = Updater(token=telegram_bot_token)

@app.route('/callback', methods=['POST'])
def webhook_handler():
    jsonParams = request.get_json(force=True)
    print("callback被调用，参数：", jsonParams)
    """Set route /hook with POST method will trigger this method."""
    if request.method == "POST":
        update = telegram.Update.de_json(jsonParams, bot)
        print(update)
        # Update dispatcher process that handler to process this message
        dispatcher.process_update(update)
        request.
    return 'ok'

# 定义键盘按钮
keyboard = [['Option 1', 'Option 2'], ['Option 3', 'Option 4']]

reply_markup = telegram.ReplyKeyboardMarkup(keyboard)

# 定义内联键盘按钮
inline_keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
                    InlineKeyboardButton("Option 2", callback_data='2')],
                   [InlineKeyboardButton("Option 3", callback_data='3'),
                    InlineKeyboardButton("Option 4", callback_data='4')]]
inline_markup = InlineKeyboardMarkup(inline_keyboard)

# 处理/start命令
def start(bot, update):
    print("----------------start---------------------")
    # bot.send_message(chat_id=update.effective_chat.id, text="Hello, I'm a bot!", reply_markup=reply_markup)
    update.message.reply_text('量化交易中心',
                              reply_markup = InlineKeyboardMarkup([[
                                  InlineKeyboardButton('充值',
                                                       url = 'https://pixnashpython.pixnet.net/blog'),
                                  InlineKeyboardButton('绑定钱包',
                                                       url = 'https://pixnashlife.pixnet.net/blog')
                                  ]])
                              )

# 处理普通键盘按钮
def button(update, context):
    query = update.message.text
    bot.send_message(chat_id=update.effective_chat.id, text="You pressed " + query)

# 处理内联键盘按钮
def inline_button(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="You pressed " + query.data, reply_markup= inline_markup)

def reply_handler(filters, update):
    """Reply message."""
    #text = update.message.text
    #update.message.reply_text(text)
    # chatgpt = ChatGPT()
    #
    # chatgpt.prompt.add_msg(update.message.text) #人類的問題 the question humans asked
    # ai_reply_response = chatgpt.get_response() #ChatGPT產生的回答 the answers that ChatGPT gave
    #
    # update.message.reply_text(ai_reply_response) #用AI的文字回傳 reply the text that AI made
    message = update.message.text
    print("收到消息===", message)
    update.message.reply_text("已收到：：" + message + "")

def despose_handler(query, context):
    print("执行内联键盘设置")
    button = InlineKeyboardButton(text="充值", callback_data="充值按钮被点击了")

    query.callback_query.message.edit_text("充值",
                                             reply_markup=InlineKeyboardMarkup(button))

# New a dispatcher for bot
# dispatcher = Dispatcher(bot, None)
dispatcher = updater.dispatcher

# Add handler for handling message, there are many kinds of message. For this handler, it particular handle text
# message.
# dispatcher.add_handler(MessageHandler(Filters.text, reply_handler))
# dispatcher.add_handler(CallbackQueryHandler(despose_handler, pattern="gogogo"))
# 注册处理函数
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('menu', start))
dispatcher.add_handler(CallbackQueryHandler(inline_button))
dispatcher.add_handler(MessageHandler(telegram.ext.Filters.text, button))

if __name__ == "__main__":
    # Running server
    app.run(debug=True)
    # 启动Bot
    # updater.start_polling()
    # updater.idle()