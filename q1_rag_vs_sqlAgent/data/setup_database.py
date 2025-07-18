"""
Database setup script for e-commerce customer support system
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import init_db, engine
from config.settings import settings
from data.sample_data import generate_sample_data

def setup_database():
    """Set up the database with tables and sample data"""
    print("Setting up e-commerce customer support database...")
    
    # Test database connection
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Database connection successful!")
    except OperationalError as e:
        print(f"Database connection failed: {e}")
        print("Please ensure PostgreSQL is running and DATABASE_URL is correctly configured.")
        return False
    
    # Create tables
    print("Creating database tables...")
    try:
        init_db()
        print("Tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False
    
    # Check if data already exists
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT COUNT(*) FROM customers"))
            customer_count = result.scalar()
            
            if customer_count > 0:
                print(f"Database already contains {customer_count} customers.")
                response = input("Do you want to regenerate sample data? (y/N): ")
                if response.lower() != 'y':
                    print("Using existing data.")
                    return True
    except Exception as e:
        print(f"Error checking existing data: {e}")
    
    # Generate sample data
    print("Generating sample data...")
    try:
        generate_sample_data(
            num_customers=100,
            num_products=50,
            num_orders=200,
            num_reviews=150,
            num_tickets=80
        )
        print("Sample data generated successfully!")
    except Exception as e:
        print(f"Error generating sample data: {e}")
        return False
    
    # Verify data generation
    try:
        with engine.connect() as connection:
            # Check customer count
            result = connection.execute(text("SELECT COUNT(*) FROM customers"))
            customer_count = result.scalar()
            
            # Check product count
            result = connection.execute(text("SELECT COUNT(*) FROM products"))
            product_count = result.scalar()
            
            # Check order count
            result = connection.execute(text("SELECT COUNT(*) FROM orders"))
            order_count = result.scalar()
            
            # Check review count
            result = connection.execute(text("SELECT COUNT(*) FROM reviews"))
            review_count = result.scalar()
            
            # Check ticket count
            result = connection.execute(text("SELECT COUNT(*) FROM support_tickets"))
            ticket_count = result.scalar()
            
            print("\nDatabase setup completed successfully!")
            print(f"Generated data:")
            print(f"  - Customers: {customer_count}")
            print(f"  - Products: {product_count}")
            print(f"  - Orders: {order_count}")
            print(f"  - Reviews: {review_count}")
            print(f"  - Support Tickets: {ticket_count}")
            
    except Exception as e:
        print(f"Error verifying data: {e}")
        return False
    
    return True

def create_indexes():
    """Create additional indexes for better performance"""
    print("Creating database indexes...")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email)",
        "CREATE INDEX IF NOT EXISTS idx_customers_city ON customers(city)",
        "CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id)",
        "CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)",
        "CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)",
        "CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand)",
        "CREATE INDEX IF NOT EXISTS idx_reviews_customer_id ON reviews(customer_id)",
        "CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON reviews(product_id)",
        "CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating)",
        "CREATE INDEX IF NOT EXISTS idx_support_tickets_customer_id ON support_tickets(customer_id)",
        "CREATE INDEX IF NOT EXISTS idx_support_tickets_status ON support_tickets(status)",
        "CREATE INDEX IF NOT EXISTS idx_support_tickets_priority ON support_tickets(priority)",
        "CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id)",
        "CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id)"
    ]
    
    try:
        with engine.connect() as connection:
            for index_sql in indexes:
                connection.execute(text(index_sql))
            connection.commit()
        print("Indexes created successfully!")
    except Exception as e:
        print(f"Error creating indexes: {e}")

def main():
    """Main setup function"""
    print("=" * 60)
    print("E-commerce Customer Support System - Database Setup")
    print("=" * 60)
    
    # Check environment
    if not settings.DATABASE_URL:
        print("ERROR: DATABASE_URL not configured!")
        print("Please set the DATABASE_URL environment variable.")
        return False
    
    # Setup database
    if not setup_database():
        print("Database setup failed!")
        return False
    
    # Create indexes
    create_indexes()
    
    print("\n" + "=" * 60)
    print("Database setup completed successfully!")
    print("You can now run the benchmark or demo applications.")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 