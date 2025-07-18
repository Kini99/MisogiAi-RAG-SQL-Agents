"""
Sample data generation for e-commerce customer support system
"""
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from faker import Faker

from config.database import SessionLocal, init_db
from models.schema import Customer, Order, Product, Review, SupportTicket, OrderItem

fake = Faker()

def generate_sample_data(num_customers=100, num_products=50, num_orders=200, num_reviews=150, num_tickets=80):
    """Generate sample data for the database"""
    
    db = SessionLocal()
    try:
        print("Generating sample data...")
        
        # Generate customers
        print("Generating customers...")
        customers = generate_customers(db, num_customers)
        
        # Generate products
        print("Generating products...")
        products = generate_products(db, num_products)
        
        # Generate orders
        print("Generating orders...")
        orders = generate_orders(db, customers, products, num_orders)
        
        # Generate reviews
        print("Generating reviews...")
        generate_reviews(db, customers, products, num_reviews)
        
        # Generate support tickets
        print("Generating support tickets...")
        generate_support_tickets(db, customers, num_tickets)
        
        db.commit()
        print("Sample data generation completed!")
        
    except Exception as e:
        db.rollback()
        print(f"Error generating sample data: {e}")
        raise
    finally:
        db.close()

def generate_customers(db: Session, count: int):
    """Generate sample customers"""
    customers = []
    
    for i in range(count):
        customer = Customer(
            email=fake.unique.email(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone=fake.phone_number(),
            address=fake.street_address(),
            city=fake.city(),
            state=fake.state(),
            country=fake.country(),
            postal_code=fake.postcode(),
            is_active=random.choice([True, True, True, False])  # 75% active
        )
        db.add(customer)
        customers.append(customer)
    
    db.flush()
    return customers

def generate_products(db: Session, count: int):
    """Generate sample products"""
    products = []
    
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Books', 'Sports', 'Beauty', 'Toys', 'Automotive']
    brands = ['TechCorp', 'FashionBrand', 'HomeStyle', 'BookWorld', 'SportMax', 'BeautyGlow', 'ToyLand', 'AutoParts']
    
    for i in range(count):
        category = random.choice(categories)
        brand = random.choice(brands)
        
        product = Product(
            name=fake.catch_phrase(),
            description=fake.text(max_nb_chars=200),
            price=round(random.uniform(10.0, 500.0), 2),
            category=category,
            brand=brand,
            sku=f"{category[:3].upper()}{brand[:3].upper()}{i:04d}",
            stock_quantity=random.randint(0, 100),
            is_active=random.choice([True, True, True, False])  # 75% active
        )
        db.add(product)
        products.append(product)
    
    db.flush()
    return products

def generate_orders(db: Session, customers, products, count: int):
    """Generate sample orders"""
    orders = []
    
    statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
    payment_methods = ['credit_card', 'paypal', 'bank_transfer', 'cash_on_delivery']
    payment_statuses = ['pending', 'paid', 'failed', 'refunded']
    
    for i in range(count):
        customer = random.choice(customers)
        status = random.choice(statuses)
        payment_method = random.choice(payment_methods)
        payment_status = random.choice(payment_statuses)
        
        # Generate order date within last 6 months
        order_date = fake.date_time_between(
            start_date='-6 months',
            end_date='now'
        )
        
        order = Order(
            customer_id=customer.id,
            order_number=f"ORD{order_date.strftime('%Y%m%d')}{i:04d}",
            status=status,
            total_amount=0.0,  # Will be calculated after adding items
            shipping_address=fake.address(),
            billing_address=fake.address(),
            payment_method=payment_method,
            payment_status=payment_status,
            created_at=order_date,
            updated_at=order_date
        )
        db.add(order)
        orders.append(order)
    
    db.flush()
    
    # Generate order items for each order
    for order in orders:
        num_items = random.randint(1, 5)
        order_products = random.sample(products, min(num_items, len(products)))
        
        total_amount = 0.0
        for product in order_products:
            quantity = random.randint(1, 3)
            unit_price = product.price
            total_price = unit_price * quantity
            total_amount += total_price
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price
            )
            db.add(order_item)
        
        # Update order total
        order.total_amount = round(total_amount, 2)
    
    db.flush()
    return orders

def generate_reviews(db: Session, customers, products, count: int):
    """Generate sample reviews"""
    
    for i in range(count):
        customer = random.choice(customers)
        product = random.choice(products)
        
        # Check if customer has ordered this product
        has_ordered = db.query(OrderItem).join(Order).filter(
            Order.customer_id == customer.id,
            OrderItem.product_id == product.id
        ).first()
        
        review = Review(
            customer_id=customer.id,
            product_id=product.id,
            rating=random.randint(1, 5),
            title=fake.sentence(nb_words=6),
            comment=fake.text(max_nb_chars=300),
            is_verified_purchase=has_ordered is not None,
            created_at=fake.date_time_between(
                start_date='-3 months',
                end_date='now'
            )
        )
        db.add(review)

def generate_support_tickets(db: Session, customers, count: int):
    """Generate sample support tickets"""
    
    priorities = ['low', 'medium', 'high', 'urgent']
    statuses = ['open', 'in_progress', 'resolved', 'closed']
    categories = ['technical', 'billing', 'shipping', 'general']
    subjects = [
        'Order not received',
        'Payment issue',
        'Product defect',
        'Shipping delay',
        'Return request',
        'Account access problem',
        'Pricing inquiry',
        'Product availability'
    ]
    
    for i in range(count):
        customer = random.choice(customers)
        priority = random.choice(priorities)
        status = random.choice(statuses)
        category = random.choice(categories)
        subject = random.choice(subjects)
        
        # Generate ticket date within last 2 months
        ticket_date = fake.date_time_between(
            start_date='-2 months',
            end_date='now'
        )
        
        # Set resolved date if status is resolved or closed
        resolved_date = None
        if status in ['resolved', 'closed']:
            resolved_date = ticket_date + timedelta(days=random.randint(1, 14))
        
        ticket = SupportTicket(
            customer_id=customer.id,
            ticket_number=f"TKT{ticket_date.strftime('%Y%m%d')}{i:04d}",
            subject=subject,
            description=fake.text(max_nb_chars=500),
            priority=priority,
            status=status,
            category=category,
            assigned_to=fake.name() if status in ['in_progress', 'resolved', 'closed'] else None,
            resolution=fake.text(max_nb_chars=300) if status in ['resolved', 'closed'] else None,
            created_at=ticket_date,
            updated_at=ticket_date,
            resolved_at=resolved_date
        )
        db.add(ticket)

if __name__ == "__main__":
    # Initialize database
    init_db()
    
    # Generate sample data
    generate_sample_data() 