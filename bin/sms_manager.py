import mimetypes
import os
from urllib.parse import urlparse

from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse


app = Flask(__name__)


GOOD_BOY_URL = "https://images.unsplash.com/photo-1518717758536-85ae29035b6d?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1350&q=80"


@app.route("/whatsapp", methods=["GET", "POST"])
def reply_whatsapp():

    num_media = int(request.values.get("NumMedia"))
    media_files = []
    for idx in range(num_media):
        media_url = request.values.get(f'MediaUrl{idx}')
        mime_type = request.values.get(f'MediaContentType{idx}')
        media_files.append((media_url, mime_type))

        req = requests.get(media_url)
        file_extension = mimetypes.guess_extension(mime_type)
        media_sid = os.path.basename(urlparse(media_url).path)

        with open(f"app_data/{media_sid}{file_extension}", 'wb') as f:
            f.write(req.content)

    response = MessagingResponse()
    if not num_media:
        msg = response.message("Send us an image!")
    else:
        msg = response.message("Thanks for the image(s).")
    msg.media(GOOD_BOY_URL)
    return str(response)


if __name__ == "__main__":
    app.run()
