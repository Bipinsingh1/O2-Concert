-- O2 Arena Ticket System – Schema Reference (generated from Django models)
-- Run: python manage.py migrate  (applies migrations automatically)
-- This file documents the intended normalized schema.

-- accounts_customuser
CREATE TABLE IF NOT EXISTS accounts_customuser (
    id BIGSERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) NOT NULL UNIQUE,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined TIMESTAMP WITH TIME ZONE NOT NULL,
    phone_number VARCHAR(20) NOT NULL DEFAULT '',
    date_of_birth DATE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- ticket_sales_ticketcategory
CREATE TABLE IF NOT EXISTS ticket_sales_ticketcategory (
    id BIGSERIAL PRIMARY KEY,
    category_type VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    price NUMERIC(8,2) NOT NULL,
    is_refundable BOOLEAN NOT NULL DEFAULT FALSE,
    is_amendable BOOLEAN NOT NULL DEFAULT FALSE,
    total_available INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- ticket_sales_ticket
CREATE TABLE IF NOT EXISTS ticket_sales_ticket (
    id BIGSERIAL PRIMARY KEY,
    ticket_number VARCHAR(30) NOT NULL UNIQUE,
    category_id BIGINT NOT NULL REFERENCES ticket_sales_ticketcategory(id),
    owner_id BIGINT REFERENCES accounts_customuser(id),
    guest_name VARCHAR(200) NOT NULL DEFAULT '',
    guest_email VARCHAR(254) NOT NULL DEFAULT '',
    is_guest_purchase BOOLEAN NOT NULL DEFAULT FALSE,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    purchase_date TIMESTAMP WITH TIME ZONE NOT NULL,
    amount_paid NUMERIC(8,2) NOT NULL,
    original_price NUMERIC(8,2) NOT NULL,
    discount_percent SMALLINT NOT NULL DEFAULT 0,
    discount_amount NUMERIC(8,2) NOT NULL DEFAULT 0,
    qr_code VARCHAR(100) NOT NULL DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- ticket_sales_ticketholder
CREATE TABLE IF NOT EXISTS ticket_sales_ticketholder (
    id BIGSERIAL PRIMARY KEY,
    ticket_id BIGINT NOT NULL REFERENCES ticket_sales_ticket(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    age_group VARCHAR(10) NOT NULL DEFAULT 'adult'
);

-- checkout_order
CREATE TABLE IF NOT EXISTS checkout_order (
    id BIGSERIAL PRIMARY KEY,
    order_number VARCHAR(30) NOT NULL UNIQUE,
    user_id BIGINT REFERENCES accounts_customuser(id),
    guest_email VARCHAR(254) NOT NULL DEFAULT '',
    ticket_id BIGINT NOT NULL UNIQUE REFERENCES ticket_sales_ticket(id),
    subtotal NUMERIC(8,2) NOT NULL,
    discount_amount NUMERIC(8,2) NOT NULL DEFAULT 0,
    total_amount NUMERIC(8,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- checkout_payment
CREATE TABLE IF NOT EXISTS checkout_payment (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL UNIQUE REFERENCES checkout_order(id),
    amount NUMERIC(8,2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'GBP',
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    stripe_payment_intent_id VARCHAR(200) NOT NULL DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- checkout_refund
CREATE TABLE IF NOT EXISTS checkout_refund (
    id BIGSERIAL PRIMARY KEY,
    payment_id BIGINT NOT NULL REFERENCES checkout_payment(id),
    amount NUMERIC(8,2) NOT NULL,
    reason TEXT NOT NULL DEFAULT '',
    stripe_refund_id VARCHAR(200) NOT NULL DEFAULT '',
    processed_by_id BIGINT REFERENCES accounts_customuser(id),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
