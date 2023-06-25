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

    vacancies_processed = 0
    salary_amount = 0 

    for vacancy in vacancies:
        
        if vacancy['salary']:
            vacancies_processed += 1
            salary_amount += predict_salary(vacancy['salary']['from'], vacancy['salary']['to'])
       
    return vacancies_processed, int(salary_amount/vacancies_processed)



def get_average_salaries_hh(langs):

    statistic_salaries ={}
      
    headers = {
        'User-Agent': '5-HH-SJ/1.0 (lamerork@gmail.com)',
        'Accept-Language': 'ru-RU'
    }
      
    for lang in langs:

        page = 0
        vacancies_processed = 0
        salary = 0
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
            response = requests.get('https://api.hh.ru/vacancies', params=payload, headers=headers)
            response.raise_for_status()
            response.status_code

            vacancies = response.json()
            pages = int(vacancies['pages'])
            
            vacancies_processed_page, salary_page = get_salaries_hh(vacancies['items'])
            
            vacancies_processed += vacancies_processed_page
            salary += salary_page
            page += 1

        statistic_salaries[lang] = {'vacancies_found': vacancies['found'], 'vacancies_processed': vacancies_processed, 'average_salary': int(salary/pages)}

    return statistic_salaries



def get_salaries_sj(vacancies):

    vacancies_processed = 0
    salary_amount = 0 

    for vacancy in vacancies['objects']:
        if vacancy['payment_from'] or vacancy['payment_to']:
            vacancies_processed += 1
            salary_amount += predict_salary(vacancy['payment_from'], vacancy['payment_to'])

    return vacancies_processed, int(salary_amount/vacancies_processed)



def get_average_salaries_sj(langs, token):

    predict_salaries = {}    
    headers = {
        'X-Api-App-Id': token
    }    
    
    for lang in langs:

        params = {
            'keyword': f'Программист {lang}',
            'town': 'Москва',
            'period': PERIOD_SJ,
            'catalogues': CATALOGUES_SJ
        }

        response = requests.get('https://api.superjob.ru/2.0/vacancies/', params=params, headers=headers)
        response.raise_for_status()
        vacancies = response.json()

        if vacancies["total"]:
            vacancies_processed, salary = get_salaries_sj(vacancies)
            predict_salaries[lang] = {'vacancies_found': vacancies['total'], 'vacancies_processed': vacancies_processed, 'average_salary': salary}

    return predict_salaries   



def get_list_vacancies(vacancies):
     
    statistic_salaries =[['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]

    for vacancy in vacancies:
        statistic_salaries.append([vacancy, vacancies[vacancy]['vacancies_found'], vacancies[vacancy]['vacancies_processed'], vacancies[vacancy]['average_salary']])

    return statistic_salaries

    

def main():

    env = Env()
    env.read_env()

    vacancies = get_average_salaries_hh(LANGS)

    table = AsciiTable(get_list_vacancies(vacancies), title='Head Hunter Moscow')
    print(table.table)

    vacancies = get_average_salaries_sj(LANGS, env.str('SUPERJOB_TOKEN'))
 
    table = AsciiTable(get_list_vacancies(vacancies), title='Super Job Moscow')
    print(table.table)

if __name__ == '__main__':
    main()