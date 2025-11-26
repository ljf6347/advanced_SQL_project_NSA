import time
import tqdm
import results

def statisticalValidation(anomalies, ref_table, tar_table, method='chi_square', normal=False):
    print("Results before validation:")
    if (normal):
        results.check_anomalies(anomalies, tar_table, tar_table)
    else:
        results.check_anomalies(anomalies, ref_table, tar_table)
    
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
    with open('results.txt', 'a') as f:
        f.write(f"Statistical validation using {method} took {end_time - start_time} seconds and validated {len(result)} anomalies.\n")
    print("Results after validation:")
    if (normal):
        results.check_anomalies(result, tar_table, tar_table)
    else:
        results.check_anomalies(result, ref_table, tar_table)
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

    feature_count = len(tar_table[0])

    # calculate means for each feature
    for value in tqdm.tqdm(tar_table, desc="Calculating means"):
        for feature in range(feature_count):
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
        for feature in range(feature_count):
            standard_deviations[feature] += (value[feature] - target_means[feature]) ** 2
    for feature in tqdm.tqdm(standard_deviations, desc="Calculating standard deviations 2/2"):
        standard_deviations[feature] = (standard_deviations[feature] / (target_lengths[feature] - 1)) ** 0.5

    # check if anomalies are beyond 3 standard deviations from any feature
    real_anomalies = []
    for anomaly in tqdm.tqdm(anomalies, desc="Validating anomalies with Z-score"):
        for feature in range(feature_count):
            if standard_deviations[feature] == 0:
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
                break
    return real_anomalies

# for dates (only have one feature that should be the dates)
def range_check(anomalies, ref_table):
    # Check outside min value or max value in reference table
    amount_of_features = len(ref_table[0])
    feature_mins = {}
    feature_maxs = {}
    real_anomalies = []
    for feature in tqdm.trange(amount_of_features, desc="Finding min/max values"):
        for record in ref_table:
            if (record[feature] is not None):
                if feature not in feature_mins:
                    feature_mins[feature] = record[feature]
                    feature_maxs[feature] = record[feature]
                else:
                    if record[feature] < feature_mins[feature]:
                        feature_mins[feature] = record[feature]
                    if record[feature] > feature_maxs[feature]:
                        feature_maxs[feature] = record[feature]
    
    for anomaly in anomalies:
        for feature in range(amount_of_features):
            if anomaly[feature] < feature_mins[feature] or anomaly[feature] > feature_maxs[feature]:
                real_anomalies.append(anomaly)
                break

    return real_anomalies

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