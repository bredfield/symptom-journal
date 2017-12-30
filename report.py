#!/usr/bin/python

import argparse
import datetime
import json
from itertools import ifilter
import os


DATE_FORMAT = '%m-%d-%Y'


def valid_date(date_string):
    """validates a user-inputted date string.

    args:
        date_string (str): properly formatted date string

    returns:
        datetime: converted datetime object
    """
    try:
        return datetime.datetime.strptime(date_string, DATE_FORMAT).date()
    except ValueError:
        raise argparse.ArgumentTypeError('Not a valid date: \'{0}\'.'.format(date_string))


def read_journal(journal_path):
    """Reads the journal at the specified path. If a journal doesn't exist,
    creates a new one after prompting the patient's name.

    args:
        journal_path (str): path to journal file to read

    returns:
        dict: json journal contents
    """
    with open(journal_path, 'rb') as infile:
        journal = json.load(infile)

    # convert string times to datetime objects
    for log in journal['journal']:
        log['date'] = datetime.datetime.strptime(log['date'], DATE_FORMAT).date()

    return journal

def parse_report_data(journal, start_date, end_date):
    """Takes a journal and collects relevant report data

    args:
        journal (dict): journal object

    returns:
        (str, []): report text, report plot data
    """
    sorted_logs = sorted(journal['journal'], key=lambda x: x['date'])
    filtered_logs = ifilter(
        lambda x: x['date'] >= start_date and x['date'] <= end_date,
        sorted_logs
    )

    # setup initial data
    report_text = '=====\nDaily symptom journal for {} ({} - {})\n=====\n\n'.format(
        journal['patient'],
        start_date.strftime(DATE_FORMAT),
        end_date.strftime(DATE_FORMAT),
    )
    report_plot_data = {}

    for log in filtered_logs:
        report_text += '--- {} ---\n'.format(log['date'].strftime(DATE_FORMAT))

        for symptom in log['symptoms']:
            report_text += '- {}: {}\n'.  format(symptom['name'], symptom['value'])

            symptom_data = (log['date'], symptom['value'])
            symptom_name = symptom['name']

            if symptom_name in report_plot_data:
                report_plot_data[symptom_name].append(symptom_data)
            else:
                report_plot_data[symptom_name] = [symptom_data]

        if len(log['notes']):
            report_text += '\n  Notes: {}\n'.format(log['notes'])

        report_text += '\n'

    return report_text, report_plot_data


def store_report_text(report_text, report_dir, report_name):
    """generates a text file from symptom data

    args:
        report_text (str): report text
        report_dir: directory to store report in
        report_name: filename for report
    """
    with open(os.path.join(report_dir, '{}.txt'.format(report_name)), 'wb') as outfile:
        outfile.write(report_text)


def store_report_plot(report_plot_data, report_dir, report_name):
    """generates a plot with symptom data and stores to a png image file

    args:
        report_plot_data (dict): dict with symptom data
        report_dir: directory to store report in
        report_name: filename for report
    """
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    # format x axis date ticks
    fig, ax = plt.subplots()
    date_format = mdates.DateFormatter(DATE_FORMAT)
    ax.xaxis.set_major_formatter(date_format)

    # plot each symptom
    for symptom_name, symptom_data in report_plot_data.iteritems():
        plt.plot([p[0] for p in symptom_data], [p[1] for p in symptom_data], label=symptom_name)

    plt.legend()

    # store figure
    fig.set_size_inches(18.5, 10.5)
    plt.savefig(
        os.path.join(report_dir, '{}_plot.png'.format(report_name)),
        dpi=100
    )


def main():
    today = datetime.date.today()

    parser = argparse.ArgumentParser('Symptom Journal Report')
    parser.add_argument(
        '-j', '--journal',
        type=str,
        default='journal.json',
        help='The path the journal you\'d like to update'
    )
    parser.add_argument(
        '-s', '--start-date',
        type=valid_date,
        default=(today - datetime.timedelta(days=30)),
        help='The start date of the report. Follows the format {}'.format(DATE_FORMAT)
    )
    parser.add_argument(
        '-e', '--end-date',
        type=valid_date,
        default=today,
        help='The start date of the report. Follows the format {}'.format(DATE_FORMAT)
    )
    parser.add_argument(
        '-r', '--reports',
        type=str,
        default='reports',
        help='The directory to store reports'
    )
    parser.add_argument(
        '-p', '--plot',
        dest='plot',
        action='store_true'
    )

    args = parser.parse_args()

    try:
        journal = read_journal(args.journal)
    except Exception as e:
        print '\n [X] Failed to read journal. Error: {}'.format(e)

    report_text, report_plot_data = parse_report_data(journal, args.start_date, args.end_date)

    report_name = '{}_{}'.format(
        args.start_date.strftime(DATE_FORMAT),
        args.end_date.strftime(DATE_FORMAT)
    )

    store_report_text(report_text, args.reports, report_name)

    if args.plot:
        store_report_plot(report_plot_data, args.reports, report_name)


if __name__ == '__main__':
    main()
