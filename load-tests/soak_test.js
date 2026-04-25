import http from 'k6/http';
import { check } from 'k6';

// Soak-тест: умеренная нагрузка длительное время (10 минут)
// Помогает найти утечки памяти и проблемы с долгосрочной стабильностью
export const options = {
  stages: [
    { duration: '1m', target: 30 },    // Рампум до 30 юзеров
    { duration: '9m', target: 30 },    // Держим 30 юзеров 9 минут
    { duration: '1m', target: 0 },     // Снижаем
  ],
  thresholds: {
    http_req_duration: ['p(99)<1500'],
    http_req_failed: ['rate<0.02'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const USERNAME = __ENV.USERNAME || 'testuser';
const PASSWORD = __ENV.PASSWORD || 'testpass12345';

export function setup() {
  const res = http.post(`${BASE_URL}/api/token/`, {
    username: USERNAME,
    password: PASSWORD,
  }, {
    headers: { 'Content-Type': 'application/json' },
  });

  if (res.status !== 200) {
    throw new Error(`Ошибка при авторизации: ${res.status}`);
  }

  return { token: res.json('access') };
}

export default function (data) {
  const headers = {
    'Authorization': `Bearer ${data.token}`,
  };

  // Последовательность реалистичных операций
  
  // 1. Пользователь смотрит список работ
  const listRes = http.get(`${BASE_URL}/api/works/?page=1&page_size=20`, { headers });
  check(listRes, {
    'список загружен': (r) => r.status === 200,
  });

  // 2. Пользователь переходит на вторую страницу
  const page2Res = http.get(`${BASE_URL}/api/works/?page=2&page_size=20`, { headers });
  check(page2Res, {
    'вторая страница загружена': (r) => r.status === 200,
  });

  // 3. Пользователь фильтрует по году
  const filterRes = http.get(`${BASE_URL}/api/works/?publication_year=2023`, { headers });
  check(filterRes, {
    'фильтрация работает': (r) => r.status === 200,
  });

  // 4. Пользователь ищет что-то
  const keywords = ['AI', 'machine learning', 'neural', 'data science', 'python'];
  const keyword = keywords[Math.floor(Math.random() * keywords.length)];
  
  const searchRes = http.get(`${BASE_URL}/api/works/?search=${keyword}`, { headers });
  check(searchRes, {
    'поиск работает': (r) => r.status === 200,
  });

  // 5. Проверка здоровья сервиса
  const healthRes = http.get(`${BASE_URL}/health/`);
  check(healthRes, {
    'сервис живой': (r) => r.status === 200,
  });
}
