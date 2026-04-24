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
from harvester.models import Conference

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
def sample_conference(db):
    """Тестовая конференция из WikiCFP"""
    from datetime import date
    
    html = '<html><head><title>Test Conference</title></head><body><h1>Test Conference</h1><p>About AI</p></body></html>'
    
    return Conference.objects.create(
        wikicfp_id='12345',
        title='Test Conference',
        event_date=date(2024, 5, 15),
        location='New York',
        deadline=date(2024, 4, 1),
        url='https://www.wikicfp.com/cfp/program.id/12345',
        raw_html=html,
        keywords='artificial intelligence, machine learning'
    )


@pytest.fixture
def multiple_conferences(db):
    """Создаёт несколько конференций для тестирования фильтрации"""
    from datetime import date
    
    conferences = []
    for i in range(5):
        html = f'<html><title>Conference {i}</title></html>'
        c = Conference.objects.create(
            wikicfp_id=f'{10000+i}',
            title=f'Conference {i} on AI',
            event_date=date(2024, 5 - i, 15),
            raw_html=html,
        )
        conferences.append(c)
    return conferences


@pytest.fixture
def sample_work(sample_conference):
    """Алиас фикстуры для исторической совместимости"""
    return sample_conference


@pytest.fixture
def multiple_works(multiple_conferences):
    """Алиас фикстуры для исторической совместимости"""
    return multiple_conferences
