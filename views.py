import time
import random
from threading import Thread, Lock, Event
import sys

class TrafficLight:
    def __init__(self, id, lock, stop_event):
        self.id = id
        self.green_time = 0
        self.red_time = 2  # Фиксированное время красного сигнала
        self.waiting_cars = 0
        self.waiting_pedestrians = 0
        self.lock = lock  # Блокировка для синхронизации
        self.green_signal = False  # Статус зеленого сигнала
        self.stop_event = stop_event  # Событие для остановки

    def update_waiting_counts(self, cars, pedestrians):
        self.waiting_cars = cars
        self.waiting_pedestrians = pedestrians

    def calculate_green_time(self, k1, k2):
        """Расчет времени зеленого сигнала на основе количества ожидающих автомобилей и пешеходов."""
        self.green_time = max(5, k1 * self.waiting_cars + k2 * self.waiting_pedestrians)  # Минимальное время 5 секунд
        return min(self.green_time, 15)  # Ограничение времени зеленого сигнала до 15 секунд

    def switch_to_green(self):
        self.green_signal = True
        print(f"Светофор {self.id} горит ЗЕЛЕНЫМ в течение {self.green_time} секунд.")
        time.sleep(self.green_time)  # Симуляция времени зеленого сигнала

    def switch_to_red(self):
        self.green_signal = False
        print(f"Светофор {self.id} горит КРАСНЫМ в течение {self.red_time} секунд.")
        time.sleep(self.red_time)  # Симуляция времени красного сигнала

    def run(self, k1, k2):
        while not self.stop_event.is_set():  # Проверка на остановку
            self.update_waiting_counts(random.randint(0, 10), random.randint(0, 10))  # Обновление данных
            green_time = self.calculate_green_time(k1, k2)
            # Синхронизация: только один светофор может быть зеленым одновременно
            with self.lock:
                self.green_time = green_time  # Обновляем значение green_time перед переключением
                self.switch_to_green()
                self.switch_to_red()

class TrafficLightSystem:
    def __init__(self):
        self.lock = Lock()  # Блокировка для синхронизации
        self.stop_event = Event()  # Событие для остановки потоков
        self.lights = [TrafficLight(i, self.lock, self.stop_event) for i in range(1, 5)]  # Создаем 4 светофора

    def start(self):
        k1 = 2  # Коэффициент для автомобилей
        k2 = 3  # Коэффициент для пешеходов

        # Запуск каждого светофора в отдельном потоке
        threads = []
        for light in self.lights:
            thread = Thread(target=light.run, args=(k1, k2))
            thread.start()
            threads.append(thread)

        # Запуск потока для ожидания команды остановки
        stop_thread = Thread(target=self.wait_for_stop_command)
        stop_thread.start()

        # Ожидание завершения потоков светофоров
        for thread in threads:
            thread.join(timeout=1)  # Ожидание завершения потоков

        # Убедимся, что поток ожидания остановки завершен
        stop_thread.join()

    def wait_for_stop_command(self):
        input("Нажмите Enter, чтобы остановить светофор и выйти...\n")  # Ожидание нажатия клавиши
        print("Идет остановка всех светофоров...")
        self.stop_event.set()  # Установка события остановки

if __name__ == "__main__":
    traffic_system = TrafficLightSystem()
    traffic_system.start()
