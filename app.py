# -*- coding: utf-8 -*-
import os
import uuid
from datetime import datetime

from flask import (Flask, render_template, request, redirect, url_for,
                    flash, send_file, session, jsonify)
from werkzeug.utils import secure_filename
from flask_login import (LoginManager, login_user, logout_user,
                          login_required, current_user)

from models import (db, Teacher, User, ACADEMIC_RANKS as MODEL_RANKS,
                     EchelonHistory, PromotionSession, PromotionQuota)
from classement import recalculate_all
from excel_io import (export_teachers_to_excel, import_teachers_from_excel,
                       generate_template_excel)
from promotion import (ACADEMIC_RANKS, RANK_RYTHMES, RYTHME_LABELS,
                        RYTHME_DURATIONS_MONTHS, duration_label,
                        calculate_guaranteed_next_date, calculate_all_rythme_dates,
                        calculate_date_for_rythme, compute_eligible_pools_by_rythme,
                        next_grade_label, parse_date)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# مجلد البيانات (يمكن توجيهه إلى قرص دائم على Render عبر متغير البيئة DATA_DIR)
# Dossier de données (peut pointer vers un disque persistant Render via DATA_DIR)
DATA_DIR = os.environ.get("DATA_DIR", BASE_DIR)
UPLOAD_FOLDER = os.path.join(DATA_DIR, "static", "uploads")
EXPORT_FOLDER = os.path.join(DATA_DIR, "static", "exports")
ALLOWED_IMAGE_EXT = {"png", "jpg", "jpeg", "gif", "webp"}
ALLOWED_EXCEL_EXT = {"xlsx", "xls"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXPORT_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret-key")

# قاعدة البيانات: SQLite افتراضيًا (يمكن استبدالها بـ PostgreSQL عبر DATABASE_URL على Render)
# Base de données : SQLite par défaut (remplaçable par PostgreSQL via DATABASE_URL sur Render)
_database_url = os.environ.get("DATABASE_URL")
if _database_url:
    # Render/Heroku fournissent souvent "postgres://", SQLAlchemy exige "postgresql://"
    if _database_url.startswith("postgres://"):
        _database_url = _database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = _database_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(DATA_DIR, "teachers.db")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 Mo

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "⚠ Veuillez vous connecter / يرجى تسجيل الدخول"
login_manager.login_message_category = "danger"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

TRANSLATIONS = {
    "fr": {
        "app_title": "Gestion des Enseignants",
        "list": "Liste des enseignants",
        "add": "Ajouter un enseignant",
        "edit": "Modifier",
        "delete": "Supprimer",
        "view": "Voir",
        "import_excel": "Importer Excel",
        "export_excel": "Exporter Excel",
        "download_template": "Télécharger le modèle Excel",
        "classement": "Classement",
        "recalculate": "Recalculer le classement",
        "serial_number": "N°",
        "full_name": "Nom et prénom",
        "birth_date": "Date de naissance",
        "marital_status": "Situation familiale",
        "children_count": "Nombre d'enfants",
        "hire_rank_date": "Date de nomination (recrutement)",
        "current_rank_date": "Date de nomination (grade actuel)",
        "appointment_decision_ref": "Référence décision de nomination",
        "financial_visa_number": "N° visa contrôleur financier",
        "financial_visa_date": "Date du visa",
        "grade": "Grade / Échelon",
        "grade_effect_date": "Date d'effet",
        "faculty": "Faculté",
        "notes": "Remarques",
        "photo": "Photo",
        "score": "Score",
        "rank": "Rang",
        "actions": "Actions",
        "save": "Enregistrer",
        "cancel": "Annuler",
        "search": "Rechercher...",
        "confirm_delete": "Confirmer la suppression ?",
        "no_data": "Aucun enseignant enregistré.",
        "lang_switch": "العربية",
        "academic_rank": "Grade académique",
        "sessions": "Sessions de promotion",
        "login": "Connexion",
        "logout": "Déconnexion",
        "username": "Identifiant",
        "password": "Mot de passe",
        "login_title": "Gestion des Enseignants",
        "login_subtitle": "Connectez-vous pour accéder à l'espace de gestion",
        "history": "Historique",
        "next_effect_date": "Prochaine date d'effet",
        "eligible": "Éligible",
        "not_eligible": "Non éligible",
        "unranked": "Sans grade académique",
    },
    "ar": {
        "app_title": "تسيير الأساتذة",
        "list": "قائمة الأساتذة",
        "add": "إضافة أستاذ",
        "edit": "تعديل",
        "delete": "حذف",
        "view": "عرض",
        "import_excel": "استيراد Excel",
        "export_excel": "تصدير Excel",
        "download_template": "تحميل نموذج Excel",
        "classement": "الترتيب",
        "recalculate": "إعادة حساب الترتيب",
        "serial_number": "الرقم التسلسلي",
        "full_name": "اللقب والإسم",
        "birth_date": "تاريخ الإزدياد",
        "marital_status": "الحالة العائلية",
        "children_count": "عدد الأبناء",
        "hire_rank_date": "تاريخ التعيين في رتبة التوظيف",
        "current_rank_date": "تاريخ التعيين في الرتبة الحالية",
        "appointment_decision_ref": "مرجع قرار التعيين",
        "financial_visa_number": "رقم تأشيرة المراقب المالي",
        "financial_visa_date": "تاريخ تأشيرة المراقب المالي",
        "grade": "الدرجة",
        "grade_effect_date": "تاريخ النفاذ",
        "faculty": "الكلية",
        "notes": "ملاحظات",
        "photo": "الصورة",
        "score": "النقطة",
        "rank": "الرتبة",
        "actions": "إجراءات",
        "save": "حفظ",
        "cancel": "إلغاء",
        "search": "بحث...",
        "confirm_delete": "تأكيد الحذف؟",
        "no_data": "لا يوجد أساتذة مسجلون.",
        "lang_switch": "Français",
        "academic_rank": "الرتبة الأكاديمية",
        "sessions": "جلسات الترقية",
        "login": "تسجيل الدخول",
        "logout": "تسجيل الخروج",
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "login_title": "تسيير الأساتذة",
        "login_subtitle": "سجّل الدخول للوصول إلى فضاء التسيير",
        "history": "السجل التاريخي",
        "next_effect_date": "تاريخ النفاذ القادم",
        "eligible": "مستحق",
        "not_eligible": "غير مستحق",
        "unranked": "بدون رتبة أكاديمية",
    },
}


def get_lang():
    return session.get("lang", "fr")


@app.context_processor
def inject_globals():
    lang = get_lang()
    return {
        "t": TRANSLATIONS[lang],
        "lang": lang,
        "dir": "rtl" if lang == "ar" else "ltr",
    }


@app.route("/set_lang/<lang_code>")
def set_lang(lang_code):
    if lang_code in TRANSLATIONS:
        session["lang"] = lang_code
    return redirect(request.referrer or url_for("index"))


def allowed_file(filename, allowed_set):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_set


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))
        flash("⚠ Identifiants incorrects / بيانات الدخول غير صحيحة", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    query = request.args.get("q", "").strip()
    q = Teacher.query
    if query:
        like = f"%{query}%"
        q = q.filter(
            db.or_(
                Teacher.full_name.ilike(like),
                Teacher.faculty.ilike(like),
                Teacher.grade.ilike(like),
            )
        )
    teachers = q.order_by(Teacher.serial_number.asc().nulls_last()
                           if db.engine.name != "sqlite" else Teacher.id.asc()).all()
    return render_template("index.html", teachers=teachers, query=query)


@app.route("/teacher/<int:teacher_id>")
@login_required
def view_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    rythme_dates = calculate_all_rythme_dates(teacher)
    guaranteed_date = calculate_guaranteed_next_date(teacher)
    return render_template(
        "view.html", teacher=teacher, rythme_dates=rythme_dates,
        guaranteed_date=guaranteed_date, rythme_labels=RYTHME_LABELS,
        durations=RYTHME_DURATIONS_MONTHS, duration_label=duration_label,
    )


@app.route("/teacher/add", methods=["GET", "POST"])
@login_required
def add_teacher():
    if request.method == "POST":
        teacher = Teacher()
        _fill_teacher_from_form(teacher, request.form)
        _handle_photo_upload(teacher, request.files.get("photo"))
        db.session.add(teacher)
        db.session.commit()
        flash("✔ " + TRANSLATIONS[get_lang()]["save"], "success")
        return redirect(url_for("index"))
    return render_template("form.html", teacher=None)


@app.route("/teacher/<int:teacher_id>/edit", methods=["GET", "POST"])
@login_required
def edit_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    if request.method == "POST":
        _fill_teacher_from_form(teacher, request.form)
        _handle_photo_upload(teacher, request.files.get("photo"))
        db.session.commit()
        flash("✔ " + TRANSLATIONS[get_lang()]["save"], "success")
        return redirect(url_for("index"))
    return render_template("form.html", teacher=teacher)


@app.route("/teacher/<int:teacher_id>/delete", methods=["POST"])
@login_required
def delete_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    db.session.delete(teacher)
    db.session.commit()
    flash("✔ " + TRANSLATIONS[get_lang()]["delete"], "success")
    return redirect(url_for("index"))


def _fill_teacher_from_form(teacher, form):
    teacher.academic_rank = form.get("academic_rank") or None
    teacher.serial_number = _to_int(form.get("serial_number"))
    teacher.full_name = form.get("full_name", "").strip()
    teacher.birth_date = form.get("birth_date") or None
    teacher.marital_status = form.get("marital_status") or None
    teacher.children_count = _to_int(form.get("children_count")) or 0
    teacher.hire_rank_date = form.get("hire_rank_date") or None
    teacher.current_rank_date = form.get("current_rank_date") or None
    teacher.appointment_decision_ref = form.get("appointment_decision_ref") or None
    teacher.financial_visa_number = form.get("financial_visa_number") or None
    teacher.financial_visa_date = form.get("financial_visa_date") or None
    teacher.grade = form.get("grade") or None
    teacher.grade_effect_date = form.get("grade_effect_date") or None
    teacher.faculty = form.get("faculty") or None
    teacher.notes = form.get("notes") or None


def _to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _handle_photo_upload(teacher, file_storage):
    if file_storage and file_storage.filename and allowed_file(file_storage.filename, ALLOWED_IMAGE_EXT):
        ext = file_storage.filename.rsplit(".", 1)[1].lower()
        filename = secure_filename(f"{uuid.uuid4().hex}.{ext}")
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file_storage.save(filepath)
        teacher.photo = filename


# ---------------------- Excel import / export ----------------------

@app.route("/excel/export")
@login_required
def excel_export():
    teachers = Teacher.query.all()
    filename = f"enseignants_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filepath = os.path.join(EXPORT_FOLDER, filename)
    export_teachers_to_excel(teachers, filepath)
    return send_file(filepath, as_attachment=True, download_name=filename)


@app.route("/excel/template")
@login_required
def excel_template():
    filepath = os.path.join(EXPORT_FOLDER, "modele_enseignants.xlsx")
    generate_template_excel(filepath)
    return send_file(filepath, as_attachment=True, download_name="modele_enseignants.xlsx")


@app.route("/excel/import", methods=["GET", "POST"])
@login_required
def excel_import():
    if request.method == "POST":
        file = request.files.get("excel_file")
        if not file or not allowed_file(file.filename, ALLOWED_EXCEL_EXT):
            flash("⚠ Fichier invalide / ملف غير صالح", "danger")
            return redirect(url_for("excel_import"))

        temp_path = os.path.join(EXPORT_FOLDER, secure_filename(file.filename))
        file.save(temp_path)

        try:
            records = import_teachers_from_excel(temp_path)
        except Exception as e:
            flash(f"⚠ Erreur de lecture: {e}", "danger")
            return redirect(url_for("excel_import"))
        finally:
            os.remove(temp_path)

        created, updated = 0, 0
        for rec in records:
            existing = None
            if rec.get("serial_number"):
                existing = Teacher.query.filter_by(serial_number=rec["serial_number"]).first()
            if not existing:
                existing = Teacher.query.filter_by(full_name=rec.get("full_name")).first()

            if existing:
                for k, v in rec.items():
                    if k in ("classement_score", "classement_rank"):
                        continue
                    setattr(existing, k, v)
                updated += 1
            else:
                rec.pop("classement_score", None)
                rec.pop("classement_rank", None)
                db.session.add(Teacher(**rec))
                created += 1

        db.session.commit()
        flash(f"✔ Importé: {created} ajouté(s), {updated} mis à jour",
              "success")
        return redirect(url_for("index"))

    return render_template("import.html")


# ---------------------- Classement ----------------------

@app.route("/classement")
@login_required
def classement_view():
    order_col = (Teacher.classement_rank.asc().nulls_last()
                 if db.engine.name != "sqlite" else Teacher.id.asc())
    groups = {}
    for rank in ACADEMIC_RANKS:
        teachers = Teacher.query.filter_by(academic_rank=rank).order_by(order_col).all()
        groups[rank] = teachers
    unranked = Teacher.query.filter(
        db.or_(Teacher.academic_rank.is_(None), Teacher.academic_rank == "")
    ).order_by(order_col).all()
    return render_template(
        "classement.html", groups=groups, ranks=ACADEMIC_RANKS,
        unranked=unranked, duration_label=duration_label,
        rank_rythmes=RANK_RYTHMES, durations=RYTHME_DURATIONS_MONTHS,
    )


@app.route("/classement/recalculate", methods=["POST"])
@login_required
def classement_recalculate():
    teachers = Teacher.query.all()
    recalculate_all(teachers)
    db.session.commit()
    flash("✔ " + TRANSLATIONS[get_lang()]["recalculate"], "success")
    return redirect(url_for("classement_view"))


@app.route("/api/teachers")
@login_required
def api_teachers():
    teachers = Teacher.query.all()
    return jsonify([t.to_dict() for t in teachers])


# ---------------------- Sessions de promotion (avancement d'échelon) ----------------------

@app.route("/sessions")
@login_required
def sessions_list():
    sessions = PromotionSession.query.order_by(PromotionSession.session_date.desc()).all()
    return render_template("sessions.html", sessions=sessions)


@app.route("/sessions/create", methods=["POST"])
@login_required
def sessions_create():
    year = request.form.get("year", "").strip()
    if not year.isdigit() or len(year) != 4:
        flash("⚠ Année invalide / سنة غير صالحة", "danger")
        return redirect(url_for("sessions_list"))

    session_date_str = f"{year}-12-31"
    if PromotionSession.query.filter_by(session_date=session_date_str).first():
        flash("⚠ Cette session existe déjà / هذه الجلسة موجودة مسبقًا", "danger")
        return redirect(url_for("sessions_list"))

    new_session = PromotionSession(session_date=session_date_str)
    db.session.add(new_session)
    db.session.commit()

    for rank, rythmes in RANK_RYTHMES.items():
        for r in rythmes:
            db.session.add(PromotionQuota(
                session_id=new_session.id, academic_rank=rank,
                rythme=r, quota_count=0,
            ))
    db.session.commit()

    flash("✔ Session créée / تم إنشاء الجلسة", "success")
    return redirect(url_for("session_detail", session_id=new_session.id))


@app.route("/sessions/<int:session_id>")
@login_required
def session_detail(session_id):
    promo_session = PromotionSession.query.get_or_404(session_id)
    session_date_dt = parse_date(promo_session.session_date)

    # groups[rank] = {rythme: [enseignants éligibles, triés par score]} — pools imbriqués
    groups = {}
    for rank in ACADEMIC_RANKS:
        teachers = Teacher.query.filter_by(academic_rank=rank).all()
        groups[rank] = compute_eligible_pools_by_rythme(teachers, rank, session_date_dt)

    quotas = {(q.academic_rank, q.rythme): q for q in promo_session.quotas}

    return render_template(
        "session_detail.html", promo_session=promo_session, groups=groups,
        quotas=quotas, rythmes=RANK_RYTHMES, rythme_labels=RYTHME_LABELS,
        durations=RYTHME_DURATIONS_MONTHS, duration_label=duration_label,
    )


@app.route("/sessions/<int:session_id>/quota", methods=["POST"])
@login_required
def session_update_quota(session_id):
    promo_session = PromotionSession.query.get_or_404(session_id)
    for q in promo_session.quotas:
        val = request.form.get(f"quota_{q.id}")
        if val is not None and val.strip().isdigit():
            q.quota_count = int(val)
    db.session.commit()
    flash("✔ Quotas mis à jour / تم تحديث الحصص", "success")
    return redirect(url_for("session_detail", session_id=session_id))


@app.route("/sessions/<int:session_id>/run", methods=["POST"])
@login_required
def session_run(session_id):
    promo_session = PromotionSession.query.get_or_404(session_id)
    if promo_session.executed:
        flash("⚠ Cette session a déjà été exécutée / تم تنفيذ هذه الجلسة مسبقًا", "danger")
        return redirect(url_for("session_detail", session_id=session_id))

    session_date_dt = parse_date(promo_session.session_date)
    quotas = {(q.academic_rank, q.rythme): q.quota_count for q in promo_session.quotas}
    promoted_count = 0

    for rank in ACADEMIC_RANKS:
        teachers = Teacher.query.filter_by(academic_rank=rank).all()
        # مجمعات متداخلة حسب العتبة (من بلغ "المتوسط" موجود أيضًا في "الحد الأدنى")
        # Pools imbriqués par seuil (qui atteint "moyen" est aussi dans "minimum")
        pools = compute_eligible_pools_by_rythme(teachers, rank, session_date_dt)
        already_promoted_ids = set()

        for rythme in RANK_RYTHMES.get(rank, []):
            # نستبعد من تمت ترقيتهم فعليًا في إيقاع أسرع خلال هذه الجلسة
            # On exclut ceux déjà réellement promus à un rythme plus rapide
            eligible = [t for t in pools.get(rythme, []) if t.id not in already_promoted_ids]

            quota = quotas.get((rank, rythme), 0)
            # عدد الحصة = 0 يعني بدون حد أقصى (يستفيد الجميع) / quota=0 -> illimité
            take = len(eligible) if quota <= 0 else min(quota, len(eligible))
            batch = eligible[:take]

            for t in batch:
                new_date = calculate_date_for_rythme(t, rythme)
                new_date_str = new_date.strftime("%Y-%m-%d") if new_date else t.grade_effect_date
                db.session.add(EchelonHistory(
                    teacher_id=t.id,
                    academic_rank=t.academic_rank,
                    old_grade=t.grade,
                    old_effect_date=t.grade_effect_date,
                    new_grade=next_grade_label(t.grade),
                    new_effect_date=new_date_str,
                    rythme=rythme,
                    session_date=promo_session.session_date,
                ))
                t.grade = next_grade_label(t.grade)
                t.grade_effect_date = new_date_str
                already_promoted_ids.add(t.id)
                promoted_count += 1

    promo_session.executed = True
    promo_session.executed_at = datetime.utcnow()
    db.session.commit()
    flash(f"✔ Session exécutée : {promoted_count} avancement(s) d'échelon / "
          f"تم تنفيذ الجلسة: {promoted_count} ترقية", "success")
    return redirect(url_for("session_detail", session_id=session_id))


with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        default_admin = User(username="admin", full_name="Administrateur", role="admin")
        # يمكن تغيير كلمة المرور الافتراضية عبر متغير البيئة ADMIN_PASSWORD
        # Le mot de passe par défaut peut être changé via la variable d'environnement ADMIN_PASSWORD
        default_admin.set_password(os.environ.get("ADMIN_PASSWORD", "admin123"))
        db.session.add(default_admin)
        db.session.commit()


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "1") == "1"
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=debug_mode, host="0.0.0.0", port=port)
