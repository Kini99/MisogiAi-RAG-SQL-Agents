-- Price Comparison Platform Database Initialization
-- This script sets up the initial database structure and sample data

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create sample platforms
INSERT INTO platforms (name, display_name, slug, is_active, priority, base_url, api_endpoint, created_at, updated_at) VALUES
('Blinkit', 'Blinkit', 'blinkit', true, 1, 'https://blinkit.com', 'https://blinkit.com/api', NOW(), NOW()),
('Zepto', 'Zepto', 'zepto', true, 2, 'https://zepto.in', 'https://zepto.in/api', NOW(), NOW()),
('Instamart', 'Swiggy Instamart', 'instamart', true, 3, 'https://instamart.in', 'https://instamart.in/api', NOW(), NOW()),
('BigBasket Now', 'BigBasket Now', 'bigbasket_now', true, 4, 'https://bigbasket.com', 'https://bigbasket.com/api', NOW(), NOW())
ON CONFLICT (slug) DO NOTHING;

-- Create sample categories
INSERT INTO categories (name, slug, parent_id, is_active, priority, created_at, updated_at) VALUES
('Fruits & Vegetables', 'fruits-vegetables', NULL, true, 1, NOW(), NOW()),
('Dairy & Eggs', 'dairy-eggs', NULL, true, 2, NOW(), NOW()),
('Beverages', 'beverages', NULL, true, 3, NOW(), NOW()),
('Snacks', 'snacks', NULL, true, 4, NOW(), NOW()),
('Personal Care', 'personal-care', NULL, true, 5, NOW(), NOW()),
('Fresh Fruits', 'fresh-fruits', 1, true, 1, NOW(), NOW()),
('Fresh Vegetables', 'fresh-vegetables', 1, true, 2, NOW(), NOW()),
('Milk & Dairy', 'milk-dairy', 2, true, 1, NOW(), NOW()),
('Soft Drinks', 'soft-drinks', 3, true, 1, NOW(), NOW()),
('Packaged Snacks', 'packaged-snacks', 4, true, 1, NOW(), NOW())
ON CONFLICT (slug) DO NOTHING;

-- Create sample brands
INSERT INTO brands (name, slug, description, logo_url, is_active, created_at, updated_at) VALUES
('Amul', 'amul', 'Leading dairy brand in India', 'https://example.com/amul-logo.png', true, NOW(), NOW()),
('Coca Cola', 'coca-cola', 'Global beverage company', 'https://example.com/coca-cola-logo.png', true, NOW(), NOW()),
('Lay''s', 'lays', 'Popular snack brand', 'https://example.com/lays-logo.png', true, NOW(), NOW()),
('Britannia', 'britannia', 'Trusted food brand', 'https://example.com/britannia-logo.png', true, NOW(), NOW()),
('Organic Valley', 'organic-valley', 'Organic dairy products', 'https://example.com/organic-valley-logo.png', true, NOW(), NOW())
ON CONFLICT (slug) DO NOTHING;

-- Create sample products
INSERT INTO products (name, slug, description, category_id, brand_id, image_url, weight, weight_unit, is_active, created_at, updated_at) VALUES
('Fresh Onions', 'fresh-onions', 'Fresh red onions, 1kg', 7, NULL, 'https://example.com/onions.jpg', 1.0, 'kg', true, NOW(), NOW()),
('Organic Bananas', 'organic-bananas', 'Organic yellow bananas, 6 pieces', 6, 5, 'https://example.com/bananas.jpg', 0.5, 'kg', true, NOW(), NOW()),
('Fresh Milk 1L', 'fresh-milk-1l', 'Fresh cow milk, 1 liter', 8, 1, 'https://example.com/milk.jpg', 1.0, 'l', true, NOW(), NOW()),
('Coca Cola 2L', 'coca-cola-2l', 'Coca Cola soft drink, 2 liters', 9, 2, 'https://example.com/cola.jpg', 2.0, 'l', true, NOW(), NOW()),
('Lay''s Classic Chips', 'lays-classic-chips', 'Classic potato chips, 30g', 10, 3, 'https://example.com/chips.jpg', 30.0, 'g', true, NOW(), NOW()),
('Britannia Bread', 'britannia-bread', 'Fresh white bread, 400g', 8, 4, 'https://example.com/bread.jpg', 400.0, 'g', true, NOW(), NOW()),
('Fresh Tomatoes', 'fresh-tomatoes', 'Fresh red tomatoes, 500g', 7, NULL, 'https://example.com/tomatoes.jpg', 0.5, 'kg', true, NOW(), NOW())
ON CONFLICT (slug) DO NOTHING;

-- Create sample prices (current prices)
INSERT INTO prices (product_id, platform_id, current_price, mrp, currency, is_active, created_at, updated_at) VALUES
(1, 1, 45.0, 60.0, 'INR', true, NOW(), NOW()),
(1, 2, 48.0, 65.0, 'INR', true, NOW(), NOW()),
(1, 3, 50.0, 62.0, 'INR', true, NOW(), NOW()),
(1, 4, 52.0, 68.0, 'INR', true, NOW(), NOW()),
(2, 1, 72.0, 120.0, 'INR', true, NOW(), NOW()),
(2, 2, 75.0, 125.0, 'INR', true, NOW(), NOW()),
(2, 3, 78.0, 130.0, 'INR', true, NOW(), NOW()),
(2, 4, 80.0, 135.0, 'INR', true, NOW(), NOW()),
(3, 1, 45.5, 65.0, 'INR', true, NOW(), NOW()),
(3, 2, 47.0, 67.0, 'INR', true, NOW(), NOW()),
(3, 3, 49.0, 70.0, 'INR', true, NOW(), NOW()),
(3, 4, 51.0, 72.0, 'INR', true, NOW(), NOW()),
(4, 1, 66.5, 95.0, 'INR', true, NOW(), NOW()),
(4, 2, 68.0, 98.0, 'INR', true, NOW(), NOW()),
(4, 3, 70.0, 100.0, 'INR', true, NOW(), NOW()),
(4, 4, 72.0, 105.0, 'INR', true, NOW(), NOW()),
(5, 1, 12.0, 20.0, 'INR', true, NOW(), NOW()),
(5, 2, 13.0, 22.0, 'INR', true, NOW(), NOW()),
(5, 3, 14.0, 25.0, 'INR', true, NOW(), NOW()),
(5, 4, 15.0, 28.0, 'INR', true, NOW(), NOW()),
(6, 1, 24.5, 35.0, 'INR', true, NOW(), NOW()),
(6, 2, 26.0, 38.0, 'INR', true, NOW(), NOW()),
(6, 3, 28.0, 40.0, 'INR', true, NOW(), NOW()),
(6, 4, 30.0, 42.0, 'INR', true, NOW(), NOW()),
(7, 1, 24.0, 40.0, 'INR', true, NOW(), NOW()),
(7, 2, 26.0, 42.0, 'INR', true, NOW(), NOW()),
(7, 3, 28.0, 45.0, 'INR', true, NOW(), NOW()),
(7, 4, 30.0, 48.0, 'INR', true, NOW(), NOW());

-- Create sample discounts
INSERT INTO discounts (product_id, platform_id, discount_type, discount_value, discount_percentage, start_date, end_date, is_active, created_at, updated_at) VALUES
(1, 1, 'percentage', 15.0, 25.0, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(1, 2, 'percentage', 17.0, 26.2, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(1, 3, 'percentage', 12.0, 19.4, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(1, 4, 'percentage', 16.0, 23.5, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(2, 1, 'percentage', 48.0, 40.0, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(2, 2, 'percentage', 50.0, 40.0, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(2, 3, 'percentage', 52.0, 40.0, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(2, 4, 'percentage', 55.0, 40.7, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(3, 1, 'percentage', 19.5, 30.0, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(3, 2, 'percentage', 20.0, 29.9, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(3, 3, 'percentage', 21.0, 30.0, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(3, 4, 'percentage', 21.0, 29.2, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(4, 1, 'percentage', 28.5, 30.0, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(4, 2, 'percentage', 30.0, 30.6, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(4, 3, 'percentage', 30.0, 30.0, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(4, 4, 'percentage', 33.0, 31.4, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(5, 1, 'percentage', 8.0, 40.0, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(5, 2, 'percentage', 9.0, 40.9, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(5, 3, 'percentage', 11.0, 44.0, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(5, 4, 'percentage', 13.0, 46.4, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(6, 1, 'percentage', 10.5, 30.0, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(6, 2, 'percentage', 12.0, 31.6, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(6, 3, 'percentage', 12.0, 30.0, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(6, 4, 'percentage', 12.0, 28.6, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(7, 1, 'percentage', 16.0, 40.0, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(7, 2, 'percentage', 16.0, 38.1, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(7, 3, 'percentage', 17.0, 37.8, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW()),
(7, 4, 'percentage', 18.0, 37.5, NOW(), NOW() + INTERVAL '30 days', true, NOW(), NOW());

-- Create sample availability data
INSERT INTO availability (product_id, platform_id, is_available, stock_quantity, delivery_time_minutes, is_active, created_at, updated_at) VALUES
(1, 1, true, 100, 15, true, NOW(), NOW()),
(1, 2, true, 85, 10, true, NOW(), NOW()),
(1, 3, true, 70, 20, true, NOW(), NOW()),
(1, 4, true, 95, 25, true, NOW(), NOW()),
(2, 1, true, 50, 15, true, NOW(), NOW()),
(2, 2, true, 45, 10, true, NOW(), NOW()),
(2, 3, true, 40, 20, true, NOW(), NOW()),
(2, 4, true, 55, 25, true, NOW(), NOW()),
(3, 1, true, 200, 15, true, NOW(), NOW()),
(3, 2, true, 180, 10, true, NOW(), NOW()),
(3, 3, true, 150, 20, true, NOW(), NOW()),
(3, 4, true, 220, 25, true, NOW(), NOW()),
(4, 1, true, 80, 15, true, NOW(), NOW()),
(4, 2, true, 75, 10, true, NOW(), NOW()),
(4, 3, true, 65, 20, true, NOW(), NOW()),
(4, 4, true, 90, 25, true, NOW(), NOW()),
(5, 1, true, 150, 15, true, NOW(), NOW()),
(5, 2, true, 140, 10, true, NOW(), NOW()),
(5, 3, true, 120, 20, true, NOW(), NOW()),
(5, 4, true, 160, 25, true, NOW(), NOW()),
(6, 1, true, 60, 15, true, NOW(), NOW()),
(6, 2, true, 55, 10, true, NOW(), NOW()),
(6, 3, true, 50, 20, true, NOW(), NOW()),
(6, 4, true, 70, 25, true, NOW(), NOW()),
(7, 1, true, 90, 15, true, NOW(), NOW()),
(7, 2, true, 85, 10, true, NOW(), NOW()),
(7, 3, true, 75, 20, true, NOW(), NOW()),
(7, 4, true, 100, 25, true, NOW(), NOW());

-- Create sample query analytics
INSERT INTO query_analytics (query_text, query_type, success, execution_time_ms, result_count, user_id, created_at) VALUES
('Which app has cheapest onions right now?', 'comparison', true, 245, 4, NULL, NOW() - INTERVAL '2 hours'),
('Show products with 30%+ discount on Blinkit', 'search', true, 189, 15, NULL, NOW() - INTERVAL '3 hours'),
('Compare fruit prices between Zepto and Instamart', 'comparison', true, 312, 8, NULL, NOW() - INTERVAL '4 hours'),
('Find best deals for ₹1000 grocery list', 'search', true, 456, 25, NULL, NOW() - INTERVAL '5 hours'),
('What''s the cheapest milk delivery today?', 'comparison', true, 178, 4, NULL, NOW() - INTERVAL '6 hours');

-- Create sample popular queries
INSERT INTO popular_queries (query_text, search_count, success_rate, last_searched_at, created_at, updated_at) VALUES
('cheapest onions', 45, 96.2, NOW(), NOW(), NOW()),
('milk delivery', 38, 94.7, NOW(), NOW(), NOW()),
('fruits discount', 32, 91.8, NOW(), NOW(), NOW()),
('vegetables price', 28, 89.3, NOW(), NOW(), NOW()),
('beverages compare', 25, 92.0, NOW(), NOW(), NOW());

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_brand_id ON products(brand_id);
CREATE INDEX IF NOT EXISTS idx_prices_product_id ON prices(product_id);
CREATE INDEX IF NOT EXISTS idx_prices_platform_id ON prices(platform_id);
CREATE INDEX IF NOT EXISTS idx_discounts_product_id ON discounts(product_id);
CREATE INDEX IF NOT EXISTS idx_availability_product_id ON availability(product_id);
CREATE INDEX IF NOT EXISTS idx_query_analytics_created_at ON query_analytics(created_at);
CREATE INDEX IF NOT EXISTS idx_popular_queries_search_count ON popular_queries(search_count DESC);

-- Create full-text search indexes
CREATE INDEX IF NOT EXISTS idx_products_name_fts ON products USING gin(to_tsvector('english', name));
CREATE INDEX IF NOT EXISTS idx_products_description_fts ON products USING gin(to_tsvector('english', description));

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres; 