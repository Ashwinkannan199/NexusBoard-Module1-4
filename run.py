from project import create_app, db, socketio # Import socketio

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # This creates all database tables 
        db.create_all()
    # app.run(debug=True) # <-- We can't use this anymore
    socketio.run(app, debug=True) # <-- Use this to run the app
    
