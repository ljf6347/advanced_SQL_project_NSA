import time
import tqdm
import datetime

def statisticalValidation(anomalies, ref_table, tar_table, method='chi_square'):
    print(f"Starting statistical validation using method: {method}")
    start_time = time.time()
    result = None
    match method:
        case 'chi_square':
            result = chi_square_validation(anomalies, ref_table, tar_table)
        case 'Z_score':
            result = Z_score_validation(anomalies, ref_table)
        case 'IQR':
            result = IQR_validation(anomalies, ref_table)
        case 'range_check':
            result = range_check(anomalies, ref_table)
        case 'threshold':
            result = threshold_validation(anomalies, ref_table, tar_table)
        case 'monte_carlo':
            result = monte_carlo_validation(anomalies, ref_table, tar_table)
        case _:
            print(f"Unknown statistical validation method: {method}")
            return anomalies
    end_time = time.time()
    print(f"Statistical validation using {method} took {end_time - start_time} seconds and validated {len(result)} anomalies.")
    return result

# for categorical datasets
def chi_square_validation(anomalies, ref_table, tar_table):
    a = 0.05
    pass

# for numerical dataset, need to be log transformed if skewed
def Z_score_validation(anomalies, tar_table):
    standard_deviations = {}
    target_sums = {}
    target_lengths = {}
    target_means = {}

    # calculate means for each feature
    for value in tqdm.tqdm(tar_table, desc="Calculating means"):
        for feature in value:
            if feature not in target_sums:
                target_sums[feature] = 0
                target_lengths[feature] = 0
                target_means[feature] = 0
                standard_deviations[feature] = 0
            target_sums[feature] += value[feature]
            target_lengths[feature] += 1
    for feature in target_sums:
        target_means[feature] = target_sums[feature] / target_lengths[feature]

    # calculate standard deviations for each feature
    for value in tqdm.tqdm(tar_table, desc="Calculating standard deviations 1/2"):
        for feature in value:
            standard_deviations[feature] += (value[feature] - target_means[feature]) ** 2
    for feature in tqdm.tqdm(standard_deviations, desc="Calculating standard deviations 2/2"):
        standard_deviations[feature] = (standard_deviations[feature] / (target_lengths[feature] - 1)) ** 0.5

    # check if anomalies are beyond 3 standard deviations from any feature
    real_anomalies = []
    for anomaly in tqdm.tqdm(anomalies, desc="Validating anomalies with Z-score"):
        for feature in anomaly:
            if standard_deviations[feature] == 1: # no other values have that feature, probably an anomaly
                break
            z_score = (anomaly[feature] - target_means[feature]) / standard_deviations[feature]
            if abs(z_score) > 3:
                real_anomalies.append(anomaly)
                break
    return real_anomalies

# for numerical dataset, need to be log transformed if skewed
def IQR_validation(anomalies, tar_table):
    # get upper and lower bound with Q1 and Q3 for each feature
    num_features = len(tar_table[0])
    feature_ranges = []
    feature_tables = []
    for feature in range(num_features):
        feature_tables.append([])
    for record in tar_table:
        for feature in range(num_features):
            feature_tables[feature].append(record[feature])
    for feature in tqdm.trange(num_features, desc="Calculating IQR ranges"):
        tar_table_sorted = sorted(feature_tables[feature])
        Q1 = tar_table_sorted[len(tar_table_sorted) // 4]
        Q3 = tar_table_sorted[len(tar_table_sorted) * 3 // 4]

        IQR = Q3 - Q1
        IQR_range = 1.5 * IQR
        lower_bound = Q1 - IQR_range
        upper_bound = Q3 + IQR_range
        feature_ranges.append({'lower_bound': lower_bound, 'upper_bound': upper_bound})

    real_anomalies = []
    for anomaly in tqdm.tqdm(anomalies, desc="Validating anomalies with IQR"):
        for feature in range(num_features):
            if anomaly[feature] < feature_ranges[feature]['lower_bound'] or anomaly[feature] > feature_ranges[feature]['upper_bound']:
                real_anomalies.append(anomaly)
    return real_anomalies

# for dates (only have one feature that should be the dates)
def range_check(anomalies, tar_table):
    # ima just check if date is outside IQR of target
    # because it is normalized we can use IQR
    return IQR_validation(anomalies, tar_table)

# check distribution change over 5%
def threshold_validation(anomalies, ref_table, tar_table):
    pass

# our methods
def monte_carlo_validation(anomalies, ref_table, tar_table):
    pass

def mean_absolute_deviation(anomalies, ref_table, tar_table):
    pass

def kernel_density_estimation(anomalies, ref_table, tar_table):
    pass