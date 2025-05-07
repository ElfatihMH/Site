from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy import and_

# models.py
import qrcode
import base64
from io import BytesIO

def generate_qr_code(data):
    qr = qrcode.make(data)
    buffered = BytesIO()
    qr.save(buffered, format="PNG")
    qr_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{qr_str}"

# تعريف قاعدة البيانات
db = SQLAlchemy()

# نموذج الاشتراك
class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    subscription_type = db.Column(db.String(10), nullable=False)  # شهري أو سنوي
    start_date = db.Column(db.Date, nullable=False)  # تاريخ بداية الاشتراك
    amount = db.Column(db.Float, nullable=False)  # المبلغ الكلي للاشتراك
    next_payment_date = db.Column(db.Date, nullable=False)  # تاريخ الدفع القادم
    paid = db.Column(db.Float, nullable=False, default=0.0)  # المبلغ المدفوع حتى الآن
    details = db.Column(db.Text)  # حقل التفاصيل الجديد
    remaining_amount = db.Column(db.Float, nullable=False, default=0.0)  # المبلغ المتبقي
    details = db.Column(db.Text, nullable=True)

    def __init__(self, name, email, phone, subscription_type, start_date, amount, paid, details=None):
        self.name = name
        self.email = email
        self.phone = phone
        self.subscription_type = subscription_type
        self.start_date = start_date
        self.amount = amount
        self.paid = paid
        self.details = details if details else ""
        self.remaining_amount = self.calculate_remaining_amount()
        self.next_payment_date = self.calculate_next_payment()  # حساب تاريخ الدفع القادم مباشرة

    def calculate_remaining_amount(self):
        """حساب المبلغ المتبقي بناءً على المبلغ الكلي والمبلغ المدفوع."""
        return self.amount - self.paid

    def calculate_next_payment(self):
        """حساب تاريخ الدفع القادم بناءً على نوع الاشتراك."""
        if self.subscription_type == 'شهري':
            return self.start_date + relativedelta(months=1)  # إضافة شهر باستخدام relativedelta
        elif self.subscription_type == 'سنوي':
            return self.start_date + relativedelta(years=1)  # إضافة سنة باستخدام relativedelta
        return self.start_date

    def update_next_payment(self):
        """تحديث تاريخ الدفع القادم عند كل تحديث للاشتراك."""
        new_next_payment = self.calculate_next_payment()
        if self.next_payment_date != new_next_payment:  # فقط إذا كان هناك تغيير
            self.next_payment_date = new_next_payment
            db.session.commit()

    def update_remaining_amount(self):
        """دالة لتحديث المبلغ المتبقي."""
        # حساب المبلغ المتبقي بناءً على المبلغ الكلي والمبلغ المدفوع
        self.remaining_amount = self.calculate_remaining_amount()  # استخدم الدالة لحساب المبلغ المتبقي
        db.session.commit()

    @staticmethod
    def get_subscriptions_about_to_expire():
        """دالة لاسترجاع الاشتراكات التي اقترب موعد سدادها أو انتهت."""
        today = datetime.today().date()
        return Subscription.query.filter(
            and_(
                Subscription.next_payment_date <= today + timedelta(days=3), 
                Subscription.next_payment_date >= today
            )
        ).all()

    @staticmethod
    def get_expired_subscriptions():
        """دالة لاسترجاع الاشتراكات التي انتهت."""
        today = datetime.today().date()
        return Subscription.query.filter(
            Subscription.next_payment_date < today
        ).all()

    def update_paid_amount(self, amount):
        """دالة لتحديث المبلغ المدفوع."""
        self.paid += amount
        self.update_remaining_amount()  # تحديث المبلغ المتبقي بعد تعديل المبلغ المدفوع
        db.session.commit()
