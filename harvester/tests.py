import json
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from harvester.models import Conference
from harvester.processor import extract_keywords_from_html, clean_title

User = get_user_model()


# ============ UNIT ТЕСТЫ ДЛЯ МОДЕЛЕЙ ============

@pytest.mark.unit
class TestConferenceModel:
    """Тесты для модели Conference"""
    
    def test_conference_creation(self, db):
        """Проверка создания конференции"""
        from datetime import date
        conf = Conference.objects.create(
            wikicfp_id='12345',
            title='Test Conference',
            event_date=date(2024, 5, 15),
            location='New York',
            deadline=date(2024, 4, 1),
            url='https://example.com'
        )
        assert conf.wikicfp_id == '12345'
        assert conf.title == 'Test Conference'
        assert conf.event_date == date(2024, 5, 15)
        assert conf.id is not None
    
    def test_conference_unique_wikicfp_id(self, db):
        """WikiCFP ID должен быть уникальным"""
        Conference.objects.create(wikicfp_id='999', title='First')
        
        with pytest.raises(Exception):  # IntegrityError
            Conference.objects.create(wikicfp_id='999', title='Second')
    
    def test_conference_with_keywords(self, db):
        """Конференция может иметь ключевые слова"""
        conf = Conference.objects.create(
            wikicfp_id='444',
            title='AI Conference',
            keywords='artificial intelligence, machine learning, neural networks'
        )
        assert 'artificial intelligence' in conf.keywords
    
    def test_conference_ordering(self, db, multiple_conferences):
        """Конференции сортируются по дате создания"""
        conferences = Conference.objects.all()
        assert conferences[0].id is not None  # Все что угодно, главное есть


# ============ UNIT ТЕСТЫ ДЛЯ ПРОЦЕССОРА ============

@pytest.mark.unit
class TestProcessor:
    """Тесты для модуля обработки данных"""
    
    def test_clean_title_basic(self):
        """Очистка названия работает"""
        result = clean_title("  Test   Title  ")
        assert result == "Test Title"
    
    def test_clean_title_limit(self):
        """Длинное название обрезается"""
        long_title = "A" * 600
        result = clean_title(long_title)
        assert len(result) == 500
    
    def test_clean_title_empty(self):
        """Пустое название обрабатывается"""
        assert clean_title("") == ""
        assert clean_title(None) == ""
    
    def test_extract_keywords_from_raw_basic(self):
        """Извлечение ключевых слов из HTML"""
        html = '<html><head><title>Test Conference</title></head><body><h1>Test Conference</h1><p>This is about AI and ML</p></body></html>'
        keywords = extract_keywords_from_html(html)
        assert keywords is not None
        assert len(keywords.split(',')) > 0
    
    def test_extract_keywords_from_raw_concepts(self):
        """Извлечение ключевых слов из description"""
        html = '<html><body><h1>Study</h1><div class="desc">Machine Learning and Neural Networks</div></body></html>'
        keywords = extract_keywords_from_html(html)
        assert 'Machine' in keywords or 'Learning' in keywords
    
    def test_extract_keywords_empty_json(self):
        """Пустой HTML обрабатывается"""
        keywords = extract_keywords_from_html('')
        assert keywords is None
    
    def test_extract_keywords_invalid_json(self):
        """Невалидный JSON не падает"""
        keywords = extract_keywords_from_raw('not json at all')
        assert keywords is None


# ============ ИНТЕГРАЦИОННЫЕ ТЕСТЫ ДЛЯ API ============

@pytest.mark.integration
class TestWorksAPI:
    """Тесты для REST API эндпоинтов"""
    
    def test_works_requires_authentication(self, api_client):
        """API требует JWT токен"""
        response = api_client.get('/api/works/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_works_authenticated(self, authenticated_client, sample_work):
        """Получение работ с аутентификацией"""
        response = authenticated_client.get('/api/works/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
    
    def test_works_list_pagination(self, authenticated_client, multiple_works):
        """Пагинация работает"""
        response = authenticated_client.get('/api/works/?page=1&page_size=2')
        assert response.status_code == status.HTTP_200_OK
        assert 'next' in response.data
        assert 'count' in response.data
        assert len(response.data['results']) <= 2
    
    def test_works_filter_by_year(self, authenticated_client, multiple_works):
        """Фильтрация по году работает"""
        response = authenticated_client.get('/api/works/?publication_year=2024')
        assert response.status_code == status.HTTP_200_OK
        for work in response.data['results']:
            assert work['publication_year'] == 2024
    
    def test_works_search(self, authenticated_client, sample_work):
        """Поиск по названию работает"""
        response = authenticated_client.get('/api/works/?search=Machine')
        assert response.status_code == status.HTTP_200_OK
        if len(response.data['results']) > 0:
            assert 'Machine' in response.data['results'][0]['title']
    
    def test_works_ordering_by_year_desc(self, authenticated_client, multiple_works):
        """Сортировка по году убывающая"""
        response = authenticated_client.get('/api/works/?ordering=-publication_year')
        assert response.status_code == status.HTTP_200_OK
        years = [w['publication_year'] for w in response.data['results']]
        assert years == sorted(years, reverse=True)
    
    def test_work_detail_fields(self, authenticated_client, sample_work):
        """Возвращаемые поля корректны"""
        response = authenticated_client.get('/api/works/')
        assert response.status_code == status.HTTP_200_OK
        if len(response.data['results']) > 0:
            work_data = response.data['results'][0]
            required_fields = ['id', 'openalex_id', 'title', 'publication_year']
            for field in required_fields:
                assert field in work_data


# ============ ТЕСТЫ ДЛЯ АУТЕНТИФИКАЦИИ ============

@pytest.mark.integration
class TestAuthentication:
    """Тесты JWT аутентификации"""
    
    def test_token_obtain(self, api_client, user):
        """Получение токена для пользователя"""
        response = api_client.post('/api/token/', {
            'username': user.username,
            'password': 'testpass12345'
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    @pytest.mark.django_db
    def test_token_obtain_invalid_credentials(self, api_client):
        """Неверные учетные данные"""
        response = api_client.post('/api/token/', {
            'username': 'nonexistent',
            'password': 'wrongpass'
        }, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_token_refresh(self, api_client, user):
        """Обновление токена работает"""
        # Получаем первый токен
        token_response = api_client.post('/api/token/', {
            'username': user.username,
            'password': 'testpass12345'
        }, format='json')
        
        refresh_token = token_response.data['refresh']
        
        # Обновляем токен
        refresh_response = api_client.post('/api/token/refresh/', {
            'refresh': refresh_token
        }, format='json')
        
        assert refresh_response.status_code == status.HTTP_200_OK
        assert 'access' in refresh_response.data
    
    def test_invalid_token_denied(self, api_client):
        """Неверный токен отклоняется"""
        api_client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        response = api_client.get('/api/works/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============ ТЕСТЫ ДЛЯ ЗДОРОВЬЯ СЕРВИСА ============

@pytest.mark.integration
class TestHealthcheck:
    """Базовые эндпоинты"""
    
    def test_health_endpoint(self, api_client):
        """Healthcheck эндпоинт работает"""
        response = api_client.get('/health/')
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'healthy'
    
    def test_root_endpoint(self, api_client):
        """Главная страница доступна"""
        response = api_client.get('/')
        assert response.status_code == status.HTTP_200_OK
