from app import create_app

app = create_app()

if __name__ == '__main__':
    # This block is for local development without Docker/Gunicorn
    app.run(host='0.0.0.0', port=5000, debug=True)
