import logging

import requests


class NckuCourseCrawler:
    CURRENT_COURSE_URL = "http://140.116.165.74/qry/qry001.php"
    COURSE_QUERY_URL = "http://140.116.165.74/qry/qry002.php"

    def __init__(self, dept_no, year='', semester=''):
        self.params = {'syear': year, 'sem': semester, 'dept_no': dept_no}

    @property
    def year(self):
        return self.params['syear']

    @year.setter
    def year(self, year):
        self.params['syear'] = year.zfill(4)

    @property
    def semester(self):
        return self.params['sem']

    @semester.setter
    def semester(self, sem):
        self.params['sem'] = sem

    @property
    def department(self):
        return self.params['dept_no']

    @department.setter
    def department(self, dept_no):
        self.params['dept_no'] = dept_no

    def get_raw_HTML(self):
        if self.params["sem"] and self.params["syear"]:
            url_suffix = NckuCourseCrawler.COURSE_QUERY_URL
        else:
            url_suffix = NckuCourseCrawler.CURRENT_COURSE_URL
        req = requests.get(url_suffix, params=self.params)
        logging.info("Parse {}".format(req.url))
        req.encoding = 'utf-8'
        raw_html = req.text
        return raw_html


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    crawler = NckuCourseCrawler(year="0103", semester=1, dept_no="AN")
    raw_HTML = crawler.get_raw_HTML()
    print(raw_HTML)
