from flask import Flask, render_template, redirect, url_for, flash, request
from config import Config
from models import db, Subscription
from forms import SubscriptionForm
from flask_migrate import Migrate
from datetime import datetime
from flask import current_app
import qrcode
import base64
from io import BytesIO
from models import generate_qr_code
from tickets import tickets_bp
from tickets.routes import tickets_bp


app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(tickets_bp)

db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/subscriptions/list')
def list_subscriptions():
    subscriptions = Subscription.query.all()
    today = datetime.utcnow().date()

    for subscription in subscriptions:
        days_remaining = (subscription.next_payment_date - today).days

        if days_remaining < 0:
            subscription.status_label = ('انتهى الاشتراك', 'danger')
        elif days_remaining <= 3:
            subscription.status_label = ('اقترب السداد', 'warning')
            if subscription.paid < subscription.amount:
                message = f"تنبيه: اشتراكك في النظام سينقضي خلال 3 أيام. يرجى الدفع قبل {subscription.next_payment_date}."
        else:
            subscription.status_label = ('نشط', 'success')

        subscription.remaining_amount = subscription.amount - subscription.paid

    return render_template('subscriptions/list.html', subscriptions=subscriptions)
@app.route('/subscriptions/statistics', methods=['GET'])
def subscription_statistics():
    subscription_type = request.args.get('type')  # "شهري" أو "سنوي" أو None
    period = request.args.get('period')  # "30" أو "90" أو None

    query = Subscription.query

    if subscription_type:
        query = query.filter(Subscription.subscription_type == subscription_type)

    if period:
        try:
            days = int(period)
            start_date = datetime.utcnow().date() - timedelta(days=days)
            query = query.filter(Subscription.start_date >= start_date)
        except ValueError:
            pass

    subscriptions = query.all()
    today = datetime.utcnow().date()

    total = len(subscriptions)
    active = expired = due_soon = 0
    total_paid = total_remaining = 0

    for subscription in subscriptions:
        days_remaining = (subscription.next_payment_date - today).days
        total_paid += subscription.paid
        total_remaining += subscription.amount - subscription.paid

        if days_remaining < 0:
            expired += 1
        elif days_remaining <= 3:
            due_soon += 1
        else:
            active += 1

    return render_template(
        'subscriptions/statistics.html',
        total=total,
        active=active,
        due_soon=due_soon,
        expired=expired,
        total_paid=total_paid,
        total_remaining=total_remaining,
        subscription_type=subscription_type,
        period=period
    )

@app.route('/subscriptions/create', methods=['GET', 'POST'])
def create_subscription():
    form = SubscriptionForm()
    if form.validate_on_submit():
        subscription = Subscription(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            subscription_type=form.subscription_type.data,
            amount=form.amount.data,
            paid=float(form.paid.data),
            start_date=datetime.utcnow(),
            details=form.details.data,

        )
        subscription.next_payment_date = subscription.calculate_next_payment()
        subscription.update_remaining_amount()

        db.session.add(subscription)
        db.session.commit()

  

        flash('تم إنشاء الاشتراك بنجاح!', 'success')
        return redirect(url_for('list_subscriptions'))
    return render_template('subscriptions/create.html', form=form)

@app.route('/subscriptions/edit/<int:id>', methods=['GET', 'POST'])
def edit_subscription(id):
    subscription = Subscription.query.get_or_404(id)
    form = SubscriptionForm(obj=subscription)

    if form.validate_on_submit():
        subscription.name = form.name.data
        subscription.email = form.email.data
        subscription.phone = form.phone.data
        subscription.subscription_type = form.subscription_type.data
        subscription.paid = form.paid.data
        subscription.next_payment_date = subscription.calculate_next_payment()
        subscription.update_remaining_amount()
        subscription.details = form.details.data


        db.session.commit()
        flash('تم تعديل الاشتراك بنجاح!', 'success')
        return redirect(url_for('list_subscriptions'))

    return render_template('subscriptions/edit.html', form=form, subscription=subscription)

@app.route('/subscriptions/delete/<int:id>')
def delete_subscription(id):
    subscription = Subscription.query.get_or_404(id)
    db.session.delete(subscription)
    db.session.commit()
    flash('تم حذف الاشتراك!', 'success')
    return redirect(url_for('list_subscriptions'))
@app.route('/subscriptions/details/<int:id>')
def subscription_details(id):
    subscription = Subscription.query.get_or_404(id)
    return render_template('subscriptions/details.html', subscription=subscription)
@app.route("/receipt/<int:subscription_id>")
def print_receipt(subscription_id):
    subscription = Subscription.query.get_or_404(subscription_id)
    qr_data = f"اسم: {subscription.name}, البريد: {subscription.email}, الهاتف: {subscription.phone}, المبلغ: {subscription.amount}"
    qr_code = generate_qr_code(qr_data)
    return render_template("subscriptions/receipt.html", subscription=subscription, qr_code=qr_code)

app.secret_key = 's0m3$uperS3cretK3y!'

if __name__ == '__main__':
    app.run(host='192.168.100.27', port=9000, debug=True)
