import json
import re
from datetime import datetime

def string_cleaning(s):
    return s.strip()


def parse_number(n):
    n = string_cleaning(n)
    if re.match(r'^-?\d+(\.\d+)?$', n):
        return float(n) if '.' in n else int(n)
    return None

def parse_date_string(s):
    s = string_cleaning(s)
    try:
        return int(datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').timestamp())
    except ValueError:
        return s

def parse_bool(b):
    b = string_cleaning(b).lower()
    if b in ['true', '1', 't']:
        return True
    elif b in ['false', '0', 'f']:
        return False
    return None

def parse_null(n):
    n = string_cleaning(n).lower()
    if n in ['true', '1', 't']:
        return None
    elif n in ['false', '0', 'f']:
        return "omit"
    return None

def update_key_value(key, value):
    if isinstance(value, dict):
        if 'S' in value:
            string_value = string_cleaning(value['S'])
            if string_value == "":
                return "omit"
            elif re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$', string_value):
                return parse_date_string(string_value)  
            return string_value
        elif 'NULL' in value:
            null_value = parse_null(value['NULL'])
            if null_value == "omit":
                return "omit"
            return null_value
        elif 'BOOL' in value:
            bool_value = parse_bool(value['BOOL'])
            if bool_value is not None:
                return bool_value
            return "omit"
        elif 'M' in value:
            map_value = map_transformation(value['M'])
            if map_value:
                return map_value
            return "omit"
        elif 'L' in value:
            list_value = []
            for item in value['L']:
                transformed_item = update_key_value(None, item)
                if transformed_item != "omit":
                    list_value.append(transformed_item)
            if list_value:
                return list_value
            return "omit"
        elif 'N' in value:
            num_value = parse_number(value['N'])
            if num_value is not None:
                return num_value
            return "omit"
        
    return "omit"

def map_transformation(input_map):
    map_output = {}
    for key, value in input_map.items():
        sanitized_key = string_cleaning(key)
        if sanitized_key == "":
            continue
        transformed_valued = update_key_value(sanitized_key, value)
        if transformed_valued != "omit":
            map_output[sanitized_key] = transformed_valued
    
    return map_output

def convert_json(input_json):
    result = []
    final_result = map_transformation(input_json)
    if final_result:
        result.append(final_result)
    print(json.dumps(result, indent=2))


input_json = {
  "number_1": {
    "N": "1.50"
  },
  "string_1": {
    "S": "784498 "
  },
  "string_2": {
    "S": "2014-07-16T20:55:46Z"
  },
  "map_1": {
    "M": {
      "bool_1": {
        "BOOL": "truthy"
      },
      "null_1": {
        "NULL ": "true"
      },
      "list_1": {
        "L": [
          {
            "S": ""
          },
          {
            "N": "011"
          },
          {
            "N": "5215s"
          },
          {
            "BOOL": "f"
          },
          {
            "NULL": "0"
          }
        ]
      }
    }
  },
  "list_2": {
    "L": "noop"
  },
  "list_3": {
    "L": [
      "noop"
    ]
  },
  "": {
    "S": "noop"
  }
}
convert_json(input_json)