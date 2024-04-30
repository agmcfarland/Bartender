import numpy as np
import multiprocessing as mp

def hamming_distance_preset_length(string1, string2, barcode_length=35, cutoff=1):
    """
    Computes the hamming distance between two strings up until the string_distance is greater than cutoff and returns that value.
    The length of string 1 and 2 are expected to be equal and do not need to be calculated.
    """
    string_distance = 0

    for n in range(barcode_length):
        if string1[n] != string2[n]:
            string_distance += 1
            if string_distance > cutoff:
                return string_distance
    return string_distance


def hamming_worker(barcode1, barcodes2_list, barcode_length, cutoff):
    """
    Worker function to calculate Hamming distances for a subset of barcodes2_list and return matches that are below or equal to the specified
    distance cutoff.
    """
    result = []
    for barcode2 in barcodes2_list:
        distance = hamming_distance_preset_length(
            string1=barcode1,
            string2=barcode2,
            barcode_length=barcode_length,
            cutoff=cutoff,
        )
        if distance <= cutoff:
            result.append([barcode1, barcode2, distance])
    return result


def hamming_distance_array(barcodes1_list, barcodes2_list, barcode_length, cutoff):
    """
    Returns an array with string1, string2, hamming_distance
    """
    distance_array = []

    with mp.Pool() as pool:
        results = [
            pool.apply_async(
                hamming_worker, (barcode1, barcodes2_list, barcode_length, cutoff)
            )
            for barcode1 in barcodes1_list
        ]

        for res in results:
            distance_array.extend(res.get())

    return distance_array
