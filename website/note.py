from . import db  # importing db from __init__.py (dot refers to any file in current package)
from sqlalchemy.sql import func
from .flashcard import Flashcard


class Note(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    inApp_id = db.Column(db.Integer)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    front_text = db.Column(db.String(10000))
    back_text = db.Column(db.String(10000))
    note_type = db.Column(db.String(150))
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'))
    flashcards = db.relationship('Flashcard')


    # Pseudo-constructor
    def create_note(inApp_id, deck_id, front, back, type):
        new_note = Note(inApp_id=inApp_id, deck_id=deck_id, 
                        front_text=front, back_text=back, note_type=type)
        db.session.add(new_note)
        db.session.commit()
        print(f'in-app note id: {new_note.inApp_id}')
        print(f'note db id: {new_note.id}')

        # Instantiate flashcards
        if type == 'basic-reverse':
            Flashcard.create_flashcard(front=front, back=back, note_id=new_note.id)
            Flashcard.create_flashcard(front=back, back=front, note_id=new_note.id)
        else:
            Flashcard.create_flashcard(front=front, back=back, note_id=new_note.id)

            
    def edit(self, front:str, back:str, type:str, deck):
        """
        Edits this note.
        """
        self.front_text = front
        self.back_text = back
        self.deck_id = deck.id
