import telebot
import time
import networkx as net
import cv2
import numpy as np
import scipy.misc
from point import Point
from mathoperation import MathOperation

bot_token = '526035971:AAGJudEYdqnT9LZE-0Rz86PQvyel9agFyNo'
bot = telebot.TeleBot(token=bot_token)
user = bot.get_me()
print("myuser is",user.id)
def find_at(msg):
        for text in msg:
                if '@' in text:
                        return text
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
        bot.send_photo(chat_id=message.chat.id, photo='http://i64.tinypic.com/2r3bj0n.jpg')

        
@bot.message_handler(content_types=['text'])
def echo(message):
    bot.send_message(message.chat.id, message.text)        
        
        
@bot.message_handler(content_types=['photo'])
def photo(message):
    print("message.photo =", message.photo)
    fileID = message.photo[-1].file_id
    print("fileID =", fileID)
    file_info = bot.get_file(fileID)
    print("file.file_path =", file_info.file_path)
    downloaded_file = bot.download_file(file_info.file_path)

    #save photo locally
    with open("image.jpg", 'wb') as new_file: #"image.jpg" is chosen 
        new_file.write(downloaded_file)
        
    #canny
    img = cv2.imread('image.jpg',0)
    edges = cv2.Canny(img,200,400)
    edges_arr = np.asarray(edges)
    edges_arr = np.expand_dims(edges_arr, axis=2)
    
    height = message.photo[3].height
    width = message.photo[3].width
    foregrounds = np.array([])
    foregroundAmount = 0
    
    #store all matho operations
    mathOperations = np.array([])

    #calculateHorizontalForegrounds
    for row in range(height):
        for column in range(width):
            #print(edges_arr[row][column])
            if edges_arr[row][column] == 255:
                foregroundAmount += 1
        if foregroundAmount > 0:
            foregroundAmount = 1        
        foregrounds = np.append(foregrounds, foregroundAmount)
        foregroundAmount = 0

        
        
        
        
        
        
    #calculate sums -> [0, 0, 1, 1, 0] became -> [(2, 0), (2, 1), (1, 0)]
    sums = np.array([])
    sumIndex = 0
    cons = foregrounds[0]
    
    if cons == 0:
        sums = np.append(sums, Point(1, 0))
    else:
        sums = np.append(sums, Point(1, 1))
    
    for index in range(foregrounds.size):
        if foregrounds[index] == cons:
            sums[sumIndex].x += 1
        else:
            sumIndex += 1
            if foregrounds[index] == 0:
                sums = np.append(sums, Point(1, 0))
            else:
                sums = np.append(sums, Point(1, 1))
            cons = foregrounds[index]
    if sums.size <= 1:
        return None
    else:
        print("calculate sums",sums)
    
    
    
    
    
    
    # start fireHorizontalGrid
    
    #deleteWhiteNoise(sums, withThreshold: 10, leftAndRightBlackValues: 15)
    for index in range(1, sums.size - 1):
        if sums[index].y == 1:
            if sums[index].x <= 10: #10 -> withThreshold
                if sums[index - 1].x > 15 or sums[index + 1].x > 15: #15 -> leftAndRightBlackValues
                    sums[index].y = 0
    if sums[0].y == 1:
        sums[0].y = 0
    #print("deleteWhiteNoise", sums)
    
    
    
    
    
    
    
    
    
    #mergeConsecutiveEqualsNumbers
    sums2 = np.array([])
    current = 0
    cons2 = sums[0].y
    sums2 = np.append(sums2, sums[0])
    
    for index in range(1, sums.size):
        if sums[index].y != cons2:
            cons2 = sums[index].y
            sums2 = np.append(sums2, sums[index])
            current += 1
        else:
            sums2[current].x = sums2[current].x + sums[index].x
    
    #print("mergeConsecutiveEqualsNumbers", sums2)
    
    
    
    
    
    #deleteBlackNoise(sums2, withBlackNoise: 16, andWhiteNoise: 15, noiseForFirstElement: 5)
    if sums2.size > 1:
        for index in range(1, sums2.size - 1):
            if sums2[index].y == 0:
                if sums2[index].x <= 16: #16 -> withBlackNoise
                    if sums2[index - 1].x >= 15 or sums2[index + 1].x >= 15: #15 -> andWhiteNoise
                        sums2[index].y = 1
        if sums2[0].y == 0:
            if sums2[0].x <= 5: #5 -> noiseForFirstElement
                sums2[0].y = 1
    
    #print("deleteBlackNoise", sums2)
    
    
    
    
    
    #mergeConsecutiveEqualsNumbers (copy)
    sums2 = np.array([])
    current = 0
    cons2 = sums[0].y
    sums2 = np.append(sums2, sums[0])
    
    for index in range(1, sums.size):
        if sums[index].y != cons2:
            cons2 = sums[index].y
            sums2 = np.append(sums2, sums[index])
            current += 1
        else:
            sums2[current].x = sums2[current].x + sums[index].x
    
    
    #print("mergeConsecutiveEqualsNumbers", sums2)            
    
    
    
    #drawHorzontalLines
    startDrawing = 0
    for index2 in range(sums2.size):
        if sums2[index2].y == 0:
            print(sums2[index2])
            for row in range(startDrawing, sums2[index2].x + startDrawing):
                for column in range(width):
                    if row != height:
                        edges_arr[row][column] = 255
        startDrawing = startDrawing + sums2[index2].x
    # compelte fireHorizontalGrid
###################################################################################

    # start fireVerticalGrid
    
                
    
    
    
    scipy.misc.toimage(edges, cmin=0.0, cmax=1.0).save('outfile.jpg')
       
    #send photo to client
    photo = open('outfile.jpg', 'rb')
    bot.send_photo(chat_id=message.chat.id, photo=photo)
    
@bot.message_handler(func=lambda msg: msg.text is not None and '@' in msg.text)
def at_answer(message):
        print(message)
        texts = message.text.split()
        at_text = find_at(texts)
        bot.reply_to(message, 'https://instagram.com/{}'.format(at_text[1:]))
while True:
        try:
                bot.polling()
        except  Exception:
                time.sleep(15)