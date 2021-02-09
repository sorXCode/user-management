from app import db
from uuid import uuid4
from flask_login import current_user

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
    def get_chat_history(cls, user_a_id, user_b_id):
        token = ConversationToken.get_token_for_users(user_a_id, user_b_id)
        # paginate
        messages = cls.query.filter_by(token=token).order_by("sent_at").all()
        return messages

    @classmethod
    def get_conversations(cls, user_id):
        tokens = ConversationToken.get_all_conversations(user_id)
        return [cls.query.filter_by(token=token).order_by("sent_at").first() for token in tokens]
    

    def __repr__(self):
        if not current_user.email==self.sender.email:
            return self.sender.email
        return self.receiver.email
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
                        cls.create_token(user_a_id=user_a_id, user_b_id=user_b_id)

        return message_token.token
    
    @classmethod
    def get_all_conversations(cls, user_id):
        conversation_tokens = cls.query.filter_by(user_a_id=user_id).all()
        return [conversation_token.token for conversation_token in conversation_tokens]
