# تطبيق تسيير الأساتذة / Application de Gestion des Enseignants

تطبيق ويب (Flask) لإدارة بيانات الأساتذة، مع استيراد/تصدير Excel،
صور، وحساب/ترتيب تلقائي — واجهة ثنائية اللغة (فرنسية / عربية، مع دعم RTL).

Application web (Flask) pour gérer les données des enseignants, avec
import/export Excel, photos, et calcul/classement automatique —
interface bilingue (français / arabe, avec support RTL).

---

## 🚀 التثبيت والتشغيل / Installation et lancement

```bash
# 1. إنشاء بيئة افتراضية / Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. تثبيت المكتبات / Installer les dépendances
pip install -r requirements.txt

# 3. تشغيل التطبيق / Lancer l'application
python app.py
```

ثم افتح المتصفح على / Puis ouvrez votre navigateur sur:
**http://localhost:5000**

قاعدة البيانات (`teachers.db`) تُنشأ تلقائيًا عند أول تشغيل.
La base de données (`teachers.db`) est créée automatiquement au premier lancement.

---

## 📁 هيكل المشروع / Structure du projet

```
teacher_app/
├── app.py              # التطبيق الرئيسي وكل المسارات / Application principale et routes
├── models.py           # نموذج قاعدة البيانات / Modèle de base de données
├── classement.py       # ⭐ منهجية الترتيب (عدّل هنا) / Méthode de classement (à modifier ici)
├── excel_io.py         # استيراد/تصدير Excel / Import-export Excel
├── requirements.txt
├── templates/          # صفحات HTML
├── static/
│   ├── css/style.css   # التنسيق (يدعم RTL و LTR)
│   ├── uploads/        # صور الأساتذة المرفوعة
│   └── exports/        # ملفات Excel المصدّرة/المؤقتة
└── teachers.db          # قاعدة البيانات SQLite (تُنشأ تلقائيًا)
```

---

## 🔐 تسجيل الدخول / Connexion

التطبيق محمي الآن بتسجيل دخول. الحساب الافتراضي عند أول تشغيل:
L'application est maintenant protégée par une connexion. Compte par défaut créé au premier lancement :

- **اسم المستخدم / Identifiant** : `admin`
- **كلمة المرور / Mot de passe** : `admin123`

⚠️ يُنصح بتغيير كلمة المرور مباشرة بعد أول استعمال (عبر تعديل جدول `users`
في قاعدة البيانات، أو بإضافة صفحة تغيير كلمة المرور لاحقًا).
⚠️ Il est recommandé de changer ce mot de passe dès la première utilisation
(en modifiant la table `users` de la base, ou en ajoutant une page de
changement de mot de passe ultérieurement).

---

## 🎓 الرتب الأكاديمية وقواعد الترقية في الدرجة
## Grades académiques et règles d'avancement d'échelon

كل أستاذ له الآن **رتبة أكاديمية** (بالإضافة إلى "الدرجة" وهي رقم السلّم
داخل الرتبة). قواعد الترقية الحالية (المطبقة في `promotion.py`):
Chaque enseignant a maintenant un **grade académique** (en plus de
"الدرجة" qui est le numéro d'échelon au sein du grade). Règles
d'avancement actuellement appliquées (dans `promotion.py`) :

مدة كل **إيقاع** موحّدة عبر كل الرتب: الحد الأدنى = 2س6ش، المتوسط = 3س،
الحد الأقصى = 3س6ش. لكن كل رتبة لا تستفيد إلا من بعض هذه الإيقاعات:
Chaque **rythme** a une durée uniforme pour tous les grades : minimum =
2 ans 6 mois, moyen = 3 ans, maximum = 3 ans 6 mois. Mais chaque grade
ne bénéficie que de certains de ces rythmes :

| الرتبة / Grade | الإيقاعات المتاحة / Rythmes disponibles |
|---|---|
| Professeur | الحد الأدنى فقط (2 ans 6 mois) — ترقية مباشرة |
| MCA | الحد الأدنى فقط (2 ans 6 mois) — نفس الشيء |
| MCB | الحد الأدنى (2 ans 6 mois) والمتوسط (3 ans) |
| MAA | الحد الأدنى (2 ans 6 mois)، المتوسط (3 ans)، الحد الأقصى (3 ans 6 mois) |
| MAB | نفس MAA (الحد الأدنى، المتوسط، الحد الأقصى) |

من بلغ مدة "المتوسط" يكون بالضرورة بلغ أيضًا مدة "الحد الأدنى" (لأنها
أقصر) — لذلك يظهر في كلتا القائمتين عند المعاينة، ويُختار له تلقائيًا
أسرع إيقاع متوفرة فيه حصة (منصب) شاغرة عند تنفيذ الجلسة.
Qui a atteint la durée "moyen" a forcément aussi atteint la durée
"minimum" (plus courte) — il apparaît donc dans les deux listes lors de
la consultation, et se voit attribuer automatiquement le rythme le plus
rapide où un poste (quota) est disponible lors de l'exécution de la
session.

### 📅 جلسات الترقية (صفحة "Sessions") / Sessions de promotion

1. أنشئ جلسة جديدة باختيار السنة (مثال: 2026 → 31/12/2026)
   Créez une nouvelle session en choisissant l'année (ex : 2026 → 31/12/2026)
2. حدّد **عدد المناصب (الحصة/Quota)** لكل رتبة وإيقاع — القيمة `0` تعني
   "غير محدود" (يستفيد كل المستحقين)
   Définissez le **nombre de postes (quota)** par grade et par rythme —
   la valeur `0` signifie "illimité" (tous les éligibles en bénéficient)
3. تُعرض قائمة الأساتذة المستحقين لكل رتبة، مرتّبين حسب نقطة الترتيب
   (الأعلى نقطة أولًا)
   La liste des enseignants éligibles par grade s'affiche, triée par
   score de classement (le plus haut score en premier)
4. اضغط **"تنفيذ الجلسة"**: يُحدَّث تلقائيًا "الدرجة" و"تاريخ النفاذ" لكل
   مستحق ضمن الحصة المحددة، ويُحفظ **سجل تاريخي كامل** (لا يُحذف أي شيء)
   Cliquez sur **"Exécuter la session"** : la "الدرجة" et "تاريخ النفاذ"
   de chaque enseignant éligible (dans la limite du quota) sont mises à
   jour automatiquement, et un **historique complet est conservé**
   (rien n'est jamais supprimé)
5. الجلسة المنفَّذة لا يمكن إعادة تنفيذها؛ يمكن إنشاء جلسة جديدة للسنة
   الموالية
   Une session déjà exécutée ne peut pas être relancée ; créez une
   nouvelle session pour l'année suivante

السجل التاريخي الكامل لكل أستاذ (كل الترقيات السابقة) يظهر في أسفل
صفحته الشخصية.
L'historique complet de chaque enseignant (tous les avancements passés)
apparaît en bas de sa fiche.

---

## 🆓 بديل مجاني بدون توقف (لا "نوم") / Alternative gratuite sans mise en veille

Render المجاني يتوقف مؤقتًا بعد فترة عدم نشاط، ويحذف الملفات بدون قرص
دائم. إن كنتم تفضلون استضافة **لا تتوقف أبدًا** (مقابل الحاجة لتجديد
شهري بسيط)، راجعوا **`PYTHONANYWHERE.md`** المرفق — دليل خطوة بخطوة
للنشر على PythonAnywhere.

Le plan gratuit de Render se met en veille après inactivité, et efface
les fichiers sans disque payant. Si vous préférez un hébergement qui **ne
s'arrête jamais** (en échange d'un simple renouvellement mensuel), consultez
**`PYTHONANYWHERE.md`** fourni — un guide pas à pas pour déployer sur
PythonAnywhere.

⚠️ Aucun hébergement n'est "gratuit et illimité" : chaque option a ses
propres contraintes (stockage, CPU, expiration, mise en veille).

---

## ☁️ النشر على Render / Déploiement sur Render

المشروع جاهز للنشر مباشرة على [Render](https://render.com) (`Procfile`,
`runtime.txt`, `render.yaml`, `gunicorn` مضمّنون).
Le projet est prêt à être déployé directement sur
[Render](https://render.com) (`Procfile`, `runtime.txt`, `render.yaml`,
`gunicorn` sont déjà inclus).

### الطريقة الأسهل — Blueprint (`render.yaml`) / Méthode la plus simple

1. ارفع مجلد المشروع إلى مستودع GitHub (خاص أو عام)
   Poussez le dossier du projet sur un dépôt GitHub (privé ou public)
2. على Render: **New +** → **Blueprint** → اختر المستودع
   Sur Render : **New +** → **Blueprint** → sélectionnez le dépôt
3. سيكتشف Render ملف `render.yaml` تلقائيًا وينشئ:
   - خدمة ويب (Python + gunicorn)
   - قرصًا دائمًا (1 GB) لحفظ قاعدة البيانات SQLite والصور بشكل دائم
   - متغير `SECRET_KEY` عشوائي وآمن تلقائيًا
   Render détecte automatiquement `render.yaml` et crée :
   - un service web (Python + gunicorn)
   - un disque persistant (1 Go) pour conserver la base SQLite et les
     photos de façon durable entre les déploiements
   - une `SECRET_KEY` aléatoire générée automatiquement
4. عند الطلب، أدخل قيمة `ADMIN_PASSWORD` (كلمة مرور المدير الافتراضية عند
   أول تشغيل) — إن تركتها فارغة ستكون `admin123`
   Quand demandé, renseignez `ADMIN_PASSWORD` (mot de passe admin par
   défaut au premier lancement) — laissé vide, ce sera `admin123`

### الطريقة اليدوية — Web Service / Méthode manuelle

1. **New +** → **Web Service** → اختر المستودع
2. **Build Command**: `pip install -r requirements.txt`
3. **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`
4. أضف متغيرات البيئة (Environment) التالية:
   Ajoutez les variables d'environnement suivantes :
   - `SECRET_KEY` = (نص عشوائي طويل / une chaîne aléatoire longue)
   - `ADMIN_PASSWORD` = (كلمة مرور المدير / mot de passe admin souhaité)
   - `FLASK_DEBUG` = `0`
5. ⚠️ بدون قرص دائم (disk)، تُحذف قاعدة SQLite والصور المرفوعة عند كل
   إعادة نشر (deploy). لإضافة قرص دائم: **Disks** → أنشئ قرصًا واربطه
   بمسار مثل `/var/data`، ثم أضف متغير `DATA_DIR=/var/data`.
   ⚠️ Sans disque persistant, la base SQLite et les photos uploadées
   sont effacées à chaque redéploiement. Pour ajouter un disque
   persistant : **Disks** → créez un disque monté sur un chemin comme
   `/var/data`, puis ajoutez la variable `DATA_DIR=/var/data`.

### قاعدة بيانات PostgreSQL بدل SQLite (اختياري) / Base PostgreSQL au lieu de SQLite (optionnel)

للاستعمال الجدي على المدى الطويل، يُفضّل استعمال قاعدة PostgreSQL (متوفرة
مجانًا على Render) بدل SQLite:
Pour un usage sérieux sur le long terme, il est préférable d'utiliser une
base PostgreSQL (disponible gratuitement sur Render) plutôt que SQLite :

1. على Render: **New +** → **PostgreSQL** → أنشئ قاعدة بيانات
   Sur Render : **New +** → **PostgreSQL** → créez une base de données
2. انسخ قيمة **Internal Database URL**
   Copiez la valeur **Internal Database URL**
3. أضفها كمتغير بيئة `DATABASE_URL` في خدمة الويب — سيتحول التطبيق
   تلقائيًا لاستعمالها (لا حاجة لتعديل الكود)
   Ajoutez-la comme variable d'environnement `DATABASE_URL` sur le
   service web — l'application basculera automatiquement dessus (aucune
   modification de code nécessaire)

---

## ⭐ منهجية الترتيب / Méthode de classement

الملف `classement.py` يحتوي على دالة `calculate_score(teacher)` وهي
**مؤقتة** حاليًا (تعتمد على الأقدمية فقط) في انتظار إرسالكم للمنهجية
الرسمية. عند استلامها:

1. افتح `classement.py`
2. عدّل محتوى الدالة `calculate_score(teacher)` بالمعايير والنقاط الحقيقية
3. أعد تشغيل التطبيق ثم اضغط "إعادة حساب الترتيب" من صفحة الترتيب

Le fichier `classement.py` contient la fonction `calculate_score(teacher)`,
actuellement **temporaire** (basée uniquement sur l'ancienneté), en
attendant que vous m'envoyiez la méthode officielle. Une fois reçue :

1. Ouvrez `classement.py`
2. Modifiez le contenu de `calculate_score(teacher)` avec les vrais critères et points
3. Relancez l'application puis cliquez sur "Recalculer le classement"

---

## ✨ الميزات / Fonctionnalités

- ✅ تسجيل دخول بتصميم عصري (Flask-Login)
  Connexion avec design moderne (Flask-Login)
- ✅ رتب أكاديمية (Professeur, MCA, MCB, MAA, MAB) وترتيب منفصل لكل رتبة
  Grades académiques et classement séparé par grade
- ✅ محرك ترقية آلي في الدرجة حسب القواعد الرسمية لكل رتبة، مع نظام حصص
  (مناصب) لكل جلسة وحفظ كامل للسجل التاريخي
  Moteur d'avancement d'échelon automatique selon les règles officielles
  par grade, avec système de quotas par session et historique complet
- ✅ إضافة / تعديل / حذف / عرض الأساتذة (مع صورة)
  Ajout / modification / suppression / consultation des enseignants (avec photo)
- ✅ استيراد ملف Excel (بالتسميات العربية أو الفرنسية للأعمدة) — يكتشف
  السجلات الموجودة (بالرقم التسلسلي أو الاسم) ويحدّثها، أو ينشئ سجلات جديدة
  Import Excel (libellés arabes ou français) — détecte les enregistrements
  existants et les met à jour, sinon en crée de nouveaux
- ✅ تصدير كل البيانات إلى Excel (بتنسيق من اليمين لليسار)
  Export de toutes les données vers Excel (feuille orientée RTL)
- ✅ تحميل نموذج Excel فارغ جاهز للتعبئة
  Téléchargement d'un modèle Excel vide prêt à remplir
- ✅ حساب وترتيب تلقائي للأساتذة (منهجية قابلة للتعديل بسهولة)
  Calcul et classement automatique (méthode facilement modifiable)
- ✅ واجهة ثنائية اللغة مع تبديل فوري (فرنسية ⇄ عربية RTL)
  Interface bilingue avec bascule instantanée (français ⇄ arabe RTL)
- ✅ بحث في القائمة
  Recherche dans la liste

---

## 🔧 ملاحظات تقنية / Notes techniques

- قاعدة البيانات: SQLite (يمكن تغييرها إلى PostgreSQL/MySQL بتعديل
  `SQLALCHEMY_DATABASE_URI` في `app.py`)
  Base de données : SQLite (remplaçable par PostgreSQL/MySQL en modifiant
  `SQLALCHEMY_DATABASE_URI` dans `app.py`)
- الصور تُخزَّن في `static/uploads/`
  Les photos sont stockées dans `static/uploads/`
- أعمدة ملف Excel معرّفة في `excel_io.py` (`COLUMNS`) — يمكن إضافة/تعديل
  الأعمدة من هناك
  Les colonnes du fichier Excel sont définies dans `excel_io.py`
  (`COLUMNS`) — vous pouvez y ajouter/modifier des colonnes
