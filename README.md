# Hearing Support Mobile App - Backend

A robust Django REST API backend for the Hearing Improvement Mobile Application, featuring custom user management, Firebase authentication (Google/Apple), JWT token rotation, multilingual dynamic response translation, and email notification systems.

## Features
- **User Authentication**: Email/Password signup with OTP verification, login, password reset, and SimpleJWT token management.
- **Social Login**: Firebase ID token authentication integration for Google & Apple login.
- **Multilingual Support**: Real-time JSON API response translation (English, Hindi, Portuguese) powered by `deep-translator` and Django Caching.
- **Account & Data Management**: User profile endpoints, account deletion, profile data wipe workflows, and login history tracking.
- **Legal & Compliance**: Hosted Privacy Policy and Terms & Conditions web pages.

## Tech Stack
- **Framework**: Django 5.2 & Django REST Framework
- **Auth**: SimpleJWT, Firebase Admin SDK
- **Database**: PostgreSQL 16 & SQLite3
- **Containerization & DevOps**: Docker, Docker Compose, Nginx, AWS ECR, AWS EC2, GitLab CI/CD

## Deployment
Automated production container deployment to AWS ECR & AWS EC2 via `.gitlab-ci.yml`.
