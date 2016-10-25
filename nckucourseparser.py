import os
import json
import logging

import pandas as pd
from bs4 import BeautifulSoup


class NckuCourseParser(object):
    PARSE_FORMATS = ['dataframe', 'json']

    def __init__(self, html):
        self.html = html
        self._include_fields, self._exclude_fields = list(), list()

    def parse(self, parse_format='dataframe', sort=False):
        if parse_format not in NckuCourseParser.PARSE_FORMATS:
            raise NoSuchFormatError('Current only support json or dataframe')

        soup = BeautifulSoup(self.html, 'html5lib')
        self.df = pd.read_html(str(soup.body.table), flavor='bs4')[0]
        self.__clean_data()

        if all(self.df['系所名稱'] == '查無課程資訊'):
            raise NoCourseAvailableError('No course available')

        if self.include_fields:
            self.df = self.df[self.include_fields]
        elif self.exclude_fields:
            self.df.drop(self.exclude_fields, axis=1, inplace=True)

        if sort:
            self.sort_courses()

        if parse_format == 'dataframe':
            return self.df
        elif parse_format == 'json':
            return self.df.to_dict(orient='records')

    def sort_courses(self, *,
                     dropna=True, delete_zero=True,
                     sort_field="餘額", ascending=False):
        if dropna:
            self.df.dropna(inplace=True)
        if delete_zero:
            self.df = self.df[self.df['餘額'] != 0]

        self.df = self.df.sort_values(by=sort_field, ascending=ascending)
        return self.df

    def __clean_data(self):
        self.df = self.df[self.df['系所名稱'] != '系所名稱']
        cleaned_columns = {col: col.strip() for col in self.df.columns.values}
        self.df.rename(columns=cleaned_columns, inplace=True)
        self.df['餘額'] = self.df['餘額'].apply(NckuCourseParser.__clean_remain)

    @staticmethod
    def __clean_remain(remain):
        if remain == '額滿':
            return 0
        elif remain == '不限':
            return float('nan')
        else:
            return float(remain)

    def export(self, file_name, path='./course_result'):
        self.export_path = path
        self.file_name = file_name

        full_file_name = os.path.join(self.export_path, self.file_name)
        with open(full_file_name, 'w', encoding='utf-8') as export_file:
            json.dump(self.df.to_dict(orient='records'),
                      export_file,
                      ensure_ascii=False,
                      indent=4)

    @property
    def include_fields(self):
        return self._include_fields

    @include_fields.setter
    def include_fields(self, in_f):
        self._exclude_fields = list()

        self._include_fields = in_f

    @property
    def exclude_fields(self):
        return self._exclude_fields

    @exclude_fields.setter
    def exclude_fields(self, ex_f):
        self._include_fields = list()

        self._exclude_fields = ex_f

    @property
    def export_path(self):
        return self._export_path

    @export_path.setter
    def export_path(self, path):
        self._export_path = path
        if not os.path.exists(self.export_path):
            os.makedirs(self.export_path)
            logging.info("Create a directoty {}".format(self.export_path))

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, f_name):
        if os.path.splitext(f_name)[-1] != '.json':
            f_name += '.json'
        self._file_name = f_name


class NoCourseAvailableError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class NoSuchFormatError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


if __name__ == '__main__':
    import sys
    from nckucoursecrawler import NckuCourseCrawler

    arg_num = len(sys.argv)
    if arg_num is 2:
        _, dept_no = sys.argv
        crawler = NckuCourseCrawler(dept_no=dept_no)
    elif arg_num is 4:
        _, dept_no, year, semester = sys.argv
        crawler = NckuCourseCrawler(dept_no=dept_no,
                                    year=year,
                                    semester=semester)
    else:
        print("arg_num should be one or three.\n"
              "one: dept_no\n"
              "three: dept_no year semester")
        exit()

    raw_HTML = crawler.get_raw_HTML()
    parser = NckuCourseParser(raw_HTML)

    try:
        parser.parse()
    except NoCourseAvailableError as e:
        print(e)
    except Exception as e:
        print(e)
    finally:
        parser.export()
