import time
from csv import reader
from datetime import datetime
from typing import List

from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.aggregated_data import AggregatedData
import config


class FileDatasource:
    def __init__(self, accelerometer_filename: str, gps_filename: str) -> None:
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename
        self.accelerometer_file = None
        self.gps_file = None
        self.accelerometer_reader = None
        self.gps_reader = None
        self.accelerometer_buffer = []
        self.gps_buffer = []

    def startReading(self, *args, **kwargs):
        self.accelerometer_file = open(self.accelerometer_filename, 'r')
        self.gps_file = open(self.gps_filename, 'r')
        self.accelerometer_reader = reader(self.accelerometer_file)
        self.gps_reader = reader(self.gps_file)

        # Skip the first line
        next(self.accelerometer_reader)
        next(self.gps_reader)

    def stopReading(self, *args, **kwargs):
        if self.accelerometer_file:
            self.accelerometer_file.close()
        if self.gps_file:
            self.gps_file.close()

    def read(self) -> List[AggregatedData]:
        aggregated_data_list = []
        try:
            batch_timestamp = datetime.now()  # Generate one timestamp for the entire batch
            for _ in range(5):
                accelerometer_data = next(self.accelerometer_reader)
                gps_data = next(self.gps_reader)

                accelerometer = Accelerometer(*map(int, accelerometer_data))
                gps = Gps(*map(float, gps_data))
                aggregated_data_list.append(AggregatedData(accelerometer, gps, batch_timestamp))

                time.sleep(0.5)  # Затримка у пів секунди між кожним читанням

        except StopIteration:
            self.accelerometer_file.seek(0)
            self.gps_file.seek(0)
            self.accelerometer_reader = reader(self.accelerometer_file)
            self.gps_reader = reader(self.gps_file)
            next(self.accelerometer_reader)  # Skip the first line
            next(self.gps_reader)  # Skip the first line
            return self.read()  # Read again after resetting the files

        except Exception as e:
            print(f"An error occurred while reading data: {e}")

        return aggregated_data_list
