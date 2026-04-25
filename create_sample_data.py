#!/usr/bin/env python
import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from harvester.models import Conference

def create_sample_conferences():
    conferences = [
        {
            'title': 'International Conference on Artificial Intelligence 2026',
            'event_date': date(2026, 10, 15),
            'location': 'Tokyo, Japan',
            'deadline': date(2026, 7, 20),
            'keywords': 'AI, machine learning, neural networks',
            'url': 'https://example.com/ai2026'
        },
        {
            'title': 'European Conference on Computer Vision 2026',
            'event_date': date(2026, 11, 8),
            'location': 'Berlin, Germany',
            'deadline': date(2026, 8, 10),
            'keywords': 'computer vision, image processing, deep learning',
            'url': 'https://example.com/cv2026'
        },
        {
            'title': 'World Congress on Big Data 2026',
            'event_date': date(2026, 12, 5),
            'location': 'San Francisco, USA',
            'deadline': date(2026, 9, 1),
            'keywords': 'big data, analytics, data science',
            'url': 'https://example.com/bd2026'
        },
        {
            'title': 'International Symposium on Cybersecurity 2026',
            'event_date': date(2026, 9, 22),
            'location': 'London, UK',
            'deadline': date(2026, 6, 30),
            'keywords': 'cybersecurity, network security, cryptography',
            'url': 'https://example.com/cs2026'
        },
        {
            'title': 'Asian Conference on Internet of Things 2026',
            'event_date': date(2026, 8, 18),
            'location': 'Singapore',
            'deadline': date(2026, 5, 25),
            'keywords': 'IoT, sensors, smart devices',
            'url': 'https://example.com/iot2026'
        },
        {
            'title': 'Global Summit on Blockchain Technology 2026',
            'event_date': date(2026, 7, 14),
            'location': 'Zurich, Switzerland',
            'deadline': date(2026, 4, 15),
            'keywords': 'blockchain, cryptocurrency, distributed systems',
            'url': 'https://example.com/bc2026'
        },
        {
            'title': 'International Conference on Quantum Computing 2026',
            'event_date': date(2026, 11, 30),
            'location': 'Boston, USA',
            'deadline': date(2026, 8, 20),
            'keywords': 'quantum computing, quantum algorithms, qubits',
            'url': 'https://example.com/qc2026'
        },
        {
            'title': 'European Conference on Software Engineering 2026',
            'event_date': date(2026, 10, 3),
            'location': 'Paris, France',
            'deadline': date(2026, 7, 5),
            'keywords': 'software engineering, agile, DevOps',
            'url': 'https://example.com/se2026'
        }
    ]

    created = 0
    for conf_data in conferences:
        # Generate unique wikicfp_id
        base_id = random.randint(10000, 99999)
        wikicfp_id = f"{base_id}"
        while Conference.objects.filter(wikicfp_id=wikicfp_id).exists():
            base_id += 1
            wikicfp_id = f"{base_id}"

        Conference.objects.create(
            wikicfp_id=wikicfp_id,
            title=conf_data['title'],
            event_date=conf_data['event_date'],
            location=conf_data['location'],
            deadline=conf_data['deadline'],
            keywords=conf_data['keywords'],
            url=conf_data['url'],
            raw_html=f"<html><body><h1>{conf_data['title']}</h1><p>Sample conference data</p></body></html>"
        )
        created += 1

    print(f"Created {created} sample conferences")

if __name__ == '__main__':
    create_sample_conferences()