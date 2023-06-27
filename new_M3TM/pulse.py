import numpy as np

class sim_pulse:
    # This class lets us define te pulse for excitation of the sample

    def __init__(self, pulse_width, fluence, delay):
        self.pulse_width = pulse_width
        self.fluence = fluence
        self.delay = delay
        self.peak_power = self.fluence/np.sqrt(2*np.pi)/self.pulse_width*10

    def create_pulse_map(self, sample):
        # This method creates a time grid and a spatially independent pulse excitation of gaussian shape
        # on this time grid.
        # The pulse is confined to nonzero values in the range of [start_pump_time, end_pump_time]
        # to save computation time. After this time, there follows one entry defining zero pump power
        # for all later times. At each timestep in the grid, the spatial dependence of the pulse is multiplied
        # via self.depth_profile

        # Input:
        # self (object). The pulse defined by the parameters above
        # sample (class object). The before constructed sample

        # Returns:
        # pump_time_grid (numpy array). 1d-array of the time grid on which the pulse is defined
        # pump_map (numpy array). 2d-array of the corresponding pump energies on the time grid (first dimension)
        # and for the whole sample (second dimension)

        pdel = self.delay
        sigma = self.pulse_width
        start_pump_time = pdel-6*sigma
        end_pump_time = pdel+6*sigma

        raw_pump_time_grid = np.arange(start_pump_time, end_pump_time, 1e-16)
        until_pump_start_time = np.arange(0, start_pump_time, 1e-14)
        pump_time_grid = np.append(until_pump_start_time, raw_pump_time_grid)

        raw_pump_grid = self.peak_power*np.exp(-((raw_pump_time_grid-pdel)/sigma)**2/2)
        pump_grid = np.append(np.zeros_like(until_pump_start_time), raw_pump_grid)

        pump_time_grid = np.append(pump_time_grid, end_pump_time+5e-15)
        pump_grid = np.append(pump_grid, 0.)

        return pump_time_grid, self.depth_profile(sample, pump_grid)

    def depth_profile(self, sample, pump_grid):
        # This method computes the depth dependence of the laser pulse and multiplies it with the time dependence.

        # Input:
        # sample (class object). The before constructed sample
        # pump_grid (numpy array). 1d-array of timely pulse shape on the time grid defined in create_pulse_map

        # Returns:
        # 2d-array of the corresponding pump energies on the time grid (first dimension)
        # and for the whole sample (second dimension)

        n_sam = sample.get_len()
        dz_sam = sample.get_params('dz')
        pendep_sam = sample.get_params('pen_dep')
        mat_blocks = sample.get_material_changes()

        max_power = self.peak_power
        powers = np.array([])
        first_layer = 0
        last_layer = 0

        for i in range(len(mat_blocks)):
            last_layer += mat_blocks[i]
            if pendep_sam[first_layer] == 1:
                powers = np.append(powers, np.zeros(mat_blocks[i]))
                first_layer = last_layer
                continue
            pen_red = np.divide(np.arange(mat_blocks[i])*dz_sam[first_layer:last_layer],
                                pendep_sam[first_layer:last_layer])
            powers = np.append(powers, max_power/pendep_sam[first_layer:last_layer]
                               * np.exp(-pen_red))
            max_power = powers[-1]*pendep_sam[last_layer-1]
            first_layer = last_layer
        excitation_map = np.multiply(pump_grid[..., np.newaxis], np.array(powers))

        return excitation_map
