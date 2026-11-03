info_count, warning_count, error_count, total_logs, unparsed_counter, unknown_level_count = 0, 0, 0, 0, 0, 0

filter_level = input('Show level (ALL/INFO/WARNING/ERROR): ').upper()

with open('server.log', 'r') as log_file:
    for line in log_file:
        total_logs += 1       # total count
        parts = line.split()    # split the current line to a list

        if len(parts) < 3:   #if the length's less than 3, its invalid
            unparsed_counter += 1   # count the invalid
            continue
        
    
        level = parts[2]    #level position

        if level == 'INFO':
            info_count += 1
        elif level == 'WARNING':
            warning_count += 1
        elif level == 'ERROR':
            error_count += 1
        else:
            unknown_level_count += 1

        if level == filter_level:
            print(line.strip())
        

# GET THE PERCENTAGE
if total_logs > 0:
    info_percentage = (info_count/total_logs) * 100
    warning_percentage = (warning_count/total_logs) * 100
    error_percent = (error_count/total_logs) * 100
else: 
    info_percentage = 0
    warning_percentage = 0
    error_percent = 0
        
print(f'TOTAL: {total_logs}\nINFO: {info_count} ({info_percentage:.1f}%)\nWARNING: {warning_count} ({warning_percentage:.1f}%)\nERROR: {error_count} ({error_percent:.1f}%)\nUNPARSED (too short): {unparsed_counter}\nUnknown level: {unknown_level_count}')