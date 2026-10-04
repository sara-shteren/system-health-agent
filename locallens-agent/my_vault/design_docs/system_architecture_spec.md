# System Architecture Specification

## Overview
This document describes the architecture of our e-commerce platform.

## Database
We use **PostgreSQL 15** as our primary database.

### Tables
- `users` - User accounts and profiles
- `products` - Product catalog
- `orders` - Purchase orders
- `inventory` - Stock levels

## Tech Stack
- Backend: Python FastAPI
- Frontend: React 18
- Database: PostgreSQL 15
- Cache: Redis
- Message Queue: RabbitMQ

## API Design
RESTful API with OpenAPI 3.0 specification.
All endpoints require JWT authentication.

## Security
- All data encrypted at rest (AES-256)
- TLS 1.3 for data in transit
- Rate limiting: 100 requests/minute per user
