date_of_birth = "12121999" ## format of DDMMYYYY e.g 12121999
last_four_digit = "123A" ## last 4 character of your IC e.g 123A

import urllib.request
import json
from datetime import datetime
from calendar import monthrange

def change_date_format(date):
    # change date format from 1960 Mar to 031960
    date = date.strip()
    date = datetime.strptime(date, '%Y %b')
    new_date = date.strftime('%m%Y')
    return new_date

def nric_checksum(nric_number_only):
    # return last letter of nric
    total = 0
    weight = "2765432"
    for i in range(len(nric_number_only)):
        total += int(weight[i])*int(nric_number_only[i])
    alphabet_map = "ABCDEFGHIZJ"
    return alphabet_map[(11 - (total % 11)) - 1]

def calculate_estimated_birth(data, day, month, year):
    # return estimate of the births before you in the same birth year
    before = 0
    for i in range(1, int(month)):
        before += int(data[f"{i:02}{year}"])
    _, number_of_day_in_month = monthrange(int(year), int(month))
    before += (int(data[month+year])/number_of_day_in_month * int(day))
    return before

# grab data from singstat
url = 'http://tablebuilder.singstat.gov.sg/api/table/tabledata/M810051'
web_url = urllib.request.urlopen(url)
response_API = web_url.read()
singstat_data=json.loads(response_API.decode('utf-8'))

# clean singstat data and change date format
data = dict()
for entry in singstat_data['Data']['row'][0]['columns']:
    data[entry['key']] = entry['value']
data = dict(zip(map(lambda x: change_date_format(x), data.keys()), data.values()))

# breakdown dob
birthyear = date_of_birth[-4:]
birthyear_first_2 = birthyear[:2]
birthyear_last_2 = birthyear[2:]
birthmonth = date_of_birth[2:4]
birthday = date_of_birth[:2]
day_of_year = datetime.strptime(date_of_birth, "%d%m%Y").timetuple().tm_yday

#generate 9 possible nric
possible_nric = []
for i in range(0, 100):
    guess_two_digit = f"{i:02}"
    nric_number_only = birthyear_last_2 + guess_two_digit + last_four_digit[:3]
    alphabet = last_four_digit[3]
    if nric_checksum(nric_number_only) == alphabet:
        possible_nric.append(nric_number_only + alphabet)

# estimate births before you for that birthyear
est = calculate_estimated_birth(data, birthday, birthmonth, birthyear)

# get the minimum difference
diff = list(map(lambda x:abs(est-int(x[2:-1])), possible_nric))
correct_index = diff.index(min(diff))

# get first letter of NRIC base on birth year
possible_first_letter = "ST"
first_letter = possible_first_letter[int(birthyear_first_2)-19]

# put everything together
print("It is likely to be:", first_letter + possible_nric[correct_index])
