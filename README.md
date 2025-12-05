![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white) ![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E) ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)

# Foodgram - социальная сеть для публикации своих рецептов

## Особенности данного проекта
- backend и frontend завернуты в docker контейнеры
- образы backend и frontend запушены на Docker Hub
- реализовано автоматическое тестирование кода на соответствие PEP8, сборка образов и отпарвка их на Docker Hub

## Запуск проекта Foodgram

- Установите себе Docker на ваш компьютер по следующей ссылке и запустите его:
```
https://www.docker.com/
```

- Клонируйте репозиторий с проектом на свой компьютер с помощью следующей команды:
```bash
git clone https://github.com/FLeyaNT/foodgram-st.git
```

- Находясь в общей папке проекта перейдите в папку infra c помощью следующей команды:
```bash
cd infra/
```

- Находясь в папке infra выполните следующую команду:
```bash
docker compose up --build
```

- В результате соберутся все образы и проект запустится в контейнерах в Docker

- Проект будет доступен по ссылке:
```
http://localhost/
```

## Автор
Литавор Илья Юрьевич (ilitavor@mail.ru)

