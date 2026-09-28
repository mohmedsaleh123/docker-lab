import os # استيراد مكتبة os للتعامل مع نظام التشغيل ومتغيرات البيئة
import psycopg2 # استيراد مكتبة psycopg2 للاتصال بقاعدة بيانات PostgreSQL
from flask import Flask, request, jsonify # استيراد Flask لإنشاء تطبيق الويب، و request للتعامل مع الطلبات، و jsonify لإرسال ردود بصيغة JSON
from psycopg2.extras import RealDictCursor # استيراد RealDictCursor لإرجاع نتائج قاعدة البيانات على شكل قواميس بدلاً من صفوف عادية

app = Flask(__name__) # إنشاء كائن تطبيق Flask وتمهيده باستخدام اسم الوحدة الحالية

def get_db_connection(): # تعريف دالة لإنشاء اتصال بقاعدة البيانات
    conn = psycopg2.connect( # إنشاء كائن الاتصال باستخدام إعدادات قاعدة البيانات
        host=os.getenv("DB_HOST", "localhost"), # قراءة عنوان الخادم من متغير البيئة DB_HOST أو استخدام 'localhost' كقيمة افتراضية
        database=os.getenv("DB_NAME", "device_db"), # قراءة اسم قاعدة البيانات من متغير البيئة DB_NAME أو استخدام 'device_db' كقيمة افتراضية
        user=os.getenv("DB_USER", "user"), # قراءة اسم المستخدم من متغير البيئة DB_USER أو استخدام 'user' كقيمة افتراضية
        password=os.getenv("DB_PASSWORD", "password") # قراءة كلمة المرور من متغير البيئة DB_PASSWORD أو استخدام 'password' كقيمة افتراضية
    )
    return conn # إرجاع كائن الاتصال الذي تم إنشاؤه ليتم استخدامه في الاستعلامات

@app.route('/api/resources', methods=['GET']) # تحديد مسار API لاسترجاع كافة الأجهزة، والسماح بطلبات GET فقط
def get_devices(): # تعريف الدالة التي ستُنفذ عند طلب هذا المسار
    try: # بدء كتلة try لمعالجة الأخطاء المحتملة أثناء الاتصال أو الاستعلام
        conn = get_db_connection() # فتح اتصال جديد بقاعدة البيانات باستخدام الدالة المعرفة مسبقاً
        cur = conn.cursor(cursor_factory=RealDictCursor) # إنشاء مؤشر (cursor) لتنفيذ الاستعلامات، مع تحديد إرجاع النتائج كقواميس
        cur.execute('SELECT * FROM devices;') # تنفيذ استعلام SQL لاسترداد جميع السجلات من جدول devices
        devices = cur.fetchall() # جلب جميع النتائج (الصفوف) التي أعادها الاستعلام وتخزينها في المتغير devices
        cur.close() # إغلاق المؤشر بعد الانتهاء من جلب البيانات لتحرير الموارد
        conn.close() # إغلاق الاتصال بقاعدة البيانات
        return jsonify(devices), 200 # تحويل قائمة الأجهزة إلى صيغة JSON وإرجاعها كاستجابة ناجحة مع رمز الحالة 200
    except Exception as e: # التقاط أي استثناء (خطأ) قد يحدث في الكتلة السابقة
        return jsonify({"error": str(e)}), 500 # إرجاع رسالة الخطأ كاستجابة JSON مع رمز حالة خطأ الخادم 500

@app.route('/api/resources/<int:id>', methods=['GET']) # تحديد مسار لاسترجاع جهاز معين بناءً على معرفه (id) الذي يجب أن يكون رقماً صحيحاً
def get_device(id): # تعريف الدالة مع تمرير المعرف (id) المستخرج من الرابط
    try: # بدء كتلة معالجة الأخطاء
        conn = get_db_connection() # فتح اتصال بقاعدة البيانات
        cur = conn.cursor(cursor_factory=RealDictCursor) # إنشاء مؤشر لاسترجاع البيانات في شكل قواميس
        cur.execute('SELECT * FROM devices WHERE id = %s;', (id,)) # تنفيذ استعلام SQL للبحث عن الجهاز الذي يطابق المعرف (id) بشكل آمن
        device = cur.fetchone() # جلب سجل واحد فقط من النتيجة وتخزينه في المتغير device
        cur.close() # إغلاق المؤشر
        conn.close() # إغلاق الاتصال بقاعدة البيانات
        if device is None: # التحقق مما إذا كان لم يتم العثور على أي جهاز بهذا المعرف
            return jsonify({"error": "Not Found"}), 404 # إرجاع استجابة "غير موجود" مع رمز الحالة 404
        return jsonify(device), 200 # إرجاع تفاصيل الجهاز بصيغة JSON مع رمز الحالة 200 للنجاح
    except Exception as e: # التقاط أي خطأ قد يحدث
        return jsonify({"error": str(e)}), 500 # إرجاع رسالة الخطأ مع رمز الحالة 500

@app.route('/api/resources', methods=['POST']) # تحديد مسار لإضافة جهاز جديد، السماح بطلبات POST فقط
def create_device(): # تعريف دالة الإنشاء
    data = request.get_json() # استخراج البيانات المرسلة في جسم الطلب (body) بصيغة JSON
    if not data or 'name' not in data: # التحقق من وجود البيانات ومن احتوائها على الحقل الأساسي 'name'
        return jsonify({"error": "Bad Request, missing name"}), 400 # إرجاع خطأ "طلب سيء" مع رمز الحالة 400 إذا كانت البيانات ناقصة
    try: # بدء كتلة معالجة الأخطاء
        conn = get_db_connection() # فتح اتصال بقاعدة البيانات
        cur = conn.cursor(cursor_factory=RealDictCursor) # إنشاء مؤشر لتنفيذ الاستعلامات
        cur.execute( # تنفيذ استعلام الإدخال
            'INSERT INTO devices (name, type, status, location) VALUES (%s, %s, %s, %s) RETURNING *;', # تعليمة الإدخال إلى الجدول وطلب إرجاع السجل المُضاف
            (data['name'], data.get('type', 'unknown'), data.get('status', 'active'), data.get('location', 'unknown')) # تمرير القيم المستخرجة من الطلب، مع توفير قيم افتراضية للحقول الاختيارية
        )
        new_device = cur.fetchone() # جلب السجل الجديد الذي تم إضافته
        conn.commit() # حفظ (تأكيد) التغييرات في قاعدة البيانات
        cur.close() # إغلاق المؤشر
        conn.close() # إغلاق الاتصال بقاعدة البيانات
        return jsonify(new_device), 201 # إرجاع بيانات الجهاز المضاف بصيغة JSON مع رمز الحالة 201 (تم الإنشاء)
    except Exception as e: # التقاط أي خطأ قد يحدث
        return jsonify({"error": str(e)}), 500 # إرجاع رسالة الخطأ مع رمز الحالة 500

@app.route('/api/resources/<int:id>', methods=['PUT']) # تحديد مسار لتحديث جهاز موجود بناءً على المعرف، السماح بطلبات PUT فقط
def update_device(id): # تعريف دالة التحديث مع المعرف
    data = request.get_json() # استخراج البيانات المرسلة في الطلب
    if not data: # التحقق من وجود بيانات لتحديثها
        return jsonify({"error": "Bad Request"}), 400 # إرجاع خطأ 400 إذا لم يتم توفير أي بيانات
    try: # بدء كتلة معالجة الأخطاء
        conn = get_db_connection() # فتح اتصال بقاعدة البيانات
        cur = conn.cursor(cursor_factory=RealDictCursor) # إنشاء مؤشر للاستعلام
        cur.execute('SELECT * FROM devices WHERE id = %s;', (id,)) # التحقق أولاً من وجود الجهاز المطلوب تحديثه
        device = cur.fetchone() # جلب نتيجة التحقق
        if device is None: # إذا لم يكن الجهاز موجوداً في القاعدة
            cur.close() # إغلاق المؤشر
            conn.close() # إغلاق الاتصال
            return jsonify({"error": "Not Found"}), 404 # إرجاع خطأ "غير موجود" 404
            
        cur.execute( # إذا كان موجوداً، ننفذ استعلام التحديث
            'UPDATE devices SET name = %s, type = %s, status = %s, location = %s WHERE id = %s RETURNING *;', # تحديث الأعمدة وطلب إرجاع السجل المُحدّث
            (data.get('name', device['name']), data.get('type', device['type']), data.get('status', device['status']), data.get('location', device['location']), id) # تمرير البيانات الجديدة، أو استخدام البيانات القديمة إذا لم يتم تقديم قيمة جديدة
        )
        updated_device = cur.fetchone() # جلب بيانات الجهاز بعد التحديث
        conn.commit() # تأكيد الحفظ في قاعدة البيانات
        cur.close() # إغلاق المؤشر
        conn.close() # إغلاق الاتصال
        return jsonify(updated_device), 200 # إرجاع بيانات الجهاز المحدثة مع رمز الحالة 200
    except Exception as e: # التقاط الأخطاء
        return jsonify({"error": str(e)}), 500 # إرجاع رسالة الخطأ 500

@app.route('/api/resources/<int:id>', methods=['DELETE']) # تحديد مسار لحذف جهاز معين باستخدام معرفه، السماح بطلبات DELETE فقط
def delete_device(id): # تعريف دالة الحذف
    try: # بدء كتلة معالجة الأخطاء
        conn = get_db_connection() # فتح اتصال بقاعدة البيانات
        cur = conn.cursor() # إنشاء مؤشر عادي (لا نحتاج لقاموس هنا لأننا نريد فقط المعرف)
        cur.execute('DELETE FROM devices WHERE id = %s RETURNING id;', (id,)) # تنفيذ أمر الحذف وطلب إرجاع المعرف المحذوف للتأكد
        deleted_id = cur.fetchone() # جلب المعرف الذي تم حذفه
        conn.commit() # تأكيد الحذف في قاعدة البيانات
        cur.close() # إغلاق المؤشر
        conn.close() # إغلاق الاتصال
        
        if deleted_id is None: # التحقق مما إذا كان الاستعلام لم يحذف أي شيء (أي الجهاز غير موجود)
            return jsonify({"error": "Not Found"}), 404 # إرجاع خطأ 404
            
        return '', 204 # إرجاع استجابة فارغة مع رمز 204 (نجاح الحذف بدون محتوى في الرد)
    except Exception as e: # التقاط الأخطاء المحتملة
        return jsonify({"error": str(e)}), 500 # إرجاع رسالة خطأ 500

if __name__ == '__main__': # التحقق مما إذا كان هذا الملف يُشغل مباشرة (وليس مستورداً كوحدة في مكان آخر)
    app.run(host='0.0.0.0', port=8000) # تشغيل خادم Flask وجعله متاحاً للوصول من أي عنوان IP على المنفذ 8000
