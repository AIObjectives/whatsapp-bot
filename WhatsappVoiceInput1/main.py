from flask import Flask, request

from whatsapp_voice_bot.helper.oepnai_api import chat_completion, transcript_audio
from whatsapp_voice_bot.helper.twilio_api import send_message

from config import config

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    return 'OK', 200

@app.route('/twilio', methods=['POST'])
def twilio():
    try:
        data = request.form.to_dict()
        print(data)
        query = data['Body']
        sender_id = data['From']
        print(f'Sender id - {sender_id}')
        # TODO
        # get the user
        # if not create
        # create chat_history from the previous conversations
        # quetion and answer
        if 'MediaUrl0' in data.keys():
            transcript = transcript_audio(data['MediaUrl0'])
            if transcript['status'] == 1:
                print(f'Query - {transcript["transcript"]}')
                response = chat_completion(transcript['transcript'])
            else:
                response = config.ERROR_MESSAGE
        else:
            print(f'Query - {query}')
            response = chat_completion(query)
        print(f'Response - {response}')
        send_message(sender_id, response)
        print('Message sent.')
    except Exception as e:
        print(e)

    return 'OK', 200
