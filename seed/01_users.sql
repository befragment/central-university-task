-- Seed: Users
-- ============================================
-- | Email              | Password     |
-- |--------------------|--------------|
-- | ivan@example.com   | password123  |
-- | maria@example.com  | password123  |
-- | alex@example.com   | password123  |
-- ============================================
-- Hash: bcrypt, cost=12

INSERT INTO "user" (id, created_at, name, email, pass_hash)
VALUES ('11111111-1111-1111-1111-111111111111', '2025-01-10', 'Иван Петров', 'ivan@example.com',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA0wQQVQJhC'),
       ('22222222-2222-2222-2222-222222222222', '2025-01-11', 'Мария Сидорова', 'maria@example.com',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA0wQQVQJhC'),
       ('33333333-3333-3333-3333-333333333333', '2025-01-12', 'Алексей Козлов', 'alex@example.com',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA0wQQVQJhC') ON CONFLICT (id) DO NOTHING;