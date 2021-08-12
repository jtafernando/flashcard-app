from .note import Note
from . import db  # importing db from __init__.py (dot refers to any file in current package)
from sqlalchemy.sql import func
from flask_login import current_user
from .note import Note


class Deck(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    inApp_id = db.Column(db.Integer)
    deck_name = db.Column(db.String(150))
    notes = db.relationship('Note')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    new_per_day = db.Column(db.Integer)
    rev_per_day = db.Column(db.Integer)
    rand_order = db.Column(db.Boolean)


    # Pseudo-constructor
    def create_deck(name:str):
        deck_name = name
        inApp_id = len(current_user.decks)
        new_daily = 5
        rev_daily = 5
        new_order = False

        new_deck = Deck(deck_name=deck_name, inApp_id=inApp_id, new_per_day=new_daily,
                        rev_per_day=rev_daily, rand_order=new_order, user_id=current_user.id)

        db.session.add(new_deck)
        db.session.commit()
        print(f'in-app deck id: {new_deck.inApp_id}')
        print(f'db id: {new_deck.id}')


    # Getters
    def get_inApp_id(self) -> int:
        return self.inApp_id

    def get_deck_name(self) -> str:
        return self.deck_name

    def get_new_per_day(self) -> int:
        return self.new_per_day
    
    def get_rev_per_day(self) -> int:
        return self.rev_per_day

    def get_rand_order(self) -> int:
        return self.rand_order

    def get_id(self) -> int:
        return self.id


    # Setters
    def set_inApp_id(self, num:int):
        self.inApp_id = num

    def set_deck_name(self, name:str):
        self.deck_name = name

    def set_new_per_day(self, num:int):
        self.new_per_day = num

    def set_rev_per_day(self, num:int):
        self.rev_per_day = num

    def set_rand_order(self, num:int):
        self.rand_order = num


    def delete_note(self, note:Note):
        """
        Deletes all flashcards of given Note object 
        and then deletes given Note object itself.
        """
        if note:
            # Delete card(s) of given note
            for card in note.flashcards:
                db.session.delete(card)
                db.session.commit()

            # Delete note
            if self.user_id == current_user.id:
                db.session.delete(note)
                db.session.commit()



