# 📱 Telegram Parser Pro (TGP)

**Профессиональный парсер Telegram каналов для анализа, поиска и сбора данных**

## 🎯 О проекте

Telegram Parser Pro — это высокопроизводительный инструмент для:
- Парсинга Telegram каналов
- Поиска по сообщениям (ключевые слова, хэштеги, даты)
- Сбора статистики и аналитики
- Экспорта результатов (JSON, CSV)
- Anti-detection (User-Agent ротация, задержки, cookies)

## 🚀 Быстрый старт

### Требования
- Python 3.11+
- pip или poetry

### Установка

```bash
git clone https://github.com/severand/TG_parser.git
cd TG_parser
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### Первый запуск

```bash
# Скопируй конфиг
cp config/config.example.json config/config.json

# Запусти парсер
python main.py --channels "channel1,channel2" --keywords "keyword1,keyword2"
```

## 📚 Документация

- [SETUP.md](./SETUP.md) — Подробная установка
- [DEVELOPMENT.md](./DEVELOPMENT.md) — Гайд разработчика
- [docs/API.md](./docs/API.md) — API документация
- [docs/EXAMPLES.md](./docs/EXAMPLES.md) — Примеры кода

## 📁 Структура проекта

```
telegram_parser/
├── config/           # Конфигурация
├── core/             # Основная логика парсера
├── network/          # Сетевой слой
├── utils/            # Утилиты
├── data/             # Модели данных
├── stats/            # Статистика
├── output/           # Вывод результатов
├── tests/            # Тесты
├── docs/             # Документация
└── scripts/          # Скрипты
```

## ✅ Статус MVP

- [x] Foundation & Utils
- [x] Network Layer
- [x] Core Parser Engine
- [x] Data Layer
- [x] Statistics & Monitoring
- [x] Output & Export
- [ ] Testing & Optimization
- [ ] Documentation & DevOps

## 📦 Версия

**v1.0.0-MVP** (активная разработка)

## 👥 Команда

Project Owner & Tech Lead: severand

## 📞 Контакты

GitHub: [severand/TG_parser](https://github.com/severand/TG_parser)

---

*Telegram Parser Pro — The Professional Way to Parse Telegram*
