# tickets/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

class TicketForm(FlaskForm):
    customer_name = StringField('اسم العميل', validators=[DataRequired()])
    service_type = StringField('نوع الخدمة', validators=[DataRequired()])
    status = SelectField('الحالة', choices=[('waiting', 'قيد الانتظار'), ('serving', 'تحت المعالجة'), ('done', 'تمت')], validators=[DataRequired()])
    submit = SubmitField('حفظ')
