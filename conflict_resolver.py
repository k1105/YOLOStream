def calculate_min_dist(center, bboxes, threshold, min_dist_constraint=0):
    min_dist = threshold ** 2
    best_match_box_id = -1

    for i, bbox in enumerate(bboxes):
        bbox_center = bbox.center()

        dist = (center['x'] - bbox_center['x']) ** 2 + (center['y'] - bbox_center['y']) ** 2

        if dist < min_dist and dist > min_dist_constraint:
            min_dist = dist
            best_match_box_id = i

    return best_match_box_id, min_dist

def resolve_conflicts(relation, people, bboxes, threshold):
    conflict_resolved = False

    while not conflict_resolved:
        conflict_resolved = True

        for i in range(len(relation)):
            if len(relation[i]) > 1:
                conflict_resolved = False

                # 距離が最も近いpersonを選ぶ
                relation[i].sort(key=lambda x: x['dist'])
                retained_person = relation[i][0]
                pending_persons = relation[i][1:]

                relation[i] = [retained_person]

                # 保留されたpersonを他のbboxに再紐付け
                for pending in pending_persons:
                    pending_person = next((p for p in people if p.id == pending['id']), None)
                    if pending_person:
                        best_match_box_id, min_dist = calculate_min_dist(
                            pending_person.bbox.center(), bboxes, threshold, pending['dist']
                        )

                        if best_match_box_id >= 0:
                            relation[best_match_box_id].append({'id': pending['id'], 'dist': min_dist})

    return relation
