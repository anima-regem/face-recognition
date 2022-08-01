import recognizer

if __name__=='__main__':
    app = recognizer.create_app()
    app.run(debug=True, port=5001)
