#!/usr/bin/env python3
'''
    Author: Jonathan Lung (https://github.com/lungj)
    ETH/ETC donations: 0xc5500095A395B4FB3ba81bB0D8e316c675d1F47C
    Because disks don't hoard themselves.

    Purpose:
        Arrange a fixed group of disks into different configurations that maximize certain
        attributes.

    Usage:
        python3 raid_arrange.py

    Optimization parameters can be set below. Search for "USER CONFIGURATION."
    If optimization is taking too long, try reducing the number of disk choices available
    for the pool.

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
from com.heresjono.raidcalc import HDD, SSD, generate_disk_configurations, print_notable_configs
import com.heresjono.raidcalc
import locale

###### USER CONFIGURATION ######
com.heresjono.raidcalc.MISSION_LENGTH = 3           # How long to keep things running in years.
MAX_FAILURE = 1 / 10000                             # 1 in 10000 chance of losing pool during mission.
MIN_CAPACITY = 6e12                                 # Minimum of 6 TB of data in array.

# The optimizer never pairs mismatched disks into a mirror.
ARRANGEMENT = []
ARRANGEMENT.extend([HDD('WD4TB', 4e12, cost=170)] * 7)      # 7x 4TB drives
ARRANGEMENT.extend([HDD('WD8TB', 8e12, cost=305)] * 6)      # 6x 8TB drives
###### END USER CONFIGURATION ######


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    configs = generate_disk_configurations(
            None,
            disks=[ARRANGEMENT],
            max_afr=1 - ((1 - MAX_FAILURE) ** (1 / com.heresjono.raidcalc.MISSION_LENGTH)),
            min_capacity=MIN_CAPACITY,
            max_cost=1e10)
    print_notable_configs(configs)