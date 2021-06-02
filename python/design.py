import pickle
import numpy as np
import matplotlib.pyplot as plt


class RingLightDesign:

    def __init__(self,param):
        self.param = param

    def get_num_lights(self):
        pos_list = self.get_light_position_list()
        return len(pos_list)

    def get_light_diameters(self):
        light_diam_list = []
        for i in range(0,self.param['number_rows']):
            light_diam = self.param['inner_diameter'] + 2*self.param['inner_margin']  
            light_diam += 2*i*(self.param['part_height'] + self.param['radial_spacing'])
            light_diam_list.append(light_diam)
        return light_diam_list 

    def get_outer_diameter(self):
        light_diam_list = self.get_light_diameters()
        return max(light_diam_list) + 2*self.param['outer_margin'] + self.param['part_height']

    def get_light_position_dict(self):
        light_diam_list = self.get_light_diameters()
        light_pos_dict = {}
        for diam in light_diam_list:
            light_pos_dict[diam] = self.get_light_positions(diam)
        return light_pos_dict

    def get_light_position_list(self):
        position_dict = self.get_light_position_dict()
        position_list = []
        for _,v in position_dict.items():
            position_list.extend(v)
        return position_list

    def get_light_positions(self,diam):
        num_lights = int(np.pi*diam/(self.param['circum_spacing'] + self.param['part_width']))
        adjusted_circum_spacing = np.pi*diam/num_lights - self.param['part_width']
        position_list = []
        for i in range(num_lights):
            angle = (adjusted_circum_spacing + self.param['part_width'])*(i + 0.5)/(0.5*diam)
            x = 0.5*diam*np.cos(angle)
            y = 0.5*diam*np.sin(angle)
            position_list.append({'x': x, 'y': y, 'angle': angle})
        return position_list

    def plot_light_positions(self, color='g', fignum=1):
        plt.figure(fignum)
        position_dict = self.get_light_position_dict()
        for diam, pos_list in position_dict.items():
            for pos in pos_list:
                plt.plot([pos['x']], [pos['y']], '.g')

    def plot_light_outlines(self, color='g', fignum=1):
        h = self.param['part_height']
        w = self.param['part_width']
        plt.figure(fignum)
        for pos in self.get_light_position_list():
            rotmat = np.array([ 
                [np.cos(pos['angle']), -np.sin(pos['angle'])], 
                [np.sin(pos['angle']),  np.cos(pos['angle'])], 
                ]) 
            pos_vec = np.array([[pos['x']], [pos['y']]])
            box_pts = np.array([
                [-0.5*h,  0.5*h, 0.5*h, -0.5*h, -0.5*h],
                [-0.5*w, -0.5*w, 0.5*w,  0.5*w, -0.5*w],
                ])
            box_pts = np.dot(rotmat, box_pts) + pos_vec
            plt.plot(box_pts[0,:], box_pts[1,:], color)


    def plot_light_diameters(self, num_pts=500, color='b', fignum=1):
        plt.figure(fignum)
        theta = np.linspace(0.0,2.0*np.pi,num_pts)
        light_diam_list = self.get_light_diameters()
        for diam in light_diam_list:
            x = 0.5*diam*np.cos(theta)
            y = 0.5*diam*np.sin(theta)
            plt.plot(x,y,color)

    def plot_boundaries(self, num_pts=500, color='r', fignum=1):
        plt.figure(fignum)
        theta = np.linspace(0.0,2.0*np.pi,num_pts)
        inner_diam = self.param['inner_diameter']
        outer_diam = self.get_outer_diameter()
        inner_x = 0.5*inner_diam*np.cos(theta)
        inner_y = 0.5*inner_diam*np.sin(theta)
        outer_x = 0.5*outer_diam*np.cos(theta)
        outer_y = 0.5*outer_diam*np.sin(theta)
        plt.plot(inner_x, inner_y, color)
        plt.plot(outer_x, outer_y, color)

    def plot(self):
        design.plot_boundaries()
        design.plot_light_diameters()
        design.plot_light_positions()
        design.plot_light_outlines()


def find_min_divisible_design(divisor, base_param, adjust_param, num_values=10):
    divisible_designs = find_divisible_designs(divisor, base_param, adjust_param)
    adjust_names = [name for name in adjust_param]
    cost_array = np.zeros(len(divisible_designs))
    for i, param in enumerate(divisible_designs):
        cost = 0.0
        for name in adjust_names:
            cost += (base_param[name] - param[name])**2
        cost_array[i] = cost
    ind_min_cost = cost_array.argmin()
    return divisible_designs[ind_min_cost], cost_array[ind_min_cost] 


def find_divisible_designs(divisor, base_param, adjust_param, num_values=10):
    adjust_names = [name for name in adjust_param]
    adjust_arrays = []
    for name in adjust_names:
        base_value = base_param[name]
        adjust_value = adjust_param[name]
        adjust_arrays.append(np.linspace(base_value - 0.5*adjust_value, base_value + 0.5*adjust_value, num_values))
    adjust_grids = np.meshgrid(*adjust_arrays)
    adjust_grid_dict = dict(zip(adjust_names, adjust_grids))
    for k,v in adjust_grid_dict.items():
        adjust_grid_dict[k] = v.flatten()

    num_test_values = adjust_grid_dict[adjust_names[0]].shape[0]
    divisible_designs = []
    for i in range(num_test_values):
        param = dict(base_param)
        for k, v in adjust_grid_dict.items():
            param[k] = v[i]
        design = RingLightDesign(param)
        num_lights = design.get_num_lights()
        if num_lights % divisor == 0:
            divisible_designs.append(param)
    return divisible_designs

# -----------------------------------------------------------------------------
if __name__ == '__main__':

    if 0:
        base_param = {
                'inner_diameter' : 72.0,
                'inner_margin'   : 4.0, 
                'outer_margin'   : 4.0, 
                'number_rows'    : 4, 
                'part_width'     : 5, 
                'part_height'    : 5,
                'radial_spacing' : 2.5,
                'circum_spacing' : 2.5,
                }
        adjust_param = {
                'radial_spacing'  : 1.0, 
                'circum_spacing'  : 1.0,
                }
    if 1:

        base_param = {
                'inner_diameter' : 72.0,
                'inner_margin'   : 4.0, 
                'outer_margin'   : 4.0, 
                'number_rows'    : 4, 
                'part_width'     : 5, 
                'part_height'    : 5,
                'radial_spacing' : 4.5,
                'circum_spacing' : 3.0,
                }
        adjust_param = {
                'radial_spacing'  : 1.0, 
                'circum_spacing'  : 1.0,
                }

    divisor = 7
    final_param, cost = find_min_divisible_design(divisor, base_param, adjust_param)
    design = RingLightDesign(final_param)
    outer_diameter = design.get_outer_diameter()
    number_led = design.get_num_lights()

    print(f'cost: {cost}')
    print()
    print(f'outer_diameter: {outer_diameter:1.3f}')
    for k,v in final_param.items():
        print(f'{k}: {v:1.3f}')
    print()
    print(f'number LED: {number_led}')
    print(f'{number_led//divisor} strings of {divisor}')


    final_param['divisor'] = divisor
    with open('param.pkl', 'wb') as f:
        pickle.dump(final_param, f)


    design.plot()
    plt.axis('equal')
    plt.grid(True)
    plt.title(f'#LED = {design.get_num_lights()}')
    plt.show()






