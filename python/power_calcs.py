import numpy as np
import matplotlib.pyplot as plt

forw_curr = 0.060
forw_volt = 1.6

vs = 12.0
led_per_string = int(vs/forw_volt)
rlim_volt = vs - led_per_string*forw_volt
rlim_pow = forw_curr*rlim_volt
rlim_val = rlim_volt/forw_curr


print()
print('strings')
print('----------------------------------')
print(f'leds per string:  {led_per_string}')
print(f'operating curr:   {forw_curr:1.3f}(A)')
print(f'led forward volt: {forw_volt:1.3f}(V)')
print(f'resister volt:    {rlim_volt:1.3f}(V)')
print(f'resister power:   {rlim_pow:1.3f}(W)')
print(f'resister value:   {rlim_val:1.0f}(Ohm)')
print()

num_led = 168
num_string = num_led//led_per_string
total_current = num_string*forw_curr
total_power = total_current*vs

print('full light')
print('----------------------------------')
print(f'number strings: {num_string}')
print(f'total current:  {total_current:1.3f}(A)')
print(f'total power:    {total_power:1.3f}(W)')
print()














