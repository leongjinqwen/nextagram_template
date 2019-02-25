from flask import Flask, redirect, url_for, render_template, request, flash,Blueprint
import braintree
from app import app,generate_client_token,find_transaction,gateway,transact
from models.user import User

checkouts_blueprint = Blueprint('checkouts',
                            __name__,
                            template_folder='templates/')

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

@checkouts_blueprint.route('/<id>/new', methods=['GET'])
def new_checkout(id):
    user = User.get_by_id(id)
    client_token = generate_client_token()
    return render_template('checkouts/new.html',user =user, client_token=client_token)

@checkouts_blueprint.route('/<transaction_id>', methods=['GET'])
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

@checkouts_blueprint.route('/payment', methods=['POST'])
def create_checkout():
    result = transact({
        'amount': request.form['amount'],
        'payment_method_nonce': request.form['payment_method_nonce'],
        'options': {
            "submit_for_settlement": True
        }
    })

    if result.is_success or result.transaction:
        return redirect(url_for('checkouts.show_checkout',transaction_id=result.transaction.id))
    else:
        for x in result.errors.deep_errors: flash('Error: %s: %s' % (x.code, x.message))
        return redirect(url_for('users.show'))