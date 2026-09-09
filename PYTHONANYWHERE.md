# 🚀 النشر على PythonAnywhere (مجاني، لا ينام أبدًا)
# Déploiement sur PythonAnywhere (gratuit, ne dort jamais)

⚠️ لا يوجد استضافة "مجانية وغير محدودة" حقًا — كل الاستضافات المجانية لها
حدود. PythonAnywhere مناسب هنا لأنه **لا يتوقف بسبب عدم النشاط** (على عكس
Render المجاني)، لكن حسابك المجاني يحتاج **تجديدًا يدويًا كل شهر** (نقرة
واحدة، أقل من دقيقة) وإلا يتوقف الموقع.

⚠️ Il n'existe pas d'hébergement vraiment « gratuit et illimité » — tous
les plans gratuits ont des limites. PythonAnywhere convient bien ici car
il **ne s'arrête pas par inactivité** (contrairement au plan gratuit de
Render), mais votre compte gratuit nécessite un **renouvellement manuel
chaque mois** (un clic, moins d'une minute), sinon le site s'arrête.

**الحدود / Limites du plan gratuit :** 512 Mo de stockage, CPU très
limité, 1 application web, expire après 1 mois sans renouvellement,
accès réseau sortant limité à une liste blanche (sans impact ici,
l'application ne contacte aucun service externe).

---

## 📋 خطوات النشر / Étapes de déploiement

### 1. إنشاء حساب / Créer un compte
اذهب إلى **https://www.pythonanywhere.com** → **Pricing & signup** →
اختر **Beginner (Free)**.
Allez sur **https://www.pythonanywhere.com** → **Pricing & signup** →
choisissez **Beginner (Free)**.

### 2. رفع المشروع / Envoyer le projet
في تبويب **Files**، ارفع ملف `LE PROJET.zip` (أو استعمل **Bash console**
لاستنساخه من GitHub إن كان هناك مستودع).
Dans l'onglet **Files**, uploadez `LE PROJET.zip` (ou utilisez une
**Bash console** pour cloner depuis GitHub si vous avez un dépôt).

ثم في **Bash console**:
Puis dans une **Bash console** :
```bash
unzip "LE PROJET.zip" -d ~/
cd ~/teacher_app
```

### 3. إنشاء بيئة افتراضية وتثبيت المكتبات / Créer un environnement virtuel et installer les dépendances
```bash
mkvirtualenv --python=/usr/bin/python3.10 teacher_env
pip install -r requirements.txt
```
(لا حاجة لتثبيت `gunicorn` أو `psycopg2-binary` هنا؛ PythonAnywhere يستعمل
WSGI الخاص به. Pas besoin d'installer `gunicorn` ni `psycopg2-binary` ici ;
PythonAnywhere utilise son propre système WSGI.)

### 4. إنشاء تطبيق ويب / Créer une application web
في تبويب **Web** → **Add a new web app** → اختر **Manual configuration**
→ **Python 3.10**.
Dans l'onglet **Web** → **Add a new web app** → choisissez
**Manual configuration** → **Python 3.10**.

- **Source code**: `/home/yourusername/teacher_app`
- **Working directory**: `/home/yourusername/teacher_app`
- **Virtualenv**: `/home/yourusername/.virtualenvs/teacher_env`

### 5. تهيئة WSGI / Configurer WSGI
افتح رابط **WSGI configuration file** (في نفس صفحة Web)، احذف كل
المحتوى، والصق محتوى ملف `pythonanywhere_wsgi.py` المرفق في المشروع —
لا تنس تغيير `yourusername` و`SECRET_KEY` و`ADMIN_PASSWORD`.
Ouvrez le lien **WSGI configuration file** (sur la même page Web),
supprimez tout le contenu, et collez le contenu du fichier
`pythonanywhere_wsgi.py` fourni dans le projet — n'oubliez pas de
remplacer `yourusername`, `SECRET_KEY` et `ADMIN_PASSWORD`.

### 6. ربط الملفات الثابتة (الصور والتنسيق) / Lier les fichiers statiques (photos et style)
في قسم **Static files** بنفس الصفحة، أضف:
Dans la section **Static files** de la même page, ajoutez :

| URL | Directory |
|---|---|
| `/static/` | `/home/yourusername/teacher_app/static` |

### 7. إعادة التحميل / Recharger
اضغط الزر الأخضر **Reload** أعلى الصفحة. موقعك متاح الآن على:
Cliquez sur le bouton vert **Reload** en haut de la page. Votre site est
maintenant accessible sur :

`https://yourusername.pythonanywhere.com`

---

## 🔄 التجديد الشهري / Renouvellement mensuel

سجّل دخولك مرة واحدة كل شهر (أي نشاط بسيط كافٍ) لتجنّب توقف التطبيق
المجاني تلقائيًا. يمكن أيضًا ضبط تذكير في هاتفك.
Connectez-vous une fois par mois (une simple activité suffit) pour
éviter l'arrêt automatique de l'application gratuite. Vous pouvez aussi
programmer un rappel sur votre téléphone.

---

## 💾 النسخ الاحتياطي / Sauvegarde

بما أن المساحة محدودة بـ 512 ميغا، يُنصح بتصدير قاعدة البيانات دوريًا عبر
زر **"Exporter Excel"** في التطبيق نفسه، أو بتحميل ملف `teachers.db`
من تبويب **Files** بانتظام.
Comme l'espace est limité à 512 Mo, il est conseillé d'exporter
régulièrement la base via le bouton **"Exporter Excel"** de
l'application elle-même, ou de télécharger le fichier `teachers.db`
depuis l'onglet **Files** de temps en temps.
