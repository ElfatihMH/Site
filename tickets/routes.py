from flask import render_template, redirect, url_for, flash, request
from . import tickets_bp
from .forms import TicketForm
from app import db
from .models import Ticket

@tickets_bp.route('/tickets/create', methods=['GET', 'POST'])
def create_ticket():
    form = TicketForm()
    if form.validate_on_submit():
        ticket = Ticket(
            customer_name=form.customer_name.data,
            service_type=form.service_type.data
        )
        db.session.add(ticket)
        db.session.commit()
        flash('تم إنشاء التذكرة بنجاح')
        return redirect(url_for('tickets.view_tickets'))
    return render_template('tickets/create_ticket.html', form=form)

#@tickets_bp.route('/tickets')
#def list_tickets():
 #   tickets = Ticket.query.all()
  #  return render_template('tickets/view_tickets.html', tickets=tickets)
@tickets_bp.route('/tickets/my_tickets')
def my_tickets():
    # افتراض أن العميل مسجل دخوله ويمكن الحصول على بياناته من الجلسة أو قاعدة البيانات
    customer_name = 'اسم العميل'  # هنا يتم جلب اسم العميل المسجل
    tickets = Ticket.query.filter_by(customer_name=customer_name).all()
    
    return render_template('tickets/my_tickets.html', tickets=tickets)

@tickets_bp.route('/tickets/delete/<int:id>')
def delete_ticket(id):
    ticket = Ticket.query.get_or_404(id)
    db.session.delete(ticket)
    db.session.commit()
    flash('تم حذف التذكرة')
    return redirect(url_for('tickets.view_tickets'))

@tickets_bp.route('/tickets/dashboard')
def ticket_dashboard():
    total = Ticket.query.count()
    waiting = Ticket.query.filter_by(status='waiting').count()
    serving = Ticket.query.filter_by(status='serving').count()
    done = Ticket.query.filter_by(status='done').count()
    return render_template('tickets/dashboard.html', total=total, waiting=waiting, serving=serving, done=done)

@tickets_bp.route('/tickets/queue')
def display_queue():
    tickets = Ticket.query.filter_by(status='waiting').all()
    return render_template('tickets/display_queue.html', tickets=tickets)
@tickets_bp.route('/tickets')
def view_tickets():
    tickets = Ticket.query.order_by(Ticket.created_at.asc()).all()
    return render_template('tickets/view_tickets.html', tickets=tickets)
@tickets_bp.route('/tickets/edit/<int:id>', methods=['GET', 'POST'])
def edit_ticket(id):
    ticket = Ticket.query.get_or_404(id)
    form = TicketForm(obj=ticket)  # نملأ النموذج بالبيانات الحالية للتذكرة

    if form.validate_on_submit():
        ticket.customer_name = form.customer_name.data
        ticket.service_type = form.service_type.data
        ticket.status = form.status.data  # تأكد من إضافة حقل الحالة في النموذج إذا لم يكن موجودًا
        db.session.commit()
        flash('تم تعديل التذكرة بنجاح')
        return redirect(url_for('tickets.view_tickets'))

    return render_template('tickets/edit_ticket.html', form=form, ticket=ticket)
