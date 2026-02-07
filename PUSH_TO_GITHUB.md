# Запушить в общий репозиторий GitHub

Организация: **Event-Discovery-Service-Backend-Develop**  
https://github.com/orgs/Event-Discovery-Service-Backend-Develop

## Если репозиторий уже создан в организации

Подставь вместо `REPO_NAME` название репозитория (например `backend` или `scientific-data-harvester`) и выполни в терминале из папки проекта:

```bash
cd "/Users/erkezhanabdraim/Desktop/backend project"

git init
git add .
git commit -m "Initial: Django Scientific Data Harvester, OpenAlex collector, API, SQLite/Postgres"

git remote add origin https://github.com/Event-Discovery-Service-Backend-Develop/REPO_NAME.git
git branch -M main
git push -u origin main
```

## Если репозитория ещё нет

1. Зайди на https://github.com/orgs/Event-Discovery-Service-Backend-Develop
2. Создай новый репозиторий (New repository), например `backend`
3. Не добавляй README, .gitignore и лицензию — они уже есть в проекте
4. В командах выше замени `REPO_NAME` на имя созданного репозитория и выполни их

## Если запросит логин/пароль

- Используй **Personal Access Token** вместо пароля: GitHub → Settings → Developer settings → Personal access tokens → создать токен с правом `repo`
- Либо настрой SSH и замени URL на: `git@github.com:Event-Discovery-Service-Backend-Develop/REPO_NAME.git`
