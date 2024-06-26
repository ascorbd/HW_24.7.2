from api import PetFriends
from settings import valid_email, valid_password, invalid_email, invalid_password #в .env и settings внесены дополнительные параметры
import os

pf = PetFriends()

#1
def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result

#2
def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0

#3
def test_add_new_pet_with_valid_data(name='Барбоскин', animal_type='двортерьер',
                                     age='4', pet_photo='images/2.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name

#4
def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()

#5
def test_successful_update_self_pet_info(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")

#6
def test_add_new_pet_simple_with_valid_data(name='Трэши', animal_type='нечто', age='1'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name

#7
def test_api_add_photo_of_pet(pet_photo='images/1.jpg'):
    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    pet_id = my_pets['pets'][0]['id']

    # Если список не пустой, то пробуем обновить фотографию
    if len(my_pets['pets']) > 0:
        status, result = pf.set_photo(auth_key, pet_id, pet_photo)
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
                # Проверяем что статус ответа = 200 и фото присутствует
        assert status == 200
        assert result['pet_photo'] == my_pets['pets'][0]['pet_photo']
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


#Добавляем дополнительные проверки
#8 Добавление питомца с некорректными данными(ожидаем ошибку 400, т.к. возвраст указан в текстовом формате, по документации API, должно быть число)
def test_add_new_pet_simple_with_invalid_data(name="House", animal_type='Doctor', age='toomuch'):
    """Проверяем что можно добавить питомца с некорректными данными"""

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 400


#9 Проверка на ввод некорректного логина и пароля(усложненная реализация, проверяет код 200, после чего проверяет на код 403 и возвращает ошибку. В случае указания корректных данных выполняется проверка по коду 200
def test_get_api_key_for_invalid_user(email=invalid_email, password=invalid_password):
    """ Задаем неверный логин/пароль и Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key, а случае ошибки возвращает сообщение о неверном логине/пароле"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    #Сверяем статус код запроса, если статус код не равен 200(SUCCESS), проверяем соответствие статуса ошибке авторизации(код 403), выводим ошибку по логину/паролю
    if status != 200:
        assert status == 403
        assert 'key' not in result
        raise Exception('Неверный логин/пароль')
    #В случае ввода корреткных данных возвращаем токен авторизации
    else:
        assert status == 200
        assert 'key' in result

#10 Согласно документации API, допустимы только форматы JPG, JPEG, PNG форматы. Подставляем недокументированный формат файла, тест возвращает 200ый статус, ожидаемый код 400(Баг!)
def test_api_add_photo_of_pet_unsupported_format(pet_photo='images/3.bmp'):
    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    pet_id = my_pets['pets'][0]['id']

    # Если список не пустой, то пробуем обновить фотографию
    if len(my_pets['pets']) > 0:
        status, result = pf.set_photo(auth_key, pet_id, pet_photo)
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
                # Проверяем что статус ответа = 400
        assert status == 400
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")

#11 В случае, если производится попытка отправить объект не в графическом формате, возвращается ошибка 500(Сервер не может обработать вложение), вместо ошибки 400, что является багом.
def test_api_add_photo_of_pet_unsupported_format2(pet_photo='images/2.pdf'):
    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    pet_id = my_pets['pets'][0]['id']

    # Если список не пустой, то пробуем обновить фотографию
    if len(my_pets['pets']) > 0:
        status, result = pf.set_photo(auth_key, pet_id, pet_photo)
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
                # Проверяем что статус ответа = 400
        assert status == 400
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")

#12 Удаление несуществующего питомца, пытаемся удалить несуществующего питомца(на уч.записи все питомцы удалены),
# запрашивается вывод питомцев без фильтра по моим, и производится попытка удаления питомца, код 200 на выходе, вероятно критический баг, позволяет удалять питомцев других пользователей
def test_successful_delete_uncreated_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key)

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
      _, my_pets = pf.get_list_of_pets(auth_key)

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key)

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 400
    assert pet_id not in my_pets.values()


#13 Пытаемся удалить питомца с несуществующим ID(Запрос отрабатывается, хотя должно приходить исключение(ID не найден)
def test_successful_delete_id_pet(pet_id='01234567-8901-1234-5678-901234567890'):
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/3.bmp")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 400
    assert pet_id not in my_pets.values()
#14 Проверяем возможность обновления данных о питомце некорректными данными(Ожидаем код 400, имя указано в числовом значении, а должен быть текст)
def test_failed_update_self_pet_info(name=555, animal_type='Skunk', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 400
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")
#15 Попытка обновления фотографии у несуществующего питомца(ожидаем код 400, на выходе 500)
def test_api_add_photo_uncreated_pet(pet_id='01234567-8901-1234-5678-901234567890', pet_photo='images/1.jpg'):
    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Если список не пустой, то пробуем обновить фотографию
    if len(my_pets['pets']) > 0:
        status, result = pf.set_photo(auth_key, pet_id, pet_photo)
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
                # Проверяем что статус ответа = 400 и фото присутствует
        assert status == 400
        assert result['pet_photo'] == my_pets['pets'][0]['pet_photo']
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


