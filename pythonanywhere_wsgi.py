# -*- coding: utf-8 -*-
"""
ملف تهيئة WSGI لاستضافة PythonAnywhere
Fichier de configuration WSGI pour l'hébergement PythonAnywhere
--------------------------------------------------------------------------
⚠️ لا يُستعمل هذا الملف مباشرة. انسخ محتواه داخل ملف WSGI الخاص بحسابك على
PythonAnywhere (يوجد في تبويب "Web" → "WSGI configuration file"،
وعادة بالمسار /var/www/<username>_pythonanywhere_com_wsgi.py).

⚠️ Ce fichier n'est pas exécuté directement. Copiez son contenu dans le
fichier WSGI de votre compte PythonAnywhere (onglet "Web" →
"WSGI configuration file", généralement situé à
/var/www/<username>_pythonanywhere_com_wsgi.py).

راجع PYTHONANYWHERE.md لخطوات النشر الكاملة خطوة بخطوة.
Voir PYTHONANYWHERE.md pour les étapes complètes de déploiement.
"""

import sys
import os

# 📌 غيّر "yourusername" باسم مستخدمك على PythonAnywhere
# 📌 Remplacez "yourusername" par votre nom d'utilisateur PythonAnywhere
project_home = '/home/yourusername/teacher_app'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# 📌 متغيرات البيئة (عدّل القيم قبل النشر) / Variables d'environnement (à adapter avant le déploiement)
os.environ['SECRET_KEY'] = 'change-this-to-a-long-random-string'
os.environ['ADMIN_PASSWORD'] = 'change-this-password'
os.environ['FLASK_DEBUG'] = '0'
# البيانات (قاعدة البيانات + الصور) تبقى داخل مجلد المشروع نفسه على القرص
# الدائم لـ PythonAnywhere — لا حاجة لـ DATA_DIR هنا.
# Les données (base + photos) restent dans le dossier du projet, sur le
# disque persistant de PythonAnywhere — pas besoin de DATA_DIR ici.

from app import app as application  # noqa
