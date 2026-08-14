import os
import redis
from flask import Flask, render_template, request, redirect, url_for
from models import db, LogEntry

app = Flask(__name__)

# Config for PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/space_logbook')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Config for Redis
redis_host = os.environ.get('REDIS_HOST', 'redis')
redis_port = int(os.environ.get('REDIS_PORT', 6379))
cache = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

# Try to initialize DB
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Warning: Database connection failed. Is PostgreSQL running? Error: {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        planet_name = request.form.get('planet_name')
        description = request.form.get('description')
        if planet_name and description:
            try:
                entry = LogEntry(planet_name=planet_name, description=description)
                db.session.add(entry)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error saving to DB: {e}")
            return redirect(url_for('index'))

    # Fetch entries from PostgreSQL
    entries = []
    try:
        entries = LogEntry.query.order_by(LogEntry.discovery_date.desc()).all()
    except Exception as e:
        print(f"Error fetching from DB: {e}")

    # Increment and get jump count from Redis
    jump_count = 0
    try:
        jump_count = cache.incr('warp_jumps')
    except Exception as e:
        print(f"Warning: Redis connection failed. Error: {e}")

    return render_template('index.html', entries=entries, jump_count=jump_count)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
