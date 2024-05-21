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