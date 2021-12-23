import multiprocessing

from data.pretraining.c4.masking_task import c4_masking_task
from data.pretraining.c4.processing import c4_processing
from data.pretraining.wdc.filtering import wdc_filtering
from data.pretraining.wdc.tasks.column_masking import column_masking_task
from data.pretraining.wdc.tasks.column_mixing import column_mixing_task
from data.pretraining.wdc.tasks.column_type_prediction import column_type_task


def smap(f):
    return f()


def run_preprocessing():
    with multiprocessing.Pool(processes=8) as pool:
        pool.map(smap, [c4_processing,
                        wdc_filtering])


def run_pretraining_tasks_creation():
    with multiprocessing.Pool(processes=8) as pool:
        pool.map(smap, [c4_masking_task,
                        column_mixing_task,
                        column_masking_task,
                        column_type_task])


def create_pretraining_tasks():
    # Note that on the above methods the paths are hardcoded

    print("###### Preprocessing started ######")
    run_preprocessing()

    print("\n###### Pretraining tasks creation started ######")
    run_pretraining_tasks_creation()

    print("\n###### Finished ######")


if __name__ == '__main__':
    create_pretraining_tasks()
