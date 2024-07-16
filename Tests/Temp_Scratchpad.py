







'''
channel = 5
binary_value = format(channel, f'0{8}b')
print(binary_value)
'''


'''
import re
def extract_information(input_string):
    # Extract the relevant information using regular expressions
    pattern = r'(?:R|C|CPE|Wo)\d+|(?<=,)(?:R|C|CPE|Wo)\d+(?=\))'
    extracted_info = re.findall(pattern, input_string)
    for i, item in enumerate(extracted_info):
        if 'CPE' in item:
            num = item[3:]
            extracted_info[i] = 'Q' + num
            extracted_info.insert(i+1, 'n' + num)
    return extracted_info

# Test cases
print(extract_information('R0-C1'))  # Output: ['R0', 'C1']
print(extract_information('R0-p(C1,R1)'))  # Output: ['R0', 'C1', 'R1']
print(extract_information('R0-p(CPE1,R1)'))  # Output: ['R0', 'CPE1', 'R1']
'''







''' 
import numpy as np

def find_phase(real, imag):
    return np.angle(real + 1j*imag, deg=True)

def find_phase_arctan(real, imag):
    if real > 0 and imag > 0:
        return (np.arctan(imag/real))*(180/np.pi)
    elif real < 0 and imag > 0:
        return 180 + (np.arctan(imag/real))*(180/np.pi)
    elif real < 0 and imag < 0:
        return 180 + (np.arctan(imag/real))*(180/np.pi)
    elif real > 0 and imag < 0:
        return 360 + (np.arctan(imag/real))*(180/np.pi)
    else:
        ValueError('Invalid Input')

def find_phase_atan2(real, imag):
    return np.arctan2(imag, real)*(180/np.pi)

print('Angle Method',find_phase(1, 1))
print('Datasheet Method',find_phase_arctan(1, 1))
print('np.arctan2 method',find_phase_atan2(1, 1))
print('Angle Method',find_phase(1, -1))
print('Datasheet Method',find_phase_arctan(1, -1))
print('np.arctan2 method',find_phase_atan2(1, -1))
print('Angle Method',find_phase(-1, -1))
print('Datasheet Method',find_phase_arctan(-1, -1))
print('np.arctan2 method',find_phase_atan2(-1, -1))
print('Angle Method',find_phase(-1, 1))
print('Datasheet Method',find_phase_arctan(-1, 1))
print('np.arctan2 method',find_phase_atan2(-1, 1))
'''
