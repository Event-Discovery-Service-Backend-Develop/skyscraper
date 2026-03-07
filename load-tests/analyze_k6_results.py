#!/usr/bin/env python3
"""
Простой скрипт для анализа результатов k6 тестирования
Использование: python analyze_k6_results.py results.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def analyze_k6_output(json_file):
    """Анализирует JSON файл с результатами k6"""
    
    with open(json_file, 'r') as f:
        lines = f.readlines()
    
    # k6 выводит JSON по одному объекту в строку
    metrics = {}
    total_requests = 0
    failed_requests = 0
    durations = []
    
    for line in lines:
        try:
            obj = json.loads(line.strip())
            if 'metric' in obj:
                metric_name = obj['metric']
                value = obj.get('data', {}).get('value', 0)
                
                if metric_name == 'http_reqs':
                    total_requests = int(value)
                elif metric_name == 'http_req_failed':
                    failed_requests = int(value)
                elif metric_name == 'http_req_duration':
                    durations.append(value)
                
                if metric_name not in metrics:
                    metrics[metric_name] = []
                metrics[metric_name].append(value)
        except json.JSONDecodeError:
            continue
    
    # Вычисляем статистику
    if durations:
        avg_duration = sum(durations) / len(durations)
        percentile_95 = sorted(durations)[int(len(durations) * 0.95)]
        percentile_99 = sorted(durations)[int(len(durations) * 0.99)]
    else:
        avg_duration = percentile_95 = percentile_99 = 0
    
    # Основные метрики
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_requests': total_requests,
        'failed_requests': failed_requests,
        'success_rate': f"{(total_requests - failed_requests) / total_requests * 100:.2f}%" if total_requests > 0 else 0,
        'avg_latency_ms': f"{avg_duration:.2f}",
        'p95_latency_ms': f"{percentile_95:.2f}",
        'p99_latency_ms': f"{percentile_99:.2f}",
    }
    
    return report


def print_report(report):
    """Красиво выводит отчет"""
    print("\n" + "=" * 60)
    print("ОТЧЕТ О НАГРУЗОЧНОМ ТЕСТИРОВАНИИ K6")
    print("=" * 60)
    
    for key, value in report.items():
        if key == 'timestamp':
            print(f"Дата/Время: {value}")
        else:
            # Красивый вывод
            label = key.replace('_', ' ').title()
            print(f"{label:.<40} {value}")
    
    print("=" * 60 + "\n")


def main():
    if len(sys.argv) < 2:
        print("Использование: python analyze_k6_results.py <path_to_results.json>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    if not Path(json_file).exists():
        print(f"Ошибка: файл {json_file} не найден")
        sys.exit(1)
    
    try:
        report = analyze_k6_output(json_file)
        print_report(report)
        
        # Сохраняем в отдельный файл
        report_file = json_file.replace('.json', '_report.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"✓ Отчет сохранен в {report_file}")
        
    except Exception as e:
        print(f"Ошибка при анализе: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
