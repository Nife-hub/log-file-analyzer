import sys 
import csv
from datetime import datetime

# STATS FOR ALL FILES
counts = {
    'info_count': 0,
    'warning_count': 0, 
    'error_count': 0, 
    'total_logs': 0, 
    'unparsed_counter': 0, 
    'unknown_level_count': 0, 
    'match_count': 0, 
    'displayed_count': 0
}

# STATS FOR EACH FILE
file_stats = {}

# INPUT FILENAME(S)
user_input = input('Enter filename(s) separated with a space: ').strip()
log_files = user_input.split()

# INPUT FILTER LEVEL
filter_level = input('Show level (ALL/INFO/WARNING/ERROR): ').strip().upper()

valid_levels = ['ALL', 'INFO', 'WARNING', 'ERROR']

# ERROR MESSAGES COUNT
error_messages = {}

# HOURLY COUNT
hourly_counts = {}

# LOG FILTERS
filtered_logs = []

# LOG-LEVEL VALIDATION
while filter_level not in valid_levels:    
    print('Invalid level')
    filter_level = input('Show level (ALL/INFO/WARNING/ERROR): ').strip().upper()

# VALIDATE THE LIMIT
while True:
    try: 
        input_limit = input('\nMax number of matches to show: ').strip()
        
        if input_limit == "":   # if no limit, display the whole thing
            limit = None
            break
        
        limit = int(input_limit)

        if limit <= 0:
            print('Limit must be greater than 0')
            continue

        break   # if the input is valid, stop the loop

    except ValueError:
        print('Enter a valid number')


# INPUT KEYWORD
keyword = input('\nKeyword (optional): ').strip()

# INPUT AND VALIDATE START TIME
while True:
    try:
        start_time_text = input('\nStart date/time (optional): ').strip()

        if start_time_text == "":   # No start-time restriction
            start_time = None
            break

        start_time = datetime.strptime(start_time_text, '%Y-%m-%d %H:%M:%S')
        break

    except ValueError:
        print('Invalid date/time. Use YYYY-MM-DD HH:MM:SS.')


# INPUT AND VALIDATE END TIME
while True:
    try:
        end_time_text = input('\nEnd date/time (optional): ').strip()

        if end_time_text == "":   # No end-time restriction
            end_time = None
            break

        end_time = datetime.strptime(end_time_text, '%Y-%m-%d %H:%M:%S')

        if start_time is not None and end_time < start_time:
            print('End time cannot be earlier than start time.')
            continue

        break

    except ValueError:
        print('Invalid date/time. Use YYYY-MM-DD HH:MM:SS.')


# ACCESS AND READ FILES 
try:
    for filename in log_files:

        # UPDATE FILE STATS
        file_stats[filename] = {
        'total': 0,
        'INFO': 0,
        'WARNING': 0,
        'ERROR': 0,
        'unparsed': 0,
        'unknown': 0
    }
        
        with open(filename, 'r', encoding='utf-8') as log_file:
            for line_index, line in enumerate(log_file, start=1):
                counts['total_logs'] += 1       # total count
                file_stats[filename]['total'] += 1  # total for each file
                parts = line.split()    # split the current line to a list

                if len(parts) < 3:   # if the length's less than 3, it's invalid
                    counts['unparsed_counter'] += 1   # count the invalid
                    file_stats[filename]['unparsed'] += 1
                    continue
            
                level = parts[2]    # level position
                timestamp_text = " ".join(parts[:2])  # timestamp

                # DATE & TIME VALIDATION
                try:
                    timestamp = datetime.strptime(timestamp_text, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    counts['unparsed_counter'] += 1
                    file_stats[filename]['unparsed'] += 1
                    continue

                # COUNT LOGS EVERY HOUR
                hour = timestamp.hour   
                if hour in hourly_counts:
                    hourly_counts[hour] += 1
                else:
                    hourly_counts[hour] = 1

                # extract the message from the list
                message = " ".join(parts[3:])  

                # CHECK FOR AND COUNT LOG LEVEL
                if level == 'INFO':
                    counts['info_count'] += 1
                    file_stats[filename]['INFO'] += 1
                elif level == 'WARNING':
                    counts['warning_count'] += 1
                    file_stats[filename]['WARNING'] += 1

                elif level == 'ERROR':
                    # count error messages
                    if message in error_messages:   # update the dictionary
                        error_messages[message] += 1
                    else:
                        error_messages[message] = 1
                    counts['error_count'] += 1
                    file_stats[filename]['ERROR'] += 1
                else:
                    counts['unknown_level_count'] += 1
                    file_stats[filename]['UNKNOWN'] += 1

                # CHECK FOR INPUTTED LEVEL AND KEYWORD
                if (
                    (filter_level == 'ALL' or level == filter_level) 
                    and keyword.lower() in line.lower() 
                    and (start_time is None or timestamp >= start_time) 
                    and (end_time is None or timestamp <= end_time)
                    ):
                    counts['match_count'] += 1

                    filtered_logs.append([timestamp, level, message])   # update filtered logs list

                    if limit is None or counts['displayed_count'] < limit:    # None is a special singleton object, and is checks object identity
                        print(f'\nLine {line_index}: {line.strip()}')
                        counts['displayed_count'] += 1

except FileNotFoundError:
    print('The requested file could not be found.')
    sys.exit(1)

except PermissionError:
    print('Not permitted to access this file')
    sys.exit(1)

except UnicodeDecodeError:  # File contains bytes that can't be decoded using the selected encoding
    print('Unable to decode the file using UTF-8 encoding.')
    sys.exit(1)


# SORT AND PRINT ERROR MESSAGES
sorted_errors = sorted(
    error_messages.items(),
    key=lambda pair: pair[1],
    reverse=True
    )

top_five = sorted_errors[:5]    # get the top 5

print('\nTOP FIVE ERROR MESSAGES')

if not top_five:
    print('No error messages found')
else:
    for position, (message, count) in enumerate(top_five, start=1):
        print(f'{position}. {message} - {count}')


# SORT AND PRINT HOURLY LOG
print('\nHOULY LOG HISTOGRAM')

for hour, count in sorted(hourly_counts.items()):
    print(f'{hour:02d}:00 | {'#' * count} ({count})')


# NO MATCH 
if counts['match_count'] == 0:
    print('\nNo matching logs found.\n')


# GET THE HIDDEN FILES
hidden_count = counts['match_count'] - counts['displayed_count']
        

# GET THE PERCENTAGE
if counts['total_logs'] > 0:
    info_percentage = (counts['info_count']/counts['total_logs']) * 100
    warning_percentage = (counts['warning_count']/counts['total_logs']) * 100
    error_percent = (counts['error_count']/counts['total_logs']) * 100
else: 
    info_percentage = 0
    warning_percentage = 0
    error_percent = 0


# PRINT THE OUTPUT
print(f'\nTOTAL: {counts['total_logs']}\n\nINFO: {counts['info_count']} ({info_percentage:.1f}%)\n\nWARNING: {counts['warning_count']} ({warning_percentage:.1f}%)\n\nERROR: {counts['error_count']} ({error_percent:.1f}%)\n\nUNPARSED: {counts['unparsed_counter']}\n\nUnknown level: {counts['unknown_level_count']}\n\nTotal Matches: {counts['match_count']}\n\nMatches shown: {counts['displayed_count']}\n\nHidden: {hidden_count}\n')


# WRITE THE SUMMARY INTO CSV FILE 
try:
    with open('summary.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Metric', 'Count'])
        writer.writerow(['Total Logs', counts['total_logs']])
        writer.writerow(['INFO', counts['info_count']])
        writer.writerow(['WARNING', counts['warning_count']])
        writer.writerow(['ERROR', counts['error_count']])
        writer.writerow(['Unknown Levels', counts['unknown_level_count']])
        writer.writerow(['Unparsed Lines', counts['unparsed_counter']])
        writer.writerow(['Matching Logs', counts['match_count']])
except PermissionError:
    print('Permission denied. Unable to write summary.csv')


# WRITE THE FILTERED LOGS INTO CSV FILE
try:
    with open('filtered_logs.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Level', 'Message'])
        writer.writerows(filtered_logs)
except PermissionError:
    print('Permission denied. Unable to write filtered_logs.csv')




# Computers store files as bytes. Text encoding defines how those bytes represent characters such as letters, numbers, and symbols.