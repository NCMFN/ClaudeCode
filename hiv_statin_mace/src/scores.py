import numpy as np

def calculate_framingham_risk(row):
    """
    Framingham Risk Score (2008 version) for 10-year CVD risk probability.
    Reference: D'Agostino et al., Circulation 2008
    Inputs: age, sex_at_birth (1=Male, 0=Female), total_cholesterol, hdl_cholesterol,
            systolic_bp, bp_treatment, smoking_status, diabetes_status
    Output: 10-year CVD risk probability (0 to 1)
    """
    age = row['age']
    # Map sex_at_birth: assume 1 is male, 0 is female for this synthetic assignment
    is_male = row['sex_at_birth'] == 1
    tc = row['total_cholesterol']
    hdl = row['hdl_cholesterol']
    sbp = row['systolic_bp']
    trt = row.get('bp_treatment', 0)
    # smoker: assume 'current' is smoker, otherwise non-smoker
    smoker = 1 if row.get('smoking_status') == 'current' else 0
    diabetes = row.get('diabetes_status', 0)

    if is_male:
        # Men coefficients
        ln_age = np.log(age)
        ln_tc = np.log(tc)
        ln_hdl = np.log(hdl)
        ln_sbp = np.log(sbp)

        sum_terms = (3.06117 * ln_age) + (1.12370 * ln_tc) - (0.93263 * ln_hdl)

        if trt:
            sum_terms += (1.99881 * ln_sbp)
        else:
            sum_terms += (1.93303 * ln_sbp)

        sum_terms += (0.65451 * smoker) + (0.57367 * diabetes)

        risk = 1 - (0.88936 ** np.exp(sum_terms - 23.9802))
    else:
        # Women coefficients
        ln_age = np.log(age)
        ln_tc = np.log(tc)
        ln_hdl = np.log(hdl)
        ln_sbp = np.log(sbp)

        sum_terms = (2.32888 * ln_age) + (1.20904 * ln_tc) - (0.70833 * ln_hdl)

        if trt:
            sum_terms += (2.82263 * ln_sbp)
        else:
            sum_terms += (2.76157 * ln_sbp)

        sum_terms += (0.52873 * smoker) + (0.69154 * diabetes)

        risk = 1 - (0.95012 ** np.exp(sum_terms - 26.1931))

    return risk

def calculate_ascvd_risk(row):
    """
    ASCVD Pooled Cohort Equation (ACC/AHA 2013).
    Input: age, sex_at_birth, race, total_cholesterol, hdl_cholesterol,
           systolic_bp, bp_treatment, diabetes, smoker
    Output: 10-year ASCVD risk probability (0 to 1)
    """
    age = row['age']
    is_male = row['sex_at_birth'] == 1
    is_black = row.get('race') == 'African American'
    tc = row['total_cholesterol']
    hdl = row['hdl_cholesterol']
    sbp = row['systolic_bp']
    trt = row.get('bp_treatment', 0)
    smoker = 1 if row.get('smoking_status') == 'current' else 0
    diabetes = row.get('diabetes_status', 0)

    ln_age = np.log(age)
    ln_tc = np.log(tc)
    ln_hdl = np.log(hdl)
    ln_sbp = np.log(sbp)

    if is_black and not is_male:
        # Black Women
        sum_terms = (17.114 * ln_age) + (0.940 * ln_tc) - (18.920 * ln_hdl) + (4.475 * ln_age * ln_hdl)
        if trt:
            sum_terms += (29.291 * ln_sbp) - (6.432 * ln_age * ln_sbp)
        else:
            sum_terms += (27.820 * ln_sbp) - (6.087 * ln_age * ln_sbp)
        sum_terms += (0.691 * smoker) + (0.874 * diabetes)
        baseline_survival = 0.9533
        mean_terms = 86.61
    elif not is_black and not is_male:
        # White/Other Women
        sum_terms = (-29.799 * ln_age) + (4.884 * ln_age**2) + (13.540 * ln_tc) - (3.114 * ln_age * ln_tc) - (13.578 * ln_hdl) + (3.149 * ln_age * ln_hdl)
        if trt:
            sum_terms += (2.019 * ln_sbp)
        else:
            sum_terms += (1.957 * ln_sbp)
        sum_terms += (7.574 * smoker) - (1.665 * ln_age * smoker) + (0.661 * diabetes)
        baseline_survival = 0.9665
        mean_terms = -29.18
    elif is_black and is_male:
        # Black Men
        sum_terms = (2.469 * ln_age) + (0.302 * ln_tc) - (0.307 * ln_hdl)
        if trt:
            sum_terms += (1.916 * ln_sbp)
        else:
            sum_terms += (1.809 * ln_sbp)
        sum_terms += (0.549 * smoker) + (0.645 * diabetes)
        baseline_survival = 0.8954
        mean_terms = 19.54
    else:
        # White/Other Men
        sum_terms = (12.344 * ln_age) + (11.853 * ln_tc) - (2.664 * ln_age * ln_tc) - (7.990 * ln_hdl) + (1.769 * ln_age * ln_hdl)
        if trt:
            sum_terms += (1.797 * ln_sbp)
        else:
            sum_terms += (1.764 * ln_sbp)
        sum_terms += (7.837 * smoker) - (1.795 * ln_age * smoker) + (0.658 * diabetes)
        baseline_survival = 0.9144
        mean_terms = 61.18

    risk = 1 - (baseline_survival ** np.exp(sum_terms - mean_terms))
    return risk
