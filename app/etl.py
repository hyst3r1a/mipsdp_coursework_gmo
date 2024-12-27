from datetime import datetime
from app.database import db
from app.models import Inventory, WasteLogs, Reasons, TimeDimension, ProductDimension, ReasonDimension, WasteFacts

def run_etl():
    # Extract: Fetch data from OLTP tables
    waste_logs = WasteLogs.query.all()
    reasons = Reasons.query.all()
    inventory = Inventory.query.all()

    # Transform: Create dimensions and facts
    # 1. Populate TimeDimension
    time_map = {}
    for log in waste_logs:
        time_key = (log.date.year, log.date.month, log.date.day)
        if time_key not in time_map:
            existing_time = TimeDimension.query.filter_by(
                day=log.date.day,
                month=log.date.month,
                year=log.date.year
            ).first()
            if existing_time:
                time_map[time_key] = existing_time.time_id
            else:
                time_entry = TimeDimension(
                    day=log.date.day,
                    week=log.date.isocalendar()[1],
                    month=log.date.month,
                    year=log.date.year
                )
                db.session.add(time_entry)
                db.session.flush()
                time_map[time_key] = time_entry.time_id

    print(f"Time Dimension Map: {time_map}")

    # 2. Populate ProductDimension
    product_map = {}
    for item in inventory:
        existing_product = ProductDimension.query.filter_by(product_name=item.name).first()
        if existing_product:
            product_map[item.id] = existing_product.product_id
        else:
            product_entry = ProductDimension(
                product_name=item.name,
                category="Uncategorized"  # Example, customize as needed
            )
            db.session.add(product_entry)
            db.session.flush()
            product_map[item.id] = product_entry.product_id

    print(f"Product Dimension Map: {product_map}")

    # 3. Populate ReasonDimension
    reason_map = {}
    for reason in reasons:
        if reason.id not in reason_map:
            existing_reason = ReasonDimension.query.filter_by(reason_name=reason.reason_name).first()
            if existing_reason:
                reason_map[reason.id] = existing_reason.reason_id
            else:
                reason_entry = ReasonDimension(reason_name=reason.reason_name)
                db.session.add(reason_entry)
                db.session.flush()
                reason_map[reason.id] = reason_entry.reason_id

    print(f"Reason Dimension Map: {reason_map}")

    # 4. Populate WasteFacts
    for log in waste_logs:
        time_id = time_map.get((log.date.year, log.date.month, log.date.day))
        product_id = product_map.get(log.inventory_id)
        reason_id = reason_map.get(log.reason)

        if not time_id:
            print(f"Missing time mapping for date: {log.date}")
        if not product_id:
            print(f"Missing product mapping for inventory_id: {log.inventory_id}")
        if not reason_id:
            print(f"Missing reason mapping for reason_id: {log.reason}")

        if not time_id or not product_id or not reason_id:
            continue

        # Check if the fact already exists
        existing_fact = WasteFacts.query.filter_by(
            time_id=time_id,
            product_id=product_id,
            reason_id=reason_id
        ).first()

        if existing_fact:
            # Update existing fact
            existing_fact.quantity = log.quantity
            existing_fact.cost = log.quantity * 10.0  # Example cost calculation
        else:
            # Add new fact
            waste_fact = WasteFacts(
                time_id=time_id,
                product_id=product_id,
                reason_id=reason_id,
                quantity=log.quantity,
                cost=log.quantity * 10.0  # Example cost calculation
            )
            db.session.add(waste_fact)

    # Load: Commit changes
    db.session.commit()
    print("ETL process completed successfully!")
