from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# الرتب الأكاديمية المتاحة / Grades académiques disponibles
ACADEMIC_RANKS = ["Professeur", "MCA", "MCB", "MAA", "MAB"]


class User(UserMixin, db.Model):
    """مستخدم لتسجيل الدخول / Utilisateur pour la connexion"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150), nullable=True)
    role = db.Column(db.String(20), default="admin")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Teacher(db.Model):
    """Modèle Enseignant / نموذج الأستاذ"""
    __tablename__ = "teachers"

    id = db.Column(db.Integer, primary_key=True)

    # الرتبة الأكاديمية / Grade académique (Professeur, MCA, MCB, MAA, MAB)
    academic_rank = db.Column(db.String(50), nullable=True)

    # الرقم التسلسلي / Numéro d'ordre
    serial_number = db.Column(db.Integer, nullable=True)

    # اللقب والاسم / Nom et prénom
    full_name = db.Column(db.String(200), nullable=False)

    # تاريخ الازدياد / Date de naissance
    birth_date = db.Column(db.String(20), nullable=True)

    # الحالة العائلية / Situation familiale
    marital_status = db.Column(db.String(50), nullable=True)

    # عدد الأبناء / Nombre d'enfants
    children_count = db.Column(db.Integer, nullable=True, default=0)

    # تاريخ التعيين في رتبة التوظيف / Date de nomination au grade de recrutement
    hire_rank_date = db.Column(db.String(20), nullable=True)

    # تاريخ التعيين في الرتبة الحالية / Date de nomination au grade actuel
    current_rank_date = db.Column(db.String(20), nullable=True)

    # مرجع قرار التعيين / Référence de la décision de nomination
    appointment_decision_ref = db.Column(db.String(200), nullable=True)

    # رقم تأشيرة المراقب المالي / Numéro visa du contrôleur financier
    financial_visa_number = db.Column(db.String(100), nullable=True)
    # تاريخ تأشيرة المراقب المالي / Date du visa
    financial_visa_date = db.Column(db.String(20), nullable=True)

    # الدرجة / Échelon (grade)
    grade = db.Column(db.String(100), nullable=True)
    # تاريخ النفاذ / Date d'effet
    grade_effect_date = db.Column(db.String(20), nullable=True)

    # الكلية / Faculté
    faculty = db.Column(db.String(200), nullable=True)

    # ملاحظات / Remarques
    notes = db.Column(db.Text, nullable=True)

    # صورة / Photo (chemin du fichier)
    photo = db.Column(db.String(300), nullable=True)

    # نقطة الترتيب المحسوبة (تُحسب لاحقًا حسب المنهجية) / Score de classement calculé
    classement_score = db.Column(db.Float, nullable=True)
    classement_rank = db.Column(db.Integer, nullable=True)
    classement_details = db.Column(db.Text, nullable=True)  # JSON détail du calcul

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    history = db.relationship(
        "EchelonHistory", backref="teacher",
        cascade="all, delete-orphan", order_by="EchelonHistory.id.desc()"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "academic_rank": self.academic_rank,
            "serial_number": self.serial_number,
            "full_name": self.full_name,
            "birth_date": self.birth_date,
            "marital_status": self.marital_status,
            "children_count": self.children_count,
            "hire_rank_date": self.hire_rank_date,
            "current_rank_date": self.current_rank_date,
            "appointment_decision_ref": self.appointment_decision_ref,
            "financial_visa_number": self.financial_visa_number,
            "financial_visa_date": self.financial_visa_date,
            "grade": self.grade,
            "grade_effect_date": self.grade_effect_date,
            "faculty": self.faculty,
            "notes": self.notes,
            "photo": self.photo,
            "classement_score": self.classement_score,
            "classement_rank": self.classement_rank,
        }


class EchelonHistory(db.Model):
    """
    سجل تاريخي لكل تغيير في الدرجة (تُحفظ كل ترقية أو تعديل يدوي)
    Historique de chaque changement d'échelon (chaque avancement ou modification manuelle)
    """
    __tablename__ = "echelon_history"

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teachers.id"), nullable=False)

    academic_rank = db.Column(db.String(50), nullable=True)
    old_grade = db.Column(db.String(100), nullable=True)
    old_effect_date = db.Column(db.String(20), nullable=True)
    new_grade = db.Column(db.String(100), nullable=True)
    new_effect_date = db.Column(db.String(20), nullable=True)

    # نوع الإيقاع: minimum / moyen / maximum / unique
    rythme = db.Column(db.String(20), nullable=True)

    # تاريخ الجلسة (31/12/XXXX) / Date de la session (31/12/XXXX)
    session_date = db.Column(db.String(20), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PromotionSession(db.Model):
    """
    جلسة ترقية سنوية (31 ديسمبر من كل سنة)
    Session annuelle d'avancement (31 décembre de chaque année)
    """
    __tablename__ = "promotion_sessions"

    id = db.Column(db.Integer, primary_key=True)
    session_date = db.Column(db.String(20), unique=True, nullable=False)  # ex: 2026-12-31
    executed = db.Column(db.Boolean, default=False)
    executed_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    quotas = db.relationship(
        "PromotionQuota", backref="session", cascade="all, delete-orphan"
    )


class PromotionQuota(db.Model):
    """
    عدد المناصب المتاحة لكل رتبة ونوع إيقاع في جلسة معينة
    Nombre de postes disponibles par grade et par rythme pour une session donnée
    """
    __tablename__ = "promotion_quotas"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("promotion_sessions.id"), nullable=False)
    academic_rank = db.Column(db.String(50), nullable=False)
    rythme = db.Column(db.String(20), nullable=False)
    quota_count = db.Column(db.Integer, nullable=False, default=0)
