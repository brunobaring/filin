# from emotion import app

# if __name__ == '__main__':
#     app.run(host='127.0.0.1', port='5000')




from emotion import create_app as emotion_create_app
emotion = emotion_create_app()

if __name__ == '__main__':
    emotion.run(host='127.0.0.1', port='5000', debug=True)