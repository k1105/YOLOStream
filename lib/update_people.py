from classes.person import Person

def update_people(relation, people, bboxes, bbox_buffer, peopleCounts, bufferedBboxCount, min_frames_for_new_person=3):
    activePersonIds = set([entry['id'] for sublist in relation for entry in sublist])
    people = [person for person in people if person.id in activePersonIds]

    for i in range(len(relation)):
        if len(relation[i]) == 0:
            # 新規のbboxに対する処理
            new_bbox = bboxes[i]
            found_similar = False

            # bbox_bufferの中に似ているbboxがあるか探す
            for key, buffered_data in bbox_buffer.items():
                buffered_bbox = buffered_data['bbox']
                if buffered_bbox.is_similar(new_bbox):
                    # バッファ内の既存のbboxが新しいbboxと類似している場合、カウントをインクリメント
                    bbox_buffer[key]['count'] += 1
                    found_similar = True
                    break

            if not found_similar:
                # 新規のbboxの場合はカウントをリセットして新しく追加
                bufferedBboxCount += 1
                bbox_buffer[bufferedBboxCount] = {'bbox': new_bbox, 'count': 1}

            # 一定回数フレームで確認されたら新規のpersonを作成
            for key, buffered_data in bbox_buffer.items():
                if buffered_data['count'] >= min_frames_for_new_person:
                    new_person = Person(peopleCounts, {'x': 0, 'y': 0}, buffered_data['bbox'])
                    people.append(new_person)
                    peopleCounts += 1
                    del bbox_buffer[key]
                    break  # 新規のpersonが作成されたらループを抜ける
        elif len(relation[i]) == 1:
            # 既存の人物を更新
            person = next((p for p in people if p.id == relation[i][0]['id']), None)
            if person:
                person.update_bbox(bboxes[i])

    # バッファをクリアする条件 (古いbboxを削除)
    bbox_buffer = {key: val for key, val in bbox_buffer.items() if val['count'] < min_frames_for_new_person}

    return people, peopleCounts, bbox_buffer, bufferedBboxCount
