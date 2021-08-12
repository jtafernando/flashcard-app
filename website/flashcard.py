# importing db from __init__.py (dot refers to any file in current package)
from . import db
from sqlalchemy.sql import func
import datetime

# New Cards:
# 1 min, 10 min
# graduate: 1 day
# easy: 4 days

# Review Cards:
# max interval: 36500 days

# Lapses:
# reset interval to 10 min
# graduate: 1 day

# again: ease - 20%
# hard: prev_interval * 120% {ease = ease - 15%}
# good: prev_interval * ease
# easy: prev_interval * (ease * easy bonus) {ease = ease + 15%}

# hard interval cant be less than previous interval (round up to next val higher than prev interval)
# good interval can't be less than hard interval


# This class defines a database table for storing flashcards
class Flashcard(db.Model):

    # Define database columns
    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'))
    front_text = db.Column(db.String(100000))
    back_text = db.Column(db.String(100000))
    due_date = db.Column(db.DateTime(timezone=True), default=func.now())
    ease = db.Column(db.Integer)
    cur_interval = db.Column(db.Interval(native=True, second_precision=None, day_precision=None))
    status = db.Column(db.String(100))

    # Static class variables
    starting_ease = 2.5
    again_demotion = .20
    hard_demotion = .15
    easy_promotion = .15
    hard_modifier = 1.20
    easy_bonus = 1.30
    max_interval = datetime.timedelta(days=36500)
    new_easy_interval = datetime.timedelta(days=4)
    new_graduation = datetime.timedelta(days=1)
    statuses = ["new", "grad", "lapse"]


    # Pseudo-constructor:
    def create_flashcard(front: str, back: str, note_id: int):
        ease = Flashcard.starting_ease
        interval = datetime.timedelta(days=0)
        status = Flashcard.statuses[0]
        new_card = Flashcard(front_text=front, back_text=back,
                             note_id=note_id, ease=ease, cur_interval=interval, status=status)
        db.session.add(new_card)
        db.session.commit()
        print(f'card db id: {new_card.id}')
        print(f'note db id: {new_card.note_id}')


    def schedule_due_date(self, button: str):
        """
        Based on button user presses, modifies due date
        for when this card will next be shown to user.
        """
        if self.status == 'new':
            self.set_new_card_due_date(button)

        elif self.status == 'grad':
            self.set_grad_card_due_date(button)
        
        else:
            self.set_lapse_card_due_date(button)


    def set_new_card_due_date(self, choice: str):
        """
        Modifies due date of card still in learing stages 
        (interval less than 1 day).
        """
        ten_minutes = datetime.timedelta(minutes=10)
        one_minute = datetime.timedelta(minutes=1)

        if choice == 'again':
            self.cur_interval = one_minute
            self.due_date = self.due_date + self.cur_interval

        elif choice == 'good':
            # Not ready to graduate from new
            if self.cur_interval < ten_minutes:
                self.cur_interval = ten_minutes
                self.due_date = self.due_date + self.cur_interval

            # Ready to graduate from new
            else:
                self.cur_interval = Flashcard.new_graduation
                self.due_date = self.due_date + self.cur_interval
                self.status = Flashcard.statuses[1]

        else:
            self.cur_interval = Flashcard.new_easy_interval
            self.due_date = self.due_date + self.cur_interval
            self.status = Flashcard.statuses[1]


    def set_lapse_card_due_date(self, button: str):
        """
        Modifies due date of a grad card that has been sent 
        back to learning stages.
        """
        ten_minutes = datetime.timedelta(minutes=10)

        if button == 'again':
            self.cur_interval = ten_minutes
            self.due_date = self.due_date + self.cur_interval
        else:  # lapsed cards are only given 2 button options
            self.cur_interval = Flashcard.new_graduation
            self.due_date = self.due_date + self.cur_interval
            self.status = Flashcard.statuses[1]


    def set_grad_card_due_date(self, button: str):
        """
        Modifies due date of card whose interval is 1 day or more.
        """
        ten_minutes = datetime.timedelta(minutes=10)

        if button == 'again':
            # Send card to lapse status
            self.cur_interval = ten_minutes
            self.due_date = self.due_date + self.cur_interval
            self.ease = self.ease - Flashcard.again_demotion
            self.status = Flashcard.statuses[2]

        elif button == 'hard':
            hard_interval = self.grad_hard_interval()
            if hard_interval > Flashcard.max_interval:
                self.cur_interval = Flashcard.max_interval
            else:
                self.cur_interval = hard_interval
            self.due_date = self.due_date + self.cur_interval
            self.ease = self.ease - Flashcard.hard_demotion

        elif button == 'good':
            good_interval = self.grad_good_interval()
            if good_interval > Flashcard.max_interval:
                self.cur_interval = Flashcard.max_interval
            else:
                self.cur_interval = good_interval
            self.cur_interval = self.grad_good_interval()
            self.due_date = self.due_date + self.cur_interval

        else:
            easy_interval = self.grad_easy_interval()
            if easy_interval > Flashcard.max_interval:
                self.cur_interval = Flashcard.max_interval
            else:
                self.cur_interval = easy_interval
            self.due_date = self.due_date + self.cur_interval
            self.ease = self.ease + Flashcard.easy_promotion


    def grad_hard_interval(self) -> datetime.timedelta:
        """
        Returns the hard interval for a card with interval of 1 day or more.
        """
        hard_interval = self.cur_interval * Flashcard.hard_modifier
        if hard_interval > self.cur_interval:
            return hard_interval
        else:
            return self.cur_interval


    def grad_good_interval(self) -> datetime.timedelta:
        """
        Returns the good interval for a card with interval of 1 day or more.
        """
        good_interval = self.cur_interval * self.ease
        hard_interval = self.grad_hard_interval()

        if good_interval > hard_interval:
            return good_interval
        else:
            return hard_interval * self.ease

    def grad_easy_interval(self) -> datetime.timedelta:
        """
        Returns the easy interval for a card with interval of 1 day or more.
        """
        easy_interval = self.cur_interval * self.ease * Flashcard.easy_bonus
        return easy_interval
