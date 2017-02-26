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
    if False:
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



    # Выводим отладочные данные в excel
    if False:
        forFileRelsSeqOverall = [x for x in rels if x.relType == "relSequent"]
        forFileClearSequentTaskGroups = copy.deepcopy(clearListOfAssociations)
        utptr_to_file.writeDebugData2ToXLS(relsSeq, forFileNeatSequentTaskGroups,
                                           forFileClearSequentTaskGroups, forFileRelsSeqOverall)

    return rels
