import requests
import json

import asyncio
import aiohttp
import logging
import traceback


#logging.basicConfig(level=logging.DEBUG)
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
    """
    API_ENDPOINTS = {
        's': "/statistics.json",
        'm': "/matches.json?per_page=1",
        # "i": "/items.json",
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
                return None

    except Exception as e:
        logger.error(f"Ошибка парсинга: {e}")
        logger.error(traceback.format_exc())
        return None
    
def get_player_ps_from_api(omeda_id: str) -> float:
    response = fetch_api_data(omeda_id)
    api_data = response 
    player_ps = round(api_data[DATA_FOR_EXTRACTION], 2)
    return player_ps

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
    """
    

    #TODO: убрать дублирование проверок с fetch_api_data
    
    tasks = []

    for player, player_info in users_dict.items():
        task = fetch_api_data(player_info['omeda_id'])
        tasks.append((player, task))
    
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
    logger.info("Data Parsing: Success")

    return users_dict

    # for player, player_info in users_dict.items():
    #     try:         

    #         response = fetch_api_data(player_info['omeda_id'])

    #         if response.status_code == 200:
    #             api_data = response
    #             logger.debug(f"API data for {player}:\n{api_data}")
    #             logger.info(f"Get API data for {player}: Success")

    #             player_ps = round(api_data[DATA_FOR_EXTRACTION], 2)
    #             player_info['player_ps'] = player_ps

    #         else:
    #             logger.info(f"Data extraction: API/GET erorr {response.status_code}")   
        
    #     except Exception as e:
    #         logger.info(f"Ошибка парсинга, {player}. {e}")
    #         player_ps = 0

    # logger.debug(f"Team_dict(get_players_score_from_api()): {users_dict}")
    # logger.info("Data Parsing: Success")



async def get_players_last_match_ps(team_dict: dict[str, dict[str, str | int | float]]) -> None:
    """
    Добавляет во вложеннный словарь пару ключ-значение 'last_match_ps': float

    Arg: 
        team_dict: dict[str, dict[str, str | int | float]] словарь с
        пользователями и информацией о них
    
    Return:
        None. Изменяется сам словарь (добавляется "last_mathc_ps")
    """
    try:
        for player, player_data in team_dict.items():
            omeda_id = player_data['omeda_id']

            last_match_ps = await get_last_match_ps_from_json(omeda_id)
            player_data['last_match_ps'] = last_match_ps
        
        logger.debug(f"get_player_last_match_ps, dict: {team_dict}")
        return None
    except Exception as e:
        logger.error(f"get_player_last_match_ps: {e}")
        return None

async def get_last_match_ps_from_json(omeda_id: str) -> float:
    """
    Возвращает last_match_ps для перерданного omeda_id

    Arg:
        omeda_id: str
    
    Return:
        last_match_ps: float
    """
    
    response = await fetch_api_data(omeda_id, "m")
    api_data = response.json()
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
        return last_game_performance_score
        

def main():
    #schedule_every_day()
    #Analitic.players_score_recorder_start(get_players_score_from_api())
    #get_players_score_from_api()
    pass


if __name__ == "__main__":
    main()
    