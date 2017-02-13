import csv

def writeTasks(taskList):
    with open('tasks.csv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter = ";")
        writer.writerow(["groupId", "groupImportance", "taskId", "taskPrior", "taskType", "taskEstimates", "taskScore"])
        writer.writerows(taskList)
    return()

def writeCands(filename, cands):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f, delimiter = ";")
        writer.writerow(["timeStamp", "candId", "candAddress", "numberOfTasks", "additionalTo", "lastGroupId", "checkSum"])
        for cand in cands:
            writer.writerow([cand[0], cand[1], cand[2], cand[3], cand[4], cand[5], cand[6]])







"""
    with open('eggs.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['Spam'] * 5 + ['Baked Beans'])
        spamwriter.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])
"""
