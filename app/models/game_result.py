from app.gamesDB import db
from datetime import datetime

class GameResult(db.Model):
    __tablename__ = "game_results"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    game_name = db.Column(db.String(50), nullable=False)
    level = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    time_spent = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    rounds = db.Column(db.Integer, nullable=False, default=1)

    user = db.relationship("User", backref="results")