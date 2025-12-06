-- Seed: Users
-- ============================================
-- | Email              | Password     |
-- |--------------------|--------------|
-- | ivan@example.com   | password123  |
-- | maria@example.com  | password123  |
-- | alex@example.com   | password123  |
-- ============================================

INSERT INTO "user" (id, created_at, name, email, pass_hash)
VALUES
    ('71038400-4523-43f3-8f2c-38722d0c4c89', '2025-01-10', 'Иван Петров', 'ivan@example.com',
     '$2b$12$fQ722.ymNPXRNLyj5fiPn.HAKJqvdrPVwToucDdvrDgVeLuJtumBe'),
    ('a450092b-15e7-4283-9710-7be1ed7886b0', '2025-01-11', 'Мария Сидорова', 'maria@example.com',
     '$2b$12$fQ722.ymNPXRNLyj5fiPn.HAKJqvdrPVwToucDdvrDgVeLuJtumBe'),
    ('efee247e-4350-483a-bb51-09453662ad07', '2025-01-12', 'Алексей Козлов', 'alex@example.com',
     '$2b$12$fQ722.ymNPXRNLyj5fiPn.HAKJqvdrPVwToucDdvrDgVeLuJtumBe')
ON CONFLICT (id) DO NOTHING;

