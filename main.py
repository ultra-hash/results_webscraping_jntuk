from bs4 import BeautifulSoup
import requests, os.path, time


def input_data(hall_ticket, course, reg, start_year, end_year):
    baseurl = "https://jntukresults.edu.in/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0"
    }
    page = requests.get(baseurl, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    courses = ['b.tech', 'm.tech', 'mba']
    course_and_link = dict()
    btw = range(start_year, end_year + 1)
    # find all links for the given data from home page
    for link in soup.find_all('td'):
        if course in courses:
            if str(course).lower() in str(link).lower():
                for i in btw:
                    if str(i) in str(link).lower():
                        u = BeautifulSoup(str(link), 'html.parser').find('a')
                        u_href = u.get('href')
                        course_and_link[u.contents[0]] = baseurl + u_href

        else:
            raise Exception('course not available, choose between "b.tech , m.tech, mba"')

    return open_links(course_and_link, hall_ticket, reg)


def open_link(url, title, hall_ticket, reg):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0"
    }
    r = requests.get(url, headers=headers)
    cookies = r.cookies
    soup = BeautifulSoup(r.text, 'html.parser')
    token = None
    for link in soup.find_all('script'):
        if 'accessToken' in str(link):
            i = str(link).find('accessToken')
            comma = str(link).find(',', i)
            token = str(link)[i + 14:comma]
    # print(len('https://jntukresults.edu.in/view-results-'))  # is 41
    url_id = url[41:-5]
    if token:
        result_url = f'https://jntukresults.edu.in/results/res.php?ht={hall_ticket}&id={url_id}&accessToken={token}'
        r = requests.get(result_url, headers=headers, cookies=cookies)
        if "Invalid Hall Ticket Number" not in r.text:
            r = str(r.text)
            with open(f'{hall_ticket}_{reg}.html', 'a') as file:
                file.write(title+'<br>')
                file.write(r)
                process_results_table(r, title, hall_ticket, reg)
    else:
        open_link(url, title, hall_ticket, reg)


def open_links(course_and_link, hall_ticket, reg):
    n = len(course_and_link)
    count = 0
    for title, url in course_and_link.items():
        sample = time.time()
        open_link(url, title, hall_ticket, reg)
        sample = time.time() - sample
        count += 1
        # print(('#'*(progress(n, count))).ljust(100, '.'), f'[{progress(n, count)}%]', f'{(len(course_and_link)-count)*(round(sample/60, 2))} remaining time')
        print(f'[{str(progress(n, count)).ljust(3," ")}%]', f'{round((len(course_and_link)-count)*sample, 2)} seconds remaining time')
    if os.path.exists(f'{hall_ticket}_{reg}.html'):
        print(f'File Generated successfully --> filename {hall_ticket}_{reg}.html')
    else:
        print('No result to print')


def process_results_table(html_data, title, hall_ticket, reg):
    soup = BeautifulSoup(html_data, "html.parser")
    result = dict()
    for i in soup.find('table').find_all('tr'):
        if '<td>' in str(i):
            rows = list(BeautifulSoup(str(i), "html.parser").find_all('td'))
            for j in range(len(rows)):
                rows[j] = str(rows[j])[4:-5]
                result[f'{rows[0]}'] = rows[1:]

            with open(f'{hall_ticket}_{reg}_dict.html', 'a') as file:
                file.write(title + '<br><br>')
                for key, value in result.items():
                    file.write(key)
                    file.write(str(value)+'<br>')
                file.write('<br>')


def progress(total, complete):
    return int((complete/total)*100)


if __name__ == "__main__":
    t1 = time.time()
    input_data('16xxx0340', 'b.tech', 'R16', 2017, 2018)  # hall_ticket_number , course, regulation, from_year, to_year
    print('Total time  Taken: ', round(time.time() - t1, 2), 'seconds')


