CREATE TABLE IF NOT EXISTS devices ( -- إنشاء جدول 'devices' إذا لم يكن موجوداً بالفعل
    id SERIAL PRIMARY KEY, -- إنشاء عمود 'id' كرقم تسلسلي تلقائي الزيادة، وتعيينه كمفتاح أساسي للجدول
    name VARCHAR(255) NOT NULL, -- عمود 'name' من نوع نصي (حتى 255 حرف)، ولا يمكن أن يكون فارغاً (NOT NULL)
    type VARCHAR(255), -- عمود 'type' لتخزين نوع الجهاز، من نوع نصي
    status VARCHAR(50), -- عمود 'status' لتخزين حالة الجهاز (نشط/غير نشط)، من نوع نصي
    location VARCHAR(255) -- عمود 'location' لتخزين موقع الجهاز، من نوع نصي
);

INSERT INTO devices (name, type, status, location) VALUES -- إضافة بعض البيانات الافتراضية (سجلين) إلى جدول devices
('Sensor-Alpha', 'Temperature', 'Active', 'Room 101'), -- السجل الأول: مستشعر حرارة نشط في الغرفة 101
('Sensor-Beta', 'Humidity', 'Inactive', 'Room 102'); -- السجل الثاني: مستشعر رطوبة غير نشط في الغرفة 102
