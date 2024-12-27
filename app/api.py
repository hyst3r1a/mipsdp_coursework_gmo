from flask import Blueprint, request, jsonify
from app.database import db
from app.models import Inventory, WasteLogs, Reasons, TimeDimension, ProductDimension, ReasonDimension, WasteFacts
from datetime import datetime
from app.etl import run_etl

api = Blueprint('api', __name__)


# Inventory CRUD
@api.route('/inventory', methods=['GET'])
def get_inventory():
    inventory = Inventory.query.all()
    return jsonify([{
        'id': item.id,
        'name': item.name,
        'quantity': item.quantity,
        'expiry_date': item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else None
    } for item in inventory])


@api.route('/inventory', methods=['POST'])
def add_inventory():
    data = request.json
    expiry_date = None
    if 'expiry_date' in data and data['expiry_date']:
        try:
            expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    new_item = Inventory(
        name=data['name'],
        quantity=data['quantity'],
        expiry_date=expiry_date
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({'message': 'Inventory item added', 'id': new_item.id})


@api.route('/inventory/<int:item_id>', methods=['PUT'])
def update_inventory(item_id):
    data = request.json
    item = Inventory.query.get_or_404(item_id)

    # Конвертація expiry_date, якщо воно передано
    expiry_date = item.expiry_date
    if 'expiry_date' in data and data['expiry_date']:
        try:
            expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    # Оновлення полів
    item.name = data.get('name', item.name)
    item.quantity = data.get('quantity', item.quantity)
    item.expiry_date = expiry_date
    db.session.commit()

    return jsonify({'message': 'Inventory item updated'})


@api.route('/inventory/<int:item_id>', methods=['DELETE'])
def delete_inventory(item_id):
    item = Inventory.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Inventory item deleted'})


# WasteLogs CRUD
@api.route('/waste', methods=['POST'])
def add_waste():
    data = request.json
    try:
        log_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    new_log = WasteLogs(
        inventory_id=data['inventory_id'],
        quantity=data['quantity'],
        reason=data['reason'],
        date=log_date
    )
    db.session.add(new_log)
    db.session.commit()
    return jsonify({'message': 'Waste log added', 'id': new_log.id})


@api.route('/waste', methods=['GET'])
def get_waste_logs():
    logs = WasteLogs.query.all()
    return jsonify([{
        'id': log.id,
        'inventory_id': log.inventory_id,
        'quantity': log.quantity,
        'reason': log.reason,
        'date': log.date.strftime('%Y-%m-%d')
    } for log in logs])


@api.route('/etl', methods=['POST'])
def run_etl_endpoint():
    try:
        run_etl()
        return jsonify({'message': 'ETL process completed successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
