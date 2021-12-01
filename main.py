import telebot
from time import sleep
import os
from datetime import datetime
from cv2 import imread, cvtColor, COLOR_BGR2GRAY, CascadeClassifier, imwrite
from pydub import AudioSegment
from init import TG_TOKEN


# Загруженные файлы сохраняются по user_id и сортируются по формату (аудио или изображение)

bot = telebot.TeleBot(TG_TOKEN)


def date_time():
    return datetime.now().strftime("%d-%m-%Y %H:%M")


def clear_temp():
    for filename in os.listdir('tmp'):
        try:
            print(f'{date_time()} * Deleting temp {filename}')
            os.remove('tmp/' + filename)
        except Exception as e:
            print(e)


def count_files(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
    return len(os.listdir(dir))


def get_size(start_path='.'):
    # На перспективу внедрить отслеживание размера хранилища

    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    # Отлавливаем голосовую запись и записываем ее во временную папку

    print(date_time() + ' *Audio processing*')
    try:
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        with open('tmp/' + f'{message.chat.id}.ogg', 'wb') as new_file:
            new_file.write(downloaded_file)
            print(f'{date_time()} *{message.chat.id}* Temp file saved')
            sleep(1)
        new_audio = write_audio(f'{message.chat.id}.ogg')

        clear_temp()

        bot.send_document(message.chat.id, open(new_audio, 'rb'))

    except Exception as e:
        print(e)


def write_audio(src):
    # Конвертируем аудио в wav формат и сохраняем в папке, соответстующей id пользователя

    try:
        f_name = src.split('.')[0]
        dir = f'data/{f_name}/audio'
        dst = f'data/{f_name}/audio/audio_message_{count_files(dir)}.wav'

        sound = AudioSegment.from_ogg('tmp/' + src)
        sound.export(dst, format='wav', bitrate='16kHz')
        print(f'{date_time()} * Edited file saved')

        return dst

    except Exception as e:
        print(e)


def write_image(img, msg_chat_id):
    # Ищем лица в изображении
    try:
        image2 = imread(img)
        gray_img = cvtColor(image2, COLOR_BGR2GRAY)

        haar_face_cascade = CascadeClassifier('content/haarcascade_frontalface_alt.xml')
        faces = haar_face_cascade.detectMultiScale(gray_img)  # Массив, содержащий количество найденых лиц

        len_faces = len(faces)
        #FACES = True if len_faces else False
        dir = f'data/{msg_chat_id}/images' #if FACES else f'data/{msg_chat_id}/no_faces'

        count_files(dir)
        imwrite(f'{dir}/{img.split("/")[-1]}', image2)
        return len_faces
    except Exception as e:
        print(e)


@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    # Отлавливаем загрузку изображений

    print(date_time() + ' *Image processing*')
    try:
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        src = 'tmp/' + file_info.file_path.split('/')[-1]
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)

        num_of_faces = write_image(src, message.chat.id)

        clear_temp()

        msg = f'Есть лица! :)' if num_of_faces else 'Лиц нет.. :('
        bot.reply_to(message, msg)

    except Exception as e:
        print(e)


def main():
    try:
        bot.infinity_polling()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
