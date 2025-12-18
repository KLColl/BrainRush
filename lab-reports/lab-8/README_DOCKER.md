# Звіт з контейнеризації проєкту

## Архітектура контейнерного рішення

### Docker образ

* Базовий образ (етап builder): `python:3.11-slim`
* Фінальний образ: `python:3.11-alpine`
* Використання багатоетапної збірки: **так** (builder → final)
* Розмір фінального образу: **(під час написання README розмір не визначено)** - команда для перевірки розміру після збірки:

```bash
# Після побудови образу

# Linux / macOS

docker images --format "{{.Repository}}:{{.Tag}}\t{{.Size}}" | grep brainrush
# або
docker image ls | grep brainrush
```

```powershell
# Windows PowerShell

docker images --format "{{.Repository}}:{{.Tag}}`t{{.Size}}" | Select-String brainrush
# або
docker image ls | Select-String brainrush
```

### docker-compose

Файли:

* `docker-compose.yml` - production (сервіси: `web`, `nginx`, `backup`)

* `docker-compose.dev.yml` - development (сервіс: `web`)

* Кількість сервісів (production): **3** (`web`, `nginx`, `backup`)

* Використовувані volumes:

  * `sqlite_data` (production) - для збереження файлу БД
  * `sqlite_data_dev` (development) - для dev-режиму

## Прийняті рішення та обґрунтування

### Вибір базового образу

Використано багатоетапну збірку (builder на `python:3.11-slim`) для встановлення залежностей із компілятором (`gcc`), а потім копіювання лише потрібних файлів у легкий `python:3.11-alpine` образ. Це зменшує розмір фінального образу та підвищує безпеку.

### Організація збереження даних

База даних SQLite зберігається у директорії `/app/instance/brainrush.db` і змонтована як Docker volume (`sqlite_data` / `sqlite_data_dev`). Додатково в проєкті є скрипт `backup.sh` та контейнер `backup` у production-compose для регулярного копіювання файлу БД у директорію `./backups` на хості.

### Оптимізації

* Багатоетапна збірка для зменшення розміру образу
* Використання `--no-cache-dir` при встановленні pip-залежностей
* Healthcheck для контейнера web (через wget)
* Nginx як статичний файловий сервер для `/static` та як зворотний проксі для Flask

## Інструкції з розгортання (production)

Інструкції для чистої системи з встановленим Docker & docker-compose:

1. Клонувати репозиторій та перейти в каталог проєкту:

```bash
git clone <repo-url>
cd BrainRush
```

2. Переконатися, що у корені наявні файли: `Dockerfile`, `docker-compose.yml`, `.env` (створити `.env` на основі `.env.example`, якщо потрібно).

3. Видалити старі контейнери та volumes (щоб почати з нуля):

```bash
# Зупинити та видалити контейнери + volumes
docker-compose -f docker-compose.yml down --volumes --remove-orphans
# Якщо використовуєте dev compose
docker-compose -f docker-compose.dev.yml down --volumes --remove-orphans
```

4. Побудувати образи та запустити служби:

```bash
# Production
docker-compose -f docker-compose.yml build
docker-compose -f docker-compose.yml -p brainrush_prod up -d    

# Або для development
docker-compose -f docker-compose.dev.yml build 
docker-compose -f docker-compose.dev.yml -p brainrush_dev up -d 
```

5. Перевірити логи та стан:

```bash
docker-compose -f docker-compose.yml ps
docker-compose -f docker-compose.yml logs -f web
# Перевірити health endpoint
curl -v http://localhost/health
# Якщо nginx працює: відкрийте http://localhost
```

6. Якщо потрібно створити бекап або відновити - використайте `backup.sh` або контейнер `backup` (опис у `backup.sh`).

## Перевірки після розгортання

* Healthcheck контейнера `web` визначається командою `wget --spider http://localhost:5000/`.
* На першому запуску додаток автоматично виконує ініціалізацію БД (викликається `init_db()` у `create_app()`).

## Можливі покращення

* Налаштування автоматичних бекапів з ротацією та відправкою на віддалене сховище
* Додавання CI/CD pipeline для автоматичної збірки та пушу образів у реєстр
* Додавання секретів через секрет-менеджер (не зберігати секрети в `.env` у репозиторії)

## Висновки

Контейнеризація дозволила відокремити середовище виконання додатку від хост-системи, забезпечити просту розгортання на будь-якій машині з Docker та контроль за станом через healthchecks. Збереження SQLite у volume дозволяє зберегти дані між перезапусками контейнера.

---

### Додаткові команди

```bash
# Побачити список томів
docker volume ls

# Видалити застарілі томи
docker volume prune

# Отримати розмір образу після побудови
docker image ls --format "{{.Repository}}\t{{.Tag}}\t{{.Size}}"
```
