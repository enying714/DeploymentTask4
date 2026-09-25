import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


grade = load('grade', 'Task4_4_GradeCLI/grade_calculator.py')
study = load('study', 'Task4_3_StudyManager/app.py')
hello = load('hello', 'Task4_2_HelloWeb/app.py')


class GradeTests(unittest.TestCase):
    def test_weighted_example(self):
        result = grade.calculate(grade.read_csv(ROOT / 'Task4_4_GradeCLI/samples/valid.csv'))
        self.assertEqual((str(result[0]), result[1]), ('79.00', 'Distinction'))

    def test_boundaries_and_rounding(self):
        for mark, expected in [('0','Fail'), ('49.99','Fail'), ('50','Pass'), ('60','Credit'),
                               ('70','Distinction'), ('79.994','Distinction'),
                               ('79.995','High Distinction'), ('80','High Distinction'), ('100','High Distinction')]:
            with self.subTest(mark=mark):
                self.assertEqual(grade.calculate([dict(assessment='A', mark=mark, weight='100')])[1], expected)

    def test_bad_marks(self):
        for mark in ['-1','101','NaN','Infinity','abc','',None]:
            with self.subTest(mark=mark), self.assertRaises(ValueError):
                grade.calculate([dict(assessment='A', mark=mark, weight='100')])

    def test_bad_weights(self):
        for weight in ['90','101','-1','NaN','abc']:
            with self.subTest(weight=weight), self.assertRaises(ValueError):
                grade.calculate([dict(assessment='A', mark='80', weight=weight)])

    def test_missing_assessments(self):
        for rows in [[], [dict(assessment='', mark=80, weight=100)]]:
            with self.assertRaises(ValueError):
                grade.calculate(rows)

    def test_csv_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'input.csv'
            for content in ['name,mark,weight\nA,80,100\n', 'assessment,mark,weight\nA,80\n',
                            'assessment,mark,weight\nA,80,100,extra\n']:
                path.write_text(content)
                with self.assertRaises(ValueError):
                    grade.read_csv(path)

    def test_cli_output_and_error_exit(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'result.csv'
            command = [sys.executable, str(ROOT / 'Task4_4_GradeCLI/grade_calculator.py'), '--csv']
            valid = subprocess.run(command + [str(ROOT / 'Task4_4_GradeCLI/samples/valid.csv'), '--output', str(output)], capture_output=True, text=True)
            self.assertEqual(valid.returncode, 0, valid.stderr)
            self.assertIn('79.00,Distinction', output.read_text())
            invalid = subprocess.run(command + [str(ROOT / 'Task4_4_GradeCLI/samples/invalid-weights.csv')], capture_output=True, text=True)
            self.assertEqual(invalid.returncode, 2)
            self.assertIn('Weights must total 100', invalid.stderr)

    def test_interactive(self):
        result = subprocess.run([sys.executable, str(ROOT / 'Task4_4_GradeCLI/grade_calculator.py')],
                                input='1\nExam\n80\n100\n', capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('High Distinction', result.stdout)


class WebTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.config = dict(TESTING=True, SECRET_KEY='test-only', DATABASE=str(Path(self.temp.name) / 'tasks.db'))
        self.app = study.create_app(self.config)
        self.client = self.app.test_client()
        self.client.get('/')
        with self.client.session_transaction() as session:
            self.csrf = session['csrf']

    def tearDown(self):
        self.temp.cleanup()

    def add(self, **overrides):
        data = dict(name='Read Docker notes', subject='SWE40006', due_date='2026-10-08', priority='High', csrf=self.csrf)
        data.update(overrides)
        return self.client.post('/tasks', data=data)

    def test_hello_and_health(self):
        client = hello.app.test_client()
        self.assertIn(b'Hello World!', client.get('/').data)
        self.assertEqual(client.get('/health').json['status'], 'ok')
        self.assertEqual(self.client.get('/health').status_code, 200)

    def test_add_complete_delete(self):
        self.assertEqual(self.add().status_code, 303)
        self.assertIn(b'Read Docker notes', self.client.get('/').data)
        self.assertEqual(self.client.post('/tasks/1/complete', data={'csrf':self.csrf}).status_code, 303)
        self.assertNotIn(b'Mark Read Docker notes complete', self.client.get('/').data)
        self.assertEqual(self.client.post('/tasks/1/delete', data={'csrf':self.csrf}).status_code, 303)
        self.assertNotIn(b'Read Docker notes', self.client.get('/').data)

    def test_validation(self):
        for invalid in [dict(name=''), dict(name='x'*121), dict(subject=''), dict(subject='x'*61),
                        dict(due_date='2026-02-30'), dict(priority='Urgent')]:
            with self.subTest(invalid=invalid):
                self.assertEqual(self.add(**invalid).status_code, 400)
        self.assertNotIn(b'Read Docker notes', self.client.get('/').data)

    def test_csrf_and_missing_id(self):
        self.assertEqual(self.add(csrf='bad').status_code, 400)
        self.assertEqual(self.client.post('/tasks/999/delete', data={'csrf':self.csrf}).status_code, 404)
        self.assertEqual(self.client.get('/tasks/1/delete').status_code, 405)

    def test_html_escaping_and_parameterized_sql(self):
        self.assertEqual(self.add(name='<script>alert(1)</script>', subject="x'); DROP TABLE tasks;--").status_code, 303)
        html = self.client.get('/').data
        self.assertNotIn(b'<script>alert(1)</script>', html)
        self.assertIn(b'&lt;script&gt;', html)
        self.assertEqual(self.client.get('/health').status_code, 200)

    def test_persists_across_app_instances(self):
        self.add()
        second = study.create_app(self.config).test_client()
        self.assertIn(b'Read Docker notes', second.get('/').data)


if __name__ == '__main__':
    unittest.main(verbosity=2)
