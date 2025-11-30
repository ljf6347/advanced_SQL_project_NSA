import time
import tqdm
import results
import datetime
from scipy import stats
from sklearn.neighbors import KernelDensity
import numpy as np

def statisticalValidation(anomalies, ref_table, tar_table, unnormalized_ref, unnormalized_tar, method='chi_square', normal=False):
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
            categorical_features = check_categorical_columns(ref_table)
            result = chi_square_validation(unnormalized_ref, unnormalized_tar, categorical_features)
        case 'Z_score':
            result = Z_score_validation(anomalies, ref_table, tar_table)
        case 'IQR':
            result = IQR_validation(anomalies, ref_table, tar_table)
        case 'range_check':
            result = range_check(anomalies, unnormalized_ref, ref_table, tar_table)
        case 'threshold':
            result = threshold_validation(ref_table, tar_table)
        case 'monte_carlo':
            result = monte_carlo_validation(anomalies, ref_table, tar_table)
        case 'mad':
            result = median_absolute_deviation(anomalies, ref_table, tar_table)
        case 'kde':
            result = kernel_density_estimation(anomalies, ref_table, tar_table)
        case _:
            print(f"Unknown statistical validation method: {method}")
            return anomalies
    end_time = time.time()
    text = ""
    if(type(result) == bool):
        if (result is True):
            text = f"Statistical validation using {method} took {end_time - start_time} seconds and validated anomalies."
        elif (result is False):
            text = f"Statistical validation using {method} took {end_time - start_time} seconds did not detect a difference."
        with open('results.txt', 'a') as f:
            f.write(f"{text}\n")
        print(text)
    else:
        text = f"Statistical validation using {method} took {end_time - start_time} seconds and validated {len(result)} anomalies."
        with open('results.txt', 'a') as f:
            f.write(f"{text}\n")
        print("Results after validation:")
        if (normal):
            results.check_anomalies(result, tar_table, tar_table)
        else:
            results.check_anomalies(result, ref_table, tar_table)
    return result

def combine_anomalies(anomalies1, anomalies2, union=False):
    set_1 = set(tuple(record) for record in anomalies1)
    set_2 = set(tuple(record) for record in anomalies2)
    if (union):
        # combine with previous anomalies
        combined_set = set_1.union(set_2)
        full_anomalies = [list(record) for record in combined_set]
    else:
        intersection_set = set_1.intersection(set_2)
        full_anomalies = [list(record) for record in intersection_set]
    return full_anomalies

# for categorical datasets
# return true if distribution has changed, false otherwise
def chi_square_validation(ref_table, tar_table, categorical_features, a_val=0.05):
    ref_sample_size = len(ref_table)
    tar_sample_size = len(tar_table)
    total_sample_size = ref_sample_size + tar_sample_size
    for feature in categorical_features:
        ref_count = {} # ref table
        tar_count = {} # tar table
        for record in ref_table:
            value = record[feature]
            if value not in ref_count:
                ref_count[value] = 1
            else:
                ref_count[value] += 1
        for record in tar_table:
            value = record[feature]
            if value not in tar_count:
                tar_count[value] = 1
            else:
                tar_count[value] += 1
        max_values = 30
        if (len(ref_count) > max_values or len(tar_count) > max_values):
            text = f"Feature {feature} has too many categories for chi-square test, skipping."
            with open('results.txt', 'a') as f:
                f.write(f"{text}\n")
            print(text)
            continue
        all_values = set(list(ref_count.keys()) + list(tar_count.keys()))
        total_chi = 0
        degrees_of_freedom = len(all_values) - 1
        # ref values
        ref_column_marginal = sum(ref_count.values())
        for value in all_values:
            row_marginal = ref_count.get(value, 0) + tar_count.get(value, 0)
            expected = (row_marginal * ref_column_marginal) / total_sample_size
            observed = ref_count.get(value, 0)
            chi = calc_chi_square(observed, expected)
            total_chi += chi
        # tar values
        tar_column_marginal = sum(tar_count.values())
        for value in all_values:
            row_marginal = ref_count.get(value, 0) + tar_count.get(value, 0)
            expected = (row_marginal * tar_column_marginal) / total_sample_size
            observed = tar_count.get(value, 0)
            chi = calc_chi_square(observed, expected)
            total_chi += chi
        p = 1 - stats.chi2.cdf(total_chi, degrees_of_freedom)
        text = f"Feature {feature} Chi-square total: {total_chi}, degrees of freedom: {degrees_of_freedom}, p-value: {p}"
        with open('results.txt', 'a') as f:
            f.write(f"{text}\n")
        print(text)
        if p < a_val:
            return True
    return False

def calc_chi_square(observed, expected):
    if expected == 0:
        return 0
    difference = observed - expected
    difference_squared = difference ** 2
    return difference_squared / expected

# for numerical dataset, need to be log transformed if skewed
def Z_score_validation(anomalies, ref_table, tar_table, union=False):
    standard_deviations = {}
    target_sums = {}
    target_lengths = {}
    target_means = {}

    feature_count = len(ref_table[0])

    # calculate means for each feature
    for value in tqdm.tqdm(ref_table, desc="Calculating means"):
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
    for value in tqdm.tqdm(ref_table, desc="Calculating standard deviations 1/2"):
        for feature in range(feature_count):
            standard_deviations[feature] += (value[feature] - target_means[feature]) ** 2
    for feature in tqdm.tqdm(standard_deviations, desc="Calculating standard deviations 2/2"):
        standard_deviations[feature] = (standard_deviations[feature] / (target_lengths[feature] - 1)) ** 0.5

    # check if anomalies are beyond 3 standard deviations from any feature
    validated_anomalies = []
    for record in tqdm.tqdm(tar_table, desc="Validating anomalies with Z-score"):
        for feature in range(feature_count):
            if standard_deviations[feature] == 0:
                break
            z_score = (record[feature] - target_means[feature]) / standard_deviations[feature]
            if abs(z_score) > 3:
                validated_anomalies.append(record)
                break
    return combine_anomalies(anomalies, validated_anomalies, union=union)

# for numerical dataset, need to be log transformed if skewed
def IQR_validation(anomalies, ref_table, tar_table, union=False):
    # get upper and lower bound with Q1 and Q3 for each feature
    num_features = len(ref_table[0])
    feature_ranges = []
    feature_tables = []
    for feature in range(num_features):
        feature_tables.append([])
    for record in ref_table:
        for feature in range(num_features):
            feature_tables[feature].append(record[feature])
    for feature in tqdm.trange(num_features, desc="Calculating IQR ranges"):
        ref_table_sorted = sorted(feature_tables[feature])
        Q1 = ref_table_sorted[len(ref_table_sorted) // 4]
        Q3 = ref_table_sorted[len(ref_table_sorted) * 3 // 4]

        IQR = Q3 - Q1
        IQR_range = 1.5 * IQR
        lower_bound = Q1 - IQR_range
        upper_bound = Q3 + IQR_range
        feature_ranges.append({'lower_bound': lower_bound, 'upper_bound': upper_bound})

    validated_anomalies = []
    for record in tqdm.tqdm(tar_table, desc="Validating anomalies with IQR"):
        for feature in range(num_features):
            if record[feature] < feature_ranges[feature]['lower_bound'] or record[feature] > feature_ranges[feature]['upper_bound']:
                validated_anomalies.append(record)
                break
    return combine_anomalies(anomalies, validated_anomalies, union=union)

# for dates (only have one feature that should be the dates)
def range_check(anomalies, unnormalized_ref_table, ref_table, tar_table, union=False):
    # Check outside min value or max value in reference table
    validated_anomalies = []
    date_cols = check_date_columns(unnormalized_ref_table)
    
    feature_mins = {}
    feature_maxs = {}
    for feature in tqdm.tqdm(date_cols, desc="Finding min/max values"):
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
    for record in tar_table:
        for feature in date_cols:
            if record[feature] < feature_mins[feature] or record[feature] > feature_maxs[feature]: 
                validated_anomalies.append(record)
                break

    return combine_anomalies(anomalies, validated_anomalies, union=union)

def check_date_columns(table):
    number_of_features = len(table[0])
    record = table[0]
    date_cols = []
    for feature in range(number_of_features):
        if (record[feature] is not None):
            if isinstance(record[feature], datetime.datetime) or isinstance(record[feature], datetime.date):
                date_cols.append(feature)
    return date_cols

def check_categorical_columns(table):
    number_of_features = len(table[0])
    record = table[0]
    categorical_cols = []
    for feature in range(number_of_features):
        if (record[feature] is not None):
            if type(record[feature]) == str or type(record[feature]) == bool:
                categorical_cols.append(feature)
    return categorical_cols

# check distribution change over 5%
def threshold_validation(ref_table, tar_table, bins=10):
    # convert to categorical ranges and call chi_square_validation
    # for each numerical feature, create 10 bins
    num_features = len(ref_table[0])

    # make bins
    binned_ref_table = []
    binned_tar_table = []

    for record in tqdm.tqdm(ref_table, desc="Binning reference table"):
        binned_ref_table.append([])
        for feature in range(num_features):
            bin_size = 1 / bins
            if (bin_size == 0):
                bin_index = 0
            else:
                bin_index = int(record[feature] / bin_size)
                if bin_index == bins:
                    bin_index -= 1
            binned_ref_table[-1].append(bin_index)
    for record in tqdm.tqdm(tar_table, desc="Binning target table"):
        binned_tar_table.append([])
        for feature in range(num_features):
            bin_size = 1 / bins
            if (bin_size == 0):
                bin_index = 0
            else:
                bin_index = int(record[feature] / bin_size)
                if bin_index == bins:
                    bin_index -= 1
            binned_tar_table[-1].append(bin_index)

    return chi_square_validation(binned_ref_table, binned_tar_table, list(range(num_features)), a_val=0.05)

# our methods
def monte_carlo_validation(anomalies, ref_table, tar_table):
    pass

def median_absolute_deviation(anomalies, ref_table, tar_table, threshold = 3):
    feature_count = len(ref_table[0])

    # Compute medians for reference table
    medians = {}
    for feature in tqdm.tqdm(range(feature_count), desc="Computing medians"):
        vals = [row[feature] for row in ref_table]
        vals.sort()
        n = len(vals)

        if n % 2 == 1:
            medians[feature] = vals[n // 2]
        else:
            medians[feature] = (vals[n // 2 - 1] + vals[n // 2]) / 2.0

    # 2. Compute MAD for each feature
    MAD = {}
    for feature in tqdm.tqdm(range(feature_count), desc="Computing MAD"):
        median_val = medians[feature]
        abs_dev = [abs(row[feature] - median_val) for row in ref_table]
        abs_dev.sort()
        n = len(abs_dev)

        if n % 2 == 1:
            MAD_val = abs_dev[n // 2]
        else:
            MAD_val = (abs_dev[n // 2 - 1] + abs_dev[n // 2]) / 2.0

        MAD[feature] = MAD_val

    # Validate anomalies from target table
    real_anomalies = []

    for anomaly in tqdm.tqdm(anomalies, desc="Validating anomalies with MAD"):
        for feature in range(feature_count):
            if MAD[feature] == 0:
                break
            deviation = abs(anomaly[feature] - medians[feature])
            mad_score = (0.6745 * deviation) / MAD[feature]

            if mad_score > threshold:
                real_anomalies.append(anomaly)
                break

    return real_anomalies

def kernel_density_estimation(anomalies, ref_table, tar_table):
    feature_count = len(ref_table[0])
    bandwidth = 0.5

    # Fit KDE for each feature in the reference table
    kde_models = {}
    for feature in tqdm.tqdm(range(feature_count), desc="Fitting KDE models"):
        data = np.array([row[feature] for row in ref_table]).reshape(-1, 1)
        kde = KernelDensity(kernel='gaussian', bandwidth=bandwidth).fit(data)
        kde_models[feature] = kde

    densities = np.zeros((len(tar_table), feature_count))
    T = np.array(tar_table)

    for f in tqdm.tqdm(range(feature_count), desc="Fitting KDE models"):
        T_data = T[:, f].reshape(-1, 1)
        logdens = kde_models[f].score_samples(T_data)
        densities[:, f] = np.exp(logdens)

    # Row-level anomaly detection
    density_threshold = 0.01
    anomalous_mask = np.any(densities < density_threshold, axis=1)
    new_anomalies = T[anomalous_mask]
    anomalies.extend(new_anomalies)

    return anomalies