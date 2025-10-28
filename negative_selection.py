import random
from statistical_validation import statisticalValidation

# Using paper's pseudocode for NSA algorithm
# ref_table = reference table, tar_table = target table
def detect_anomalies(connection, ref_table, tar_table, features, detector_count, matching_threshold):
    attempts = 0
    detectors = []
    max_attempts = detector_count * 10

    while len(detectors) < detector_count and attempts < max_attempts:
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

    A = statisticalValidation(anomalies, ref_table, tar_table)
    return A

def generateRandomDetector(features):
    detector = {}
    for feature in features:
        detector[feature] = random.uniform(0, 1)
    return detector

def sampleFrom(R, number):
    return random.sample(R, number)

# using Euclidean distance
def calculateDistance(candidate, record):
    distance = 0
    for feature in candidate:
        feature_distance = (candidate[feature] - record[feature]) ** 2
        distance += feature_distance
    euclidean_distance = distance ** 0.5
    return euclidean_distance

