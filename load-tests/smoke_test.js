import http from 'k6/http';
import { check, group } from 'k6';
import { Counter, Trend } from 'k6/metrics';

// Кастомные метрики
const failureRate = new Counter('failures');
const httpDuration = new Trend('http_req_duration');

// Конфиг для дымового теста
export const options = {
  stages: [
    { duration: '30s', target: 10 },   // Рампим до 10 юзеров за 30 сек
    { duration: '1m30s', target: 10 }, // Держим 10 юзеров 1.5 минуты
    { duration: '20s', target: 0 },    // Снижаем до 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.1'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const USERNAME = __ENV.USERNAME || 'testuser';
const PASSWORD = __ENV.PASSWORD || 'testpass12345';

let accessToken = '';

// Получаем токен перед запуском тестов
export function setup() {
  const loginRes = http.post(`${BASE_URL}/api/token/`, {
    username: USERNAME,
    password: PASSWORD,
  }, {
    headers: { 'Content-Type': 'application/json' },
  });

  if (loginRes.status !== 200) {
    throw new Error(`Ошибка авторизации: ${loginRes.status}`);
  }

  const token = loginRes.json('access');
  return { token };
}

export default function (data) {
  const headers = {
    'Authorization': `Bearer ${data.token}`,
    'Content-Type': 'application/json',
  };

  group('GET /api/works/ - Получение списка работ', () => {
    const res = http.get(`${BASE_URL}/api/works/`, { headers });
    httpDuration.add(res.timings.duration);
    
    check(res, {
      'статус 200': (r) => r.status === 200,
      'ответ получен': (r) => r.body.length > 0,
      'есть результаты': (r) => r.json().results !== undefined,
    }) || failureRate.add(1);
  });

  group('GET /api/works/?page=1&page_size=5 - Пагинация', () => {
    const res = http.get(`${BASE_URL}/api/works/?page=1&page_size=5`, { headers });
    
    check(res, {
      'статус 200': (r) => r.status === 200,
      'page_size=5': (r) => r.json().results.length <= 5,
    }) || failureRate.add(1);
  });

  group('GET /api/works/ с фильтром года', () => {
    const res = http.get(`${BASE_URL}/api/works/?publication_year=2024`, { headers });
    
    check(res, {
      'статус 200': (r) => r.status === 200,
      'фильтрация работает': (r) => {
        const results = r.json().results;
        return results.length === 0 || results.every(w => w.publication_year === 2024);
      },
    }) || failureRate.add(1);
  });

  group('GET /api/works/ с поиском', () => {
    const res = http.get(`${BASE_URL}/api/works/?search=machine`, { headers });
    
    check(res, {
      'статус 200': (r) => r.status === 200,
    }) || failureRate.add(1);
  });

  group('GET /health/ - Healthcheck', () => {
    const res = http.get(`${BASE_URL}/health/`);
    
    check(res, {
      'статус 200': (r) => r.status === 200,
      'healthy': (r) => r.json().status === 'healthy',
    }) || failureRate.add(1);
  });
}
