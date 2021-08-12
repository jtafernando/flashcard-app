from .deck import Deck
from . import db  # importing db from __init__.py (dot refers to any file in current package)
from flask_login import UserMixin


# This class defines a database table for storing users
class User(db.Model, UserMixin):

    # Define database columns
    id = db.Column(db.Integer, primary_key=True)    # primary_key sets column as id for db objects in this table
    email = db.Column(db.String(150), unique=True)  # max email length is 150 chars; each user must have unique email
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    decks = db.relationship('Deck')  # link user to their decks


    def get_deck(self, deck_name):
        """
        Given a deck name, returns corresponding deck.
        Makes sure that deck belongs to user.
        """
        for deck in self.decks:
            if deck.deck_name == deck_name:
                if deck.user_id == self.id:
                    return deck


    def delete_deck(self, deck:Deck):
        """
        Deletes specified deck from database. 
        Makes sure deck belongs to user.
        """
        if deck:
            # Delete all notes in deck
            for note in deck.notes:
                deck.delete_note(note)

            # Delete deck
            if deck.user_id == self.id:  # check if deck belongs to user
                db.session.delete(deck)
                db.session.commit()
