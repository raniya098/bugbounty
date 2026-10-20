from app.bootstrap import create_initialized_app

app = create_initialized_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
