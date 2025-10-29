from datetime import datetime
import random
import time
from statistical_validation import statisticalValidation

# Using paper's pseudocode for NSA algorithm
# ref_table = reference table, tar_table = target table
def detect_anomalies(ref_table, tar_table, features, detector_count, matching_threshold):
    start = time.time()
    attempts = 0
    detectors = []
    max_attempts = detector_count * 10

    # normalize and convert data to numbers to calculate distance
    ref_table, tar_table = normalize_data(ref_table, tar_table)

    # generate detectors
    while len(detectors) < detector_count and attempts < max_attempts:
        isValid = True
        candidate = generateRandomDetector(features, ref_table)
        for record in sampleFrom(ref_table, 100):
            distance = calculateDistance(candidate, record)
            if distance < matching_threshold:
                isValid = False
                break
        if isValid:
            detectors.append(candidate)
        attempts += 1

    # find anomalies
    anomalies = []
    chunk_size = 10000
    size_of_t = len(tar_table)
    for i in range(0, size_of_t, chunk_size):
        chunk = tar_table[i:i + chunk_size]
        for record in chunk:
            for detector in detectors:
                distance = calculateDistance(detector, record)
                if distance < matching_threshold:
                    anomalies.append(record)
                    break

    end = time.time()
    print(f"The NSA algorithm took {end - start} seconds and found {len(anomalies)} anomalies.")

    A = statisticalValidation(anomalies, ref_table, tar_table)
    return A

# make random numbers for each feature
def generateRandomDetector(features, ref_table):
    detector = {}
    for feature in features:
        # get example feature from a record in the table to see what type it is
        for record in ref_table:
            min = min(record[feature] for record in ref_table)
            max = max(record[feature] for record in ref_table)
            detector[feature] = random.uniform(min, max)
    return detector

def sampleFrom(R, number):
    return random.sample(R, number)

# normalize reference data between 0 and 1, apply same transformation to target data
def normalize_data(reference_data, target_data):
    # get list of features
    features = []
    for record in reference_data:
        for feature in record:
            if feature not in features:
                features.append(feature)

    # convert values to numbers
    for feature in features:
        for record in reference_data:
            if (record[feature] is not None):
                if type(record[feature]) == int or type(record[feature]) == float:
                    record[feature] = float(record[feature])
                elif type(record[feature]) == bool:
                    if (record[feature] == True):
                        record[feature] = 1.0
                    else:
                        record[feature] = 0.0
                elif type(record[feature]) == str:
                    record[feature] = int(len(record[feature]))
                elif type(record[feature]) == list:
                    record[feature] = int(len(record[feature]))
                elif type(record[feature]) == datetime:
                    record[feature] = time.mktime(datetime.datetime.strptime(record[feature], "%d/%m/%Y").timetuple())

    # find minimum and maximum for each feature
    feature_mins = {}
    feature_maxs = {}
    for feature in features:
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
    for feature in features:
        range = feature_maxs[feature] - feature_mins[feature]
        for record in reference_data:
            if (record[feature] is not None):
                normalized_reference_data.append((record[feature] - feature_mins[feature]) / range)
        for record in target_data:
            if (record[feature] is not None):
                normalized_target_data.append((record[feature] - feature_mins[feature]) / range)
    return normalized_reference_data, normalized_target_data

# using Euclidean distance
def calculateDistance(candidate, record):
    distance = 0
    for feature in candidate:
        feature_distance = (candidate[feature] - record[feature]) ** 2
        distance += feature_distance
    euclidean_distance = distance ** 0.5
    return euclidean_distance

