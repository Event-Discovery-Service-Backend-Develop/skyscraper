import os
import django
from django.conf import settings

# Это нужно для инициализации Django при запуске тестов
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

if not settings.configured:
    django.setup()

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from harvester.models import Work

User = get_user_model()


@pytest.fixture
def api_client():
    """Клиент для API запросов"""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    """API клиент с JWT токеном"""
    from rest_framework_simplejwt.tokens import RefreshToken
    
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    return api_client


@pytest.fixture
def user(db):
    """Тестовый пользователь"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass12345'
    )


@pytest.fixture
def sample_work(db):
    """Тестовая научная работа из OpenAlex"""
    import json
    
    raw = {
        'id': 'https://openalex.org/W123456',
        'title': 'Test Work on Machine Learning',
        'doi': 'https://doi.org/10.1234/test',
        'publication_year': 2024,
        'keywords': ['machine learning', 'neural networks']
    }
    
    return Work.objects.create(
        openalex_id='W123456',
        title='Test Work on Machine Learning',
        doi='10.1234/test',
        publication_year=2024,
        raw_json=json.dumps(raw),
        keywords='machine learning, neural networks'
    )


@pytest.fixture
def multiple_works(db):
    """Создаёт несколько работ для тестирования фильтрации"""
    import json
    
    works = []
    for i in range(5):
        raw = {
            'id': f'https://openalex.org/W{100000+i}',
            'title': f'Work {i} on AI',
            'publication_year': 2024 - i,
        }
        w = Work.objects.create(
            openalex_id=f'W{100000+i}',
            title=f'Work {i} on AI',
            publication_year=2024 - i,
            raw_json=json.dumps(raw),
        )
        works.append(w)
    return works
