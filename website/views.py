# This file is a blueprint. It stores a bunch of routes (urls) for our website.
from flask import Blueprint, render_template, request, url_for, redirect, flash, jsonify, json
from werkzeug.utils import redirect
from flask_login import login_required, current_user
from .deck import Deck
from .note import Note
from . import db
import numpy as np


views = Blueprint('views', __name__)



@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    """
    Renders home page and handles all requests on home page.
    """
    if request.method == 'POST':
        if 'deckName' in request.form:
            return post_new_deck_req()
        elif 'newCardsPerDay' in request.form:
            return post_deck_settings_req()
        else:
            return post_delete_deck_req()

    return render_template("home.html", user=current_user)


def post_new_deck_req():
    """
    Makes a post request to create new deck.
    """
    deck_name = request.form.get('deckName')
    Deck.create_deck(deck_name)
    flash('New deck created.', category='success')
    return redirect(url_for('views.home'))


def post_deck_settings_req():
    """
    Makes a post request to update deck settings for deck 
    specified in request form.
    """
    cur_deck = current_user.get_deck(request.form.get('deck'))
    cur_deck.set_new_per_day(request.form.get('newCardsPerDay'))
    cur_deck.set_rev_per_day(request.form.get('reviewCardsPerDay'))

    new_order = request.form.get('newCardOrder')
    if new_order == 'option1':
        cur_deck.set_rand_order(False)
    else:
        cur_deck.set_rand_order(True)

    db.session.commit()
    flash('Settings saved.', category='success')
    return redirect(url_for('views.home'))


def post_delete_deck_req():
    """
    Makes a post request delete deck specified in request form.
    """
    deck = current_user.get_deck(request.form.get('deckToDelete'))
    current_user.delete_deck(deck)
    return redirect(url_for('views.home'))


@views.route('/add-cards', methods=['GET', 'POST'])
def card_builder():
    """
    Renders card_builder page and handles all requests on card_builder page.
    """
    if request.method == 'POST':
        post_add_note_req()

    return render_template("card_builder.html", user=current_user)


def post_add_note_req():
    """
    Creates new note and flashcards, and adds them to deck specified by request form.
    """
    # Get request data
    deck = current_user.get_deck(request.form.get('deckSelect'))
    deck_id = deck.id
    inApp_id = len(deck.notes)
    front = request.form.get('front')
    back = request.form.get('back')
    has_reverse = request.form.get('reverseCardCheck')

    # Create note
    if has_reverse == 'option1':
        Note.create_note(inApp_id=inApp_id, deck_id=deck_id, front=front, back=back, type='basic-reverse')
    else:
        Note.create_note(inApp_id=inApp_id, deck_id=deck_id, front=front, back=back, type='basic')

    flash('Flashcard(s) added.', category='success')
    return redirect(url_for('views.card_builder'))


@views.route('/card-library')
def card_library():
    """
    Renders card_library page and handles all requests on card_library page.
    """
    return render_template("card_library.html", user=current_user)
    

# @views.route('/update-cur-card', methods=['POST'])
# def update_study_session():
#     cur_card = np.random.rand()
#     return jsonify('', render_template('current_card.html', user=current_user, front=cur_card))


@views.route('/study-session', methods=['GET', 'POST'])
def study_session():
    """
    Renders study_session page with first flashcard to study and handles all requests on study_session page.
    """
    print("python reached")
    print(request.get_json())
    req_data = json.loads(request.data)
    deck_id = req_data['deckId']
    #deck_id = request.get_json()['deckId']
    cur_deck = Deck.query.get(deck_id)
    cur_card = cur_deck.notes[0].flashcards[0]
    front = cur_card.front_text
    #back = cur_card.back_text
    #front = current_user.decks[0].notes[0].flashcards[0].front_text
    #return jsonify({front: front})
    return jsonify('', render_template('study_session.html', user=current_user, front=front))

@views.route('/stats')
def stats():
    return render_template("stats.html", user=current_user)