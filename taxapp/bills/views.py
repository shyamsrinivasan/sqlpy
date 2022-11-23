from flask import render_template, flash, redirect, url_for
from . import bills_bp
from .forms import NewInvoice
from .models import Bill, Items
from taxapp import db


@bills_bp.route('/new-invoice', methods=['GET', 'POST'])
def generate_invoice():
    """generate new invoice - form to enter particulars for new invoice"""
    # return redirect(url_for('customer.choose_customer'))

    bill = Bill()

    if bill is None or len(bill.items) == 0:
        bill.items = [Items(bill_item="example")]
        flash(message="empty bill provided", category='primary')

    form = NewInvoice(obj=bill)

    if form.validate_on_submit():
        form.populate_obj(bill)
        db.session.commit()
        flash(message="changes saved", category="success")
        return redirect(url_for('customer.customer_overview'))

    return render_template('newbill_2.html', form=form)
