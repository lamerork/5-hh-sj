import requests
import time
from environs import Env
from terminaltables import AsciiTable



def predict_salary(salary_from, salary_to):

    if salary_from and salary_to:
            return int((salary_from + salary_to)/2)
        
    if salary_from:
            return int(salary_from * 1.2)
        
    if salary_to:
            return int(salary_to * 0.8)
    


def predict_salary_hh(vacancy):
        return predict_salary(vacancy['salary']['from'], vacancy['salary']['to'])


  
def get_salaries_hh(vacancies):

    vacancies_processed = 0
    salary_amount = 0 

    for vacancy in vacancies:
        
        if vacancy['salary']:
            vacancies_processed += 1
            salary_amount += predict_salary_hh(vacancy)
       
    return vacancies_processed, int(salary_amount/vacancies_processed)


def get_vacancies_hh(langs):

    result ={}
      
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
                'area': '1',
                'period': '30',
                'page': page,
                'per_page': '100'
                }
         
            time.sleep(0.25)
            response = requests.get('https://api.hh.ru/vacancies', params=payload, headers=headers)
            response.raise_for_status()

            vacancies = response.json()['items']
            pages = int(response.json()['pages'])
            
            vacancies_processed_page, salary_page = get_salaries_hh(vacancies)
            
            vacancies_processed += vacancies_processed_page
            salary += salary_page
            page += 1
#            print(f'Язык {lang} Страница: {page} из {pages} Всего найдено: {vacancies_processed}')
        result[lang] = {'vacancies_found': response.json()['found'], 'vacancies_processed': vacancies_processed, 'average_salary': int(salary/pages)}
    return result


def predict_salary_sj(vacancy):
    return predict_salary(vacancy['payment_from'], vacancy['payment_to'])



def get_salaries_sj(vacancies):

    vacancies_processed = 0
    salary_amount = 0 

    for vacancy in vacancies['objects']:
        if predict_salary_sj(vacancy):
            vacancies_processed += 1
            salary_amount += predict_salary_sj(vacancy)

    return vacancies_processed, int(salary_amount/vacancies_processed)

     

def get_vacancies_sj(langs, token):

    result = {}    
    headers = {
        'X-Api-App-Id': token
    }    
    
    for lang in langs:

        params = {
            'keyword': f'Программист {lang}',
            'town': 'Москва',
            'period': 7,
            'catalogues': 48
        }

        response = requests.get('https://api.superjob.ru/2.0/vacancies/', params=params, headers=headers)
        response.raise_for_status()
        vacancies = response.json()

        if vacancies["total"]:
            vacancies_processed, salary = get_salaries_sj(vacancies)
            result[lang] = {'vacancies_found': vacancies['total'], 'vacancies_processed': vacancies_processed, 'average_salary': salary}

    return result   

def print_results(items, title):
     
    result =[['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]

    for item in items:
        result.append([item, items[item]['vacancies_found'], items[item]['vacancies_processed'], items[item]['average_salary']])

    table = AsciiTable(list(result), title=title)
    print(table.table)

def main():

    env = Env()
    env.read_env()

    langs = ['JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'C#']

    result = get_vacancies_hh(langs)
    print_results(result, 'Head Hunter Moscow')

    result = get_vacancies_sj(langs, env.str('SUPERJOB_TOKEN'))
    print_results(result, 'Super Job Moscow')
 
    
if __name__ == '__main__':
    main()