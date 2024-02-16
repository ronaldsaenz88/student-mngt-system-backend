from app.main import app


if __name__ == "__main__":
    # Define default value for PORT variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=True)
