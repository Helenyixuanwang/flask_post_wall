-- migrations/001_add_reset_tokens.sql
-- Migration: Add password reset functionality
-- Date: 2025-05-27

ALTER TABLE users 
ADD COLUMN reset_token VARCHAR(255) NULL,
ADD COLUMN reset_token_expires DATETIME NULL;