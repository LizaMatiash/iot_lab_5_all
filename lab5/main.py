from kivy.app import App
from kivy_garden.mapview import MapMarker, MapView
from kivy.clock import Clock
from lineMapLayer import LineMapLayer
from scipy.signal import find_peaks

import requests as requests


class MapViewApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.accelerometer_data = []
        self.gps_data = []
        self.line_layer = LineMapLayer()
        self.window_size = 20 
        self.data_window = [] 

    def on_start(self):
        """
        Встановлює необхідні маркери, викликає функцію для оновлення мапи
        """
        self.load_data_from_api()
        self.mapview.add_layer(self.line_layer)

        initial_position = self.gps_data[0] if self.gps_data else (0, 0)
        self.update_car_marker(initial_position)
        Clock.schedule_interval(self.update, 1/8)

    def update(self, *args):
        """
        Викликається регулярно для оновлення мапи
        """
        if self.accelerometer_data and self.gps_data:

            accelerometer_point = self.accelerometer_data.pop(0)
            gps_point = self.gps_data.pop(0)

            self.update_car_marker(gps_point) 

            self.update_route(gps_point)  


            self.data_window.append((accelerometer_point, gps_point))


            if len(self.data_window) == self.window_size:
                self.detect_peaks_and_minima()

    def update_car_marker(self, point):
        """
        Оновлює відображення маркера машини на мапі
        :param point: GPS координати
        """

        self.car_marker.lat, self.car_marker.lon = point

    def load_data_from_api(self):

        response = requests.get("http://localhost:8000/processed_agent_data/")
        data = response.json()


        self.accelerometer_data = [[float(record['x']), float(record['y']), float(record['z'])] for record in data]
        self.gps_data = [(float(record['longitude']), float(record['latitude'])) for record in data]

    def load_accelerometer_data(self):

        with open('data.csv', 'r') as f:
            for line in f:
                data = line.strip().split(',')
                self.accelerometer_data.append([float(x) for x in data])

    def load_gps_data(self):

        with open('gps.csv', 'r') as f:
            for line in f:
                data = line.strip().split(',')
                self.gps_data.append((float(data[0]), float(data[1])))

    def check_road_quality(self, accelerometer_point, gps_point):
        """
        Перевіряє якість дороги і додає відповідний маркер на мапу
        """
        if accelerometer_point[2] > 17300:
            self.add_marker(gps_point, "images/bump.png") 
        elif accelerometer_point[2] < 7000:
            self.add_marker(gps_point, "images/pothole.png")

    def update_route(self, gps_point):
        """
        Оновлює маршрут на мапі
        """

        self.line_layer.add_point(gps_point)

    def add_marker(self, point, image_path):
        """
        Додає маркер на мапу
        :param point: GPS координати
        :param image_path: шлях до зображення маркера
        """
        marker = MapMarker(lat=point[0], lon=point[1], source=image_path)
        self.mapview.add_marker(marker)

    def detect_peaks_and_minima(self):
        """
        Знаходить піки та мінімуми на кожних window_size точках GPS та акселерометра
        та додає маркери на мапу
        """
        gps_points = [data[1] for data in self.data_window]
        accelerometer_points = [data[0] for data in self.data_window]

        z_values = [point[2] for point in accelerometer_points]

        peaks_max, _ = find_peaks([val for val in z_values], height=0)
        peaks_min, _ = find_peaks([-val for val in z_values], height=0)


        for peak in peaks_max:
            self.check_road_quality(accelerometer_points[peak], gps_points[peak])
        for minimum in peaks_min:
            self.check_road_quality(accelerometer_points[minimum], gps_points[minimum])

        self.data_window = []

    def build(self):
        """
        Ініціалізує мапу MapView (zoom, lat, lon)
        :return: мапу
        """
        initial_lat, initial_lon = self.gps_data[0] if self.gps_data else (50.33956017984955600,30.28635085351856000)
        initial_zoom = 15

        self.mapview = MapView(zoom=initial_zoom, lat=initial_lat, lon=initial_lon)
        self.car_marker = MapMarker(lat=initial_lat, lon=initial_lon)
        self.mapview.add_marker(self.car_marker)
        return self.mapview


if __name__ == '__main__':
    MapViewApp().run()
