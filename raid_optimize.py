#!/usr/bin/env python3
'''
    Author: Jonathan Lung (https://github.com/lungj)
    ETH/ETC donations: 0xc5500095A395B4FB3ba81bB0D8e316c675d1F47C
    Because disks don't hoard themselves.

    Purpose:
        Determine disk pool configurations to achieve performance-cost-reliability
        tradeoffs.

    Usage:
        python3 raid_optimize.py

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
from com.heresjono.raidcalc import HDD, SSD, generate_disk_configurations, print_notable_configs
import com.heresjono.raidcalc
import locale

###### USER CONFIGURATION ######
com.heresjono.raidcalc.MISSION_LENGTH = 3               # How long to keep things running in years.
MAX_FAILURE = 1 / 10000                                 # 1 in 10000 chance of losing pool during mission.
MIN_CAPACITY = 6e12                                     # Minimum of 6 TB of data in array.
MAX_COST = 1500                                         # Spend no more than $1500 on disks.

DISK_CHOICES = [                                        # What disks are being considered?
    # The following values are for new drives in Canada (after taxes).
    # Average failure rate (AFR) goes up after 3 years for HDD (source: Backblaze).
    HDD('WD4TB', 4e12, afr=0.06, cost=170, replacement_time=96),    # Ship and shuck.
    HDD('WD8TB', 8e12, afr=0.06, cost=305, replacement_time=96),    # Ship and shuck.
    SSD('WD Blue 3D 1TB', 1e12, cost=190, replacement_time=24),     # Walk to store.
    ]
###### END USER CONFIGURATION ######


if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    configs = generate_disk_configurations(
            DISK_CHOICES,
            max_afr=1 - ((1 - MAX_FAILURE) ** (1 / com.heresjono.raidcalc.MISSION_LENGTH)),
            min_capacity=MIN_CAPACITY,
            max_cost=MAX_COST)
    print_notable_configs(configs)
