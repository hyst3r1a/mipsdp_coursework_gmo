from app.database import db


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    expiry_date = db.Column(db.Date)


class Reasons(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reason_name = db.Column(db.String(120), nullable=False)


class WasteLogs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'))
    quantity = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Integer, db.ForeignKey('reasons.id'))
    date = db.Column(db.Date, nullable=False)


class TimeDimension(db.Model):
    __tablename__ = 'time_dimension'
    time_id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer, nullable=False)
    week = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<TimeDimension (ID: {self.time_id}, Month: {self.month}, Year: {self.year})>"


class ProductDimension(db.Model):
    __tablename__ = 'product_dimension'
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(80), nullable=True)

    def __repr__(self):
        return f"<ProductDimension {self.product_name} (ID: {self.product_id})>"


class ReasonDimension(db.Model):
    __tablename__ = 'reason_dimension'
    reason_id = db.Column(db.Integer, primary_key=True)
    reason_name = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<ReasonDimension {self.reason_name} (ID: {self.reason_id})>"


class WasteFacts(db.Model):
    __tablename__ = 'waste_facts'
    waste_id = db.Column(db.Integer, primary_key=True)
    time_id = db.Column(db.Integer, db.ForeignKey('time_dimension.time_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product_dimension.product_id'), nullable=False)
    reason_id = db.Column(db.Integer, db.ForeignKey('reason_dimension.reason_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<WasteFacts (ID: {self.waste_id}, Quantity: {self.quantity}, Cost: {self.cost})>"
