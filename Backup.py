
import vk_api
import requests
from datetime import datetime
import json

def get_all_photos_vk(user_id, vk_session):
    try:
        # Получаем все фотографии пользователя VK
        photos = []
        offset = 0
        while True:
            # response = vk_session.method("photos.getAll", {"owner_id": user_id, "offset": offset})
            response = vk_session.method("photos.get", {"owner_id": user_id, "album_id": "profile", "extended": 1})
            if response and "items" in response:
                photos.extend(response["items"])
                if len(response["items"]) < 200:  # максимальное количество фотографий в одном запросе - 200
                    break
                offset += 200
            else:
                print("Ошибка при получении фотографий VK: Ответ от VK API не содержит ожидаемых данных")
                return None
        return photos
    except vk_api.exceptions.ApiError as e:
        # Обработка ошибок VK API
        print("Ошибка при получении фотографий VK:", e)
        return None
    except Exception as ex:
        # Обработка других исключений
        print("Произошла ошибка:", ex)
        return None

def create_folder_yandex_disk(folder_name, token):
    try:
        # Проверяем существует ли папка на Яндекс.Диске
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = {"Authorization": f"OAuth {token}"}
        params = {"path": f"/{folder_name}"}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            print(f"Папка '{folder_name}' уже существует на Яндекс.Диске")
            return True
        elif response.status_code == 404:
            # Создаем папку на Яндекс.Диске, если ее нет
            response = requests.put(url, headers=headers, params=params)
            if response.status_code == 201:
                print(f"Папка '{folder_name}' успешно создана на Яндекс.Диске")
                return True
            else:
                print(f"Ошибка при создании папки '{folder_name}' на Яндекс.Диске:", response.text)
                return False
        else:
            print(f"Ошибка при проверке существования папки '{folder_name}' на Яндекс.Диске:", response.text)
            return False
    except Exception as ex:
        # Обработка других исключений
        print("Произошла ошибка при проверке существования папки на Яндекс.Диске:", ex)
        return False

def upload_photos_to_yandex_disk(photos, folder_name, token):
    uploaded_photos_info = []  # Список для хранения информации о загруженных фотографиях
    try:
        # Загружаем фотографии в папку на Яндекс.Диске
        for photo in photos:
            url = photo["sizes"][-1]["url"]  # берем URL фотографии максимального размера
            response = requests.get(url)
            if response.status_code == 200:
                file_name = f"{photo['likes']['count']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                upload_url = f"https://cloud-api.yandex.net/v1/disk/resources/upload?path=/{folder_name}/{file_name}"
                headers = {"Authorization": f"OAuth {token}"}
                upload_response = requests.get(upload_url, headers=headers)
                upload_data = upload_response.json()
                if "href" in upload_data:
                    upload_href = upload_data["href"]
                    upload_file = requests.put(upload_href, data=response.content)
                    if upload_file.status_code == 201:
                        print(f"Фотография успешно загружена на Яндекс.Диск: {file_name}")
                                                # Добавляем информацию о загруженной фотографии в список
                        uploaded_photos_info.append({
                            "file_name": file_name,
                            "size": photo["sizes"][-1]["type"]  # сохраняем реальный размер фото
                        })
                    else:
                        print(f"Ошибка загрузки фотографии на Яндекс.Диск: {file_name}", upload_file.text)
                else:
                    print(f"Ошибка получения ссылки для загрузки фотографии на Яндекс.Диск: {file_name}")
            else:
                print(f"Ошибка загрузки фотографии: Не удалось получить доступ к {url}")
    except Exception as ex:
        # Обработка других исключений
        print("Произошла ошибка при загрузке на Яндекс.Диск:", ex)
    finally:
        # Сохраняем информацию о загруженных фотографиях в JSON-файл
        if uploaded_photos_info:
            try:
                with open("uploaded_photos_info.json", "w") as json_file:
                    json.dump(uploaded_photos_info, json_file, indent=4)
                print("Информация о загруженных фотографиях сохранена в файле 'uploaded_photos_info.json'")
            except Exception as ex:
                print("Ошибка при сохранении информации о загруженных фотографиях:", ex)

def main():
    # Ввод данных от пользователя
    vk_user_id = input("Введите ID пользователя VK: ")
    yandex_disk_token = input("Введите токен с Полигона Яндекс.Диска: ")
    yandex_disk_folder_name = input("Введите имя папки на Яндекс.Диске для загрузки фотографий: ")

    # Авторизация в VK
    vk_session = vk_api.VkApi(token='vk1.a.grxtir1WBSFrHn144G11ANqTsERzGjBlGe4zMu0MgxOiJTKJSYenbZ8GZG8mpIp5CAU4h3so3J8bhwglnkvhLPiUaxKmVaPIJ9kuW-8WsH1qqEDO5k3w-ZdSVEzhwY2mZjJkvBNi1u824NS9L6zHRS92z0FdJG8uJEf5oeFzvcYJyD2TmoRDiqB9zeDUbFBd')

    # Получение всех фотографий пользователя VK
    photos = get_all_photos_vk(vk_user_id, vk_session)
    if photos:
        # Создание папки на Яндекс.Диске или проверка существования папки
        if create_folder_yandex_disk(yandex_disk_folder_name, yandex_disk_token):
            # Загрузка фотографий в папку на Яндекс.Диске
            upload_photos_to_yandex_disk(photos, yandex_disk_folder_name, yandex_disk_token)
    else:
        print("Не удалось получить фотографии пользователя VK")

if __name__ == "__main__":
    main()
