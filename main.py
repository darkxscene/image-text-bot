import telebot
from PIL import Image, ImageDraw, ImageFont
import os

TOKEN = ''

bot = telebot.TeleBot(TOKEN)

user_text_storage = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне сначала текст, который ты хочешь наложить на фото.")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_text_storage[message.chat.id] = message.text
    bot.reply_to(message, f"Текст '{message.text}' принят! Теперь отправь мне саму фотографию.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    
    if chat_id not in user_text_storage:
        bot.reply_to(message, "Сначала отправь мне текст, а уже потом присылай фото!")
        return
    
    bot.reply_to(message, "Обрабатываю фото, подожди секунду...")

    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    input_path = "input.jpg"
    output_path = "output.jpg"
    
    with open(input_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    img = Image.open(input_path)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", size=int(img.size[1] * 0.05)) 
    except:
        font = ImageFont.load_default()
    
    text = user_text_storage[chat_id]
    
    width, height = img.size
    
    text_box = draw.textbbox((0, 0), text, font=font)
    text_width = text_box[2] - text_box[0]
    text_height = text_box[3] - text_box[1]
    
    x = (width - text_width) / 2
    y = height - text_height - int(height * 0.1)
    
    draw.text((x, y), text, fill="white", font=font, stroke_width=3, stroke_fill="black")

    img.save(output_path)

    with open(output_path, 'rb') as photo:
        bot.send_photo(chat_id, photo)
        
    os.remove(input_path)
    os.remove(output_path)

print("Бот успешно запущен и ждет сообщений...")
bot.infinity_polling()