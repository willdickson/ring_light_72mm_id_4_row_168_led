import os
import sys
import math
import pickle
import pcbnew
from design import RingLightDesign


def nm_to_mm(value):
    return value*1.0e-6

def mm_to_nm(value):
    return value*1.0e6

def rad_to_deg(value):
    return 180.0*value/math.pi

def deg_to_rad(value):
    return 180.0*value/math.pi

# -----------------------------------------------------------------------------
if __name__ == '__main__':

    param_filename = sys.argv[1]
    pcb_filename = sys.argv[2]

    center_x = 100
    center_y = 100
    resistor_offset = 5.0
    mount_hole_radius = 76.0
    mount_hole_offset = 0.5
    
    with open(param_filename, 'rb') as f:
        param = pickle.load(f)
    
    design = RingLightDesign(param)
    pos_list = design.get_light_position_list()
    outer_diam = design.get_outer_diameter()
    
    
    pcb = pcbnew.LoadBoard(pcb_filename)

    led_pos_dict = {}
    led_angle_dict = {}
    led_uvec_dict = {}

    module_list = [module for module in pcb.GetModules()]

    for module in module_list:
        ref_str = str(module.GetReference())
        if 'D' in ref_str:
            led_num = int(ref_str[1:])
            print(f'LED# {led_num}: {ref_str}')
    
            pos = pos_list[led_num-1]
            led_pos_x = pos['x'] + center_x
            led_pos_y = pos['y'] + center_y
            x_nm = mm_to_nm(led_pos_x)
            y_nm = mm_to_nm(led_pos_y)
            angle_deg = rad_to_deg(pos['angle'])

            led_pos_dict[led_num] = led_pos_x, led_pos_y
            led_angle_dict[led_num] = angle_deg
            uvec_denom = math.sqrt(pos['x']**2 + pos['y']**2)
            led_uvec_dict[led_num] = pos['x']/uvec_denom, pos['y']/uvec_denom

            # Move modules to new position
            pos = module.GetPosition()
            pos.x = int(x_nm)
            pos.y = int(y_nm)
            module.SetPosition(pos)
            module.SetOrientation(-10.0*angle_deg)

            # Make value invisible
            value_obj = module.Value()
            value_obj.SetVisible(False)

    for module in module_list:
        ref_str = str(module.GetReference())
        if 'R' in ref_str:
            r_num = int(ref_str[1:])
            print(f'R# {r_num}: {ref_str}')

            con_led_num = r_num*param['divisor']

            led_pos = led_pos_dict[con_led_num]
            uvec = led_uvec_dict[con_led_num]

            #new_pos_x = led_pos[0] 
            #new_pos_y = led_pos[1] 
            new_pos_x = led_pos[0] + resistor_offset*uvec[0]
            new_pos_y = led_pos[1] + resistor_offset*uvec[1]
            new_pos_x_nm = mm_to_nm(new_pos_x)
            new_pos_y_nm = mm_to_nm(new_pos_y)
            
            pos = module.GetPosition()
            pos.x = int(new_pos_x_nm)
            pos.y = int(new_pos_y_nm)
            module.SetPosition(pos)
            module.SetOrientation(-10.0*(led_angle_dict[con_led_num]-90.0))

            value_obj = module.Value()
            value_obj.SetVisible(False)

            ref_obj = module.Reference()
            ref_obj.SetVisible(False)


    mount_hole_dict = {} 
    for module in module_list:
        ref_str = str(module.GetReference())
        if 'M' in ref_str:
            hole_num = int(ref_str[1:])
            mount_hole_dict[hole_num] = module

    num_mount_hole = len(mount_hole_dict)
    angle_step = (2.0*math.pi)/float(num_mount_hole) 
    for hole_num, module in mount_hole_dict.items():
        angle_rad = (hole_num-1)*angle_step + mount_hole_offset*angle_step
        print(hole_num, rad_to_deg(angle_rad))
        pos = module.GetPosition()
        pos.x = int(mm_to_nm(mount_hole_radius*math.cos(angle_rad) + center_x))
        pos.y = int(mm_to_nm(mount_hole_radius*math.sin(angle_rad) + center_y))
        module.SetPosition(pos)



    pathname, basename = os.path.split(pcb_filename)
    new_basename = 'mod_{}'.format(basename)
    new_filename = os.path.join(pathname,new_basename)
    
    pcb.Save(new_filename)



