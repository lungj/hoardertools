#!/usr/bin/env python3
'''
    Author: Jonathan Lung (https://github.com/lungj)
    ETH/ETC donations: 0xc5500095A395B4FB3ba81bB0D8e316c675d1F47C
    Because disks don't hoard themselves.

    Purpose:
        Provide functionality for calculating information about RAID pools.

    Optimization parameters can be set below. Search for "USER CONFIGURATION."
    If optimization is taking too long, try a lower max cost and/or reducing the number of
    disk choices available for the pool.

    Output for probabilities is given as odds. For morbid comparison, over the course of
    your lifetime, historically, you are likely to experience (US numbers):

        Death by terrorist                      1 in 5 000 000
        Death by lightning                      1 in 700 000
        Death by asteroid strike                1 in 75 000
        Death by accidental gunshot wound       1 in 8 000
        Death by peptic ulcer disease           1 in 700
        Death by car accident                   1 in 77
        Death by heart-disease                  1 in 7
        Death                                   1 in 1

    Disclaimer:
        Standard disclaimer. Execution of the bytes contained herein are at your own risk.

        The values produced are probabilities; a supposedly reliable system could break in
        a week or vice-versa. No guarantees are provided on the correctness of the
        outputs. In other words, this program cannot predict the future.

        Some of the maths here are approximations that work for "realistic" inputs.
        So don't go setting annual failure rate (AFR) to 0.9 (90%).

        Garbage in, garbage out.
        Speed measurements are for sequential throughput only.
        Assumes write endurance of SSDs is not a limiting factor.
        Defaults may not be reflective of your assumptions.

        Assumes remainder of system is no a bottleneck.

        These failure rate results assume the rest of the system is 100% reliable.
        These failure rate results assume disk failures are independent and evenly
        distributed. Always make backups!
        RAID/REDUNDANCY IS NOT A BACKUP.
        KEEP THE BACKUPS OFF-SITE!

        DON'T FORGET TO INCORPORATE THE COST OF BACKUPS AND REPLACEMENT DISKS INTO YOUR
        COSTS! And, of course, things like the device housing everything, electricity,
        shipping, etc. This program does not optimize on enclosure costs for large arrays.

        TCO costs are approximations in NPV and do not account for things like taxes and
        technology getting cheaper.
'''

import locale

def entab(x:str):
    '''Entab string x and add a newline at the end.'''
    s = ''
    for line in x.split('\n'):
        s += '    ' + line + '\n'
    return s


def count_sames(lst:list):
    '''Return the number of times the first element is repeated at the beginning of lst.'''
    if not lst:
        return 0

    first = lst[0]
    count = 0
    for item in lst:
        if item == first:
            count += 1

    return count

class Disk(object):
    '''Representation of a physical disk.'''
    def __init__(self,
                name: str,                  # Friendly name of disk for display purposes.
                capacity: int,              # Size of disk in bytes.
                speed:int=100e6,            # Speed of disk in bytes per second.
                afr:float=0.12,             # Annual failure rate [0, 1).
                cost:float=100,             # Price in currency of choice.
                replacement_time:float=72   # Hours from failure until a replacement is installed.
                ):

        self._name = name
        self._capacity = capacity
        self._speed = speed
        self._afr = afr
        self._cost = cost
        self._replacement_time = replacement_time


    @property
    def name(self):
        '''Return drive name.'''
        return self._name


    @property
    def cost(self):
        '''Return drive cost.'''
        return self._cost


    @property
    def capacity(self):
        '''Return drive cost.'''
        return self._capacity


    @property
    def replacement_time(self):
        '''Return time to replace disk.'''
        return self._replacement_time


    @property
    def read_time(self):
        '''Return time to read whole disk in hours.'''
        return self._capacity / self._speed / (60 * 60)


    @property
    def write_time(self):
        '''Return time to write whole disk in hours.'''
        return self._capacity / self._speed / (60 * 60)


    @property
    def rebuild_time(self):
        '''Return time to copy this disks contents onto another one like itself.'''
        return max(self._read_time, self._write_time)


    @property
    def hourly_failure(self):
        '''Return probability of failing in a one-hour interval.'''
        # This is an approximation.
        return self._afr / (365 * 24)


    @property
    def read_throughput(self):
        '''Return read throughput in bytes per second.'''
        return self._speed


    @property
    def write_throughput(self):
        '''Return write throughput in bytes per second.'''
        return self._speed


    @property
    def annual_failure(self):
        '''Return probability of failing during one year.'''
        return self._afr


    @property
    def rebuild_failure(self):
        '''Return likelihood of data loss if this disk fails.'''
        return 1


    @property
    def annual_cost(self):
        '''Return expected cost of replacement for this disk per year.'''
        return self.annual_failure * self._cost


    @property
    def tco(self):
        '''Return expected cost of replacement over MISSION_LENGTH years.'''
        return self.annual_cost * MISSION_LENGTH + self._cost


    @property
    def mission_loss(self):
        '''Likelihood of failure during mission.'''
        return 1 - (1 - self._afr) ** MISSION_LENGTH


    def __repr__(self):
        return self.name


class HDD(Disk):
    '''Representation of a hard disk drive.'''
    def __init__(self,
                name: str,                  # Friendly name of disk for display purposes.
                capacity: int,              # Size of disk in bytes.
                speed:int=100e6,            # Speed of disk in bytes per second.
                afr:float=0.12,             # Annual failure rate [0, 1).
                cost:float=100,             # Price in currency of choice.
                replacement_time:float=72   # Hours from failure until a replacement is installed.
                ):

        super().__init__(name, capacity, speed, afr, cost, replacement_time)


class SSD(Disk):
    '''Representation of a solid state disk.'''
    def __init__(self,
                name: str,                  # Friendly name of disk for display purposes.
                capacity: int,              # Size of disk in bytes.
                speed:int=300e6,            # Speed of disk in bytes per second.
                afr:float=0.01,             # Annual failure rate [0, 1).
                cost:float=100,             # Price in currency of choice.
                replacement_time:float=72   # Hours from failure until a replacement is installed.
                ):

        super().__init__(name, capacity, speed, afr, cost, replacement_time)


class DiskArray(object):
    '''Stripe of devices.'''
    def __init__(self,
        disks:list      # List of Disks or Mirrors.
        ):
        self._disks = disks


    @property
    def cost(self):
        '''Return cost of array.'''
        return sum([disk.cost for disk in self._disks])


    @property
    def capacity(self):
        '''Return capacity of array.'''
        return sum([disk.capacity for disk in self._disks])


    @property
    def hourly_failure(self):
        '''Return probability of failing in a one-hour interval.'''
        p = 1
        for disk in self._disks:
            p = p * (1 - disk.hourly_failure)
        return 1 - p


    @property
    def read_time(self):
        '''Return time to read whole mirror in hours.'''
        return max([disk.read_time for disk in self._disks]) / len(self._disks)


    @property
    def write_time(self):
        '''Return time to write whole mirror in hours.'''
        return max([disk.write_time for disk in self._disks]) / len(self._disks)


    @property
    def read_throughput(self):
        '''Return read throughput in bytes per second.'''
        return min([disk.read_throughput for disk in self._disks]) * len(self._disks)


    @property
    def write_throughput(self):
        '''Return write throughput in bytes per second.'''
        return min([disk.write_throughput for disk in self._disks]) * len(self._disks)


    @property
    def rebuild_time(self):
        '''Return time to rebuild mirror in hours.'''
        write = max([disk.write_time for disk in self._disks])
        read = max([disk.read_time for disk in self._disks])        # Assume only one disk works
        return max(write, read)


    @property
    def rebuilds_per_year(self):
        '''Return expected number of times the array will need rebuilding per year.'''
        return sum([disk.annual_failure for disk in self._disks])


    @property
    def annual_failure(self):
        '''Return probability of failing during one year.'''
        p = 1
        for disk in self._disks:
            p = p * (1 - disk.annual_failure)
        return 1 - p


    @property
    def rebuild_failure(self):
        '''Return worst-case probability of a failure during rebuild.'''
        return max([disk.rebuild_failure for disk in self._disks])


    @property
    def annual_cost(self):
        '''Return expected cost of replacement for disks per year.'''
        return sum([disk.annual_cost for disk in self._disks])


    @property
    def tco(self):
        '''Return expected cost of replacement over MISSION_LENGTH years.'''
        return self.annual_cost * MISSION_LENGTH + self.cost


    @property
    def mission_loss(self):
        '''Likelihood of failure during mission.'''
        return 1 - (1 - self.annual_failure) ** MISSION_LENGTH


    def __repr__(self):
        s = 'Stripe:\n'
        s = s + ''.join([entab(repr(device)) + '' for device in self._disks])
        return s.strip()


class Mirror(DiskArray):
    '''Mirror of homogenous disks.'''
    def __init__(self,
                disks:list  # List of Disks.
                ):
        self._disks = disks

    @property
    def hourly_failure(self):
        '''Return probability of failing in a one-hour interval.'''
        p = 1
        for disk in self._disks:
            p = p * (1 - disk.hourly_failure)
        return 1 - p


    @property
    def capacity(self):
        '''Return usable capacity of mirror.'''
        return min([disk.capacity for disk in self._disks])


    @property
    def rebuilds_per_year(self):
        '''Return expected number of times the array will need rebuilding per year.'''
        # This is an approximation.
        return sum([disk.annual_failure for disk in self._disks])


    @property
    def write_time(self):
        '''Return time to write whole mirror in hours.'''
        return max([disk.write_time for disk in self._disks])


    @property
    def read_throughput(self):
        '''Return read throughput in bytes per second.'''
        return min([disk.read_throughput for disk in self._disks]) * len(self._disks)


    @property
    def write_throughput(self):
        '''Return write throughput in bytes per second.'''
        return min([disk.write_throughput for disk in self._disks])


    @property
    def rebuild_failure(self):
        '''Return probability of a failure during rebuild.'''
        # Assume "average" disk failure if different disks have different failure rates.
        p_each_disk_survives = ((1 - self.hourly_failure) ** (self.rebuild_time + self.replacement_time))
        return (1 - p_each_disk_survives) ** (len(self._disks) - 1)


    @property
    def replacement_time(self):
        '''Return the worst-case time to replace a disk in the mirror.'''
        return max([disk.replacement_time for disk in self._disks])


    @property
    def annual_failure(self):
        '''Return probability of failing during one year.'''

        # Approximation for few rebuilds.
        return self.rebuild_failure * self.rebuilds_per_year


    @property
    def annual_cost(self):
        '''Return expected cost of replacement for disks per year.'''
        return sum([disk.annual_cost for disk in self._disks])


    def __repr__(self):
        s = 'Mirror: ' + ' '.join([repr(device) for device in self._disks])
        return s


def _generate_disk_selections(
        options:list,               # List of Disks that can be used.
        chosen:list,                # List of Disks chosen for combination.
        results:list,               # Accumulator.
        min_capacity:int,           # Minimum capacity disks need to provide in bytes.
        max_cost:float,             # Maximum cost for all Disks in currency of choice.
        running_cost:float=0,       # Cost of chosen Disks in currency of choice.
        running_capacity:int=0      # Capacity provided by chosen Disks.
        ):
    '''Helper function for finding all combinations of disks that satisfy price limit and
       minimum capacity.
    '''
    if running_cost > max_cost:
        return results

    if running_capacity > min_capacity:
        results.append(chosen)

    for idx, option in enumerate(options):
        _generate_disk_selections(options[idx:], chosen + [option], results, min_capacity,
                max_cost, running_cost + option.cost, running_capacity + option.capacity)

    return results


def _generate_partitions(
        item:Disk,      # Item to partition.
        count:int,      # Number of times item needs to appear.
        maxlen:int,     # Maximum number of times item can appear in newly generated partitions.
        chosen:list,    # Partitions generated so far.
        result:list     # Accumulator.
        ):
    '''Partition item.'''

    if count == 0:
        result.append(chosen)
        return

    for i in range(min(count, maxlen), 0, -1):
        _generate_partitions(item, count - i, i, chosen + [[item] * i], result)


def generate_partitions(
        item:Disk,      # Item to partition.
        count:int       # Number of times item needs to appear.
        ):
    '''Partition item.

        E.g., unique partitions of three "A"s:

        aaa
        aa a
        a a a
    '''

    result = []
    _generate_partitions(item, count, count, [], result)

    return result


def _generate_disk_configurations(
        disks:list,         # List of Disks to put into DiskArray.
        chosen:list,        # Configuration so far of Disks.
        configs:list,       # Accumulator of valid DiskArray configurations.
        min_read:int,       # Minimum read throughput in bytes per second.
        min_write:int,      # Minimum write throughput in bytes per second.
        min_capacity:int,   # Minimum capacity of results.
        max_afr:float       # Maximum annual failure rate of results.
        ):
    '''Generate list of configurations involving disks that satisfy constraints.'''

    if not disks:
        mirrors = [Mirror(mirror[:]) for mirror in chosen]
        ary = DiskArray(mirrors)

        if ary.capacity >= min_capacity and \
            ary.annual_failure <= max_afr and \
            ary.read_throughput >= min_read and \
            ary.write_throughput >= min_write:
            configs.append(ary)
        return

    same = count_sames(disks)
    remainder = disks[same:]

    for partition in generate_partitions(disks[0], same):
        _generate_disk_configurations(remainder, chosen + partition, configs, min_read,
            min_write, min_capacity, max_afr)


def generate_disk_configurations(
        options:list,                       # List of Disks that can be acquired.
        disks:list=None,                    # Pre-seed a list of disks to arrange.
        min_capacity:int=1e12,              # Capacity of disks in bytes.
        min_read_throughput:int=0,          # Minimum read throughput in bytes per second.
        min_write_throughput:int=0,         # Minimum write throughput in bytes per second.
        max_afr:float=0.0001,               # Maximum annual failure rate.
        max_cost:float=5000                 # Maximum cost in currency of choice.
        ):
    '''Generate list of configurations involving disks that satisfy constraints.'''

    if not disks:
        selections = _generate_disk_selections(options, [], [], min_capacity, max_cost)
        print("%i combinations of disks generated." % len(selections))
    else:
        selections = disks

    configs = []
    for selection in selections:
        _generate_disk_configurations(selection, [], configs, min_read_throughput,
            min_write_throughput, min_capacity, max_afr)

    print("%i viable configurations generated." % len(configs))

    return configs


def print_pool_info(
        config:DiskArray,
        title:str=''):
    '''Pretty-print information about an array configuration.'''

    print('=== %sPool  ===' % (title + ' '))
    print(entab(repr(config)))
    print('Capacity (GB)                                {:n}'.format(config.capacity / 1e9))
    print()
    print('Cost                                         ' + locale.currency(config.cost, grouping=True))
    print('Annual replacement costs                     ' + locale.currency(config.annual_cost, grouping=True))
    print('Total cost of ownership                      ' + locale.currency(config.tco, grouping=True))
    print()
    print('Read speed (MB/s)                            {:n}'.format(config.read_throughput / 1e6))
    print('Write speed (MB/s)                           {:n}'.format(config.write_throughput / 1e6))
    print()
    print('Likelihood of data loss/year                 1 in {:n}'.format(int(1 / max(config.annual_failure, 1e-25))))
    print('Likelihood of data loss during mission       1 in {:n}'.format(int(1 / max(config.mission_loss, 1e-25))))


def print_notable_configs(
        configs:list    # List of DiskArrays.
        ):
    '''Pretty-print a list of notable configurations that are maximal/minimal on
       various attributes.'''

    if not configs:
        print("No configs.")
        return

    notable_attributes = {
        'Cheapest': ['cost', '__lt__'],
        'Most Reliable': ['annual_failure', '__lt__'],
        'Fastest Write': ['write_throughput', '__gt__'],
        'Fastest Read': ['read_throughput', '__gt__'],
        'Biggest': ['capacity', '__gt__'],
        'Lowest TCO': ['tco', '__lt__'],
    }

    notable = {key: configs[0] for key in notable_attributes}

    for config in configs:
        for att, test in notable_attributes.items():
            if getattr(getattr(config, test[0]), test[1])(getattr(notable[att], test[0])):
                notable[att] = config

    for att, config in notable.items():
        print_pool_info(config, att)
        print()
