import random
import string
import sys
import unittest
from datetime import datetime

import requests

BASE_URL = None
INVALID_REQUESTS = [400, 409, 422]
VALID_REQUESTS = [200, 201, 204]


class VerifyStudents(unittest.TestCase):
    FIRST_NAMES = [
        'Anne', 'Bart', 'Cyan', 'Desmond', 'Edwina', 'Frank', 'Gal',
        'Henry', 'Ina', 'Judy', 'Kate', 'Louis', 'Mark', 'Nancy', 'Oswald',
        'Percy', 'Quincy', 'Rebecca', 'Susan', 'Triana', 'Ulf', 'Veronica',
        'Wanda', 'Xavier', 'Yolanda', 'Zander',
    ]

    LAST_NAMES = [
        'Abernathy', 'Brinkley', 'Crispin', 'Drummond', 'Edwards', 'Frank',
        'Gladfeld', 'Iriqouois', 'Jones', 'Kapshaw', 'Livery', 'Matthews',
        'Nuncle', 'Oswego', 'Penny', 'Quincy', 'Reynolds', 'Stevens', 'Tingle',
        'Ulfmanson', 'Violet', 'Walters', 'Xavier', 'Yellen', 'Zingle',
    ]

    def get(self, query_args={}, path=None):
        return requests.get(self.url(path), params=query_args)

    def post(self, body_dict={}, path=None):
        return requests.post(self.url(path), json=body_dict)

    def random_string(self, length=10):
        return ''.join([random.choice(string.ascii_letters) for i in range(length)])

    def url(self, path=None):
        if path is None:
            path = self.path()
        return BASE_URL + path

    def valid_student(self, **kwargs):
        student = {
            'email': '{}@example.com'.format(self.random_string(12)),
            'first_name': random.choice(self.FIRST_NAMES),
            'last_name': random.choice(self.LAST_NAMES),
        }
        student.update(kwargs)
        return student

    def assert_get_in(self, expected_status, msg, path=None, query_args={}):
        response = self.get(query_args=query_args, path=path)
        return self.assert_status_in(response, expected_status, msg)

    def assert_post_in(self, body_dict, expected_status, msg):
        response = self.post(body_dict)
        return self.assert_status_in(response, expected_status, msg)

    def assert_status_in(self, response, expected_status, msg):
        status = response.status_code
        if status not in expected_status:
            self.fail(msg + ': expected any status in {}, got {}'.format(expected_status, status))
        return response


class VerifyCreate(VerifyStudents):
    def path(self):
        return '/students'

    def test_fail_missing_last_name(self):
        to_create = self.valid_student(last_name=None)
        self.assert_post_in(to_create, INVALID_REQUESTS, 'With no last name')

    def test_fail_missing_email_or_username(self):
        to_create = self.valid_student(email='')
        self.assert_post_in(to_create, INVALID_REQUESTS, 'With no email or username')

    def test_fail_duplicate_email(self):
        to_create = self.valid_student()
        self.assert_post_in(to_create, VALID_REQUESTS, 'With valid data having an arbitrary email')
        self.assert_post_in(to_create, INVALID_REQUESTS, 'With valid data but the same arbitrary email')

    def test_generates_display_name(self):
        to_create = self.valid_student()
        doc = self.assert_post_in(
            to_create, VALID_REQUESTS,
            'With valid data to check display_name'
        ).json()
        self.assertEqual(
            doc['display_name'],
            '{} {}'.format(to_create['first_name'], to_create['last_name']))

    def test_can_provide_display_name(self):
        to_create = self.valid_student(display_name='The Boss')
        doc = self.assert_post_in(
            to_create, VALID_REQUESTS,
            'With valid data to override generated display_name'
        ).json()
        self.assertEqual(doc['display_name'], 'The Boss')

    def test_can_fetch_created(self):
        to_create = self.valid_student()
        created = self.assert_post_in(
            to_create, VALID_REQUESTS, 'With valid data to re-fetch').json()
        fetched = self.get(path='/students/{}'.format(created['id'])).json()
        for k in to_create:
            self.assertEqual(fetched[k], to_create[k])
        self.assertEqual(fetched['id'], created['id'])

    def test_fills_in_date_fields(self):
        to_create = self.valid_student()
        created = self.assert_post_in(
            to_create, VALID_REQUESTS,
            'With valid data to check dates'
        ).json()
        for date_field in ['created_at', 'started_at']:
            self.assertIn(date_field, created)
            self.assertIsNotNone(created[date_field])
            self.assertNotEqual(created[date_field], '')
        started_at = datetime.strptime(created['started_at'], '%Y-%m-%d')
        self.assertEqual(created['started_at'], started_at.strftime('%Y-%m-%d'))
        created_at = datetime.strptime(created['created_at'], '%Y-%m-%d %H:%M:%S')
        self.assertEqual(created['created_at'], created_at.strftime('%Y-%m-%d %H:%M:%S'))


class VerifyFetch(VerifyStudents):
    def test_fetch_invalid_id(self):
        self.assert_get_in([404], 'With invalid ID', path='/students/9876')


class VerifySearch(VerifyStudents):
    def create(self, **kwargs):
        to_create = self.valid_student(**kwargs)
        return self.post(to_create, path='/students').json()

    def path(self):
        return '/students'

    def assert_first_names(self, doc, expected_sorted_names):
        self.assertEqual(len(doc['students']), len(expected_sorted_names))
        actual_sorted_names = sorted([s['first_name'] for s in doc['students']])
        self.assertEqual(actual_sorted_names, expected_sorted_names)

    def test_no_criteria_is_invalid(self):
        self.assert_get_in(INVALID_REQUESTS, 'With no criteria')

    def test_empty_results_with_records_and_no_match(self):
        self.create()
        doc = self.assert_get_in(
            [200], 'With no match',
            query_args={'name': 'Grover Cleveland'}
        ).json()
        self.assertEqual(doc['students'], [])

    def test_single_match_first_name(self):
        for first_name in ['Steve', 'Simone', 'Sylvie', 'Sharky']:
            self.create(first_name=first_name)
        doc = self.assert_get_in(
            [200], 'With a single match on first_name',
            query_args={'name': 'imon'}
        ).json()
        self.assertEqual(len(doc['students']), 1)
        self.assertEqual(doc['students'][0]['first_name'], 'Simone')

    def test_multiple_match_any_name(self):
        self.create(first_name="Jamie", last_name="Jameson")
        self.create(first_name="Jimbo", display_name="James Garrison III")
        self.create(first_name="Jennifer")
        self.create(first_name="Jackie")
        doc = self.assert_get_in(
            [200], 'With multiple matches on name',
            query_args={'name': 'JAM'}
        ).json()
        self.assert_first_names(doc, ['Jamie', 'Jimbo'])

    def test_no_match_started_after(self):
        doc = self.assert_get_in(
            [200], 'With no match checking started_after',
            query_args={'started_after': '2019-10-31'}
        ).json()
        self.assertEqual(doc['students'], [])

    def test_multiple_matches_started_after(self):
        self.create(first_name="Chuck", started_at="2016-11-09")
        self.create(first_name="Carol", started_at="2019-01-13")
        self.create(first_name="Cindy", started_at="2018-04-08")
        self.create(first_name="Carl", started_at="2017-09-12")
        doc = self.assert_get_in(
            [200], 'With multiple matches checking started_after',
            query_args={'started_after': '2018-03-31'}
        ).json()
        self.assert_first_names(doc, ['Carol', 'Cindy'])


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("Usage: python {} url-of-solution".format(sys.argv[0]))
        sys.exit(1)

    BASE_URL = sys.argv[1].rstrip('/')
    # lop this off so unittest doesn't try to do something with it
    del(sys.argv[1])

    try:
        response = requests.get(BASE_URL + '/service/health')
        if response.status_code >= 400:
            print("FAIL: Health check got bad status ({}), not continuing".format(response.status_code))
            sys.exit(1)
    except requests.RequestException as e:
        print("FAIL: Caught exception with health check -- {}".format(e))
        sys.exit(1)
    unittest.main(verbosity=2)
