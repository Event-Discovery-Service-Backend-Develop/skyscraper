import http from 'k6/http';
import { check, group } from 'k6';

// Стресс-тест: постепенное увеличение нагрузки до 200 конкурентных юзеров
export const options = {
  stages: [
    { duration: '2m', target: 50 },    // Рампум до 50 за 2 минуты
    { duration: '2m', target: 100 },   // Увеличиваем до 100 за 2 минуты
    { duration: '3m', target: 200 },   // Увеличиваем до 200 за 3 минуты (КРИТИЧЕСКИЙ УРОВЕНЬ)
    { duration: '3m', target: 200 },   // Держим 200 юзеров 3 минуты
    { duration: '2m', target: 0 },     // Плавное снижение
  ],
  thresholds: {
    // 95-й процентиль латенси не должен превышать 1 сек
    http_req_duration: ['p(95)<1000', 'p(99)<2000'],
    // Доля ошибок не должна быть больше 5%
    http_req_failed: ['rate<0.05'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const USERNAME = __ENV.USERNAME || 'testuser';
const PASSWORD = __ENV.PASSWORD || 'testpass12345';

export function setup() {
  const loginRes = http.post(`${BASE_URL}/api/token/`, {
    username: USERNAME,
    password: PASSWORD,
  }, {
    headers: { 'Content-Type': 'application/json' },
  });

  if (loginRes.status !== 200) {
    throw new Error(`Ошибка авторизации: статус ${loginRes.status}`);
  }

  return { token: loginRes.json('access') };
}

export default function (data) {
  const headers = {
    'Authorization': `Bearer ${data.token}`,
    'Content-Type': 'application/json',
  };

  // Основной запрос - получение работ
  group('Основной API запрос', () => {
    const res = http.get(`${BASE_URL}/api/works/?page=1&page_size=20`, { headers });
    
    check(res, {
      'статус 200': (r) => r.status === 200,
      'есть данные': (r) => r.json().results !== undefined,
      'время отклика < 1с': (r) => r.timings.duration < 1000,
    });
  });

  // Запросы с разными параметрами (имитируем реальное поведение)
  const page = Math.floor(Math.random() * 5) + 1;
  
  group('Запрос с параметрами', () => {
    const res = http.get(`${BASE_URL}/api/works/?page=${page}&publication_year=2024`, { headers });
    
    check(res, {
      'статус 200': (r) => r.status === 200,
    });
  });

  // Запрос с поиском
  group('Запрос с поиском', () => {
    const keywords = ['machine', 'learning', 'data', 'neural', 'ai'];
    const keyword = keywords[Math.floor(Math.random() * keywords.length)];
    
    const res = http.get(`${BASE_URL}/api/works/?search=${keyword}`, { headers });
    
    check(res, {
      'статус 200': (r) => r.status === 200,
    });
  });

  // Запрос healthcheck
  group('Healthcheck', () => {
    const res = http.get(`${BASE_URL}/health/`);
    
    check(res, {
      'healthcheck OK': (r) => r.status === 200,
    });
  });
}

export function handleSummary(data) {
  // Сохраняем результаты в JSON
  const summary = {
    timestamp: new Date().toISOString(),
    total_requests: data.metrics.http_reqs.value,
    failed_requests: data.metrics.http_req_failed.value,
    duration_seconds: data.state.testRunDurationMs / 1000,
  };
  
  return {
    'stress_test_results.json': JSON.stringify(summary, null, 2),
  };
}
