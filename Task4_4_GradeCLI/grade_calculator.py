"""Weighted grade CLI. Decimal arithmetic; demonstration grade bands."""
import argparse
import csv
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path


def number(value, label):
    try:
        result = Decimal(str(value))
    except InvalidOperation:
        raise ValueError(f'{label} must be a number.') from None
    if not result.is_finite() or result < 0 or result > 100:
        raise ValueError(f'{label} must be a finite number between 0 and 100.')
    return result


def calculate(rows):
    if not rows:
        raise ValueError('At least one assessment is required.')
    total_weight = Decimal(0)
    total = Decimal(0)
    for row in rows:
        name = str(row.get('assessment') or '').strip()
        if not name:
            raise ValueError('Every assessment needs a name.')
        mark = number(row.get('mark'), f'{name}: mark')
        weight = number(row.get('weight'), f'{name}: weight')
        total_weight += weight
        total += mark * weight / 100
    if total_weight != 100:
        raise ValueError(f'Weights must total 100; received {total_weight}.')
    score = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    grade = next(label for threshold, label in [(80, 'High Distinction'), (70, 'Distinction'),
                 (60, 'Credit'), (50, 'Pass'), (0, 'Fail')] if score >= threshold)
    return score, grade


def read_csv(path):
    with open(path, newline='', encoding='utf-8-sig') as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ['assessment', 'mark', 'weight']:
            raise ValueError('CSV header must be assessment,mark,weight in that order.')
        rows = list(reader)
        if any(None in row or any(value is None for value in row.values()) for row in rows):
            raise ValueError('Each CSV row must contain exactly three fields.')
        return rows


def interactive():
    try:
        count = int(input('Number of assessments (1-50): '))
    except ValueError:
        raise ValueError('Assessment count must be an integer.') from None
    if not 1 <= count <= 50:
        raise ValueError('Assessment count must be between 1 and 50.')
    return [dict(assessment=input(f'Assessment {i+1} name: '), mark=input('Mark (0-100): '),
                 weight=input('Weight (%): ')) for i in range(count)]


def main(argv=None):
    parser = argparse.ArgumentParser(description='Calculate a weighted grade. Bands: HD 80, D 70, C 60, P 50.')
    parser.add_argument('--csv', type=Path, help='Input CSV with assessment,mark,weight columns')
    parser.add_argument('--output', type=Path, help='Write result CSV to this path')
    args = parser.parse_args(argv)
    try:
        rows = read_csv(args.csv) if args.csv else interactive()
        score, grade = calculate(rows)
        if args.output:
            with args.output.open('w', newline='', encoding='utf-8') as handle:
                writer = csv.writer(handle)
                writer.writerow(['score', 'grade'])
                writer.writerow([str(score), grade])
        print(f'Weighted result: {score}/100\nGrade: {grade}')
        print('Demonstration rules: round half up to two decimals before classification.')
        return 0
    except (ValueError, OSError, csv.Error, EOFError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
