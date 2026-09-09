# -*- coding: utf-8 -*-
"""
استيراد وتصدير بيانات الأساتذة من/إلى ملفات Excel
Import / export des données des enseignants depuis / vers Excel
"""

import pandas as pd
from models import Teacher

# ترتيب وأسماء الأعمدة في ملف Excel (يطابق الجدول المرسل)
# Ordre et noms des colonnes du fichier Excel (correspond au tableau fourni)
COLUMNS = [
    ("academic_rank", "الرتبة الأكاديمية"),
    ("serial_number", "الرقم التسلسلي"),
    ("full_name", "اللقب والإسم"),
    ("birth_date", "تاريخ الإزدياد"),
    ("marital_status", "الحالة العائلية"),
    ("children_count", "عدد الأبناء"),
    ("hire_rank_date", "تاريخ التعيين في رتبة التوظيف"),
    ("current_rank_date", "تاريخ التعيين في الرتبة الحالية"),
    ("appointment_decision_ref", "مرجع قرار التعيين"),
    ("financial_visa_number", "رقم تأشيرة المراقب المالي"),
    ("financial_visa_date", "تاريخ تأشيرة المراقب المالي"),
    ("grade", "الدرجة"),
    ("grade_effect_date", "تاريخ النفاذ"),
    ("faculty", "الكلية"),
    ("notes", "ملاحظات"),
    ("classement_score", "نقطة الترتيب"),
    ("classement_rank", "الرتبة"),
]

FIELD_TO_LABEL = dict(COLUMNS)
LABEL_TO_FIELD = {v: k for k, v in COLUMNS}


def export_teachers_to_excel(teachers, filepath):
    """يصدّر قائمة الأساتذة إلى ملف Excel / Exporte la liste vers un fichier Excel"""
    rows = []
    for t in teachers:
        d = t.to_dict()
        row = {FIELD_TO_LABEL[field]: d.get(field) for field, _ in COLUMNS}
        rows.append(row)

    df = pd.DataFrame(rows, columns=[label for _, label in COLUMNS])
    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="الأساتذة")
        worksheet = writer.sheets["الأساتذة"]
        # ضبط اتجاه الورقة من اليمين لليسار / Feuille orientée de droite à gauche
        worksheet.sheet_view.rightToLeft = True
        for i, col in enumerate(df.columns, start=1):
            max_len = max([len(str(col))] + [len(str(v)) for v in df[col].fillna("")])
            worksheet.column_dimensions[worksheet.cell(row=1, column=i).column_letter].width = min(max_len + 4, 40)

    return filepath


def import_teachers_from_excel(filepath):
    """
    يقرأ ملف Excel ويعيد قائمة القواميس الجاهزة للإدخال في قاعدة البيانات.
    Lit un fichier Excel et retourne une liste de dictionnaires prêts à insérer.
    Le fichier peut utiliser les libellés arabes (comme le modèle fourni)
    ou directement les noms techniques des champs.
    """
    df = pd.read_excel(filepath)
    df = df.rename(columns=lambda c: str(c).strip())

    records = []
    for _, row in df.iterrows():
        record = {}
        for col in df.columns:
            field = LABEL_TO_FIELD.get(col, col if col in FIELD_TO_LABEL else None)
            if field is None:
                continue
            value = row[col]
            if pd.isna(value):
                value = None
            elif field == "children_count":
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    value = None
            elif field in ("birth_date", "hire_rank_date", "current_rank_date",
                            "financial_visa_date", "grade_effect_date"):
                value = _format_date(value)
            record[field] = value

        if record.get("full_name"):
            records.append(record)

    return records


def _format_date(value):
    try:
        return pd.to_datetime(value).strftime("%Y-%m-%d")
    except Exception:
        return str(value) if value is not None else None


def generate_template_excel(filepath):
    """ينشئ نموذج Excel فارغ بنفس أعمدة الجدول الأصلي / Génère un modèle Excel vide"""
    df = pd.DataFrame(columns=[label for _, label in COLUMNS])
    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="الأساتذة")
        writer.sheets["الأساتذة"].sheet_view.rightToLeft = True
    return filepath
