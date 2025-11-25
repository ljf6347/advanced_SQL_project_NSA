import datetime
import time
import tqdm
import decimal
from tqdm import trange

def table_to_numbers(table, number_of_features):
    cur_record = 0
    for record in tqdm.tqdm(table, desc="Converting data to numbers"):
        for feature in range(number_of_features):
            if (record[feature] is not None):
                if type(record[feature]) == bool:
                    if (record[feature] == True):
                        table[cur_record][feature] = 1
                    else:
                        table[cur_record][feature] = 0
                elif type(record[feature]) == str:
                    # really should calculate distance later with strings by levenshtein distance
                    length = len(record[feature])
                    table[cur_record][feature] = int(length)
                elif type(record[feature]) == list:
                    # really should calculate distance later with set intersections or something
                    table[cur_record][feature] = int(len(record[feature]))
                elif isinstance(record[feature], datetime.datetime):
                    table[cur_record][feature] = time.mktime(record[feature].timetuple())

                # datetime.date (but NOT datetime.datetime)
                elif isinstance(record[feature], datetime.date):
                    dt = datetime.datetime.combine(record[feature], datetime.time())
                    table[cur_record][feature] = time.mktime(dt.timetuple())
                elif type(record[feature]) is decimal.Decimal:
                    table[cur_record][feature] = float(record[feature])
                # else:
                #     print(f"Unknown data type: {type(record[feature])}")
        cur_record += 1
    return table

# normalize reference data between 0 and 1, apply same transformation to target data
def normalize_data(reference_data, target_data, features):
    # convert values to numbers
    amount_of_features = len(features)
    reference_data = table_to_numbers(reference_data, amount_of_features)
    target_data = table_to_numbers(target_data, amount_of_features)

    # find minimum and maximum for each feature
    feature_mins = {}
    feature_maxs = {}
    for feature in trange(amount_of_features, desc="Finding min/max values"):
        for record in reference_data:
            if (record[feature] is not None):
                if feature not in feature_mins:
                    feature_mins[feature] = record[feature]
                    feature_maxs[feature] = record[feature]
                else:
                    if record[feature] < feature_mins[feature]:
                        feature_mins[feature] = record[feature]
                    if record[feature] > feature_maxs[feature]:
                        feature_maxs[feature] = record[feature]

    # normalize both datasets
    normalized_reference_data = []
    normalized_target_data = []
    for feature in trange(amount_of_features, desc="Normalizing data"):
        value_range = feature_maxs[feature] - feature_mins[feature]
        for record_num in range(len(reference_data)):
            if (feature == 0):
                normalized_reference_data.append([])
            if (reference_data[record_num][feature] is not None and value_range > 0):
                normalized_reference_data[record_num].append((reference_data[record_num][feature] - feature_mins[feature]) / value_range)
            if (value_range == 0):
                normalized_reference_data[record_num].append(0.0)
        for record_num in range(len(target_data)):
            if (feature == 0):
                normalized_target_data.append([])
            if (target_data[record_num][feature] is not None and value_range > 0):
                normalized_target_data[record_num].append((target_data[record_num][feature] - feature_mins[feature]) / value_range)
            if (value_range == 0):
                normalized_target_data[record_num].append(0.0)
    return normalized_reference_data, normalized_target_data