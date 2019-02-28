from flask import Flask, redirect, url_for, render_template, request, flash,Blueprint
import braintree
from app import app,generate_client_token,find_transaction,gateway,transact
from models.user import User
from models.image import Image
from models.donation import Donation
from instagram_web.util.mail_helper import send_pay_email
from flask_login import current_user,login_required
from decimal import *
from peewee import fn

checkouts_blueprint = Blueprint('checkouts',
                            __name__,
                            template_folder='templates')

TRANSACTION_SUCCESS_STATUSES = [
    braintree.Transaction.Status.Authorized,
    braintree.Transaction.Status.Authorizing,
    braintree.Transaction.Status.Settled,
    braintree.Transaction.Status.SettlementConfirmed,
    braintree.Transaction.Status.SettlementPending,
    braintree.Transaction.Status.Settling,
    braintree.Transaction.Status.SubmittedForSettlement
]

# @checkouts_blueprint.route('/', methods=['GET'])
# def index():
#     return redirect(url_for('checkouts.new_checkout'))

@checkouts_blueprint.route('/<int:id>/new', methods=['GET'])
@login_required
def new_checkout(id):
    image = Image.get_by_id(id)
    user = User.get_by_id(image.user)
    client_token = generate_client_token()
    return render_template('checkouts/new.html',image=image,user=user, client_token=client_token)

@checkouts_blueprint.route('/<int:id>/payment', methods=['POST'])
@login_required
def create_checkout(id):
    amt = float(request.form['amount'])
    result = transact({
        'amount': ("%.2f" % amt ),
        'payment_method_nonce': request.form['payment_method_nonce'],
        'options': {
            "submit_for_settlement": True
        }
    })

    if result.is_success or result.transaction:
        image = Image.get_by_id(id)
        user = User.get_by_id(image.user)
        donation = Donation(donor=current_user.id,image=id,amount=result.transaction.amount)
        donation.save()
        send_pay_email(current_user,result.transaction.amount)
        send_pay_email(user,result.transaction.amount)
        return redirect(url_for('checkouts.show_checkout',transaction_id=result.transaction.id))
    else:
        for x in result.errors.deep_errors: flash('Error: %s: %s' % (x.code, x.message))
        return redirect(url_for('users.show'))

@checkouts_blueprint.route('/<transaction_id>', methods=['GET'])
@login_required
def show_checkout(transaction_id):
    transaction = find_transaction(transaction_id)
    result = {}
    if transaction.status in TRANSACTION_SUCCESS_STATUSES:
        result = {
            'header': 'Sweet Success!',
            'icon': 'success',
            'message': 'Your transaction has been successfully processed.'
        }
    else:
        result = {
            'header': 'Transaction Failed',
            'icon': 'fail',
            'message': 'Your transaction has a status of ' + transaction.status + '.'
        }

    return render_template('checkouts/show.html', transaction=transaction, result=result)

@checkouts_blueprint.route('/summary/<int:id>',methods=['GET'])
def summary(id):
    user = User.get_by_id(id)
    if current_user.id == user.id:
        images = Image.select().where(Image.user==id)
        donations = Donation.select().where(Donation.image.in_(images))
        ttl = Donation.select(fn.SUM(Donation.amount).alias('total')).where(Donation.image.in_(images))
        return render_template('checkouts/summary.html',donations=donations,ttl=ttl)
    return render_template('401.html'), 401     