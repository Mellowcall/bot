from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPoll
from telethon.tl.functions.messages import GetMessagesRequest
import asyncio

API_ID = 24492602
API_HASH = 'c66abf1e59b7978b373bb658f758658a'
PHONE_NUMBER = '+79060202522'
TARGET_CHANNEL = '@sprot_and_oil'

client = TelegramClient('user_session', API_ID, API_HASH)

SOURCE_CHANNELS = [
    '@Bookmakers_Rating',
    '@ftlive', '@ufceurasia', '@sportsru', '@ofnews', '@okkosport',
    '@zhfootballll', '@KrysMF23', '@khl_official_telegram',
    '@news_matchtv', '@transferyi', '@sportrian',
    '@tennisprimesport', '@vgik_of',
    '@rfsruofficial', '@kgenich', '@shhhnyakin', '@pervsport', '@sovsport', '@neutka', '@firstallsport', '@championat', '@myachrus'
]

FILTER_WORDS = [
    'акция', 'erid', 'розыгрыш', 'фрибет', 'фонбет', 'pari', 'winline',
    'марафон', 'лига ставок', 'betboom', 'olimp',
    'olimpbet', 'бетсити', 'winline'
]

last_sent_messages = {}

@client.on(events.NewMessage(chats=SOURCE_CHANNELS))
async def handle_new_message(event):
    try:
        if any(word in event.message.text.lower() for word in FILTER_WORDS):
            return

        source_channel_id = event.message.peer_id.channel_id

        if source_channel_id in last_sent_messages:
            last_sent_id, last_sent_time = last_sent_messages[source_channel_id]
            if event.message.id <= last_sent_id:
                return
            if (event.message.date - last_sent_time).total_seconds() < 60:
                return

        # Получаем полное сообщение
        full_message = await client(GetMessagesRequest(
            peer=event.message.peer_id,
            id=[event.message.id]
        ))
        
        if full_message and full_message.messages:
            message = full_message.messages[0]
            
            # Проверяем, нет ли в сообщении опроса
            if isinstance(message.media, MessageMediaPoll):
                # Если есть опрос, пересылаем только текст сообщения
                await client.send_message(TARGET_CHANNEL, message.message)
            elif message.grouped_id:
                # Пересылаем всю группу сообщений, исключая опросы
                grouped_message_ids = [m.id for m in full_message.messages if m.grouped_id == message.grouped_id]
                await client.forward_messages(TARGET_CHANNEL, grouped_message_ids, event.message.peer_id)
            else:
                # Если нет группировки и нет опроса, пересылаем одно сообщение
                await client.forward_messages(TARGET_CHANNEL, [message.id], event.message.peer_id)

        last_sent_messages[source_channel_id] = (event.message.id, event.message.date)

        print(f"Сообщение успешно обработано")

    except Exception as e:
        print(f'Ошибка при обработке сообщения: {e}')

async def main():
    await client.start(phone=PHONE_NUMBER)
    print("Бот запущен и ожидает сообщения...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())