from classes.person import Person
from classes.char_data import CharData

def update_people(relation, people, bboxes, bbox_buffer, peopleCounts, bufferedBboxCount, min_frames_for_new_person=3, max_frame_age=10, max_lost_frames=3):
    activePersonIds = set([entry['id'] for sublist in relation for entry in sublist])

    # 既存の人物を保持しつつ、lostFrameCountをインクリメントする
    for person in people:
        if person.id not in activePersonIds:
            person.lostFrameCount += 1
        else:
            person.lostFrameCount = 0  # 見つかったらリセット

    # lostFrameCountがmax_lost_framesを超えたpersonだけを削除
    people = [person for person in people if person.lostFrameCount < max_lost_frames]

    # 新しいbboxesに対する処理
    for i in range(len(relation)):
        if len(relation[i]) == 0:
            new_bbox = bboxes[i]
            found_similar = False

            # bbox_bufferの中に似ているbboxがあるか探す
            for key, buffered_data in bbox_buffer.items():
                buffered_bbox = buffered_data['bbox']
                if buffered_bbox.is_similar(new_bbox):
                    bbox_buffer[key]['count'] += 1
                    bbox_buffer[key]['frame_count'] = 0
                    found_similar = True
                    break

            if not found_similar:
                bufferedBboxCount += 1
                bbox_buffer[bufferedBboxCount] = {'bbox': new_bbox, 'count': 1, 'frame_count': 0}

            # 一定回数フレームで確認されたら新規のpersonを作成
            for key, buffered_data in bbox_buffer.items():
                if buffered_data['count'] >= min_frames_for_new_person:
                    new_person = Person(peopleCounts, {'x': 0, 'y': 0}, buffered_data['bbox'], CharData("k", 0, 0, 1), "walking")
                    people.append(new_person)
                    peopleCounts += 1
                    del bbox_buffer[key]
                    break
        elif len(relation[i]) == 1:
            person = next((p for p in people if p.id == relation[i][0]['id']), None)
            if person:
                person.update_bbox(bboxes[i])
                person.update_moving_status(200, 200)

    # 古いバッファをクリア
    bbox_buffer = {key: val for key, val in bbox_buffer.items() if val['frame_count'] < max_frame_age or val['count'] >= min_frames_for_new_person}

    # フレームごとにframe_countをインクリメント
    for key in bbox_buffer:
        bbox_buffer[key]['frame_count'] += 1

    return people, peopleCounts, bbox_buffer, bufferedBboxCount
