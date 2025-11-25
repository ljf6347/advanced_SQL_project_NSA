import datetime
import decimal
import random
import time
from statistical_validation import statisticalValidation
import tqdm
from tqdm import trange

# Using paper's pseudocode for NSA algorithm
# ref_table = reference table, tar_table = target table
def detect_anomalies(ref_table, tar_table, features, detector_count, matching_threshold=None, method='chi_square'):
    start = time.time()
    attempts = 0
    detectors = []
    max_attempts = detector_count * 10
    if matching_threshold is None:
        matching_threshold = 0.1 * len(features)

    # normalize and convert data to numbers to calculate distance
    print("Normalizing data...")
    ref_table, tar_table = normalize_data(ref_table, tar_table, features)

    # generate detectors
    while len(detectors) < detector_count and attempts < max_attempts:
        print(f"\rGenerating detectors: {len(detectors)}/{detector_count} attempts {attempts}/{max_attempts}", end="")
        isValid = True
        candidate = generateRandomDetector(features)
        for record in sampleFrom(ref_table, 100):
            distance = calculateDistance(candidate, record)
            if distance < matching_threshold:
                isValid = False
                break
        if isValid:
            detectors.append(candidate)
        attempts += 1
    
    print('\nGenerated ' + str(len(detectors)) + ' detectors')
    if (len(detectors) < detector_count / 4):
        print("Couldn't generate enough detectors, exiting.")
        return []

    # find anomalies
    anomalies = []
    chunk_size = 10000
    size_of_t = len(tar_table)
    for i in tqdm.tqdm(range(0, size_of_t, chunk_size), desc="Detecting anomalies"):
        chunk = tar_table[i:i + chunk_size]
        for record in chunk:
            for detector in detectors:
                distance = calculateDistance(detector, record)
                if distance < matching_threshold:
                    anomalies.append(record)
                    break

    end = time.time()
    print(f"The NSA algorithm took {end - start} seconds and found {len(anomalies)} anomalies.")

    A = statisticalValidation(anomalies, ref_table, tar_table, method=method)
    return A

# make random numbers for each feature
def generateRandomDetector(features):
    detector = {}
    for feature in range(len(features)):
        detector[feature] = random.uniform(0, 1)
    return detector

def sampleFrom(R, number):
    return random.sample(R, number)

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

# using Euclidean distance
def calculateDistance(candidate, record):
    distance = 0
    for feature in candidate:
        feature_distance = (candidate[feature] - record[feature]) ** 2
        distance += feature_distance
    euclidean_distance = distance ** 0.5
    return euclidean_distance

