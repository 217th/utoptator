# https://www.tutorialspoint.com/python/

from filloriginaldata import (createDictDevs, createDictPriors, createDictTaskTypes, createArrayLabourQuotas)
import utptr_log as log
import copy
import random
import utptr_classes
import utptr_from_file
import utptr_to_file
import utptr_rels
import datetime

print("----- (%s) Начало программы -----" % datetime.datetime.now().strftime("%H:%M:%S.%f"))
log.general('program launched')

silentMode = "babble"  # Режим тишины. "silent" - сокращённые сообщения. "babble" - полные сообщения
dictTaskTypes = createDictTaskTypes()
dictPriors = createDictPriors()
# dictDevs = createDictDevs(silentMode)
# listLabourHoursQuotas = createArrayLabourQuotas(list(dictDevs.keys()), silentMode)

print("----- (%s) Импортируем разработчиков -----" % datetime.datetime.now().strftime("%H:%M:%S.%f"))
initialDevsArray = utptr_from_file.readDevs(4, 28)
for dev in initialDevsArray:
    print(dev.devId, dev.devName, dev.devType, dev.hoursPrimary, dev.hoursSecondary, dev.hoursExcess)


def сreateTasksArray(n, silentMode="silent"):
    tasksArray = []
    if n > 0:
        for i in range(n):
            task = utptr_classes.Task(dictPriors, dictTaskTypes, initialDevsArray, silentMode)
            tasksArray.append(task)
        for task in tasksArray:
            task.setRandomRelations(tasksArray, silentMode)
    else:
        print('Попросили слишком мало задач. Массив задач не заполнен.')
    return (tasksArray)


print("----- (%s) Создаём задачи -----" % datetime.datetime.now().strftime("%H:%M:%S.%f"))
originalTasksArray = сreateTasksArray(10, "silent")
log.general('list of %s tasks is created' % len(originalTasksArray))

taskGroups = []
i = 0

'''
for groupMeta in [     # ТЕСТОВЫЙ НАБОР МЕТАДАННЫХ
    [[2], [0], "h"], [[2], [1], "h"], [[2], [2], "n"],
    [[3, 1], [5], "l"]
    ]:
        taskGroups.append(utptr_classes.Group(i, groupMeta[0], groupMeta[1], groupMeta[2]))
        i += 1
del groupMeta
'''

for groupMeta in [  # ПРОМЫШЛЕННЫЙ НАБОР МЕТАДАННЫХ
    [[2], [0], "h"], [[2], [1], "h"], [[2], [2], "h"], [[2], [3], "n"], [[2], [4], "n"], [[2], [5], "l"],
    # Вся поддержка
    [[3], [0], "h"], [[1], [0], "h"], [[3], [1], "h"], [[1], [1], "h"], [[3], [2], "h"], [[1], [2], "h"],
    # Немедл., оч. выс., выс. - сначала ошибки, потом разработка
    [[3, 1], [3], "n"],  # Высокенький - ошибки и разработка в одной группе
    [[3, 1], [4], "n"],  # Нормальный - ошибки и разработка в одной группе
    [[3, 1], [5], "l"]  # Низкий - ошибки и разрбаботка в одной группе
    ]:
        taskGroups.append(utptr_classes.Group(i, groupMeta[0], groupMeta[1], groupMeta[2], "bubble"))
        i += 1
del groupMeta

log.general('start distributing tasks by groups')
print("----- (%s) Распределяем задачи по группам -----" % datetime.datetime.now().strftime("%H:%M:%S.%f"))
for group in taskGroups:
    group.fillAndSort(originalTasksArray, "babble")

def createOverallRelationsArray(silentMode = "silent"):
    # Временная функция для заполнения массива связей тестовыми данными
    relsNeatArray = []
    for group in taskGroups:
        for task in group.tasks:
            if task.relAlternative:
                for assocTaskId in task.relAlternative:
                    relsNeatArray.append(utptr_rels.Relation("relAlternative", task.taskId, group.groupId, assocTaskId, silentMode))
            if task.relConcurrent:
                for assocTaskId in task.relConcurrent:
                    relsNeatArray.append(utptr_rels.Relation("relConcurrent", task.taskId, group.groupId, assocTaskId, silentMode))
            if task.relSequent:
                for assocTaskId in task.relSequent:
                    relsNeatArray.append(utptr_rels.Relation("relSequent", task.taskId, group.groupId, assocTaskId, silentMode))

    relsNeatArray = utptr_rels.cleanRelsFromClones(relsNeatArray)
    relsNeatArray = utptr_rels.completeConcurrentRelations(relsNeatArray)
    relsNeatArray = utptr_rels.completeSequentRelations(relsNeatArray)

    return relsNeatArray

print("----- (%s) Заполняем связи между задачами -----" % datetime.datetime.now().strftime("%H:%M:%S.%f"))
originalRelsArray = createOverallRelationsArray("silent")
print("----- (%s) Валидируем связи между задачами -----" % datetime.datetime.now().strftime("%H:%M:%S.%f"))
originalRelsConflictArray = utptr_rels.validateRels([x.taskId for x in originalTasksArray], originalRelsArray)


if originalRelsConflictArray:
    for relConflict in originalRelsConflictArray:
        relConflict.print()

else:
    print("Валидация пройдена. Связи между задачами - бесконлфиктные.")
    log.general('no conflict in relations')
    del originalRelsConflictArray

    # Логирование сделано до этого момента

    if any(len(x.tasks) > 0 for x in taskGroups):
        candId = -1
        cands = []
        forFileRawCandMetaArray = list()
        forFileRawCandTasksArray = list()


        def cleanCandsFromClones(cands, silentMode="silent"):
            for cand in reversed(cands):
                if cands.index(cand) > 0:
                    for candPrev in cands[0: cands.index(cand)]:
                        if (round(cand.checkSum, 1) == round(candPrev.checkSum, 1)) and\
                                (cand.lastGroupId == candPrev.lastGroupId) and\
                                (cand.additionalTo == candPrev.additionalTo):
                            log.cand(cand.candId, 'deleting candidate because it\'s equal to...', candPrev.candId)
                            '''
                            if silentMode is not "silent":
                                print("Дубли | id %s, checkSum %s, lastGroup %s | id %s, checkSum %s, lastGroup %s" % (
                                cand.candId, cand.checkSum, cand.lastGroupId, candPrev.candId, candPrev.checkSum,
                                candPrev.lastGroupId))
                            '''
                            for i, j in enumerate(forFileRawCandMetaArray):
                                if j[1] == cand.candId:
                                    forFileRawCandMetaArray[i].append("del")
                            cands.pop(cands.index(cand))
                            break
            return cands


        def fillSingleCand(group, basicCand, method, silentMode="silent"):
            # Создание кандидата - входы:
            #   - целочисленный идентификатор для нового кандидата
            #   - объект класса Group (включая и задачи, отнесённые к группе)
            #   - объект класса Candidate, являющийся "базовым" для нового
            #   - метод заполнения кандидата
            #   - квоты часов разработки (если отсутствует базовый кандидат)
            #   - массив с данными о связях задач (если отсутствует базовый кандидат)
            #   - массив со всеми задачами (применяется при обработке связей)
            # Создание кандидата - выходы:
            #   - новый объект класса Candidate
            #   - forFileRawCandTasks - список задач в кандидате для экспорта в файл
            #   - forFileCandMeta - метаданные кандидата для экспорта в файл

            global candId
            candId += 1

            # Создаём объект newCand, который потом добавим в массив cands
            # Вся логика по наполнению кандидата задачами - в Candidate.__init__
            newCand = utptr_classes.Candidate(
                candId,
                group,
                basicCand,
                method,
                initialDevsArray,
                originalRelsArray,
                originalTasksArray,
                silentMode
            )

            # Заполняем мета-информацию о сырых кандидатах для вывода в файл
            if newCand.additionalTo:
                forFileAddTo = 'addTo '+str(newCand.additionalTo.candId)
            else:
                forFileAddTo = False
            forFileCandMeta = list([
                forFileAddTo,
                newCand.candId,
                newCand.lastGroupId,
                round(newCand.checkSum, 1),
                'amnt '+str(len(newCand.tasks)),
                [x.hoursPrimary for x in newCand.hoursUnused],
                method])

            # Заполняем мета-информацию о задачах, вошедших в сырой кандидат, для вывода в файл
            forFileRawCandTasks = list()
            for task in newCand.tasks:
                forFileRawCandTasks.append([
                    newCand.candId,
                    newCand.lastGroupId,
                    task.taskId,
                    task.taskPrior,
                    task.taskType,
                    [x.hours for x in task.taskEstimates],
                    round(task.taskScore, 1),
                    task.relConcurrent,
                    task.relAlternative,
                    task.relSequent
                ])

            # Операции с глобальными объектами - кандидаты на вынос из функции
            global cands
            cands.append(newCand)
            global forFileRawCandTasksArray
            forFileRawCandTasksArray.extend(forFileRawCandTasks)
            global forFileRawCandMetaArray
            forFileRawCandMetaArray.append(forFileCandMeta)

            return ()


        def fillCandsWithTasksFromSpecificGroupAndOnSpecificBasicCand(group, basicCand, silentMode="silent"):
            global cands
            if group.importance == "h":
                fillSingleCand(group, basicCand, "direct", silentMode)
                completelyIn = cands[-1].isGroupCompletelyIn(group)
                if not completelyIn:
                    for i in range(len(group.tasks) + 1): fillSingleCand(group, basicCand, "scroll", silentMode)
                    for i in range(len(group.tasks) * 2): fillSingleCand(group, basicCand, "shuffle", silentMode)
            elif group.importance == "n":
                fillSingleCand(group, basicCand, "direct", silentMode)
                completelyIn = cands[-1].isGroupCompletelyIn(group)
                if not completelyIn:
                    for i in range(len(group.tasks) + 1): fillSingleCand(group, basicCand, "scroll", silentMode)
                    for i in range(len(group.tasks) + 1): fillSingleCand(group, basicCand, "shuffle", silentMode)
            elif group.importance == "l":
                fillSingleCand(group, basicCand, "direct", silentMode)
                completelyIn = cands[-1].isGroupCompletelyIn(group)
                if not completelyIn:
                    for i in range(len(group.tasks) + 1): fillSingleCand(group, basicCand, "shuffle", silentMode)


        for i, group in enumerate(taskGroups):
            log.group(group.groupId, 'start creating candidates for group', '')
            print("----- (%s) Формируем кандидатов для группы %s -----" % (
                datetime.datetime.now().strftime("%H:%M:%S.%f"),
                group.groupId)
                  )
            if i is 0:
                fillCandsWithTasksFromSpecificGroupAndOnSpecificBasicCand(group, False, silentMode)
                cands = cleanCandsFromClones(cands, "silent")
            else:
                for basicCand in cands:
                    if (basicCand.lastGroupId + 1 == group.groupId) and (not basicCand.isUsed):
                        fillCandsWithTasksFromSpecificGroupAndOnSpecificBasicCand(group, basicCand, silentMode)
                        basicCand.isUsed = True
                        cands = cleanCandsFromClones(cands, "silent")

        # ▼▼▼▼▼▼▼ Склейка в один проход, удаление всех кандидатов, заканчивающихся непоследней группой,▼▼▼▼▼▼▼
        candsAssembled = copy.deepcopy(cands)
        print("----- (%s) Склеиваем кандидатов -----" % datetime.datetime.now().strftime("%H:%M:%S.%f"))
        log.general('start gluing the candidates last to first')
        for i in range(len(taskGroups)):
            for cand in reversed(candsAssembled):
                log.cand(cand.candId, 'start gluing the candidate. pass...', i)
                if cand.additionalTo:
                    # Приклеиваем к более позднему всё из более раннего
                    # hoursUnused остаётся от позднего
                    # lastGroupId остаётся от позднего
                    cand.tasks.extend(cand.additionalTo.tasks)
                    cand.checkSum += cand.additionalTo.checkSum
                    cand.additionalTo = cand.additionalTo.additionalTo

        candsAssembled.sort(key=lambda x: x.lastGroupId, reverse=True)
        for cand in reversed(candsAssembled):
            if cand.lastGroupId < taskGroups[-1].groupId:
                candsAssembled.pop(candsAssembled.index(cand))
                log.cand(cand.candId, 'deleting candidate glued to the major. last group is...', cand.lastGroupId)

        candsAssembled = cleanCandsFromClones(candsAssembled, "silent")
        # ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

        print("----- (%s) После склейки: -----" % datetime.datetime.now().strftime("%H:%M:%S.%f"))
        for cand in candsAssembled:
            log.cand(cand.candId, 'candidate still alive after the gluing and cleaning clones')
            cand.print()

        # ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼ Заполнение всего необходимого для экспорта в excel ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼

        log.general('start preparing data for export to excel')
        print("----- (%s) Готовим данные для вывода в файл -----" % datetime.datetime.now().strftime("%H:%M:%S.%f"))
        # Заполнение исходного списка задач для экспорта в файл
        forFileTasksList = []
        for group in taskGroups:
            for task in group.tasks:
                forFileTasksList.append([
                    group.groupId,
                    group.importance,
                    task.taskId,
                    task.taskPrior,
                    task.taskType,
                    [x.hours for x in task.taskEstimates],
                    round(task.taskScore, 1),
                    task.relConcurrent,
                    task.relAlternative,
                    task.relSequent
                ])

        # Заполнение массива межзадачных связей для экспорта в файл
        forFileRelsList = []
        for rel in originalRelsArray:
            forFileRelsList.append([
                rel.relType,
                rel.subjTaskId,
                rel.subjTaskGroupId,
                rel.assocTaskId
            ])

        # Заполнение списка настроек попытки для экспорта в файл
        forFileTrySettings = list()
        forFileTrySettings.append(initialDevsArray)

        forFileRawCandOnlyActiveArray = list()
        for record in forFileRawCandMetaArray:
            if 'del' in record:
                pass
            else:
                if record[0] == False:
                    record[0] = ""
                forFileRawCandOnlyActiveArray.append(record)

        # Заполнение массива с мета-информацией по финальным склеенным кандидатам для экспорта в файл
        forFileFinalCandMetaArray = []
        for cand in candsAssembled:
            forFileFinalCandMetaArray.append([
                cand.candId,
                len(cand.tasks),
                round(cand.getScore(), 1),
                [x.hoursPrimary for x in cand.hoursUnused],
                round(cand.checkSum, 1)])

        # Заполнение массива с подробной информацией о задачах, вошедших в финальные кандидаты, для экспорта в файл
        forFileFinalCandsTasksList = []
        for cand in candsAssembled:
            forFileSingleFinalCandTasksList = []
            for task in cand.tasks:
                forFileSingleFinalCandTasksList.append([
                    cand.candId,
                    len(cand.tasks),
                    round(cand.getScore(), 1),
                    [x.hoursPrimary for x in cand.hoursUnused],
                    round(cand.checkSum, 1),
                    task.taskId,
                    task.taskPrior,
                    task.taskType,
                    [x.hours for x in task.taskEstimates],
                    task.taskScore,
                    task.relConcurrent,
                    task.relAlternative,
                    task.relSequent
                    ])
            forFileFinalCandsTasksList.append(forFileSingleFinalCandTasksList)

        forFileFinalCandsRelsList = []
        for cand in candsAssembled:
            for rel in cand.rels:
                forFileFinalCandsRelsList.append([
                    cand.candId,
                    rel.relType,
                    rel.subjTaskId,
                    rel.assocTaskId,
                    rel.isActive
                ])

    # ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

        # Экспорт в excel
        log.general('start exporting to excel')
        print("----- (%s) Выводим в файл -----" % datetime.datetime.now().strftime("%H:%M:%S.%f"))
        utptr_to_file.writeReportToXLS(
            forFileTrySettings,
            forFileTasksList,
            forFileRelsList,
            forFileRawCandMetaArray,
            forFileRawCandOnlyActiveArray,
            forFileRawCandTasksArray,
            forFileFinalCandMetaArray,
            forFileFinalCandsTasksList,
            forFileFinalCandsRelsList
        )
        print("----- (%s) Экспорт завершён -----" % datetime.datetime.now().strftime("%H:%M:%S.%f"))

    else:
        print("Все группы задач пусты.")

    log.general('program finished')
