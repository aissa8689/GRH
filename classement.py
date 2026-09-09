# -*- coding: utf-8 -*-
"""
منهجية حساب وترتيب الأساتذة / Méthode de calcul et classement des enseignants
--------------------------------------------------------------------------
هذا الملف مخصص لوضع المعادلة الحقيقية للترتيب التي سترسلها لاحقًا.
Ce fichier est l'endroit où intégrer la VRAIE méthode de classement
que vous fournirez prochainement.

طريقة الاستعمال / Utilisation:
- عدّل الدالة calculate_score(teacher) بالمعايير والنقاط الحقيقية.
- Modifiez uniquement la fonction calculate_score(teacher) ci-dessous.
- أعد تشغيل عملية "إعادة حساب الترتيب" من التطبيق بعد التعديل.
- Relancez ensuite "Recalculer le classement" depuis l'application.

الدالة الحالية هي مثال بسيط مؤقت (marché à blanc) قابل للاستبدال بالكامل.
"""

import json
from datetime import datetime


def _years_since(date_str):
    """يحسب عدد السنوات المنقضية منذ تاريخ معين بصيغة YYYY-MM-DD"""
    if not date_str:
        return 0
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            d = datetime.strptime(str(date_str).strip(), fmt)
            return round((datetime.utcnow() - d).days / 365.25, 2)
        except (ValueError, TypeError):
            continue
    return 0


def calculate_score(teacher):
    """
    يحسب نقطة الترتيب لأستاذ واحد.
    Calcule le score de classement d'un enseignant.

    ⚠️ هذه معادلة مؤقتة توضيحية فقط - استبدلها بالمنهجية الحقيقية.
    ⚠️ Ceci est une formule TEMPORAIRE d'exemple - à remplacer par la
       vraie méthode que vous fournirez.

    Renvoie (score, details_dict)
    """
    details = {}

    # مثال: الأقدمية في الرتبة الحالية (عدد السنوات) x 2 نقاط
    seniority_current_rank = _years_since(teacher.current_rank_date)
    details["seniority_current_rank_years"] = seniority_current_rank
    points_seniority = seniority_current_rank * 2

    # مثال: الأقدمية في التوظيف
    seniority_hire = _years_since(teacher.hire_rank_date)
    details["seniority_hire_years"] = seniority_hire
    points_hire = seniority_hire * 1

    total_score = round(points_seniority + points_hire, 2)
    details["points_seniority_current_rank"] = round(points_seniority, 2)
    details["points_hire"] = round(points_hire, 2)
    details["total_score"] = total_score
    details["note"] = (
        "صيغة مؤقتة - في انتظار المنهجية الرسمية / Formule temporaire, "
        "en attente de la méthode officielle."
    )

    return total_score, details


def recalculate_all(teachers):
    """
    يعيد حساب الترتيب لكل الأساتذة ويرتّبهم تنازليًا حسب النقطة.
    Recalcule le score de tous les enseignants et les classe par ordre décroissant.
    """
    scored = []
    for t in teachers:
        score, details = calculate_score(t)
        t.classement_score = score
        t.classement_details = json.dumps(details, ensure_ascii=False)
        scored.append(t)

    scored.sort(key=lambda x: (x.classement_score or 0), reverse=True)
    for idx, t in enumerate(scored, start=1):
        t.classement_rank = idx

    return scored
