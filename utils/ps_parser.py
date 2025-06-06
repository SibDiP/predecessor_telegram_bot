"""
Асинхронное получение и парсинг performance scores игроков из API Omeda.

Этот модуль предоставляет функции для получения статистики игроков и performance scores
матчей с использованием асинхронных HTTP-запросов. Поддерживается получение средних
performance scores и scores последнего матча для нескольких игроков.

Ключевые функции:
    fetch_api_data: Получает JSON-данные из API Omeda для конкретного игрока
    get_player_ps_from_api: Извлекает средний performance score игрока
    get_players_score_from_api: Асинхронно получает performance scores для нескольких игроков
    get_last_match_ps_from_json: Извлекает performance score из последнего матча

Вызывает различные исключения, связанные с запросами к API, включая ошибки соединения и таймауты.
"""
import requests

import asyncio
import aiohttp
import logging
import traceback


logger = logging.getLogger(__name__)
requests.adapters.DEFAULT_TIMEOUT = 10

BASE_OMEDA_ADRESS = "https://omeda.city/players/"
DATA_FOR_EXTRACTION = "avg_performance_score"

async def fetch_api_data(omeda_id: str, target_json: str = "s"
) -> dict:
    """
    Получение json файлов из omeda.ciy API.

    Arg:
        omeda_id: str. Идентификатор игрока
        json: str. "s" - /statistics.json, "m" - /matches.json

    Return:
        dict json-ответ от API.
        
    Raises:
        aiohttp.ClierntResposeError ответ сервера отличен от 200
        aiohttp.aiohttp.ClientError при ошибках соединения
        aiohttp.TimeoutError при превышении таймаута
        Exeption: При прочих ошибках при получении данных
    """
    API_ENDPOINTS = {
        's': "/statistics.json",
        'm': "/matches.json?per_page=1",
    }
    url = f"{BASE_OMEDA_ADRESS}{omeda_id}{API_ENDPOINTS[target_json]}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                logger.debug(f"Response URL: {url}")
                logger.debug(f"Response status type: {type(response.status)}")
                logger.debug(f"Response status: {response.status}")

                if response.status == 200:
                    logger.info(f"Get API response for {omeda_id}: Success")
                    return await response.json()

    except Exception as e:
        logger.error(f"Ошибка парсинга: {e}")
        logger.error(traceback.format_exc())
        raise
    
async def get_player_ps_from_api(omeda_id: str) -> float:
    """
    Получение среднего значения ps для игрока из API.

    Args:
        omeda_id: str. Идентификатор игрок
    Returns:
        float: Среднее значение ps игрока.
    Raises:
        Exeption: При прочих ошибках при получении данных (fetch_api_data)
    """
   
    response = await fetch_api_data(omeda_id)
    
    api_data = response 
    player_ps = round(api_data[DATA_FOR_EXTRACTION], 2)
    return player_ps

#Ассинхронный парсинг для получения ps игроков из API
async def get_players_score_from_api(
    users_dict: dict[str, dict[str, str]],
    last_match_ps=True) -> dict[str, dict[str, str | float]]:
    """
    Получение среднего значения ps для игроков из API и возврат в виде
    сортированного словаря.

    Args:
        users_dict: dict[name:{'omeda_id':str}].

    Returns:
        dict: {name : {'omeda_id':str, 'player_ps': float}}.

    Raises:
            KeyError: Если ключ не найден в словаре (обрабатывается локально)

            aiohttp.ClierntResposeError ответ сервера отличен от 200
            aiohttp.aiohttp.ClientError при ошибках соединения
            aiohttp.TimeoutError при превышении таймаута
            Exeption: При прочих ошибках при получении данных
    """
    # Создаём список задач для асинхронного выполнения
    tasks = []
    
    # Создаём задачи для асинхронного выполнения
    
    # для /delta_ps
    # порядок: ответ от API /statistics.json для среднего значения ps (float), 
    # затем ответ от API /matches.json для последнего матча игрока (float), и так
    # для каждого игрока
    if last_match_ps:
        for player, player_info in users_dict.items():
            task = get_player_ps_from_api(player_info['omeda_id'])
            tasks.append((player, task))
            task = get_last_match_ps_from_json(player_info['omeda_id'])
            tasks.append((player, task))
    #Для ежедневного обновления ps в базе данных
    else:
        for player, player_info in users_dict.items():
            task = get_player_ps_from_api(player_info['omeda_id'])
            tasks.append((player, task))

    # Запускаем задачи асинхронно
    fetch_results = await asyncio.gather(*(task for _, task in tasks))
    logger.debug(f"fetch_results: {fetch_results}")

    i = 0
    for (player, _), response in zip(tasks, fetch_results):
        
            if i == 0 or i % 2 == 0:
                if response is not None:
                    player_ps = response
                    users_dict[player]['player_ps'] = player_ps
                    logger.debug(f"{__name__}, API data for {player}:\n{response}")
                    logger.info(f"Get API data for {player}: Success")
                else:
                    logger.info(f"Data extraction failed for {player}. Setting player_ps to 0.")
                    users_dict[player]['player_ps'] = 0

            else:
                if response is not None:
                    last_match_ps = response
                    users_dict[player]['last_match_ps'] = last_match_ps
                    logger.debug(f"{__name__}, API data for {player}:\n{response}")
                    logger.info(f"last_match_ps API data for {player}: Success")
                else:
                    logger.info(f"Data extraction failed for {player}. Setting last_match_ps to 0.")
                    users_dict[player]['last_match_ps'] = 0
            i += 1
            
    logger.debug(f"Team_dict(get_players_score_from_api()): {users_dict}")
    logger.info("Парсинг информации из API: Success")

    return users_dict

async def get_last_match_ps_from_json(omeda_id: str) -> float:
    """
    Возвращает last_match_ps для перерданного omeda_id
    Arg:
        omeda_id: str

    Return:
        last_match_ps: float
    """
    response = await fetch_api_data(omeda_id, "m")
    api_data = response
    logger.debug(f"get_last_match_ps_from_json, api_data: {api_data}")

    try:
        for match in api_data.get('matches', []):
            for player in match.get('players', []):
                if player.get('id') == omeda_id:
                    last_game_performance_score = round(
                        player.get('performance_score'), 2)
                    logger.debug(f"{get_last_match_ps_from_json.__name__} last_game_performance_score: {last_game_performance_score}")
                    return last_game_performance_score

    except Exception as e:
        logger.error(f"{get_last_match_ps_from_json.__name__} ошибка!: {e}")
        last_game_performance_score = 0
        raise

    finally:
        return last_game_performance_score


def main():
    pass


if __name__ == "__main__":
    main()
    