from tqdm import trange
# missing records should have 5, 10, 20, or 50 percent missing
# others should find 20%

def get_difference(table1, table2):
    t1_set = set(tuple(record) for record in table1)
    t2_set = set(tuple(record) for record in table2)
    difference = t2_set - t1_set
    return difference

def get_intersection(table1, table2):
    t1_set = set(tuple(record) for record in table1)
    t2_set = set(tuple(record) for record in table2)
    intersection = t1_set & t2_set
    return intersection

def check_anomalies(found_anomalies, ref_table, tar_table):
    actual_anomalies = list(get_difference(ref_table, tar_table))
    not_anomalies = list(get_intersection(ref_table, tar_table))
    not_predicted = list(get_difference(tar_table, found_anomalies))

    true_positives = len(get_intersection(found_anomalies, actual_anomalies))
    false_positives = len(get_intersection(found_anomalies, not_anomalies))
    true_negatives = len(get_intersection(not_predicted, not_anomalies))
    false_negatives = len(get_intersection(not_predicted, actual_anomalies))
    
    print(f"True Positives: {true_positives}")
    print(f"False Positives: {false_positives}")
    print(f"True Negatives: {true_negatives}")
    print(f"False Negatives: {false_negatives}")

    print(f"Precision: {precision(true_positives, false_positives)}")
    print(f"Recall: {recall(true_positives, false_negatives)}")
    print(f"Accuracy: {accuracy(true_positives, true_negatives, false_positives, false_negatives)}")

def recall(tp, fn):
    if (tp + fn) == 0:
        return 0
    return tp / (tp + fn)

def precision(tp, fp):
    if (tp + fp) == 0:
        return 0
    return tp / (tp + fp)

def accuracy(tp, tn, fp, fn):
    total = tp + tn + fp + fn
    if total == 0:
        return 0
    return (tp + tn) / total
