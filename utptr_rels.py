import utptr_to_file
import operator
import copy

class Relation:
# Атрибуты класса Relations:
#   type - тип: relSequent, relConcurrent, relAlternative
#   subjTaskGroupId - id группы основной задачи
#   subjTaskId - задача, к которой применима связь
#   assocTaskId - задача, с которой связана subjectTask
#   isUsed - по умолчанию False

# Суть: заводить массив relations до попыток заполнения кандидатов.
# В relations сохранять все связи.
# Для каждой связи указывается список "базовых" задач (для которых должно применяться правило связи) и условий, которые должны выполняться.
# Уникальный объект характеризуется type, subjectTaskId
# При исполнении логика такая: для дошли до задачи, ищем её среди relations. Если нашли и "использовали" relation, удаляем её из массива (или помечаем как неактивную).

    def hl(self, funcName, color="g"):
        silentMode = False
        if not silentMode:
            if color == "g":
                return ("\x1b[0;36;42m" + "(" + funcName + "):" + "\x1b[0m" + " ")
        if color == "r":
            return ("\x1b[0;36;41m" + "(" + funcName + "):" + "\x1b[0m" + " ")
        if color == "y":
            return ("\x1b[0;36;43m" + "(" + funcName + "):" + "\x1b[0m" + " ")
        if color == "b":
            return ("\x1b[0;36;44m" + "(" + funcName + "):" + "\x1b[0m" + " ")
        else:
            return ("")

    def __init__(self, relType, subjectTaskId, subjectTaskGroupId, associatedTaskId, silentMode = "silent"):
        self.relType = relType
        self.subjTaskGroupId = subjectTaskGroupId
        self.subjTaskId = subjectTaskId
        self.assocTaskId = associatedTaskId
        self.isUsed = False
        if silentMode is not "silent":
            print(self.hl("Relation.__init__", "g") + "Создана связь типа %s - %s (группа %s) - %s" % (self.relType, self.subjTaskId, self.subjTaskGroupId, self.assocTaskId))


class RelConflict:
# Атрибуты класса RelConflict:
#   taskId1, taskId2 - id задач
#   rels - массив типов связей между двумя задачами
#   description - текстовое описание

    def __init__(self, taskId1, taskId2, rels, description):
        self.taskId1 = taskId1
        self.taskId2 = taskId2
        self.rels = rels
        self.description = description


def cleanRelsFromClones(rels, silentMode = "silent"):
    for rel in reversed(rels):
        if rels.index(rel) > 0:
            for relPrev in rels[0: rels.index(rel)]:
                if (rel.relType == relPrev.relType) and (rel.subjTaskId == relPrev.subjTaskId) and (rel.assocTaskId == relPrev.assocTaskId):
                    if silentMode is not "silent":
                        print("Удаляем дубль: %s %s - %s" % (rel.relType, rel.subjTaskId, rel.assocTaskId))
                    rels.pop(rels.index(rel))
                    break
    return rels


def completeConcurrentRelations(rels, silentMode="silent"):
    # Дозаполняем массив межзадачных связей rels в случаях, подобных: (A conc B, B conc C, A not conc C)
    # Для каждой записи массива rels с типом relConcurrent делаем следующее:
    #   - создаём список, в который включаем subjTaskId и assocTaskId
    #   - прогоняем в цикле все остальные записи массива
    #   - если среди остальных записей находится такая relConcurrent, что у неё только один элемент соответствует
    #       имеющимся в листе (а второй не соответствует), добавляем отсутствующий элемент в лист
    #   - гоняем циклы до тех пор, пока не будет одного полного прохода, в котором не добавили ни один элемент
    #   - в получившемся списке для группы одновременных задач удаляем дублирующиеся taskId
    #   - делаем это для всех групп одновременных задач, формируем из них массив neatListOfAssociations
    #   - удаляем дубликаты из массива neatListOfAssociations, получаем clearListOfAssociations
    #   - чистим rels от всех записей с типом relConcurrent
    #   - вместо старых записей для каждого элемента clearListOfAssociations заводим новые записи в rels
    #   - возвращаем rels

    relsConc = [x for x in rels if x.relType == "relConcurrent"]

    neatListOfAssociations = []
    # Массив, каждый элемент которого - список задач, имеющих прямую или косвенную связь relConcurrent
    forFileNeatConcurrentTaskGroups = []

    for rel in relsConc:
        assocTaskIds = [rel.subjTaskId, rel.assocTaskId]
        # Формируем элемент, который потом будет добавлен в массив neatListOfAssociations

        areAllTasksInList = False
        while not areAllTasksInList:
            areAllTasksInList = True
            for rel1 in relsConc:
                if operator.xor((rel1.subjTaskId in assocTaskIds), (rel1.assocTaskId in assocTaskIds)):
                    if rel1.subjTaskId in assocTaskIds:
                        assocTaskIds.extend([rel1.assocTaskId])
                    else:
                        assocTaskIds.extend([rel1.subjTaskId])
                    areAllTasksInList = False
        neatListOfAssociations.append(sorted(assocTaskIds))
        forFileNeatConcurrentTaskGroups.append(sorted(assocTaskIds))

    clearListOfAssociations = []
    # clearListOfAssociations - это neatListOfAssociations, очищенный от дублирующихся элементов
    for assocTaskIds in neatListOfAssociations:
        if assocTaskIds not in clearListOfAssociations:
            clearListOfAssociations.append(assocTaskIds)
    del neatListOfAssociations

    # Удаляем все элементы из исходного массива rels, которые совпадают с элементами overall массива
    for rel in reversed(rels):
        for assocTaskIds in clearListOfAssociations:
            if (rel.relType == "relConcurrent") and (rel.subjTaskId in assocTaskIds) and (rel.assocTaskId in assocTaskIds):
                rels.pop(rels.index(rel))
                break

    # Наполняем исходный массив (который будет отдан наружу из функции) элементами, формируемыми из overall массива
    for assocTaskIds in clearListOfAssociations:
        for i in range(len(assocTaskIds) - 1):
            for j in range(i + 1, len(assocTaskIds)):
                rels.append(
                    Relation("relConcurrent", assocTaskIds[i], -1, assocTaskIds[j], silentMode))
                rels.append(
                    Relation("relConcurrent", assocTaskIds[j], -1, assocTaskIds[i], silentMode))

    # Выводим отладочные данные в excel
    if True:
        forFileRelsConcOverall = [x for x in rels if x.relType == "relConcurrent"]
        forFileClearConcurrentTaskGroups = copy.deepcopy(clearListOfAssociations)
        utptr_to_file.writeDebugData1ToXLS(relsConc, forFileNeatConcurrentTaskGroups,
                                           forFileClearConcurrentTaskGroups, forFileRelsConcOverall)

    return rels


def completeSequentRelations(rels, silentMode="silent"):
    # Дозаполняем массив межзадачных связей rels в случаях, подобных: (A seq B, B seq C, A not seq C)
    # Для каждой записи массива rels с типом relSequent делаем следующее:
    #   - берём subjTaskId и assocTaskId, ищем связь relSequent, в которой assocTaskId будет выступать как subjTaskId
    #   - если находим такую, то создаём связь первого subjTaskId и второго assocTaskId
    #       (при условии, что ранее её не сущестовало)
    #   - повторяем проходы по relsSeq до тех пор, пока не случится один проход, в ходе которого
    #       ни одной новой связи не добавили
    #   - добавляем в rels недостающие связи (или удаляем все, а потом заново создаём ???)
    #   - возвращаем rels

    relsSeq = [x for x in rels if x.relType == "relSequent"]

    neatListOfAssociations = []
    forFileNeatSequentTaskGroups = []

    for rel in relsSeq:
        assocTaskIds = [rel.subjTaskId, rel.assocTaskId]

        areAllTasksInList = False
        while not areAllTasksInList:
            areAllTasksInList = True
            for rel1 in relsSeq:
                if (rel1.subjTaskId == assocTaskIds[0]) and (not rel1.assocTaskId in assocTaskIds[1:]):
                    # Случай, когда найден второй и последующий предшественник rel.subjTaskId
                    # Добавляем предшественника в группу
                    assocTaskIds.extend([rel1.assocTaskId])
                    areAllTasksInList = False
                if (rel1.subjTaskId in assocTaskIds[1:]) and (not rel1.assocTaskId in assocTaskIds):
                    # Случай, когда нашли связь, в которой предшественник первой связи является последователем второй
                    # Добавляем предшественника второй связи в группу предшественников первой
                    # Проверяем при этом, что предшественник второй не равен главному последователю
                    assocTaskIds.extend([rel1.assocTaskId])
                    areAllTasksInList = False

        neatListOfAssociations.append([assocTaskIds[0]]+sorted(assocTaskIds[1:]))
        forFileNeatSequentTaskGroups.append([assocTaskIds[0]]+sorted(assocTaskIds[1:]))

    clearListOfAssociations = []
    # clearListOfAssociations - это neatListOfAssociations, очищенный от дублирующихся элементов
    for assocTaskIds in neatListOfAssociations:
        if assocTaskIds not in clearListOfAssociations:
            clearListOfAssociations.append(assocTaskIds)
    del neatListOfAssociations

    # Удаляем все элементы из исходного массива rels, которые совпадают с элементами overall массива
    for rel in reversed(rels):
        for assocTaskIds in clearListOfAssociations:
            if (rel.relType == "relSequent") and (rel.subjTaskId == assocTaskIds[0]) and (rel.assocTaskId in assocTaskIds[1:]):
                rels.pop(rels.index(rel))
                break

    # Наполняем исходный массив (который будет отдан наружу из функции) элементами, формируемыми из overall массива
    for assocTaskIds in clearListOfAssociations:
        for i in range(1, len(assocTaskIds)):
            rels.append(Relation("relSequent", assocTaskIds[0], -2, assocTaskIds[i], silentMode))

    # Выводим отладочные данные в excel
    if True:
        forFileClearSequentTaskGroups = copy.deepcopy(clearListOfAssociations)
        forFileRelsSeqOverall = [x for x in rels if x.relType == "relSequent"]
        utptr_to_file.writeDebugData2ToXLS(relsSeq, forFileNeatSequentTaskGroups, forFileClearSequentTaskGroups, forFileRelsSeqOverall)

    return rels


def validateRels(taskIds, rels):
    # Бесконфликтные сценарии:
    #   - (A alt B) and (B alt A) == True
    #   - (A conc B) and (B conc A) == True
    #   - (A seq B) xor (B seq A) == True
    #   - ((A alt B) or (B alt A)) xor ((A conc B) or (B conc A)) == True
    #   - ((A conc B) or (B conc A)) xor ((A seq B) or (B seq A)) == True
    relConflictsArray = []
    
    for taskId1 in taskIds[:(len(taskIds)-1)]:
        for taskId2 in taskIds[(taskIds.index(taskId1)+1):]:
            relsForCouple = [x for x in rels if (
                ((taskId1 == x.subjTaskId) and (taskId2 == x.assocTaskId)) or
                ((taskId2 == x.subjTaskId) and (taskId1 == x.assocTaskId))
            )]
            if len([x.relType for x in relsForCouple if x == "relAlternative"]) not in [0, 2]:
                relConflictsArray.append(RelConflict(taskId1, taskId2, [x.relType for x in relsForCouple],
                                                     "кол-во relAlternative не 0 и не 2"))
            if len([x.relType for x in relsForCouple if x == "relConcurrent"]) not in [0, 2]:
                relConflictsArray.append(RelConflict(taskId1, taskId2, [x.relType for x in relsForCouple],
                                                     "кол-во relConcurrent не 0 и не 2"))
            if len([x.relType for x in relsForCouple if x == "relSequent"]) not in [0, 1]:
                relConflictsArray.append(RelConflict(taskId1, taskId2, [x.relType for x in relsForCouple],
                                                     "кол-во relSequent не 0 и не 1"))
            if ("relAlternative" in [x.relType for x in relsForCouple]) and\
                    ("relConcurrent" in [x.relType for x in relsForCouple]):
                relConflictsArray.append(RelConflict(taskId1, taskId2, [x.relType for x in relsForCouple],
                                                     "одновременно relConcurrent и relAlternative"))
            if ("relConcurrent" in [x.relType for x in relsForCouple]) and\
                    ("relSequent" in [x.relType for x in relsForCouple]):
                relConflictsArray.append(RelConflict(taskId1, taskId2, [x.relType for x in relsForCouple],
                                                     "одновременно relConcurrent и relSequent"))

    return relConflictsArray