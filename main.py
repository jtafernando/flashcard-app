from website import create_app

# export FLASK_APP=website
# export FLASK_ENV=development
# flask run

app = create_app()  # flask app object

if __name__ == '__main__':
    # Run app and start up server
    app.run(debug=True)  # debug=True lets method rerun app whenever change made to code
