# predecessor_telegram_bot

A Telegram bot built with **aiogram**. It demonstrates the core principles of working with the library, including message handling, commands, FSM states and database access. Based on the [telegram-tutorial](https://github.com/MasterGroosha/telegram-tutorial) course.

## Usage

As of the time of writing, the bot is available at this [link](https://t.me/pred_ps_bot).

## Features

The bot tracks the **Performance Score** in the game Predecessor using the omeda.city API. It can:

* **Add a player:** the user can add a player to the database by name and Omeda ID.
* **Remove a player:** the user can remove a player from the database.
* **Show players' PS:** the bot displays the current PS of tracked players as well as the change compared to the previous day.
* **Daily PS update:** the bot automatically refreshes player PS values every day.

## Technologies

* **Python** — programming language.
* **aiogram** — framework for building Telegram bots.
* **SQLAlchemy** — ORM for database access.
* **SQLite** — database that stores player information.
* **asyncio** — library for asynchronous tasks.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/SibDiP/predecessor_telegram_bot.git
   ```

2. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   ```

3. Activate the virtual environment:

   ```bash
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate  # Windows
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Configure the bot:

   * Create a bot in Telegram via @BotFather and get the token.
   * Create a `.env` file in the project root and add the token there:

     ```
     TELEGRAM_BOT_TOKEN=your_bot_token
     LOGGING_MODE=INFO
     ```

## Run

```bash
python main.py
```

## Testing

```bash
pytest
```

## Project structure

* `main.py`: bot entry point.
* `utils/`: helper modules.
    * `users_manager.py`: user database access.
    * `ps_parser.py`: parsing PS data from the API.
    * `ps_data_manager.py`: PS data management.
    * `ps_analitic_tools.py`: PS data analysis.
* `tests/`: tests.

## License

MIT License | 2025 | Dmitrii Pivnev

## Contacts

sibdip — https://github.com/SibDiP

<details>
<summary>Русская версия</summary>

# predecessor_telegram_bot

Telegram-бот с использованием aiogram. Демонстрирует основные принципы работы с библиотекой aiogram, включая обработку сообщений, создание команд, использование состояний и работу с базой данных. Основой послужил учебный курс https://github.com/MasterGroosha/telegram-tutorial.

## Использование

На момент создания, бот доступен для использования по данной [ссылке](https://t.me/pred_ps_bot).

## Функциональность бота

Этот бот предназначен для отслеживания показателя Performance Score в игре Predecessor, на основе omeda.city API. Возможности:

* **Добавление игрока:** пользователь может добавить игрока в базу данных, указав его имя и Omeda ID.
* **Удаление игрока:** пользователь может удалить игрока из базы данных.
* **Получение информации о PS игроков:** бот может отображать текущий PS игроков, а также изменение PS по сравнению с предыдущим днём.
* **Ежедневное обновление PS:** бот автоматически обновляет значения PS игроков каждый день.

## Технологии

* **Python** — язык программирования.
* **aiogram** — библиотека для создания Telegram-ботов.
* **SQLAlchemy** — ORM для работы с базой данных.
* **SQLite** — база данных для хранения информации об игроках.
* **asyncio** — библиотека для асинхронных задач.

## Установка

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/SibDiP/predecessor_telegram_bot.git
   ```

2. Создайте виртуальное окружение:

   ```bash
   python3 -m venv .venv
   ```

3. Активируйте виртуальное окружение:

   ```bash
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate  # Windows
   ```

4. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

5. Настройте бота:

   * Создайте бота в Telegram с помощью @BotFather и получите токен.
   * Создайте файл `.env` в корне проекта и добавьте туда токен бота:

     ```
     TELEGRAM_BOT_TOKEN=ваш_токен_бота
     LOGGING_MODE=INFO
     ```

## Запуск

```bash
python main.py
```

## Тестирование

```bash
pytest
```

## Структура проекта

* `main.py`: основной файл бота.
* `utils/`: вспомогательные модули.
    * `users_manager.py`: модуль для работы с базой данных пользователей.
    * `ps_parser.py`: модуль для парсинга данных о PS с API.
    * `ps_data_manager.py`: модуль для управления данными о PS.
    * `ps_analitic_tools.py`: модуль для анализа данных о PS.
* `tests/`: тесты.

## Лицензия

MIT License | 2025 | Dmitrii Pivnev

## Контакты

sibdip — https://github.com/SibDiP

</details>
