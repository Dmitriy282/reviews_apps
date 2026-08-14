from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class LogEntry(db.Model):
    __tablename__ = 'log_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    planet_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    discovery_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<LogEntry {self.planet_name}>"
