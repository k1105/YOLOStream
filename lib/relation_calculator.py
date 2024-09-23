from lib.conflict_resolver import resolve_conflicts

def update_relation(people, bboxes, threshold):
    relation = [[] for _ in range(len(bboxes))]

    for person in people:
        center = person.bbox.center()
        min_dist = threshold ** 2
        box_id = -1
        for i, bbox in enumerate(bboxes):
            bbox_center = bbox.center()

            dist = (center['x'] - bbox_center['x']) ** 2 + (center['y'] - bbox_center['y']) ** 2

            if dist < min_dist:
                min_dist = dist
                box_id = i

        if box_id >= 0:
            relation[box_id].append({'id': person.id, 'dist': min_dist})

    return resolve_conflicts(relation, people, bboxes, threshold)