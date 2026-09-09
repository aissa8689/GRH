# -*- coding: utf-8 -*-
"""
قواعد الترقية في الدرجة (تغيير الدرجة/الإيقاع) حسب الرتبة الأكاديمية
Règles d'avancement d'échelon selon le grade académique
--------------------------------------------------------------------------
كل "إيقاع" (rythme) له مدة دنيا موحدة عبر كل الرتب:
Chaque "rythme" a une durée minimale, UNIFORME pour tous les grades :

    - الحد الأدنى / Minimum  : 2 ans et 6 mois (30 mois)
    - المتوسط / Moyen        : 3 ans          (36 mois)
    - الحد الأقصى / Maximum  : 3 ans et 6 mois (42 mois)

لكن كل رتبة لا تستفيد إلا من بعض هذه الإيقاعات:
Mais chaque grade ne bénéficie que de certains de ces rythmes :

    - الأستاذ (Professeur)   : الحد الأدنى فقط (تمر مباشرة)
                                 Minimum seulement (passage direct)
    - أستاذ محاضر أ (MCA)     : الحد الأدنى فقط (نفس الشيء)
                                 Minimum seulement (identique)
    - أستاذ محاضر ب (MCB)     : الحد الأدنى والمتوسط (عدد مناصب لكل واحد)
                                 Minimum et Moyen (quota de postes pour chacun)
    - أستاذ مساعد أ (MAA)     : الحد الأدنى والمتوسط والحد الأقصى
                                 Minimum, Moyen et Maximum
    - أستاذ مساعد ب (MAB)     : نفس الشيء (MAA)
                                 Identique au MAA

⚠️ يمكن تعديل هذه القيم بسهولة أدناه إذا تغيّرت المنهجية الرسمية.
⚠️ Ces valeurs sont facilement modifiables ci-dessous si la méthode
   officielle venait à changer.
"""

import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

# الرتب الأكاديمية بالترتيب / Grades académiques dans l'ordre
ACADEMIC_RANKS = ["Professeur", "MCA", "MCB", "MAA", "MAB"]

# مدة كل إيقاع بالأشهر — موحدة عبر كل الرتب
# Durée (en mois) de chaque rythme — uniforme pour tous les grades
RYTHME_DURATIONS_MONTHS = {
    "minimum": 30,  # 2 ans et 6 mois
    "moyen": 36,    # 3 ans
    "maximum": 42,  # 3 ans et 6 mois
}

# الإيقاعات المتاحة لكل رتبة، من الأسرع إلى الأبطأ
# Rythmes disponibles par grade, du plus rapide au plus lent
RANK_RYTHMES = {
    "Professeur": ["minimum"],
    "MCA": ["minimum"],
    "MCB": ["minimum", "moyen"],
    "MAA": ["minimum", "moyen", "maximum"],
    "MAB": ["minimum", "moyen", "maximum"],
}

RYTHME_LABELS = {
    "minimum": {"fr": "Minimum", "ar": "الحد الأدنى"},
    "moyen": {"fr": "Moyen", "ar": "المتوسط"},
    "maximum": {"fr": "Maximum", "ar": "الحد الأقصى"},
}


def duration_label(months):
    if months is None:
        return "-"
    years = months // 12
    rem = months % 12
    if rem == 0:
        return f"{years} ans"
    if rem == 6:
        return f"{years} ans et 6 mois"
    return f"{years} ans et {rem} mois"


def get_rythmes(academic_rank):
    """الإيقاعات المتاحة لرتبة معينة، من الأسرع إلى الأبطأ"""
    return RANK_RYTHMES.get(academic_rank, [])


def get_duration_months(rythme):
    """مدة إيقاع معين بالأشهر (موحدة عبر كل الرتب)"""
    return RYTHME_DURATIONS_MONTHS.get(rythme)


def get_slowest_rythme(academic_rank):
    rythmes = get_rythmes(academic_rank)
    return rythmes[-1] if rythmes else None


def parse_date(date_str):
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(str(date_str).strip(), fmt)
        except (ValueError, TypeError):
            continue
    return None


def calculate_date_for_rythme(teacher, rythme):
    """
    يحسب تاريخ الاستحقاق لإيقاع معين، انطلاقًا من "تاريخ النفاذ" الحالي.
    Calcule la date d'éligibilité pour un rythme donné, à partir de la
    dernière "تاريخ النفاذ" (date d'effet).
    """
    base_date = parse_date(teacher.grade_effect_date) or parse_date(teacher.current_rank_date)
    months = get_duration_months(rythme)
    if not base_date or months is None:
        return None
    return base_date + relativedelta(months=months)


def calculate_all_rythme_dates(teacher):
    """يرجع {rythme: تاريخ} لكل الإيقاعات المتاحة لرتبة هذا الأستاذ"""
    rythmes = get_rythmes(teacher.academic_rank)
    return {r: calculate_date_for_rythme(teacher, r) for r in rythmes}


def calculate_guaranteed_next_date(teacher):
    """
    تاريخ الترقية المضمون (أبطأ إيقاع متاح لرتبته)، بصرف النظر عن الترتيب
    أو الحصص. Date de promotion garantie (rythme le plus lent disponible
    pour son grade), indépendamment du classement ou des quotas.
    """
    rythme = get_slowest_rythme(teacher.academic_rank)
    if not rythme:
        return None
    return calculate_date_for_rythme(teacher, rythme)


def is_eligible_for_rythme(teacher, rythme, session_date):
    d = calculate_date_for_rythme(teacher, rythme)
    if not d or not session_date:
        return False
    return d <= session_date


def compute_eligible_pools_by_rythme(teachers, academic_rank, session_date):
    """
    يُرجع، لكل إيقاع متاح لهذه الرتبة، قائمة كل الأساتذة الذين بلغوا مدته
    الدنيا (مرتبين تنازليًا حسب النقطة). ⚠️ القوائم متداخلة عمدًا: من بلغ
    مدة "المتوسط" يظهر بالضرورة أيضًا في قائمة "الحد الأدنى" (لأن مدته
    أطول). هذا طبيعي: يُستعمل عند التنفيذ الفعلي لاستبعاد من تمت ترقيته
    فعليًا (حسب الحصة) من القوائم الأبطأ، وليس فقط من بلغ العتبة.

    Renvoie, pour chaque rythme disponible pour ce grade, la liste de
    TOUS les enseignants ayant atteint sa durée minimale (triés par score
    décroissant). ⚠️ Les listes se chevauchent volontairement : qui a
    atteint la durée "moyen" apparaît forcément aussi dans "minimum" (car
    sa durée est plus longue). C'est normal : à l'exécution réelle, on
    exclut ceux effectivement promus (selon le quota) des rythmes plus
    lents, pas seulement ceux ayant atteint le seuil.

    Renvoie {rythme: [enseignants]}
    """
    rythmes = get_rythmes(academic_rank)
    result = {}
    for rythme in rythmes:
        elig = [t for t in teachers if is_eligible_for_rythme(t, rythme, session_date)]
        elig.sort(key=lambda t: (t.classement_score or 0), reverse=True)
        result[rythme] = elig
    return result


def next_grade_label(current_grade):
    """
    يحاول زيادة رقم الدرجة تلقائيًا (مثال: '5' -> '6'، '5ème échelon' -> '6ème échelon').
    Incrémente automatiquement le numéro d'échelon si un nombre est détecté.
    """
    if not current_grade:
        return current_grade
    match = re.search(r"\d+", str(current_grade))
    if not match:
        return current_grade
    number = int(match.group())
    return current_grade[:match.start()] + str(number + 1) + current_grade[match.end():]
