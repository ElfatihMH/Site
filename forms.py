from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, FloatField, DateField
from wtforms.validators import DataRequired, Email
from wtforms import TextAreaField

class SubscriptionForm(FlaskForm):
    name = StringField('الاسم', validators=[DataRequired()])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    phone = StringField('رقم الهاتف', validators=[DataRequired()])
    start_date = DateField('تاريخ بداية الاشتراك', validators=[DataRequired()], format='%Y-%m-%d')
    subscription_type = SelectField('نوع الاشتراك', choices=[('شهري', 'شهري'), ('سنوي', 'سنوي')])
    amount = FloatField('المبلغ الإجمالي', validators=[DataRequired()])  # المبلغ المستحق ثابت
    paid = FloatField('المبلغ المدفوع', validators=[DataRequired()])
    submit = SubmitField('إضافة الاشتراك')
    details = TextAreaField('تفاصيل الاشتراك')
    def calculate_remaining_amount(self):
        """
        دالة لحساب المبلغ المتبقي بشكل ديناميكي بناءً على المبلغ المستحق والمبلغ المدفوع.
        """
        if self.amount.data is not None and self.paid.data is not None:
            remaining = self.amount.data - self.paid.data
            return remaining if remaining >= 0 else 0.0  # التأكد من أن المبلغ المتبقي لا يكون سالبًا
        return 0.0

