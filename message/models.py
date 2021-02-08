from app import db
from uuid import uuid4

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.String)
    token = db.Column(db.String)
    sent_at = db.Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)

    @classmethod
    def send_message(cls, receiver, sender, message):
        message = cls(receiver=receiver, sender=sender, message=message)
        message.token = ConversationToken.get_token_for_users(sender.id, receiver.id)
        message.save()

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_conversation_history(cls, user_a_id, user_b_id):
        token = ConversationToken.get_token_for_users(user_a_id, user_b_id)
        # paginate
        messages = cls.query.filter_by(token=token).sort_by("sent_at").all()
        return messages


class ConversationToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_a_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_b_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    token = db.Column(db.String)

    @classmethod
    def create_token(cls, user_a_id, user_b_id):
        token = uuid4().hex
        message_token = [cls(user_a_id=user_a_id, user_b_id=user_b_id, token=token),
                        cls(user_a_id=user_b_id, user_b_id=user_a_id, token=token)]
        
        for entry in message_token:
            db.session.add(entry)
        
        db.session.commit()
        return message_token[0]
    
    @classmethod
    def get_token_for_users(cls, user_a_id, user_b_id):
        message_token = cls.query.filter_by(user_a_id=user_a_id, user_b_id=user_b_id).first() or \
                        cls.query.filter_by(user_b_id=user_a_id, user_a_id=user_b_id).first() or \
                        cls.create_token(user_a_id=user_a_id, user_b_id=user_b_id)

        return message_token.token