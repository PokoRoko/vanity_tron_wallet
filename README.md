# ❇️ Tron Vanity Wallet Generator

![Logo](pic.png)

## 📜 Project Description

A Python utility for generating Tron wallets with a custom address prefix/suffix. It uses multiprocessing to accelerate generation on multi-core systems.

When a matching wallet is found, the program outputs the seed phrase, private key, and address, does not save them to a file, and exits.

## ⚙️ Configuration

Configuration is set via the `config` variable with the following options:

- `num_processes`: number of parallel processes. Defaults to the number of logical cores minus one.
- `show_log`: whether to log progress.
- `log_count`: logging frequency (every N generations).
- `is_included`: whether to search for a substring anywhere in the address.
- `keyword_included`: substring to search for.
- `register_accuracy`: case sensitivity for checks. Ignored if `use_leet = True`.
- `use_leet`: consider leetspeak equivalents (e.g., a→4, o→0, etc.).
- `start_with`: string the address must start with. Note: Tron addresses start with `T`.
- `end_with`: string the address must end with.
- `is_simetric`: whether to look for symmetry (palindromic substrings) in the address.
- `simtric_deep`: symmetry depth (minimum number of mirrored character pairs).
- `stop_on_found`: stop execution on the first match.

### 🚀 How it Works
1. The program spawns several processes to generate Tron wallets in parallel. Each process works independently and generates wallets until it finds an address matching the search criteria (start and/or end).
2. On each iteration, the process checks whether the generated address meets the specified criteria.
3. If the address matches, the program terminates all processes, outputs the found wallet (seed phrase, private key, and address), and exits without saving anything to a file.
4. Progress logging shows the number of attempts for each process every configured number of generated wallets.

## Security Recommendations
- When running in an isolated environment (container), ensure logging is disabled or clear container logs immediately.
- When running in a terminal, do not use IDLE and be sure to clear logs/history.
- Print secrets once in a “no-history” subshell, copy them, then clear the clipboard and scrollback. This way nothing lands in the shell history; only the on-screen output remains, which you immediately erase.

## Run
1. Ensure you have the package manager [uv](https://docs.astral.sh/uv/guides/install-python/) installed.
2. Sync dependencies: `uv sync`

3. Safe execution
```
# Run the script in a separate session without history
( unset HISTFILE; HISTSIZE=0; SAVEHIST=0; python3 tron_generate.py )

# Clear the clipboard
pbcopy </dev/null

# Clear the screen and terminal scrollback
clear && printf "\e[3J"
```
4. Regular execution

```
uv run python tron_generate.py
```


# ❇️ Генератор красивых Tron-кошельков

## 📜 Описание проекта

Утилита на Python для генерации Tron-кошельков с кастомным префиксом/суффиксом адреса. Использует многопроцессорность для ускорения на многоядерных системах.

При нахождении подходящего кошелька программа выводит сид-фразу, приватный ключ и адрес; не сохраняет их в файл и завершает работу.

## ⚙️ Настройка

### Параметры конфигурации:
Конфигурация программы задаётся через переменную `config`, которая содержит следующие параметры:

- `num_processes`: количество параллельных процессов. По умолчанию равно числу логических ядер минус один.
- `show_log`: логировать прогресс или нет.
- `log_count`: периодичность логирования (через каждые N генераций).
- `is_included`: выполнять ли поиск вхождения подстроки в адресе.
- `keyword_included`: подстрока для поиска вхождения.
- `register_accuracy`: чувствительность к регистру при проверках. Не работает, если `use_leet = True`.
- `use_leet`: учитывать leetspeak-эквиваленты символов (например, a→4, o→0 и т.п.).
- `start_with`: строка, с которой должен начинаться адрес. Примечание: адреса Tron начинаются с `T`.
- `end_with`: строка, которой должен заканчиваться адрес.
- `is_simetric`: искать ли симметрию (палиндромные подстроки) в адресе.
- `simtric_deep`: глубина симметрии (минимальное число зеркальных пар символов).
- `stop_on_found`: останавливать выполнение при первом найденном совпадении.

### 🚀 Логика работы:
1. Программа создаёт несколько процессов для параллельной генерации Tron-кошельков. Каждый процесс работает независимо и генерирует кошельки до тех пор, пока не будет найден адрес, соответствующий условиям поиска (начало и/или конец).
2. На каждой итерации генерации процесс проверяет, соответствует ли сгенерированный адрес заданным критериям.
3. Если адрес удовлетворяет условиям, программа завершает все процессы, выводит найденный кошелек (сид-фразу, приватный ключ и адрес) и завершает работу без сохранения в файл.
4. Логирование прогресса отображает количество попыток для каждого процесса через заданное количество сгенерированных кошельков.


## Рекомендации по безопасности
- При запуске в изолированной среде (контейнере) убедитесь, что выключено логирование, или сразу очищайте логи контейнера.
- При запуске в терминале не делайте этого в IDLE и обязательно очищайте логи/историю.
- Выводите секреты один раз в терминал в «без истории» подпроцессе, скопируйте их, затем очистите буфер обмена и скроллбек. Так ничего не попадёт в файл истории; останется только визуальный вывод, который вы тут же сотрёте.


## Запуск
1.  Проверьте, что у вас установлен пакетный менеджер [uv](https://docs.astral.sh/uv/guides/install-python/).
2. Синхронизируйте зависимости: `uv sync`

3. Безопасный запуск
```
# Запустить скрипт в отдельной сессии без истории
( unset HISTFILE; HISTSIZE=0; SAVEHIST=0; python3 tron_generate.py )

# Очистка буфера обмена
pbcopy </dev/null

# Очистить экран и скроллбек терминала:
clear && printf "\e[3J"
```
4. Запуск в обычном режиме 

```
uv run python tron_generate.py
```