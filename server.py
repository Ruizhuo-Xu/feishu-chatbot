#!/usr/bin/env python3.8

import os
import logging
import requests
import pdb
import json
from api import MessageApiClient
from event import MessageReceiveEvent, UrlVerificationEvent, EventManager
from flask import Flask, jsonify
from dotenv import load_dotenv, find_dotenv
from chatgpt import Chat

# load env parameters form file named .env
load_dotenv(find_dotenv())

app = Flask(__name__)
chat = Chat()

# load from env
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
VERIFICATION_TOKEN = os.getenv("VERIFICATION_TOKEN")
ENCRYPT_KEY = os.getenv("ENCRYPT_KEY")
LARK_HOST = os.getenv("LARK_HOST")


# init service
message_api_client = MessageApiClient(APP_ID, APP_SECRET, LARK_HOST)
event_manager = EventManager()
msg_id_buffer = []

character_prompt = "请输入数字选择机器人对话风格：" + \
                    "\n\t1.你是一个非常友善的助手" + \
                    "\n\t2.你是一个资深的程序员" + \
                    "\n\t3.你是一个温柔善良的小姐姐" + \
                    "\n\t4.你是一个有礼貌的绅士" + \
                    "\n\t其他：您也可以输入您希望的风格"
set_character = False
    
@event_manager.register("url_verification")
def request_url_verify_handler(req_data: UrlVerificationEvent):
    # url verification, just need return challenge
    if req_data.event.token != VERIFICATION_TOKEN:
        raise Exception("VERIFICATION_TOKEN is invalid")
    return jsonify({"challenge": req_data.event.challenge})


@event_manager.register("im.message.receive_v1")
def message_receive_event_handler(req_data: MessageReceiveEvent):
    global set_character
    sender_id = req_data.event.sender.sender_id
    message = req_data.event.message
    if message.message_type != "text":
        logging.warn("Other types of messages have not been processed yet")
        return jsonify()
        # get open_id and text_content
    open_id = sender_id.open_id
    msg_id = message.message_id
    # text_content = message.content
    text_content = json.loads(message.content)
    content = text_content['text']
    print(content)
    if msg_id in msg_id_buffer:
        return jsonify()
    else:
        msg_id_buffer.append(msg_id)
    if set_character:
        set_character = False
        if content in ['1', '2', '3', '4']:
            character = chat.set_character(content)
        else:
            character = chat.set_character('-1', content)
        reply = json.dumps({'text': "当前对话风格设置为：" + character})
        message_api_client.send_text_with_open_id(open_id, reply)
        return jsonify()
    else:
        if content == "对话结束" or content == '3':
            chat.reset()
            reply = json.dumps({'text': '本轮对话结束, 下一条消息将开启新的对话！'})
            message_api_client.send_text_with_open_id(open_id, reply)
            return jsonify()
        if content == "设置角色" or content == '1':
            set_character = True
            reply = json.dumps({'text': character_prompt})
            message_api_client.send_text_with_open_id(open_id, reply)
            return jsonify()

    print(f'tc:{text_content}')
    answer = chat.ask(content)
    print(f'ans:{answer}')
    reply = json.dumps(answer)
    # echo text message
    message_api_client.send_text_with_open_id(open_id, reply)
    return jsonify()


@app.errorhandler
def msg_error_handler(ex):
    logging.error(ex)
    response = jsonify(message=str(ex))
    response.status_code = (
        ex.response.status_code if isinstance(ex, requests.HTTPError) else 500
    )
    return response


@app.route("/", methods=["POST"])
def callback_event_handler():
    # init callback instance and handle
    event_handler, event = event_manager.get_handler_with_event(VERIFICATION_TOKEN, ENCRYPT_KEY)

    return event_handler(event)


if __name__ == "__main__":
    # init()
    app.run(host="0.0.0.0", port=3000, debug=True)
