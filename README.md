# NotesCloud - Микросервисное приложение для работы с заметками

Облачный сервис для создания и управления заметками с поддержкой медиафайлов (изображения, видео, аудио).

## 🏗️ Архитектура

Проект построен на микросервисной архитектуре с использованием следующих компонентов:

```
┌─────────────┐
│   Nginx     │ :80 - Балансировщик нагрузки
└──────┬──────┘
       │
┌──────▼──────┐
│  KrakenD    │ :8080 - API Gateway
└──────┬──────┘
       │
       ├──────────────┬──────────────┬──────────────┐
       │              │              │              │
┌──────▼──────┐ ┌────▼─────┐ ┌──────▼──────┐ ┌────▼─────┐
│   Notes     │ │  Users   │ │   Media     │ │ Frontend │
│  Service    │ │ Service  │ │  Service    │ │   Vue3   │
│   :8001     │ │  :8002   │ │   :8003     │ │  :3000   │
└──────┬──────┘ └────┬─────┘ └──────┬──────┘ └──────────┘
       │              │              │
┌──────▼──────┐ ┌────▼─────┐ ┌──────▼──────┐
│ PostgreSQL  │ │PostgreSQL│ │ PostgreSQL  │
│   :5432     │ │  :5433   │ │   :5434     │
└─────────────┘ └────┬─────┘ └─────────────┘
                     │
                ┌────▼─────┐
                │  Redis   │
                │  :6380   │
                └──────────┘
```

### Сервисы

- **Notes Service** - Управление заметками (CRUD операции)
- **Users Service** - Аутентификация, авторизация, управление пользователями
- **Media Service** - Загрузка, хранение и обработка медиафайлов (S3 + ClamAV)
- **Frontend** - Vue 3 + Vite SPA приложение
- **KrakenD** - API Gateway для маршрутизации запросов
- **Nginx** - Балансировщик нагрузки и reverse proxy

## ✨ Основные возможности

### Пользователи
- ✅ Регистрация с загрузкой аватара
- ✅ Вход/выход (JWT токены)
- ✅ Автоматическое обновление токенов
- ✅ Система ролей *в процессе доработки*
- ✅ Профиль пользователя с аватаром

### Заметки
- ✅ Создание заметок с текстом
- ✅ Прикрепление медиафайлов (видео, изображения, аудио)
- ✅ Просмотр всех заметок пользователя
- ✅ Просмотр детальной информации о заметке
- ✅ Удаление заметок с каскадным удалением медиафайлов

### Медиафайлы
- ✅ Загрузка файлов в S3-совместимое хранилище
- ✅ Антивирусная проверка (ClamAV)
- ✅ Валидация типов и размеров файлов
- ✅ Генерация уникальных URL для доступа
- ✅ Поддержка категорий (аватары, вложения заметок)

### Безопасность
- ✅ JWT аутентификация (Access + Refresh токены)
- ✅ Хранение refresh токенов в Redis
- ✅ Антивирусная проверка загружаемых файлов
- ✅ CORS настройки
- ✅ Валидация входных данных

## 🚀 Быстрый старт

### Предварительные требования

- Docker & Docker Compose v2.x или выше
- S3-совместимое хранилище (AWS S3, MinIO, etc.)

**Важно:** На Linux если у вас установлен docker-compose v1.x, обновите до v2.x:
```bash
# Удалите старую версию
sudo apt remove docker-compose

# Установите Docker Compose v2 (плагин)
sudo apt update
sudo apt install docker-compose-plugin

# Проверьте версию (должна быть 2.x)
docker compose version
```

### Установка

1. **Клонируйте репозиторий**
```bash
git clone https://github.com/GIT01-byte/Notes_pet.git
cd Notes_pet
```

2. **Создайте сеть Docker**
```bash
docker network create app-network
```

3. **Настройте переменные окружения**
```bash
cp .env.template .env
```

Отредактируйте `.env` файл:
```env
# PostgreSQL для каждого сервиса
NOTES_DB_NAME=notes_db
NOTES_DB_USER=notes_user
NOTES_DB_PWD=your_password

USERS_DB_NAME=users_db
USERS_DB_USER=users_user
USERS_DB_PWD=your_password

MEDIA_DB_NAME=media_db
MEDIA_DB_USER=media_user
MEDIA_DB_PWD=your_password

# S3 настройки
MEDIA_S3_ACCESSKEY=your_access_key
MEDIA_S3_SECRETKEY=your_secret_key
MEDIA_S3_ENDPOINTURL=https://s3.amazonaws.com
MEDIA_S3_BUCKETNAME=your_bucket_name
```

4. **Запустите приложение**
```bash
# Для Docker Compose v2.x (рекомендуется)
docker compose up -d

# Или для старой версии v1.x
docker-compose up -d
```

5. **Проверьте статус сервисов**
```bash
docker compose ps  # для v2.x
# или
docker-compose ps  # для v1.x
```

6. **Откройте приложение**
```
http://localhost
```

## 📡 API Эндпоинты

Все запросы проходят через API Gateway (KrakenD) на порту 80 через Nginx.

### 🔐 Аутентификация (Users Service)

#### Регистрация
```http
POST /user/register/
Content-Type: multipart/form-data

username: string (3-64 символа)
email: string (опционально)
password: string (минимум 8 символов)
profile: string (JSON, опционально)
avatar_file: file (опционально, макс 5MB)
```

#### Вход
```http
POST /user/login/
Content-Type: application/x-www-form-urlencoded

username: string
password: string
grant_type: password
```

**Ответ:**
```json
{
  "access_token": "eyJ...",
  "access_expire": 1234567890,
  "refresh_token": "eyJ..."
}
```

#### Обновление токенов
```http
POST /user/refresh_tokens/
Content-Type: application/json

{
  "refresh_token": "eyJ..."
}
```

#### Выход
```http
POST /user/logout/
Authorization: Bearer <access_token>
```

#### Информация о текущем пользователе
```http
GET /user/self_info/
Authorization: Bearer <access_token>
```

**Ответ:**
```json
{
  "jwt_payload": {
    "sub": "1",
    "exp": 1234567890,
    "jti": "uuid",
    "role": "RegularUser",
    "iat": 1234567890
  },
  "user_db": {
    "id": 1,
    "username": "user",
    "email": "user@example.com",
    "is_active": true,
    "role": "RegularUser",
    "profile": {},
    "avatar": [
      {
        "uuid": "uuid",
        "s3_url": "https://...",
        "category": "avatar",
        "content_type": "image/jpeg"
      }
    ]
  }
}
```

### 📝 Заметки (Notes Service)

#### Создать заметку
```http
POST /notes/create?title=<title>&content=<content>
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

video_files: file[] (опционально)
image_files: file[] (опционально)
audio_files: file[] (опционально)
```

**Ответ:**
```json
{
  "message": "Заметка 'Title' успешно создана",
  "note_id": 1,
  "uploaded_files": {
    "video": ["uuid1", "uuid2"],
    "image": ["uuid3"],
    "audio": ["uuid4"]
  }
}
```

#### Получить все заметки пользователя
```http
GET /notes/get_all_notes/
Authorization: Bearer <access_token>
```

**Ответ:**
```json
{
  "data": [
    {
      "id": 1,
      "title": "Заметка",
      "content": "Содержимое",
      "user": "username",
      "video_files": [...],
      "image_files": [...],
      "audio_files": [...]
    }
  ]
}
```

#### Получить заметку по ID
```http
GET /notes/get_note/{note_id}/
Authorization: Bearer <access_token>
```

#### Удалить заметку
```http
DELETE /notes/delete/{note_id}/
Authorization: Bearer <access_token>
```

### 📁 Медиафайлы (Media Service)

#### Загрузить файл
```http
POST /media_service/upload?upload_context=<context>&entity_id=<id>
Content-Type: multipart/form-data

file: file

Параметры:
- upload_context: "post_attachment" | "avatar"
- entity_id: ID заметки или пользователя
```

**Ответ:**
```json
{
  "ok": true,
  "message": "Файл 'filename.jpg' успешно загружен",
  "file": {
    "uuid": "uuid",
    "s3_url": "https://...",
    "content_type": "image/jpeg",
    "category": "image",
    "uploaded_at": "2024-01-01T00:00:00"
  }
}
```

#### Получить метаданные файла
```http
GET /media_service/files/{file_uuid}/
```

#### Просмотреть файл (редирект на S3)
```http
GET /media_service/files/{file_uuid}/view/
```

#### Удалить файл
```http
DELETE /media_service/files/delete/{file_uuid}/
```

### 🏥 Health Checks

```http
GET /notes_service/health_check/
GET /users_service/health_check/
GET /media_service/health_check/
```

## 🛠️ Технологический стек

### Backend
- **FastAPI** - Веб-фреймворк
- **SQLAlchemy** - ORM
- **Alembic** - Миграции БД
- **PostgreSQL** - База данных
- **Redis** - Кэш и хранилище токенов
- **Pydantic** - Валидация данных
- **JWT** - Аутентификация
- **Loguru** - Логирование
- **ClamAV** - Антивирусная проверка
- **Boto3** - S3 клиент

### Frontend
- **Vue 3** - UI фреймворк
- **Vite** - Сборщик
- **TailwindCSS** - Стилизация
- **Font Awesome** - Иконки

### Infrastructure
- **Docker & Docker Compose** - Контейнеризация
- **Nginx** - Reverse proxy
- **KrakenD** - API Gateway
- **S3** - Объектное хранилище

## 📂 Структура проекта

```
Notes_pet/
├── notes-service/          # Сервис заметок
│   ├── api/               # API эндпоинты
│   ├── core/              # Модели, схемы, конфигурация
│   ├── exceptions/        # Обработка ошибок
│   ├── integrations/      # Интеграции с другими сервисами
│   └── alembic/           # Миграции БД
├── users-service/         # Сервис пользователей
│   ├── api/               # API эндпоинты
│   ├── core/              # Модели, схемы, конфигурация
│   ├── services/          # Бизнес-логика
│   └── alembic/           # Миграции БД
├── media-service/         # Сервис медиафайлов
│   ├── api/               # API эндпоинты
│   ├── core/              # Модели, схемы, S3 клиент
│   ├── service/           # Обработка файлов
│   └── alembic/           # Миграции БД
├── frontend/              # Vue 3 приложение
│   ├── src/
│   │   ├── App.vue       # Главный компонент
│   │   └── main.js       # Точка входа
│   └── public/
├── docker-compose.yaml    # Оркестрация сервисов
├── krakend.json          # Конфигурация API Gateway
├── nginx.conf            # Конфигурация Nginx
└── .env.template         # Шаблон переменных окружения
```

## 🔧 Разработка

### Запуск отдельного сервиса

```bash
# Notes Service
cd notes-service
docker-compose up -d

# Users Service
cd users-service
docker-compose up -d

# Media Service
cd media-service
docker-compose up -d
```

### Локальная разработка (без Docker)

1. Установите зависимости:
```bash
cd <service-name>
pip install -r requirements.txt
```

2. Настройте `.env` файл

3. Примените миграции:
```bash
alembic upgrade head
```

4. Запустите сервис:
```bash
python main.py
```

### Создание миграций

```bash
cd <service-name>
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## 📊 Мониторинг

### Логи сервисов
```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f notes-service
docker-compose logs -f notes-users-service
docker-compose logs -f notes-media-service
```

### Статус контейнеров
```bash
docker-compose ps
```

### Проверка здоровья сервисов
Фронтенд отображает статус всех сервисов в верхней панели (зеленый/красный индикатор).

## 🔐 Система ролей *в процессе доработки*

- **RegularUser** - Обычный пользователь (CRUD своих заметок)
- **AdminUser** - Администратор (полный доступ)
- **ModeratorUser** - Модератор (управление контентом)
- **ReadOnlyUser** - Только чтение
- **GuestUser** - Гостевой доступ

## 🐛 Известные проблемы и TODO

- [ ] Доработать систему ролей и разрешений для пользователей
- [ ] Добавить разрешения для пользователей в сервис заметок
- [ ] Внедрить SOLID принципы (15-20%)
- [ ] Синхронизация сохранения файлов в медиа-сервис
- [ ] Добавить пагинацию для списка заметок
- [ ] Реализовать поиск по заметкам
- [ ] Добавить теги для заметок

## 📝 Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для получения дополнительной информации.

## 👥 Контакты

Для вопросов и предложений создавайте Issue в репозитории.
