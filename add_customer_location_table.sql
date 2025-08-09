-- Migration: Add CustomerLocation table for customer live location tracking
-- This enables customers to share their location for better provider matching

-- Create customer_locations table
CREATE TABLE IF NOT EXISTS customer_locations (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    accuracy DECIMAL(6, 2),
    address_components JSON,
    formatted_address TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Index for performance
    INDEX idx_customer_locations_customer_id (customer_id),
    INDEX idx_customer_locations_active (is_active),
    INDEX idx_customer_locations_updated (last_updated)
);

-- Add comment to the table
ALTER TABLE customer_locations COMMENT = 'Customer live location tracking for better service provider matching';

-- Verify table creation
SELECT 'customer_locations table created successfully' AS status;