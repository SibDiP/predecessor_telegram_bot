"""
Аналитический инструмент для сравнения performance scores (PS) игроков 
в различные временные периоды.

Этот модуль предоставляет функциональность для анализа и расчета разницы 
в performance scores игроков, генерируя отчет сравнения с визуальными 
индикаторами изменений показателей.

Основные возможности:
    Сравнивает performance scores игроков между начальным и текущим наборами данных
    Формирует строку с разницей показателей и ссылками на игроков
    Использует эмодзи-индикаторы для отображения динамики изменений (зеленый/красный/желтый)
"""

import logging
import traceback

import utils.ps_parser as ps_parser
logger = logging.getLogger(__name__)

class Analitic:
    """
    Класс для аналитики данных и рссчёта разницы в PS.
    """

    @staticmethod
    def difference_players_score_records(
        data_start: dict[str, dict[str, str| int |float]],
        data_end: dict[str, dict[str, str| int |float]],
    ) -> str:
        """
        Сравнивает записи performance scores (PS) игроков и генерирует форматированную строку с результатами.

        Вычисляет разницу в performance scores игроков между двумя временными точками
        и создает форматированную строку с деталями, включая:
            Средний показатель эффективности
            Изменение показателя
            Результат последнего матча
            Никнейм игрока со ссылкой на его профиль

        Args:
            data_start (dict[str, dict[str, str| int |float]]): Начальные данные PS игроков из базы данных
            data_end (dict[str, dict[str, str| int |float]]): Текущие данные PS игроков

        Returns:
            str: Форматированная строка с результатами сравнения performance scores игроков

        Raises:
            Exception: При возникновении проблем с доступом к данным игроков
        """
        
        result_string = (f"<u>#{'avg':^7}|{'delta':^13}|{'last':^11}|{'nick':^10}#</u>\n")

        up_down_neutral_emoji = ("🟢","🔴","🟡")
        compare_index : int = None
        compare_difference : float = None

        for player, player_data in data_end.items():
            
            try:
                current_ps = data_start[player]['player_ps_day']
                next_ps = player_data['player_ps_day']
                last_match_ps = player_data['last_match_ps']

            except Exception as e:
                logger.error(f"difference_players_score_records: {e}")
                logger.error(traceback.format_exc())
                raise
            
            compare_difference = abs(next_ps - current_ps)

            if next_ps > current_ps:
                compare_index = 0
            elif next_ps < current_ps:
                compare_index = 1
            elif next_ps == current_ps:
                compare_index = 2

            result_string += (
                f"{current_ps:0>6.2f} | " +
                f"{up_down_neutral_emoji[compare_index]} {compare_difference:0>4.2f} | " +
                f"{last_match_ps:0>6.2f} | " +
                f'''<a href="{ps_parser.BASE_OMEDA_ADRESS}{player_data['omeda_id']}">{player[:7]}</a>\n'''
                )
        return  result_string

def main():
    pass


if __name__ == "__main__":
    main()