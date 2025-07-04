#!/usr/bin/env python3

from participant import Participant
from pose_estimation_data import PoseEstimationData 

def main():

    par1 = Participant('./', "265465", 'Todd', 39)
    ped = PoseEstimationData("265465", "./database.json", './video_recordings')
    ped.run_pe_and_update_db()


if __name__ == "__main__":
    main()