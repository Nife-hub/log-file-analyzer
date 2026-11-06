import sys 
import csv
from datetime import datetime

info_count, warning_count, error_count, total_logs, unparsed_counter, unknown_level_count, match_count, displayed_count = 0, 0, 0, 0, 0, 0, 0, 0

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
        with open(filename, 'r', encoding='utf-8') as log_file:
            for line_index, line in enumerate(log_file, start=1):
                total_logs += 1       # total count
                parts = line.split()    # split the current line to a list

                if len(parts) < 3:   # if the length's less than 3, it's invalid
                    unparsed_counter += 1   # count the invalid
                    continue
            
                level = parts[2]    # level position
                timestamp_text = " ".join(parts[:2])  # timestamp

                # DATE & TIME VALIDATION
                try:
                    timestamp = datetime.strptime(timestamp_text, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    unparsed_counter += 1
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
                    info_count += 1
                elif level == 'WARNING':
                    warning_count += 1

                elif level == 'ERROR':
                    # count error messages
                    if message in error_messages:   # update the dictionary
                        error_messages[message] += 1
                    else:
                        error_messages[message] = 1
                    error_count += 1
                else:
                    unknown_level_count += 1

                # CHECK FOR INPUTTED LEVEL AND KEYWORD
                if (
                    (filter_level == 'ALL' or level == filter_level) 
                    and keyword.lower() in line.lower() 
                    and (start_time is None or timestamp >= start_time) 
                    and (end_time is None or timestamp <= end_time)
                    ):
                    match_count += 1

                    filtered_logs.append([timestamp, level, message])   # update filtered logs list

                    if limit is None or displayed_count < limit:    # None is a special singleton object, and is checks object identity
                        print(f'\nLine {line_index}: {line.strip()}')
                        displayed_count += 1

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
if match_count == 0:
    print('\nNo matching logs found.\n')


# GET THE HIDDEN FILES
hidden_count = match_count - displayed_count
        

# GET THE PERCENTAGE
if total_logs > 0:
    info_percentage = (info_count/total_logs) * 100
    warning_percentage = (warning_count/total_logs) * 100
    error_percent = (error_count/total_logs) * 100
else: 
    info_percentage = 0
    warning_percentage = 0
    error_percent = 0


# PRINT THE OUTPUT
print(f'\nTOTAL: {total_logs}\n\nINFO: {info_count} ({info_percentage:.1f}%)\n\nWARNING: {warning_count} ({warning_percentage:.1f}%)\n\nERROR: {error_count} ({error_percent:.1f}%)\n\nUNPARSED: {unparsed_counter}\n\nUnknown level: {unknown_level_count}\n\nTotal Matches: {match_count}\n\nMatches shown: {displayed_count}\n\nHidden: {hidden_count}\n')


# WRITE THE SUMMARY INTO CSV FILE 
try:
    with open('summary.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Metric', 'Count'])
        writer.writerow(['Total Logs', total_logs])
        writer.writerow(['INFO', info_count])
        writer.writerow(['WARNING', warning_count])
        writer.writerow(['ERROR', error_count])
        writer.writerow(['Unknown Levels', unknown_level_count])
        writer.writerow(['Unparsed Lines', unparsed_counter])
        writer.writerow(['Matching Logs', match_count])
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