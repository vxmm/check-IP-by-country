import re
import requests
import time
import csv
import os

def find_matching_ips(input_filename):
    regex_pattern = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"  # IP address regex pattern
    matches = []
    with open(input_filename, 'r') as file:
        for line in file:
            for match in re.findall(regex_pattern, line):
                matches.append(match)
    return matches

def write_ips_to_csv(ips, output_filename):
    with open(output_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["IP Address"])  
        for ip in ips:
            writer.writerow([ip])

def get_request_ip(ip_list):
    throttle = 60
    for element in ip_list:
        try:
            r = requests.get('https://freeipapi.com/api/json/' + element)
            response_data = r.json()
            country_name = response_data.get("countryName")
            print(f"Country for {element} is: {country_name}")
        except (requests.exceptions.JSONDecodeError, requests.exceptions.RequestException) as e:
            print(f"Error occurred while processing {element}: {e}")
            continue  # Skip to the next IP address in the list
        throttle -= 1
        if throttle < 3 and (ip_list.index(element) != len(ip_list) - 1):  # Forego throttle if it's the last element
            for i in range(60, 0, -1):
                print(f"You've hit the throttle limit. Resuming execution in: {i} seconds")
                time.sleep(1)
                if i == 1:
                    throttle = 60

class FilterIP:
    def _init_(self, ip_list):
        self.ip_list = ip_list

    def remove_private_ip(self):
        regex_pattern = r"^(10\.\d{1,3}\.\d{1,3}\.\d{1,3})|(172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3})|(192\.168\.\d{1,3}\.\d{1,3})$"
        filtered_list = [ip for ip in self.ip_list if not re.match(regex_pattern, ip)]
        return filtered_list

if _name_ == '_main_':
    for filename in os.listdir('.'):
        if filename.endswith('-config'):
            input_filename = filename
            base_name = os.path.splitext(input_filename)[0]
            output_csv_filename = f"extracted-ips-{base_name}.csv"

            ip_matches = find_matching_ips(input_filename)
            write_ips_to_csv(ip_matches, output_csv_filename)

            filtered_ip = FilterIP(ip_matches)
            public_ips = filtered_ip.remove_private_ip()

            get_request_ip(public_ips)