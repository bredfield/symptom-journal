#!/usr/bin/python

import argparse
import datetime
import json
import os
import shutil
import sys


DATE_FORMAT = '%m-%d-%Y'


def read_journal(journal_path):
    """Reads the journal at the specified path. If a journal doesn't exist,
    creates a new one after prompting the patient's name.

    args:
        journal_path (str): path to journal file to read

    returns:
        dict: json journal contents
    """
    try:
        with open(journal_path, 'rb') as infile:
            return json.load(infile)
    except Exception as e:
        pass

    # no journal found, start a new one
    print '\n--- No journal found, let\'s start a new one.'
    print '> What\'s your full name?'
    name_input = sys.stdin.readline().rstrip()

    return {
        'patient': name_input,
        'journal': []
    }


def get_existing_symptoms(journal):
    """Given a journal w/ proper format, aggregates all the symptoms

    args:
        journal (dict)

    returns:
        [str]: array of symptom names
    """
    symptoms = []

    for log in journal['journal']:
        symptoms.extend([
            symptom['name'] for symptom in log['symptoms'] if symptom["name"] not in symptoms
        ])

    return symptoms


def get_date():
    """Prompts the user for the date to log. Defaults to today's date

    returns:
        datetime: date to log
    """
    today = datetime.date.today()

    print "\n> What date is this log for? (leave blank for today [{}])".format(
        today.strftime(DATE_FORMAT)
    )

    date_input = sys.stdin.readline().rstrip()

    # parse date, default to today
    try:
        return datetime.datetime.strptime(date_input, DATE_FORMAT)
    except Exception as e:
        return today


def log_symptom(existing_symptoms):
    """Logs a new symptom via stdin. Constructs a list of symptom options based on existing ones.
    Will act recursively if input is invalid.

    args:
        [str]: list of existing symptoms

    returns:
        dict: symptom
    """
    num_existing_symptoms = len(existing_symptoms)
    new_symptom_option = num_existing_symptoms + 1
    done_option = new_symptom_option + 1

    for i, existing_symptom in enumerate(existing_symptoms):
        print '{option}: {name}'.format(
            option=i+1,
            name=existing_symptom
        )

    print '{}: Log new symptom'.format(new_symptom_option)
    print '{}: Done adding symptoms'.format(done_option)
    print '> Choose a symptom option from the above list'

    option_input = int(sys.stdin.readline().rstrip())

    # existing symptom
    if option_input <= num_existing_symptoms:
        symptom_name = existing_symptoms[option_input - 1]
    # new symptom (prompt user for name)
    elif option_input == new_symptom_option:
        print '> What\'s the name of the symptom you\'d like to log?'
        symptom_name = sys.stdin.readline().rstrip()
    # user is done adding symptoms
    elif option_input == done_option:
        return None
    # bad option, ty again
    else:
        print "\n[X] Invalid option! Try that again.\n"
        return log_symptom(existing_symptoms)

    print '> On a scale of 0 to 10, how severe is the symptom?'
    symptom_value = int(sys.stdin.readline().rstrip())

    if symptom_value < 0 or symptom_value > 10:
        print "\n[X] Invalid symptom severity! Try that again.\n"
        return log_symptom(existing_symptoms)

    return {
        'name': symptom_name,
        'value': symptom_value
    }

def log_notes():
    """Prompts the user to log notes for the entry

    returns:
        str: note
    """
    print '\n> Log notes for today\'s entry (optional). Single line only.'
    return sys.stdin.readline().rstrip()


def write_journal(journal_path, journal, journal_archive_dir):
    """writes the updated journal to it\'s JSON file path

    args:
        journal_path (str): path to write
        journal (dict): updated journal to write
        journal_archive_dir (str): path to archive directory

    """
    # write main journal file
    with open(journal_path, 'wb') as outfile:
        json.dump(journal, outfile, sort_keys=True, indent=4)

    # and archive for posderity
    if not os.path.exists(journal_archive_dir):
        os.makedirs(journal_archive_dir)

    today = datetime.datetime.now().isoformat()
    journal_archive_path = os.path.join(journal_archive_dir, "archive_{}.json".format(today))

    shutil.copyfile(journal_path, journal_archive_path)

def main():
    print "============================="
    print "=== Daily Symptom Journal ==="
    print "============================="
    parser = argparse.ArgumentParser('Symptom Journal Log')
    parser.add_argument(
        '-j', '--journal',
        type=str,
        default='journal.json',
        help='The path the journal you\'d like to update'
    )
    parser.add_argument(
        '-a', '--archive',
        type=str,
        default='journal_archive',
        help='The journal archive directory path'
    )
    parser.add_argument(
        '-n', '--num-daily-symptoms',
        type=int,
        default=5,
        help='The number of daily symptoms to log'
    )

    args = parser.parse_args()

    journal = read_journal(args.journal)

    print '\n--- Oh hi, {}.'.format(journal['patient'])

    existing_symptoms = get_existing_symptoms(journal)

    # log symptoms!
    log = {
        'date': get_date().strftime(DATE_FORMAT),
        'symptoms': []
    }

    while len(log['symptoms']) < args.num_daily_symptoms:
        print '\n--- Logging symptom {i} of {total}'.format(
            i=len(log['symptoms']) + 1,
            total=args.num_daily_symptoms
        )

        symptom = log_symptom(existing_symptoms)

        # done adding symptoms
        if not symptom:
            break

        log['symptoms'].append(symptom)

        # remove symptom from existing options once logged
        if symptom['name'] in existing_symptoms:
            existing_symptoms.remove(symptom['name'])

    # prompt user to log an optional note
    log['notes'] = log_notes()

    journal['journal'].append(log)

    write_journal(args.journal, journal, args.archive)

    print '\n=== Successfully wrote journal entry #{}!'.format(len(journal['journal']))


if __name__ == '__main__':
    main()
