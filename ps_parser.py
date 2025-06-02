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
                logger.debug(f"Response status type: {type(response.status)}")
                logger.debug(f"Full response: {await response.text()}")
                logger.debug(f"Response status: {response.status}")
                logger.debug(f"Response content: {response.content}")

                if response.status == 200:
                    logger.info(f"Get API response for {omeda_id}: Success")
                    return await response.json()

                logger.error(f"Data extraction: API/GET erorr {response.status_code}, URL:{url}") 
                #None - используется для обработки ошибок и ответа пользователю в чате  
                raise aiohttp.ClientResponseError(response.status)

    except aiohttp.ClientResponseError as e:
        logger.error(f"Получение данных, статус ответа не 200: API/GET erorr {e}")
        logger.error(traceback.format_exc())
        raise

    except aiohttp.ClientError as e:
        logger.error(f"Получение данных: API/GET erorr {e}")
        logger.error(traceback.format_exc())
        raise
    
    except aiohttp.TimeoutError as e:
        logger.error(f"Получение данных, время timeout превышено: API/GET erorr {e}")
        logger.error(traceback.format_exc())
        raise

    except Exception as e:
        logger.error(f"Ошибка парсинга: {e}")
        logger.error(traceback.format_exc())
        raise
    
async def get_player_ps_from_api(omeda_id: str) -> float:
    """
    Получение среднего значения ps для игрока из API.

    Args:
        omeda_id: str. Идентификатор игрока

    Returns:
        float: Среднее значение ps игрока.
    
    Raises:
        aiohttp.ClierntResposeError ответ сервера отличен от 200
        aiohttp.aiohttp.ClientError при ошибках соединения
        aiohttp.TimeoutError при превышении таймаута
        Exeption: При прочих ошибках при получении данных
    """
    response = await fetch_api_data(omeda_id)
    api_data = response 
    player_ps = round(api_data[DATA_FOR_EXTRACTION], 2)
    return player_ps

#Ассинхронный парсинг для получения ps игроков из API
async def get_players_score_from_api(
    users_dict: dict[str, dict[str, str]]
    ) -> dict[str, dict[str, str | float]]:
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
    
    for player, player_info in users_dict.items():
        task = fetch_api_data(player_info['omeda_id'])
        tasks.append((player, task))
    # Запускаем задачи асинхронно
    fetch_results = await asyncio.gather(*(task for _, task in tasks))
    logger.debug(f"fetch_results: {fetch_results}")

    for (player, _), response in zip(tasks, fetch_results):
        if response is not None:
            try:
                player_ps = round(response[DATA_FOR_EXTRACTION], 2)
                users_dict[player]['player_ps'] = player_ps
                logger.debug(f"{__name__}, API data for {player}:\n{response}")
                logger.info(f"Get API data for {player}: Success")
            except KeyError as e:
                logger.error(f"Ошибка извлечения данных для {player}: {e}")
                users_dict[player]['player_ps'] = 0
        else:
            logger.info(f"Data extraction failed for {player}. Setting player_ps to 0.")
            users_dict[player]['player_ps'] = 0

    logger.debug(f"Team_dict(get_players_score_from_api()): {users_dict}")
    logger.info("Парсинг информации из API: Success")

    return users_dict
        
def main():
    pass


if __name__ == "__main__":
    main()
    