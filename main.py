import requests
import time
from environs import Env
from terminaltables import AsciiTable

TIME_SLEEP = 0.25
AREA_HH = '1'
PERIOD_HH = '30'
PER_PAGE = '100'
PERIOD_SJ = 7
CATALOGUES_SJ = 48
LANGS = ['JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'C#']


def predict_salary(salary_from, salary_to):

    if salary_from and salary_to:
        return int((salary_from + salary_to)/2)
    if salary_from:
        return int(salary_from * 1.2)
    if salary_to:
        return int(salary_to * 0.8)


def get_salaries_hh(vacancies):

    non_zero_salaries_vacancies = 0
    salary_amount = 0

    for vacancy in vacancies:
        if vacancy['salary']:
            non_zero_salaries_vacancies += 1
            salary_amount += predict_salary(vacancy['salary']['from'],
                                            vacancy['salary']['to'])
    try:
        average_salary = int(salary_amount/non_zero_salaries_vacancies)
    except ZeroDivisionError:
        average_salary = 0
    return non_zero_salaries_vacancies, average_salary


def get_average_salaries_hh(langs):

    salary_statistic = {}

    headers = {
        'User-Agent': '5-HH-SJ/1.0 (lamerork@gmail.com)',
        'Accept-Language': 'ru-RU'
    }

    for lang in langs:
        all_vacancies = []
        page = 0
        pages = 1

        while page < pages:

            payload = {
                'text': f'Программист {lang}',
                'area': AREA_HH,
                'period': PERIOD_HH,
                'page': page,
                'per_page': PER_PAGE
                }

            time.sleep(TIME_SLEEP)
            response = requests.get('https://api.hh.ru/vacancies',
                                    params=payload,
                                    headers=headers)
            response.raise_for_status()

            page_vacancies = response.json()
            all_vacancies += [vacancy for vacancy in page_vacancies['items']]
            pages = int(page_vacancies['pages'])
            page += 1

        vacancies_processed, salary = get_salaries_hh(all_vacancies)
        salary_statistic[lang] = {'vacancies_found': page_vacancies['found'],
                                    'vacancies_processed': vacancies_processed,
                                    'average_salary': salary}

    return salary_statistic


def get_salaries_sj(vacancies):

    non_zero_salaries_vacancies = 0
    salary_amount = 0

    for vacancy in vacancies:
        if vacancy['payment_from'] or vacancy['payment_to']:
            non_zero_salaries_vacancies += 1
            salary_amount += predict_salary(vacancy['payment_from'],
                                            vacancy['payment_to'])

    try:
        average_salary = int(salary_amount/non_zero_salaries_vacancies)
    except ZeroDivisionError:
        average_salary = 0
    return non_zero_salaries_vacancies, average_salary


def get_average_salaries_sj(langs, token):

    salary_statistic = {}
    headers = {
        'X-Api-App-Id': token
    }

    for lang in langs:
        all_vacancies = []
        page = 0
        pages = 1
        while page < pages:
            params = {
                'page': page,
                'keyword': f'Программист {lang}',
                'town': 'Москва',
                'count': PER_PAGE,
                'period': PERIOD_SJ,
                'catalogues': CATALOGUES_SJ,
            }

            response = requests.get('https://api.superjob.ru/2.0/vacancies/',
                                    params=params,
                                    headers=headers)
            response.raise_for_status()
            page_vacancies = response.json()
            all_vacancies += [vacancy for vacancy in page_vacancies['objects']]
            page += 1
            pages = page_vacancies['total']

        vacancies_processed, average_salary = get_salaries_sj(all_vacancies)
        salary_statistic[lang] = {'vacancies_found': len(all_vacancies),
                                    'vacancies_processed': vacancies_processed,
                                    'average_salary': average_salary}
    return salary_statistic


def get_table_vacancy(vacancy_statistics):

    salary_statistics = [['Язык программирования',
                          'Вакансий найдено',
                          'Вакансий обработано',
                          'Средняя зарплата']]

    for vacancy_statistic in vacancy_statistics:
        salary_statistics.append([vacancy_statistic,
                                   vacancy_statistics[vacancy_statistic]['vacancies_found'],
                                   vacancy_statistics[vacancy_statistic]['vacancies_processed'],
                                   vacancy_statistics[vacancy_statistic]['average_salary']])

    return salary_statistics


def main():

    env = Env()
    env.read_env()

    salary_statistic = get_average_salaries_hh(LANGS)

    table = AsciiTable(get_table_vacancy(salary_statistic), title='Head Hunter Moscow')
    print(table.table)

    salary_statistic = get_average_salaries_sj(LANGS, env.str('SUPERJOB_TOKEN'))

    table = AsciiTable(get_table_vacancy(salary_statistic), title='Super Job Moscow')
    print(table.table)


if __name__ == '__main__':
    main()
