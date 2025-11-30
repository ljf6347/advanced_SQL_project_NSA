import random
import time
import copy
from statistical_validation import statisticalValidation
import tqdm
from normalization import normalize_data

# Using paper's pseudocode for NSA algorithm
# ref_table = reference table, tar_table = target table
def detect_anomalies(ref_table, tar_table, features, detector_count, matching_threshold=None, method='chi_square', normal=False):
    start = time.time()
    unnormalized_ref_table = copy.deepcopy(ref_table) # needed to detect date and categorical values during validation
    unnormalized_tar_table = copy.deepcopy(tar_table)
    attempts = 0
    detectors = []
    max_attempts = detector_count * 100
    if matching_threshold is None:
        avg_dist = 0.28
        matching_threshold = ((avg_dist**2) * len(features)) ** 0.5

    # normalize and convert data to numbers to calculate distance
    print("Normalizing data...")
    ref_table_norm, tar_table_norm = normalize_data(ref_table, tar_table, features)

    # generate detectors
    while len(detectors) < detector_count and attempts < max_attempts:
        if (attempts % 1000) == 0 or len(detectors) % 10 == 0:
            print(f"\rGenerating detectors: {len(detectors)}/{detector_count} attempts {attempts}/{max_attempts}", end="")
        isValid = True
        candidate = generateRandomDetector(features)
        for record in sampleFrom(ref_table_norm, 1000):
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
    size_of_t = len(tar_table_norm)
    for i in tqdm.tqdm(range(0, size_of_t, chunk_size), desc="Detecting anomalies"):
        chunk = tar_table_norm[i:i + chunk_size]
        for record in chunk:
            for detector in detectors:
                distance = calculateDistance(detector, record)
                if distance < matching_threshold:
                    anomalies.append(record)
                    break

    end = time.time()
    print(f"The NSA algorithm took {end - start} seconds and found {len(anomalies)} anomalies.")
    with open('results.txt', 'a') as f:
        f.write(f"The NSA algorithm took {end - start} seconds and found {len(anomalies)} anomalies.\n")

    A = statisticalValidation(anomalies, ref_table_norm, tar_table_norm, unnormalized_ref_table, unnormalized_tar_table, method=method, normal=normal)
    return A

# make random numbers for each feature
def generateRandomDetector(features):
    detector = {}
    for feature in range(len(features)):
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

