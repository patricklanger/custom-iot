from flask import Flask, render_template
import requests
import json


app = Flask(__name__)

device_object = [
    {
        "name": "device_1",
        "attributes": [
            {
                "name": "temperature",
                "d": 23,  # digit / wert
                "u": "°C"  # unit / maßeinheit
            },
            {
                "name": "accelerometer",
                "d": [0.5, 0.7, -0.4],
                "u": "g"
            }
        ]
    },
    {
        "name": "device_2",
        "attributes": [
            {
                "name": "temperature",
                "d": 24,  # digit / wert
                "u": "°C"  # unit / maßeinheit
            },
            {
                "name": "accelerometer",
                "d": [0.1, 0.2, -0.9],
                "u": "g"
            }
        ]
    }
]


@app.route('/')
def get_device_dashboard():
    try:
        # TODO Device abfrage an aiocoap-rd.
        # TODO kann http-webserver mit coap auf aiocoap-rd zugreifen??
        res = device_object  # requests.get("https://api.npoint.io/4af156202f984d3464c3")
    except:
        return
    # alle dives als josn objekte
    all_devices = res  # json.loads(res.text)
    # webseite rendern mit allen devices
    return render_template("index.html", all_devices=all_devices)

# @app.route('/blog/<page>')
# def get_blog_page(page):
#     try:
#         res =requests.get("https://api.npoint.io/4af156202f984d3464c3")
#     except:
#         return
#     all_posts = json.loads(res.text)
#     blog_page = next((blog_post for blog_post in all_posts if int(blog_post["id"]) == int(page)), None)
#     print(blog_page)
#     return render_template("post.html", blog_page=blog_page)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
