import collections
import re
from sys import argv

import requests
import transliterate
from bs4 import BeautifulSoup
from translate import Translator

url1 = argv[1]
url1 = str(url1)


def get_array(url):
    url_main = url
    response_main = requests.get(url_main)
    main_page = BeautifulSoup(response_main.text, 'lxml')
    urls = main_page.find_all('a', class_='card-cover')
    persons = {}

    for url in urls:
        url_str = str(url)
        find = re.compile(r'/persons/\d{4}/[^"]*')
        url_part = find.findall(url_str)
        for url1 in url_part:
            info_arr = []
            new_url = "https://www.culture.ru" + str(url1)
            response = requests.get(new_url)
            page = BeautifulSoup(response.text, 'lxml')
            name = page.find_all('h1', class_="about-entity_title")
            info = page.find_all('div', class_="attributes_value")
            about = page.find_all('em')
            about_info = ''
            if about:
                about = str(about[0])

                for i in about:
                    if match(i):
                        about_info += i
                    else:
                        continue

            for name in name:
                info_arr.append(about_info)
                for point in info:
                    info_arr.append(point.text)
                persons[name.text] = info_arr

    return persons


def match(text):
    text = text.lower()
    alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя—!»«,.? '
    if text in alphabet:
        return True
    else:
        return False


def create_main_info(info_array, translator):
    persons = info_array

    with open('section_russian_authors2.scs', 'a') as f1:
        f1.write("section_russian_authors -> rrel_key_sc_element:" + '\n')

        [last] = collections.deque(persons, maxlen=1)

        for key in persons:
            name = transliterate.translit(key, reversed=True)
            s = name.split()
            s1 = "_".join(s)
            s2 = re.sub(r"[']", "", s1)
            s2.replace('-', '_')
            name1 = 'person_' + s2

            if key == list(persons.keys())[-1]:
                f1.write(name1 + ';;' + '\n')
            else:
                f1.write(name1 + ';' + '\n')

        f1.write('section_russian_authors = [*^"file://section_russian_authors2.scsi"*];;')

        with open('section_russian_authors2.scsi', 'a') as f:
            for key in persons:
                name = transliterate.translit(key, reversed=True)
                s = name.split()
                s1 = "_".join(s)
                s2 = re.sub(r"[']", "", s1)
                s2.replace('-', '_')
                name1 = 'person_' + s2
                f.write('\n' + name1 + ' <- person;' + '\n' + '=> nrel_main_idtf:' + '\n' + '[' + str(
                    key) + ']' + '(*<- lang_ru;;*);' + '\n')

                i = 3
                info_prof = []
                temp = persons[key]

                while i < len(temp):
                    info_prof.append(temp[i])
                    i += 1

                info_prof = get_prof(info_prof, translator)
                if info_prof is not None:
                    for i in info_prof:
                        f.write('<- ' + i + ';' + '\n')

                html_name = name1 + '.html'
                html_name = 'htmls/' + html_name
                html_text = persons[key][0]
                with open(html_name, 'a') as html:
                    html.write(html_text)

                f.write('<= nrel_main_info::' + '\n' + '"file://' + html_name + '"' + ' (* <-lang_ru;; *);' + '\n')

                date = temp[1]
                date = get_date(date)
                f.write(' => nrel_date_of_birth:' + '\n' + 'date_' + date[
                    2] + '\n' + '(*' + '\n' + '=> nrel_main_idtf:' + '\n' + '[' + date[
                            0] + ']' + '(* <- lang_ru;;*);;' + '\n' + '*);' + '\n')
                temp = temp[2]
                country = get_country(temp, translator)
                f.write('=> nrel_place_of_birth:' + '\n' + 'country_' + country + ';' + '\n')
                f.write(' => nrel_date_of_death:' + '\n' + 'date_' + date[
                    3] + '\n' + '(*' + '\n' + '=> nrel_main_idtf:' + '\n' + '[' + date[
                            1] + ']' + '(* <- lang_ru;;*);;' + '\n' + '*);;' + '\n')
                print(key + 'created...')


def get_date(date):
    date = str(date)
    date_split = date.split(' — ', maxsplit=1)
    birth_date = date_split[0]
    die_date = date_split[1]

    birth_month = get_month(birth_date)
    die_month = get_month(die_date)
    birth_day = get_day(birth_date)
    die_day = get_day(die_date)
    birth_year = get_year(birth_date)
    die_year = get_year(die_date)

    all_date = []

    birth_date_str = birth_day + ' ' + birth_month[0] + ' ' + birth_year
    all_date.append(birth_date_str)
    die_date_str = die_day + ' ' + die_month[0] + ' ' + die_year
    all_date.append(die_date_str)
    birth_date = birth_day + '_' + birth_month[1] + '_' + birth_year
    all_date.append(birth_date)
    die_date = die_day + '_' + die_month[1] + '_' + die_year
    all_date.append(die_date)

    return all_date


def get_month(date):
    birth_date = date
    month = []
    month_d = ''
    find_month = re.compile(r'января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря')
    birth_month = find_month.findall(birth_date)
    month_str = birth_month[0]
    birth_month.clear()

    if month_str == 'января':
        month_d = '01'
    elif month_str == 'февраля':
        month_d = '02'
    elif month_str == 'марта':
        month_d = '03'
    elif month_str == 'апреля':
        month_d = '04'
    elif month_str == 'мая':
        month_d = '05'
    elif month_str == 'июня':
        month_d = '06'
    elif month_str == 'июля':
        month_d = '07'
    elif month_str == 'августа':
        month_d = '08'
    elif month_str == 'сентября':
        month_d = '09'
    elif month_str == 'октября':
        month_d = '10'
    elif month_str == 'ноября':
        month_d = '11'
    elif month_str == 'декабря':
        month_d = '12'

    month.append(month_str)
    month.append(month_d)

    return month


def get_day(date):
    date = date
    find_day = re.compile(r'\d{2} ')
    day = find_day.findall(date)
    day = day[0]
    day = day.replace(' ', '')

    return day


def get_year(date):
    date = date
    find_year = re.compile(r'\d{4}')
    year = find_year.findall(date)
    year = year[0]

    return year


def get_country(country, translator):
    if country == 'Российская империя':
        result = 'Russian_empire'
    else:
        country = country
        result = translator.translate(country)
        result = result.replace(' ', '_')
        result = result.replace('.', '')
        result = result.replace(',', '')
        result = result.replace('?', '')
        result = result.replace('-', '_')

    if len(result) > 30:
        return 'Russia'
    else:
        return result


def get_prof(info_prof, translator):
    prof = info_prof
    result_arr = []
    for i in prof:
        result = translator.translate(i)
        result = result.replace(' ', '_')
        result = result.replace('.', '')
        result = result.replace(',', '')
        result = result.replace('?', '')
        result = result.replace('-', '_')
        result = result.lower()
        result_arr.append(result)

    prof.clear()

    for i in result_arr:
        if len(i) > 20:
            return None
    else:
        return result_arr


def main(url):
    translator = Translator(from_lang="russian", to_lang="english")
    person_array = get_array(url)
    create_main_info(person_array, translator)

    exit()


main(url1)
