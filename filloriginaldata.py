def CreateDictDevs(silentMode = "silent"):
    """ Создаём словарь разработчиков"""
    keys = [0, 1, 2, 3, 5]
    values = ["Petya", "Sasha", "Pasha", "Masha", "Serezha"]
    dictDevs = {k: v for (k, v) in zip(keys, values)}
    if silentMode is not "silent": print ("ID разработчиков: %s" % list(dictDevs.keys()))
    return (dictDevs)

def CreateDictPriors():
    """ Создаём словарь приоритетов """
    return ({
        0 : "Немедленный",
        1 : "Очень высокий",
        2 : "Высокий",
        3 : "Высокенький",
        4 : "Нормальный",
        5 : "Низкий"})

def CreateDictTaskTypes():
    """ Словарь типов задач """
    return ({
        1 : "Разработка",
        2 : "Поддержка",
        3 : "Ошибка"})
    
def CreateArrayLabourQuotas(keyList, silentMode = "silent"):
    """ Пока одномерный массив квот рабочих часов разработчиков - пока заполняем рандомайзером. Впоследствии будет три строки: часы основного состава, часы резерва, допустимое превышение (%). Превышение может расходоваться на задачи только очень высокого и высокого приоритетов."""
    import random
    labourHourQuotas = []
    for i in range(max(keyList)+1):
        if i in keyList:
            labourHourQuotas.append (random.choice([0, 20, 20, 20, 30, 30, 40, 40]))
        else:
            labourHourQuotas.append (0)
    if silentMode is not "silent": print ("Часы разработчиков: %s\n------------------------------" % labourHourQuotas)
    return (labourHourQuotas)