import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import Token, AccessToken
from rest_framework_simplejwt.authentication import JWTAuthentication


class NotificationsConsumer(WebsocketConsumer):
    room_group_name = 'notifications'

    def connect(self):
        token = self.scope.get('query_string').decode('utf-8').split('=')[1]
        print(token)

        try:
            jwt_auth = AccessToken(token)
            user = jwt_auth['user_id']
            print(user, type(user))
        except TokenError:
            user = None

        if user:
            self.accept()
            async_to_sync(self.channel_layer.group_add)(
                str(user), self.channel_name
            )
        else:
            self.close()

    def disconnect(self, close_code):
        pass

    def send_notification(self, event):
        message = event["message"]

        self.send(text_data=json.dumps({"message": message}))
