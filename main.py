import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    StickerMessage,
    StickerSendMessage
)

app = Flask(__name__)

# 環境変数を取得
CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


@app.route("/callback", methods=['POST'])
def callback():
    # ヘッダのX-Line-Signatureを取得
    signature = request.headers['X-Line-Signature']

    # JSONを取得
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 取得した情報を扱う　もしデータが改竄されてたらエラーになる
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# テキストメッセージが来たとき
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text + '!'))


# スタンプが来たとき
@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker(event):
    line_bot_api.reply_message(
        event.reply_token,
        (
            StickerSendMessage(
                package_id='1',
                sticker_id='1'
            ),
            StickerSendMessage(
                package_id='1',
                sticker_id='2'
            )
        ))
    # スタンプにはpackage_idとsticker_idが存在する
    # package_idは、スタンプの購入単位で振られている　「熱盛スタンプ」には○番、
    # 「しゃべる！Seyana!アカネチャン」には△番というように振られている
    # sticker_idは、スタンプ1枚1枚に振られている固有のID
    # Messaging APIで返信できるスタンプは限られている
    # → https://developers.line.biz/media/messaging-api/sticker_list.pdf
    #
    # リプライメッセージをタプルで指定すると、同時に複数のメッセージが送れる　最大：5コ


if __name__ == "__main__":
    # app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
